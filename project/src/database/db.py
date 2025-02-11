from datetime import datetime, timedelta
from sqlalchemy import create_engine, func, DATE
from sqlalchemy.orm import sessionmaker
from .models import Shipments, Rates, Invoices, InvoiceItems

class dbInstance:
    def __init__(self, db_params:dict):
        try:
            connectionString = 'mysql+pymysql://{0}:{1}@{2}:{3}/{4}'.format(db_params['user'], db_params['password'], db_params['host'], db_params['port'], db_params['database'])
            self.engine = create_engine(connectionString)
            # logger.info("Database connected")
        except Exception as e:
            # logger.error("Error connecting to database:\n" + e)
            raise e

    def _insertInvoice(self, account_id:int, issued_at:datetime, shipments_amounts:dict, invoice_status:str='UNPAID'):
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
        return new_invoice.id

    def _insertInvoiceItems(self, invoice_id:int, shipments_quantity:dict, shipments_rates:dict):
        Session = sessionmaker(bind=self.engine)
        session = Session()
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
        session.commit()

    def charge_customer(self, account_id:int, date:str, status:str=None):

        # Get the first and last day of the billable period (previous month)
        date_exec = datetime.strptime(date, '%Y-%m-%d')
        issued_at = date_exec.replace(day=1)
        start_date = (date_exec - timedelta(days=1)).replace(day=1)
        end_date = (date_exec.replace(day=1) - timedelta(days=1))

        Session = sessionmaker(bind=self.engine)
        session = Session()
        # Get the total number of shipments for the account_id between start_date and end_date grouped by country (US -> National | Other -> International)
        shipments_by_country = session.query(Shipments.country, func.count(Shipments.account_id)).filter(Shipments.account_id == account_id).filter(Shipments.created_at >= start_date).filter(Shipments.created_at <= end_date).group_by(Shipments.country).all()

        # Get the total number of shipments for the account_id between start_date and end_date grouped by day and country
        shipments_by_day = session.query(func.date(Shipments.created_at), Shipments.country, func.count(Shipments.account_id)).filter(Shipments.account_id == account_id).filter(Shipments.created_at >= start_date).filter(Shipments.created_at <= end_date).group_by(func.date(Shipments.created_at), Shipments.country).all()

        # Get current rates for the account_id or the default rates if the account_id has no rates
        current_rates = session.query(Rates.shipment_type, Rates.price).filter(Rates.account_id == account_id).all()
        if current_rates == []:
            current_rates = session.query(Rates.shipment_type, Rates.price).filter(Rates.account_id.is_(None)).all()

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
        # Rates for each type of shipment
        shipments_rates = {rate[0]: float(rate[1]) for rate in current_rates}
        # Amounts to charge in the invoice for each type of shipment
        shipments_amounts = {shipment_type: quantity * shipments_rates[shipment_type] for shipment_type, quantity in shipments_quantity.items()}

        # TODO: Add control to avoid duplicates
        invoice_id = self._insertInvoice(account_id, issued_at, shipments_amounts, status)
        self._insertInvoiceItems(invoice_id, shipments_by_day, shipments_rates)