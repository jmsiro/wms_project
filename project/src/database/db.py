from datetime import datetime, timedelta
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, func, case
from sqlalchemy.sql import exists
from sqlalchemy.exc import IntegrityError as sqlalchemyIntegrityError
from pymysql.err import IntegrityError as pymysqlIntegrityError
from ..models.models import Shipments, Rates, Invoices, InvoiceItems, Accounts, ShipmentTypes
from ..logs.logs import logger

logger = logger.getLogger("DATABASE")

class DbInstance:
    def __init__(self, con_str:str=None, test:bool=False):
        self.test = test
        self.connection = None
        self.transaction = None
        if self.test:
            # Legacy, used for mocked tests (deprecated)
            logger.info("Test - No database parameters provided")
        else:
            try:
                self.engine = create_engine(con_str)
                logger.info("Database connected")
            except Exception as e:
                logger.error("Error connecting to database:\n" + e.__str__())
                raise e

    def get_savepoint_session(self):
        self.connection = self.engine.connect()
        self.transaction = self.connection.begin()
        Session = sessionmaker(bind=self.connection, join_transaction_mode="create_savepoint")
        session = Session()
        return session
    
    def rollback_savepoint(self):
        self.transaction.rollback()
        self.connection.close()
    
    def close_connection(self):
        self.connection.close()

    def get_session(self):
        Session = sessionmaker(bind=self.engine)
        session = Session()
        return session
    
    def rollback_changes(self, session:sessionmaker):
        session.rollback()

    def close_session(self, session:sessionmaker):
        session.close()
    
    def commit_changes(self, session:sessionmaker):
        if self.transaction:
            self.transaction.commit()
        else:
            session.commit()
    
    def account_exists(self, account_id:int, session:sessionmaker) -> Accounts:
        account = session.query(Accounts).filter(Accounts.id == account_id).first() is not None
        return account
    
    def get_shipments_quantity(self, account_id:int, start_date:datetime, end_date:datetime, session:sessionmaker) -> dict:
        # USA shipments
        national_shipments = session.query(Shipments.country)\
            .filter(Shipments.account_id == account_id,
                    Shipments.country == "US",
                    Shipments.created_at >= start_date,
                    Shipments.created_at <= end_date).count()
        # Every other country
        international_shipments = session.query(Shipments.country)\
            .filter(Shipments.account_id == account_id,
                    Shipments.country != "US",
                    Shipments.created_at >= start_date,
                    Shipments.created_at <= end_date).count()
        
        shipments_quantity = {
            "NATIONAL": national_shipments,
            "INTERNATIONAL": international_shipments
        }
        return shipments_quantity
    
    def get_shipments_by_day(self, account_id:int, start_date:datetime, end_date:datetime, session:sessionmaker) -> list:
        shipments_by_day = session.query(
            func.date(Shipments.created_at), Shipments.country, func.count(Shipments.account_id)).\
                filter(Shipments.account_id == account_id, 
                       Shipments.created_at >= start_date, 
                       Shipments.created_at <= end_date).\
                    group_by(func.date(Shipments.created_at), Shipments.country).\
                        with_entities(func.date(Shipments.created_at), Shipments.country, func.count(Shipments.account_id)).all()
        return shipments_by_day

    def insert_invoice(self, session:sessionmaker, account_id:int, issued_at:datetime, shipments_amounts:dict, invoice_status:str="UNPAID") -> dict:

        new_invoice = Invoices(
            account_id=account_id,
            issued_at=issued_at,
            invoice_number="",
            status=invoice_status,
            amount=sum(shipments_amounts.values())
        )
        session.add(new_invoice)
        # Use flush to create a new object and get back the PK
        try:
            session.flush()
        except sqlalchemyIntegrityError or pymysqlIntegrityError:
            logger.error(f"Invoice already exists for Account Id # {account_id} with date: {issued_at.strftime("%B %d, %Y")}")
            session.rollback()
            return {"data": None, "message": "Invoice already exists"}
        except Exception as e:
            logger.error("Error creating invoice:\n" + e.__str__())
            session.rollback()
            return {"data": None, "message": e}
        
        # Update invoice number using PK gotten from flush
        session.query(Invoices).filter(Invoices.id == new_invoice.id).\
            update({Invoices.invoice_number: f"SH-{account_id}-{new_invoice.id}"})
        session.commit()

        return new_invoice.to_dict()

    def insert_invoice_items(self, invoice_id:int, shipment_type_id:int,rate:float, date:str, q:int, type:str, session:sessionmaker) -> InvoiceItems:
        new_invoice_item = InvoiceItems(
            invoice_id=invoice_id,
            shipment_type_id=shipment_type_id,
            description=f"National shipments of {date}" if type == "NATIONAL" else f"International shipment of {date}",
            quantity=q,
            unit_price=rate,
            amount=q * rate)
        session.add(new_invoice_item)
        session.commit()
        return new_invoice_item.to_dict()

    def get_rates(self, account_id:int, session:sessionmaker) -> dict:
        
        if session.query(exists().where(Rates.account_id == account_id)).scalar():
            current_rates = session.query(Rates).\
                join(ShipmentTypes, Rates.shipment_type_id == ShipmentTypes.id).\
                    filter(Rates.account_id == account_id).\
                        with_entities(ShipmentTypes.name, Rates.price).all()
        else:
            current_rates = session.query(Rates).\
                join(ShipmentTypes, Rates.shipment_type_id == ShipmentTypes.id).\
                    filter(Rates.account_id.is_(None)).\
                        with_entities(ShipmentTypes.name, Rates.price).all()
        
        # Rates for each type of shipment
        current_rates = {rate[0]: float(rate[1]) for rate in current_rates}
        return current_rates

    def create_update_rates(self, account_id:int, shipment_type_id:int, rate:float, session:sessionmaker) -> dict:
        session.query(Rates).\
            where(Rates.account_id == account_id).\
                where(Rates.shipment_type_id == shipment_type_id).\
                    update({'price': rate, 'updated_at':datetime.now()})
        session.commit()
        rates = self.get_rates(account_id, session)
        return rates
        
    def get_invoice_rates(self, invoice_id:str, session:sessionmaker) -> list:
        shipment_type_case = case((InvoiceItems.description.like("%International%"), "INTERNATIONAL"), else_="NATIONAL")
        invoice_rates = session.query(shipment_type_case, func.sum(InvoiceItems.amount)/func.sum(InvoiceItems.quantity)).\
            filter(InvoiceItems.invoice_id == invoice_id).\
                group_by(shipment_type_case).\
                    with_entities(shipment_type_case, func.sum(InvoiceItems.amount)/func.sum(InvoiceItems.quantity)).all()
        
        # Rates for each type of shipment
        invoice_rates = {rate[0]: float(rate[1]) for rate in invoice_rates}
        return invoice_rates

    def get_invoice(self, account_id:int, invoice_number:str, session:sessionmaker) -> Invoices:
        invoice = session.query(Invoices).filter(
            Invoices.account_id == account_id, 
            Invoices.invoice_number == invoice_number).first()
        return invoice
    
    def get_invoice_items(self, invoice_id:int, session:sessionmaker) -> list:
        invoice_items = session.query(InvoiceItems).filter(InvoiceItems.invoice_id == invoice_id).all()
        return invoice_items

    def get_invoice_amounts_by_type(self, invoice_id:int, session:sessionmaker) -> list:
        invoice_shipments = session.query(ShipmentTypes.name, func.sum(InvoiceItems.amount)).\
            join(ShipmentTypes, InvoiceItems.shipment_type_id == ShipmentTypes.id).\
            filter(InvoiceItems.invoice_id == invoice_id).\
                group_by(ShipmentTypes.name).\
                    with_entities(ShipmentTypes.name, func.sum(InvoiceItems.amount)).all()
        return invoice_shipments
    
    def get_accounts(self) -> list:
        session = self.get_session()
        accounts = session.query(Accounts).with_entities(Accounts.id).all()
        self.close_session(session)
        return accounts
    
    def get_shipment_type_id(self, name:str, session:sessionmaker) -> int:
        shipment_type = session.query(ShipmentTypes).filter(ShipmentTypes.name == name).with_entities(ShipmentTypes.id).first()
        return shipment_type
    
    def get_shipment_type_name(self, id:int, session:sessionmaker) -> str:
        shipment_type = session.query(ShipmentTypes).filter(ShipmentTypes.id == id).with_entities(ShipmentTypes.name).first()
        return shipment_type