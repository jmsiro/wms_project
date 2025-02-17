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

from src.services.billing import BillingService

class TestChargeCustomer(unittest.TestCase):
    def setUp(self):
        """Mock database and session setup"""
        self.mock_db = MagicMock() 
        self.mock_session = MagicMock() 
        self.billing_service = BillingService(self.mock_db, True) 

    def testNoShipments(self):
        """No shipments"""
        self.mock_db.account_exists.return_value = True
        self.mock_db.get_shipments_quantity.return_value = {"NATIONAL": 0, "INTERNATIONAL": 0}  # Simulate no shipments
        result = self.billing_service.charge_customer(account_id=2, year=2024, month=1, status="PAID", session=self.mock_session)
        self.assertIsNone(result["data"]) 

    def testNoAccount(self):
        """No account"""
        self.mock_db.account_exists.return_value = None 
        result = self.billing_service.charge_customer(account_id=5, year=2025, month=1, status="PAID", session=self.mock_session)
        self.assertIsNone(result["data"])  

    def testDuplicateInvoice(self):
        """Duplicated invoice"""
        self.mock_db.account_exists.return_value = True
        self.mock_db.insert_invoice.return_value = {"data": None, "message": "Invoice already exists"}  
        result = self.billing_service.charge_customer(account_id=1, year=2025, month=1, status="UNPAID", session=self.mock_session)
        self.assertEqual(result["message"], "Invoice already exists")

    def testReturnedData(self):
        """Returned data"""
        self.mock_db.account_exists.return_value = True
        self.mock_db.get_shipments_quantity.return_value = {'NATIONAL': 28, 'INTERNATIONAL': 28}
        self.mock_db.get_shipments_by_day.return_value = [(datetime.date(2025, 1, 1), 'US', 1), (datetime.date(2025, 1, 1), 'CA', 1), (datetime.date(2025, 1, 5), 'US', 2), (datetime.date(2025, 1, 5), 'CA', 2), (datetime.date(2025, 1, 10), 'US', 3), (datetime.date(2025, 1, 10), 'CA', 3), (datetime.date(2025, 1, 15), 'US', 4), (datetime.date(2025, 1, 15), 'CA', 4), (datetime.date(2025, 1, 20), 'US', 5), (datetime.date(2025, 1, 20), 'CA', 5), (datetime.date(2025, 1, 25), 'US', 6), (datetime.date(2025, 1, 25), 'CA', 6), (datetime.date(2025, 1, 30), 'US', 7), (datetime.date(2025, 1, 30), 'CA', 7)]
        self.mock_db.get_rates.return_value = {'NATIONAL': 10.0, 'INTERNATIONAL': 25.0}
        self.mock_db.insert_invoice.return_value = {'id': 55, 'account_id': 2, 'issued_at': datetime.datetime(2025, 2, 1, 0, 0), 'invoice_number': 'SH-2-55', 'status': 'UNPAID', 'amount': 980.00}
        self.mock_db.insert_invoice_items.side_effect = [{'id': 281, 'invoice_id': 52, 'description': 'National shipments of 2025-01-01', 'quantity': 1, 'unit_price': 10.00, 'amount': 10.00}, {'id': 282, 'invoice_id': 52, 'description': 'International shipment of 2025-01-01', 'quantity': 1, 'unit_price': 25.00, 'amount': 25.00}, {'id': 283, 'invoice_id': 52, 'description': 'National shipments of 2025-01-05', 'quantity': 2, 'unit_price': 10.00, 'amount': 20.00}, {'id': 284, 'invoice_id': 52, 'description': 'International shipment of 2025-01-05', 'quantity': 2, 'unit_price': 25.00, 'amount': 50.00}, {'id': 285, 'invoice_id': 52, 'description': 'National shipments of 2025-01-10', 'quantity': 3, 'unit_price': 10.00, 'amount': 30.00}, {'id': 286, 'invoice_id': 52, 'description': 'International shipment of 2025-01-10', 'quantity': 3, 'unit_price': 25.00, 'amount': 75.00}, {'id': 287, 'invoice_id': 52, 'description': 'National shipments of 2025-01-15', 'quantity': 4, 'unit_price': 10.00, 'amount': 40.00}, {'id': 288, 'invoice_id': 52, 'description': 'International shipment of 2025-01-15', 'quantity': 4, 'unit_price': 25.00, 'amount': 100.00}, {'id': 289, 'invoice_id': 52, 'description': 'National shipments of 2025-01-20', 'quantity': 5, 'unit_price': 10.00, 'amount': 50.00}, {'id': 290, 'invoice_id': 52, 'description': 'International shipment of 2025-01-20', 'quantity': 5, 'unit_price': 25.00, 'amount': 125.00}, {'id': 291, 'invoice_id': 52, 'description': 'National shipments of 2025-01-25', 'quantity': 6, 'unit_price': 10.00, 'amount': 60.00}, {'id': 292, 'invoice_id': 52, 'description': 'International shipment of 2025-01-25', 'quantity': 6, 'unit_price': 25.00, 'amount': 150.00}, {'id': 293, 'invoice_id': 52, 'description': 'National shipments of 2025-01-30', 'quantity': 7, 'unit_price': 10.00, 'amount': 70.00}, {'id': 294, 'invoice_id': 52, 'description': 'International shipment of 2025-01-30', 'quantity': 7, 'unit_price': 25.00, 'amount': 175.00}]

        result = self.billing_service.charge_customer(account_id=2, year=2025, month=1, status="PAID", session=self.mock_session)

        with self.subTest():
            """Validate response data"""
            self.assertIsInstance(result["data"], dict)
        with self.subTest():
            """Validate Account ID"""
            self.assertEqual(result["data"]["account_id"], 2) 
        with self.subTest():
            """Validate Invoice Data"""       
            self.assertEqual(result["data"]["status"], "PAID")
            self.assertRegex(result["data"]["invoice_number"], r"SH-\d+-\d+") 
            self.assertEqual(result["data"]["amount"], 980.00)
        with self.subTest():
            """Validate date formats"""
            date_format = "%B %d, %Y"
            self.assertTrue(bool(datetime.datetime.strptime(result["data"]["issued_date"], date_format)))
        with self.subTest():
            """Validate billing period"""
            billing_start, billing_end = result["data"]["billing_period"].split(" - ")
            self.assertEqual(datetime.datetime.strptime(billing_start, date_format).month, 1)
            self.assertEqual(datetime.datetime.strptime(billing_end, date_format).month, 1)

    def tearDown(self):
        """Reset mocks"""
        self.mock_db.reset_mock()
        self.mock_session.reset_mock()

if __name__ == "__main__":
    unittest.main(verbosity=2)
