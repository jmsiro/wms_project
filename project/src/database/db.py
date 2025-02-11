from datetime import datetime, timedelta
from sqlalchemy import create_engine, func, case
from sqlalchemy.orm import sessionmaker
from .models import Shipments, Rates, Invoices, InvoiceItems
from ..logs.logs import logger

logger = logger.getLogger("DATABASE")

class dbInstance:
    def __init__(self, db_params:dict):
        try:
            connectionString = 'mysql+pymysql://{0}:{1}@{2}:{3}/{4}'.format(db_params['user'], db_params['password'], db_params['host'], db_params['port'], db_params['database'])
            self.engine = create_engine(connectionString)
            logger.info("Database connected")
        except Exception as e:
            logger.error("Error connecting to database:\n" + e)
            raise e

    def _insertInvoice(self, account_id:int, issued_at:datetime, shipments_amounts:dict, invoice_status:str='UNPAID') -> dict:
        Session = sessionmaker(bind=self.engine)
        session = Session()
        last_id = session.query(Invoices.id).order_by(Invoices.id.desc()).first()
        if last_id is None:
            last_id = [0]

        new_invoice = Invoices(
            account_id=account_id,
            issued_at=issued_at,
            invoice_number="",
            status=invoice_status,
            amount=sum(shipments_amounts.values())
        )
        session.add(new_invoice)
        session.flush()
        session.query(Invoices).filter(Invoices.id == new_invoice.id).update({Invoices.invoice_number: 'SH-{0}-{1}'.format(account_id, new_invoice.id)}, synchronize_session=False)
        session.commit()
        return {"id": new_invoice.id, "invoice_number": new_invoice.invoice_number, "issued_date": new_invoice.issued_at}

    def _insertInvoiceItems(self, invoice_id:int, shipments_quantity:dict, shipments_rates:dict) -> list:
        Session = sessionmaker(bind=self.engine)
        session = Session()
        items = []
        for shipments_date, shipments_country, quantity in shipments_quantity:
            shipment_type = 'NATIONAL' if shipments_country == 'US' else 'INTERNATIONAL'
            new_invoice_item = InvoiceItems(
                invoice_id=invoice_id,
                description="National shipments of {0}".format(shipments_date) if shipment_type == 'NATIONAL' else "International shipment of {0}".format(shipments_date),
                quantity=quantity,
                unit_price=shipments_rates[shipment_type],
                amount=quantity * shipments_rates[shipment_type]
            )
            session.add(new_invoice_item)
            # Save item as dict removing the '_sa_instance_state' key that's not needed
            item_dict = new_invoice_item.__dict__.copy()
            item_dict.pop('_sa_instance_state', None)
            if item_dict.get('invoice_id', None) is not None:
                items.append(item_dict)
        session.commit()
        
        return items
    
    def _getRates(self, account_id:int, session:sessionmaker) -> list:
        current_rates = session.query(Rates.shipment_type, Rates.price).filter(Rates.account_id == account_id).all()
        if current_rates == []:
            current_rates = session.query(Rates.shipment_type, Rates.price).filter(Rates.account_id.is_(None)).all()
        # Rates for each type of shipment
        current_rates = {rate[0]: float(rate[1]) for rate in current_rates}
        return current_rates

    def charge_customer(self, account_id:int, year:int, month:int, status:str=None) -> dict:
        """
        Create invoice to charge the customer for the shipments made in the billed period.
        Args:
            account_id (int): Id of the cutomer account to charge for the shipments.
            year (int): Year of the period to charge.
            month (int): Month of the period to charge.
            status (str, optional): Status of the created bill. Defaults to None.

        Returns:
            invoice_data (dict): Data of the invoice to be used in the creation of the document.
        """
        # Get the first and last day of the billable period using year and month 
        start_date = datetime.strptime("{year}-{month}-01".format(year=year, month=month), "%Y-%m-%d")
        # Issued date, always the first day of the next billable month
        issued_at = (start_date + timedelta(days=32)).replace(day=1)    
        # Get last day of billable period detraing one day from issued_date
        end_date = (issued_at - timedelta(days=1))
        
        Session = sessionmaker(bind=self.engine)
        session = Session()
        # Get the total number of shipments for the account_id between start_date and end_date grouped by country (US -> National | Other -> International)
        shipments_by_country = session.query(Shipments.country, func.count(Shipments.account_id)).filter(Shipments.account_id == account_id).filter(Shipments.created_at >= start_date).filter(Shipments.created_at <= end_date).group_by(Shipments.country).all()
        # Get the total number of shipments for the account_id between start_date and end_date grouped by day and country
        shipments_by_day = session.query(func.date(Shipments.created_at), Shipments.country, func.count(Shipments.account_id)).filter(Shipments.account_id == account_id).filter(Shipments.created_at >= start_date).filter(Shipments.created_at <= end_date).group_by(func.date(Shipments.created_at), Shipments.country).all()
        # Get current rates for the account_id or the default rates if the account_id has no rates
        shipments_rates =  self._getRates(account_id, session)

        # Quantity of shipments by type (National | International)
        shipments_quantity = {
            'NATIONAL': 0,
            'INTERNATIONAL': 0
        }
        for shipment in shipments_by_country:
            if shipment[0] == 'US':
                shipments_quantity['NATIONAL'] += shipment[1]
            else:
                shipments_quantity['INTERNATIONAL'] += shipment[1]
        if shipments_quantity['NATIONAL'] == 0 and shipments_quantity['INTERNATIONAL'] == 0:
            # logger.info("No shipments to charge")
            return
        # Amounts to charge in the invoice for each type of shipment
        shipments_amounts = {shipment_type: quantity * shipments_rates[shipment_type] for shipment_type, quantity in shipments_quantity.items()}

        # TODO: Add control to avoid duplicates
        invoice_data = self._insertInvoice(account_id, issued_at, shipments_amounts, status)
        invoice_items = self._insertInvoiceItems(invoice_data['id'], shipments_by_day, shipments_rates)
        invoice_data['issued_date'] = invoice_data['issued_date'].strftime("%B %d, %Y")
        invoice_data['billing_period'] = "{0} - {1}".format(start_date.strftime("%B %d, %Y"), end_date.strftime("%B %d, %Y"))
        invoice_data['items'] = invoice_items
        
        return invoice_data
    
    def reprocess_invoice(self, account_id:int, invoice_number:str, dry_run:bool=True) -> None:
        """
        Reprocess an invoice to get new amount per shipment type.
        Args:
            account_id (int): Id of the cutomer account related to the invoice.
            invoice_number (str): Invoice number to reprocess.
            dry_run (bool, optional): Defines if the reprocess will commit the changes or not. Defaults to True.
        """
        
        Session = sessionmaker(bind=self.engine)
        session = Session()

        # TODO: Previous query to check if account exists? Need table.        
        # Get the invoice to reprocess and its items
        invoice = session.query(Invoices).filter(Invoices.account_id == account_id).filter(Invoices.invoice_number == invoice_number).first()
        if invoice is None:
            logger.error("Invoice {0} not found for Account Id # {1}".format(invoice_number, account_id))
            return
        
        invoice_items = session.query(InvoiceItems).filter(InvoiceItems.invoice_id == invoice.id).all()

        shipment_type_case = case((InvoiceItems.description.like("%International%"), 'INTERNATIONAL'), else_='NATIONAL')
        invoice_shipments = session.query(shipment_type_case, func.sum(InvoiceItems.amount)).filter(InvoiceItems.invoice_id == invoice.id).group_by(shipment_type_case).all()
        amounts = {'current': {item[0]: float(item[1]) for item in invoice_shipments}, 'new': {'NATIONAL': 0, 'INTERNATIONAL': 0}}
        current_rates =  self._getRates(account_id, session)
        
        for item in invoice_items:
            shipment_type = 'INTERNATIONAL' if 'International' in item.description else 'NATIONAL'
            amounts['new'][shipment_type] += current_rates[shipment_type] * item.quantity
            
            if not dry_run and invoice.status == 'UNPAID':
                item.unit_price = current_rates[shipment_type]
                item.amount = current_rates[shipment_type] * item.quantity

        difference = sum(amounts['new'].values()) - sum(amounts['current'].values())
        if not dry_run and invoice.status == 'UNPAID':
            invoice.amount = sum(amounts['new'].values())
            
        if difference != 0:
            logger.info("Difference of ${0} found in invoice {1}.\n-> National shipments {2}\n-> International shipments {3}".format(difference, invoice.invoice_number, amounts['new']['NATIONAL'] - amounts['current']['NATIONAL'], amounts['new']['INTERNATIONAL'] - amounts['current']['INTERNATIONAL']))
            if not dry_run and invoice.status == 'UNPAID':
                is_update = input("Are you sure? (y/n): ").lower()
                if is_update == 'y':
                    logger.info("Committing changes...")
                    session.commit()
                elif is_update == 'n':
                    logger.info("Update aborted.")
                    session.rollback()
                else:
                    logger.info("Invalid input. Update aborted.")
                    session.rollback()
        else:
            logger.info("No difference found in invoice {0}".format(invoice.invoice_number))