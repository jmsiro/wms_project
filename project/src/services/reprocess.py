from ..logs.logs import logger
from ..database.db import DbInstance
from .rates import RatesService
from datetime import datetime, timedelta
from sqlalchemy.orm import sessionmaker

logger = logger.getLogger("REPROCESS")

class BillReprocessor:
    def __init__(self, db: DbInstance, test:bool=False):
        self.db = db 
        self.test = test

    def _calculate_amounts(self, invoice_shipments:list, invoice_items: list, current_rates: dict, dry_run:bool, invoice_status:str, session:sessionmaker) -> dict:
        # Initializing amounts to be compared
        amounts = {
            "current": {item[0]: float(item[1]) for item in invoice_shipments}, 
            "new": {"NATIONAL": 0, "INTERNATIONAL": 0}
        }
        # Calculate new amounts using current rates
        for item in invoice_items:
            shipment_type = self.db.get_shipment_type_name(item.shipment_type_id, session)
            shipment_type_name = shipment_type[0]
            amounts["new"][shipment_type_name] += current_rates[shipment_type_name] * item.quantity
           
            # Update items data for "No Dry Run" & Unpaid invoices 
            if not dry_run and invoice_status == "UNPAID":
                item.unit_price = current_rates[shipment_type_name]
                item.amount = current_rates[shipment_type_name] * item.quantity
        return amounts
    
    def _response_handler(self, result:dict, session:sessionmaker) -> dict:
        logger.info("Committing changes...")
        try:
            self.db.commit_changes(session) 
            result["data"]["updated"] = True
            result["message"] = "Invoice updated"
        except Exception as e:
            logger.error("Error updating invoice:\n" + e.__str__())
            result["message"] = "Error updating invoice"
            self.db.rollback_changes(session)
        return result

    def reprocess_invoice(self, account_id:int, invoice_number:str, dry_run:bool=True, session:sessionmaker=None) -> None:
        """
        Reprocess an invoice to get new amount per shipment type.
        Args:
            account_id (int): Id of the cutomer account related to the invoice.
            invoice_number (str): Invoice number to reprocess.
            dry_run (bool, optional): Defines if the reprocess will commit the changes or not. Defaults to True.
        """
        if not self.test:
            session = self.db.get_session()
       
        #  Check if account exists
        if not self.db.account_exists(account_id, session):
            logger.error(f"Account Id # {account_id} not found")
            self.db.close_session(session)
            return {"data": None, "message": "Account not found"}
        # Get the invoice to reprocess
        invoice = self.db.get_invoice(account_id, invoice_number, session)
        if invoice is None:
            logger.error(f"Invoice {invoice_number} not found for Account Id # {account_id}")
            self.db.close_session(session)
            return {"data": None, "message": "Invoice not found"}
        
        # Initialize result 
        result = { "data": {
            "invoice_number": invoice.invoice_number, 
            "current_amount": float(invoice.amount), 
            "new_amount": None, 
            "difference": 0, 
            "national_shipments_difference": None,
            "international_shipments_difference": None, 
            "updated": False},
            "message": "Invoice reprocessed"}

        # Compare current rates with invoice rates
        invoice_rates = self.db.get_invoice_rates(invoice.id, session)
        current_rates = RatesService(self.db).get_rates(account_id, session)
        rates_difference = {rate: current_rates[rate] - invoice_rates[rate] for rate in invoice_rates}
        if all(val == 0 for val in rates_difference.values()):
            logger.info(f"No difference found in rates for invoice {invoice.invoice_number}")
            self.db.close_session(session)
            return result

        # Get invoice items to calculate new amounts
        invoice_items = self.db.get_invoice_items(invoice.id, session)
        if invoice_items == []:
            logger.error(f"No items found for invoice {invoice.invoice_number}")
            return {"data": None, "message": "No items found for invoice"} 
        
        invoice_shipments = self.db.get_invoice_amounts_by_type(invoice.id, session)
        # Calculate new amounts and difference, if dry_run is False update invoice items amounts
        amounts = self._calculate_amounts(invoice_shipments, invoice_items, current_rates, dry_run, invoice.status, session)
        difference = sum(amounts["new"].values()) - sum(amounts["current"].values())
        result["data"]["new_amount"] = sum(amounts["new"].values())
        result["data"]["difference"] = difference
        result["data"]["national_shipments_difference"] = amounts["new"]["NATIONAL"] - amounts["current"]["NATIONAL"]
        result["data"]["international_shipments_difference"] = amounts["new"]["INTERNATIONAL"] - amounts["current"]["INTERNATIONAL"]

        # Update invoice amount and result if dry_run is False
        if not dry_run and invoice.status == "UNPAID":
            logger.info(f"Updating invoice {invoice.invoice_number} with new amount of ${result['data']['new_amount']}")
            invoice.amount = sum(amounts["new"].values())
            result = self._response_handler(result, session)
            self.db.close_session(session)

        logger.info(f"Difference of ${difference} found in invoice {invoice_number}.\n\
                    ► National shipments {result["data"]["national_shipments_difference"]}\n\
                    ► International shipments {result["data"]["international_shipments_difference"]}"
                    )           
        
        return result
