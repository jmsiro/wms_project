from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, DateTime, VARCHAR, Enum, DECIMAL, ForeignKey, PrimaryKeyConstraint, UniqueConstraint
  
Base = declarative_base() 

class MyBase(Base):
    __abstract__ = True
    def to_dict(self):
        return {field.name:getattr(self, field.name) for field in self.__table__.c}

class Accounts(MyBase):
    
    __tablename__ = 'accounts'

    id = Column(Integer, primary_key=True)
    account_name = Column(VARCHAR(45))
    created_at = Column(DateTime)

class Shipments(MyBase):

    __tablename__ = 'shipments'

    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey('accounts.id'))
    created_at = Column(DateTime)
    country = Column(VARCHAR(45))
    is_billed = Column(Integer)

class ShipmentTypes(MyBase):
    
    __tablename__ = 'shipment_types'

    id = Column(Integer, primary_key=True)
    name = Column(VARCHAR(45))

class Rates(MyBase):

    __tablename__ = 'rates'

    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey('accounts.id'))
    shipment_type_id = Column(Integer, ForeignKey('shipment_types.id'))
    price = Column(DECIMAL(4,2))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class Invoices(MyBase):

    __tablename__ = 'invoices'

    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey('accounts.id'))
    issued_at = Column(DateTime)
    invoice_number = Column(VARCHAR(128))
    status = Column(Enum("UNPAID", "PAID", "VOIDED"))
    amount = Column(DECIMAL(9,2))

    __table_args__ = (PrimaryKeyConstraint("id", name="id_pk"), UniqueConstraint('account_id', 'issued_at', name='unique_invoice'))

class InvoiceItems(MyBase):

    __tablename__ = 'invoice_items'

    id = Column(Integer, primary_key=True)
    invoice_id = Column(Integer, ForeignKey('invoices.id'))
    shipment_type_id = Column(Integer, ForeignKey('shipment_types.id'))
    description = Column(VARCHAR(128))
    quantity = Column(Integer)
    unit_price = Column(DECIMAL(9,2))
    amount = Column(DECIMAL(9,2))