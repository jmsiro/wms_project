from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, DateTime, VARCHAR, Enum, DECIMAL, ForeignKey, PrimaryKeyConstraint, UniqueConstraint
  
Base = declarative_base() 

class Accounts(Base):
    
    __tablename__ = 'accounts'

    id = Column(Integer, primary_key=True)
    account_name = Column(VARCHAR(45))
    created_at = Column(DateTime)

class Shipments(Base):

    __tablename__ = 'shipments'

    id = Column(Integer, primary_key=True)
    account_id = Column(Integer)
    created_at = Column(DateTime)
    country = Column(VARCHAR(45))
    is_billed = Column(Integer)

class Rates(Base):

    __tablename__ = 'rates'

    id = Column(Integer, primary_key=True)
    account_id = Column(Integer)
    shipment_type = Column(Enum("NATIONAL", "INTERNATIONAL"))
    price = Column(DECIMAL(4,2))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class Invoices(Base):

    __tablename__ = 'invoices'

    id = Column(Integer, primary_key=True)
    account_id = Column(Integer)
    issued_at = Column(DateTime)
    invoice_number = Column(VARCHAR(128))
    status = Column(Enum("UNPAID", "PAID", "VOIDED"))
    amount = Column(DECIMAL(9,2))

    __table_args__ = (PrimaryKeyConstraint("id", name="id_pk"), UniqueConstraint('account_id', 'issued_at', name='unique_invoice'))

class InvoiceItems(Base):

    __tablename__ = 'invoice_items'

    id = Column(Integer, primary_key=True)
    invoice_id = Column(Integer, ForeignKey('invoices.id'))
    description = Column(VARCHAR(128))
    quantity = Column(Integer)
    unit_price = Column(DECIMAL(9,2))
    amount = Column(DECIMAL(9,2))