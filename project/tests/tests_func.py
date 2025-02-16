import os
import sys
import unittest
from pathlib import Path
from unittest import mock
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

PATH = Path(os.path.dirname(__file__)).parent.absolute()
SCRIPT_DIR = os.path.join(PATH,"src")
if SCRIPT_DIR not in sys.path:
    sys.path.append(os.path.dirname(SCRIPT_DIR))
from src.database import db
from src.services.billing import BillingService
from src.services.reprocess import BillReprocessor

Session = sessionmaker()
engine = create_engine(os.environ["CONN"])
db_instance = db.DbInstance(test=True)

class TestChargeCustomer(unittest.TestCase):
    def setUp(self):
        self.connection = engine.connect()
        # Begin transaction
        self.trans = self.connection.begin()
        # Bind Session to the connection, using join_transaction_mode = "create_savepoint" 
        self.session = Session(
            bind=self.connection, join_transaction_mode="create_savepoint"
        )

    def testNoShipments(self):
        """No shipments"""
        self.assertEqual(BillingService(db_instance, True).charge_customer(account_id=2, year=2024, month=1, status="PAID", session=self.session)["data"], None)
    
    def testNoAccount(self):
        """No account"""
        self.assertEqual(BillingService(db_instance, True).charge_customer(account_id=5, year=2025, month=1, status="PAID", session=self.session)["data"], None)
        self.session.commit()

    def testDuplicateInvoice(self):
        """Duplicated invoice"""
        self.assertEqual(BillingService(db_instance, True).charge_customer(account_id=1, year=2025, month=1, status="UNPAID", session=self.session)["message"], "Invoice already exists")
        self.session.commit()

    def testReturnedData(self):
        """Returned data"""
        account = 2
        year = 2025
        month = 1
        result = BillingService(db_instance, True).charge_customer(account_id=account, year=year, month=month, status="PAID", session=self.session)["data"]
        with self.subTest():
            """Result is dict"""
            self.assertIsInstance(result, dict)
        with self.subTest():
            """Account is the same"""
            self.assertEqual(result["account_id"], account)
        with self.subTest():
            """Status set correctly"""
            self.assertEqual(result["status"], "PAID")
        with self.subTest():
            """Invoice number has correct format"""
            self.assertRegex(result["invoice_number"], r"SH-\d+-\d+") # SH-1-1
        with self.subTest():
            """Charges type and length"""
            self.assertIsInstance(result["items"], list)
            self.assertGreater(len(result["items"]), 0)
        with self.subTest():
            """Invoice total vs sum of items"""
            self.assertEqual(result["amount"], sum([item["amount"] for item in result["items"]]))
        with self.subTest():
            "Date format"
            format = "%B %d, %Y"
            self.assertTrue(bool(datetime.strptime(result["issued_date"], format)))
        with self.subTest():
            "Billed period"
            format = "%B %d, %Y"
            between = result["billing_period"].split(" - ")
            begin = datetime.strptime(between[0], format)
            end = datetime.strptime(between[1], format)
            # Same month
            self.assertEqual(
                (begin.month, end.month), (month, month)
            )
            # Same year
            self.assertEqual(
                (begin.year, end.year), (year, year)
            )
            # Validate one month period
            self.assertEqual(
                begin.replace(month=begin.month+1) - timedelta(days=1), end
            )

    def tearDown(self):
        self.session.close()
        # Rollback to the savepoint. Everything that happened with the Session above is rb (including calls to commit()) 
        self.trans.rollback()
        self.connection.close()

class TestReprocessInvoice(unittest.TestCase):
    def setUp(self):
        self.connection = engine.connect()
        # Begin transaction
        self.trans = self.connection.begin()
        # Bind Session to the connection, using join_transaction_mode = "create_savepoint" 
        self.session = Session(
            bind=self.connection, join_transaction_mode="create_savepoint"
        )

    def testNoInvoice(self):
        """No invoice"""
        self.assertEqual(BillReprocessor(db_instance, True).reprocess_invoice(account_id=1, invoice_number="LVK-1-1", dry_run=True, session=self.session)["message"], "Invoice not found")
    
    def testNoAccount(self):
        """No account"""
        self.assertEqual(BillReprocessor(db_instance, True).reprocess_invoice(account_id=50, invoice_number="SH-1-1", session=self.session)["data"], None)

    def testDryRun(self):
        """Dry run"""
        with self.subTest():
            """Dry run mode enabled"""
            self.assertEqual(BillReprocessor(db_instance, True).reprocess_invoice(account_id=1, invoice_number="SH-1-1", dry_run=True, session=self.session)["data"]["updated"], False)
        with self.subTest():
            """Default dry run mode"""
            self.assertEqual(BillReprocessor(db_instance, True).reprocess_invoice(account_id=1, invoice_number="SH-1-1", session=self.session)["data"]["updated"], False)

    def testUpdateData(self):
        """Update data"""
        result = BillReprocessor(db_instance, True).reprocess_invoice(account_id=1, invoice_number="SH-1-1", dry_run=False, session=self.session)['data']
        if result["difference"] > 0:
            self.assertEqual(result["updated"], True)
        elif result["difference"] == 0:
            self.assertEqual(result["updated"], False)

    def tearDown(self):
        self.session.close()
        # Rollback to the savepoint. Everything that happened with the Session above is rb (including calls to commit()) 
        self.trans.rollback()
        self.connection.close()

if __name__ == "__main__":
    unittest.main(verbosity=2)