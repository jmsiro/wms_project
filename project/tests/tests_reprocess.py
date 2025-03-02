import os
import sys
import unittest
import datetime
from pathlib import Path
from unittest.mock import MagicMock

PATH = Path(os.path.dirname(__file__)).parent.absolute()
SCRIPT_DIR = os.path.join(PATH,"src")
if SCRIPT_DIR not in sys.path:
    sys.path.append(os.path.dirname(SCRIPT_DIR))

from src.services.reprocess import BillReprocessor
from src.models.models import Invoices, InvoiceItems

class TestReprocessInvoice(unittest.TestCase):
    def setUp(self):
        """Mock database and session setup"""
        self.mock_db = MagicMock()
        self.mock_session = MagicMock()
        self.bill_reprocessor = BillReprocessor(self.mock_db, True)
        self.mock_invoice = Invoices(id=1, account_id=1, issued_at=datetime.date(2025,2,1), invoice_number="SH-1-1", status="UNPAID", amount=700.00)
        self.mock_invoice_items = [
            InvoiceItems(invoice_id=1, description='National shipments of 2025-01-01', quantity=1, unit_price=5.0, amount=5.0),
            InvoiceItems(invoice_id=1, description='International shipment of 2025-01-01', quantity=1, unit_price=20.0, amount=20.0),
            InvoiceItems(invoice_id=1, description='National shipments of 2025-01-05', quantity=2, unit_price=5.0, amount=10.0),
            InvoiceItems(invoice_id=1, description='International shipment of 2025-01-05', quantity=2, unit_price=20.0, amount=40.0),
            InvoiceItems(invoice_id=1, description='National shipments of 2025-01-10', quantity=3, unit_price=5.0, amount=15.0),
            InvoiceItems(invoice_id=1, description='International shipment of 2025-01-10', quantity=3, unit_price=20.0, amount=60.0),
            InvoiceItems(invoice_id=1, description='National shipments of 2025-01-15', quantity=4, unit_price=5.0, amount=20.0),
            InvoiceItems(invoice_id=1, description='International shipment of 2025-01-15', quantity=4, unit_price=20.0, amount=80.0),
            InvoiceItems(invoice_id=1, description='National shipments of 2025-01-20', quantity=5, unit_price=5.0, amount=25.0),
            InvoiceItems(invoice_id=1, description='International shipment of 2025-01-20', quantity=5, unit_price=20.0, amount=100.0),
            InvoiceItems(invoice_id=1, description='National shipments of 2025-01-25', quantity=6, unit_price=5.0, amount=30.0),
            InvoiceItems(invoice_id=1, description='International shipment of 2025-01-25', quantity=6, unit_price=20.0, amount=120.0),
            InvoiceItems(invoice_id=1, description='National shipments of 2025-01-30', quantity=7, unit_price=5.0, amount=35.0),
            InvoiceItems(invoice_id=1, description='International shipment of 2025-01-30', quantity=7, unit_price=20.0, amount=140.0)
        ]

    def testNoInvoice(self):
        """No invoice"""
        self.mock_db.get_invoice.return_value = None 
        result = self.bill_reprocessor.reprocess_invoice(account_id=1, invoice_number="LVK-1-1", dry_run=True, session=self.mock_session)
        self.assertEqual(result["message"], "Invoice not found")

    def testNoAccount(self):
        """No account"""
        self.mock_db.account_exists.return_value = None 
        result = self.bill_reprocessor.reprocess_invoice(account_id=50, invoice_number="SH-1-1", session=self.mock_session)
        self.assertIsNone(result["data"])

    def testDryRun(self):
        """Dry run"""
        self.mock_db.account_exists.return_value = True  
        self.mock_db.get_invoice.return_value = self.mock_invoice  

        result = self.bill_reprocessor.reprocess_invoice(account_id=1, invoice_number="SH-1-1", dry_run=True, session=self.mock_session)
        
        with self.subTest():
            """Validate response data"""
            self.assertFalse(result["data"]["updated"]) 
        with self.subTest():
            """Validate message"""
            self.assertEqual(result["message"], "Invoice reprocessed")

    def testCommitChanges(self):
        """Commit changes"""
        self.mock_db.account_exists.return_value = True
        self.mock_db.get_invoice.return_value = self.mock_invoice
        self.mock_db.get_invoice_rates.return_value = {'NATIONAL': 5.0, 'INTERNATIONAL': 20.0}
        self.mock_db.get_rates.return_value = {'NATIONAL': 10.0, 'INTERNATIONAL': 40.0}
        self.mock_db.get_invoice_items.return_value = self.mock_invoice_items
        self.mock_db.get_invoice_amounts_by_type.return_value = [('NATIONAL', 140.0), ('INTERNATIONAL', 560.0)] 
        self.mock_db.get_shipment_type_name.side_effect = [("NATIONAL",), ("INTERNATIONAL",), ("NATIONAL",), ("INTERNATIONAL",), ("NATIONAL",), ("INTERNATIONAL",), ("NATIONAL",), ("INTERNATIONAL",), ("NATIONAL",), ("INTERNATIONAL",), ("NATIONAL",), ("INTERNATIONAL",), ("NATIONAL",), ("INTERNATIONAL",)]

        result = self.bill_reprocessor.reprocess_invoice(account_id=1, invoice_number="SH-1-1", dry_run=False, session=self.mock_session)

        with self.subTest():
            """Validate response data"""
            self.assertTrue(result["data"]["updated"])
        with self.subTest():
            """Validate message"""
            self.assertEqual(result["message"], "Invoice updated")
        with self.subTest():
            """Validate new amount"""
            self.assertEqual(result["data"]["new_amount"], 1400.00)

    def tearDown(self):
        """Reset mocks"""
        self.mock_db.reset_mock()
        self.mock_session.reset_mock()


if __name__ == "__main__":
    unittest.main(verbosity=2)
