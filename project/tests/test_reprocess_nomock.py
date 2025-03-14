import os
import sys
import unittest
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from utils.file_exe import file_exec

PATH = Path(os.path.dirname(__file__)).parent.absolute()
SCRIPT_DIR = os.path.join(PATH,"src")
if SCRIPT_DIR not in sys.path:
    sys.path.append(os.path.dirname(SCRIPT_DIR))
from src.database import db
from src.services.reprocess import BillReprocessor

Session = sessionmaker()
db_instance = db.DbInstance(os.environ["CONN_TEST"])

class TestReprocessInvoice(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(os.environ["CONN_TEST"])
        self.connection = self.engine.connect()
        # Begin transaction
        self.trans = self.connection.begin()
        # Bind Session to the connection, using join_transaction_mode = "create_savepoint" 
        self.session = Session(
            bind=self.connection, join_transaction_mode="create_savepoint"
        )
        file_exec(os.path.join(PATH, "tests", "utils", "test_setUp.sql"), self.connection)

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
        file_exec(os.path.join(PATH, "tests", "utils", "test_tearDown.sql"), self.connection)
        self.session.close()
        self.connection.close()

if __name__ == "__main__":
    unittest.main(verbosity=2)