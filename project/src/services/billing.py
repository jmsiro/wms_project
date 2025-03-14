from ..logs.logs import logger
from ..database.db import DbInstance
from .rates import RatesService
from datetime import datetime, timedelta
from sqlalchemy.orm import sessionmaker

logger = logger.getLogger("BILLING")

class BillingService:
    def __init__(self, db: DbInstance, test:bool=False):
        self.db = db 
        self.test = test

    def _insert_invoice(self, account_id:int, issued_at:datetime, shipments_amounts:dict, status:str="UNPAID", session:sessionmaker=None) -> dict:
        new_invoice = self.db.insert_invoice(session, account_id, issued_at, shipments_amounts, status)
        if new_invoice.get("message", None):
            return new_invoice
        
        invoice_data = {
            "data": {
                "account_id": account_id, 
                "id": new_invoice['id'], 
                "invoice_number": new_invoice['invoice_number'], 
                "status": status, 
                "amount": sum(shipments_amounts.values()), 
                "issued_date": new_invoice["issued_at"]
                }, 
            "message": "Invoice created"}
        
        return invoice_data

    def _insert_invoice_items(self, invoice_id:int, shipments_quantity:dict, shipments_rates:dict, session:sessionmaker) -> list:
        items = []
        for shipments_date, shipments_country, quantity in shipments_quantity:
            name = "NATIONAL" if shipments_country == "US" else "INTERNATIONAL"
            shipment_type = self.db.get_shipment_type_id(name, session)
            shipment_type_id = shipment_type[0]
            new_invoice_item = self.db.insert_invoice_items(
                invoice_id=invoice_id,
                shipment_type_id=shipment_type_id,
                rate=shipments_rates[name], 
                date=shipments_date,
                q=quantity,
                type=name,
                session=session)
            if new_invoice_item.get("invoice_id", None) is not None:
                items.append(new_invoice_item)   
        return items

    def charge_customer(self, account_id, year:int, month:int, status:str=None, session:sessionmaker=None) -> dict:
        """
        Create invoice to charge the customer for the shipments made in the billed period.
        Args:
            account_id: Id of the customer account to charge for the shipments.
            year (int): Year of the period to charge.
            month (int): Month of the period to charge.
            status (str, optional): Status of the created bill. Defaults to None.

        Returns:
            invoice_data (dict): Data of the invoice to be used in the creation of the document.
        """
        if not self.test:
            session = self.db.get_savepoint_session()
        
        if not self.db.account_exists(account_id, session):
            logger.error(f"Account Id # {account_id} not found")
            if not self.test:
                self.db.close_connection()
            self.db.close_session(session)
            return {"data": None, "message": "Account not found"}

        # Get the first and last day of the billable period using year and month 
        start_date = datetime.strptime("{year}-{month}-01".format(year=year, month=month), "%Y-%m-%d")
        # Issued date, always the first day of the next billable month
        issued_at = (start_date + timedelta(days=32)).replace(day=1)    
        # Get last day of billable period substracting one day from issued_date
        end_date = (issued_at - timedelta(days=1))
        
        # Quantity of shipments by type (National | International)
        shipments_quantity = self.db.get_shipments_quantity(account_id, start_date, end_date, session)
        # Shipments for the account_id between dates grouped by day and country
        shipments_by_day = self.db.get_shipments_by_day(account_id, start_date, end_date, session)
        # Current rates for the account_id or the default rates if the account_id has no rates
        shipments_rates =  RatesService(self.db).get_rates(account_id, session)

        if shipments_quantity["NATIONAL"] == 0 and shipments_quantity["INTERNATIONAL"] == 0:
            logger.info(f"No shipments to charge for Account Id # {account_id} in {start_date.strftime("%B %d, %Y")} - {end_date.strftime("%B %d, %Y")}")
            return {"data": None, "message": "No shipments to charge"}
        
        # Amounts to charge in the invoice for each type of shipment
        shipments_amounts = {shipment_type: quantity * shipments_rates[shipment_type] for shipment_type, quantity in shipments_quantity.items()}
        
        invoice_data = self._insert_invoice(account_id, issued_at, shipments_amounts, status, session)
        if invoice_data["data"] is None:
            self.db.close_session(session)
            if not self.test:
                self.db.rollback_savepoint()
            return invoice_data
        
        try:
            invoice_items = self._insert_invoice_items(invoice_data["data"]["id"], shipments_by_day, shipments_rates, session)
            self.db.commit_changes(session)
        except Exception as e:
            logger.error("Error creating invoice items:\n" + e.__str__())
            self.db.close_session(session)
            if not self.test:
                self.db.rollback_savepoint()
            return {"data": None, "message": "Error creating invoice items"}
        
        invoice_data["data"]["issued_date"] = invoice_data["data"]["issued_date"].strftime("%B %d, %Y")
        invoice_data["data"]["billing_period"] = f"{start_date.strftime("%B %d, %Y")} - {end_date.strftime("%B %d, %Y")}"
        invoice_data["data"]["items"] = invoice_items
        
        self.db.close_session(session)
        if not self.test:
            self.db.close_connection()
        logger.info(f"Invoice created for Account Id # {account_id} with number {invoice_data['data']['invoice_number']}")
        return invoice_data
    
    def charge_all(self, year:int, month:int) -> list:
        accounts = self.db.get_accounts()
        accounts_id = [id[0] for id in accounts]

        invoices = []
        for account in accounts_id:
            logger.info(f"Processing Account Id # {account}")
            invoice = self.charge_customer(account_id=account, year=year, month=month, status='UNPAID')
            invoices.append(invoice)
        return invoices