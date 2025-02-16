import os
import sys
import unittest
from pathlib import Path
from unittest import mock
from datetime import datetime, timedelta

PATH = Path(os.path.dirname(__file__)).parent.absolute()
SCRIPT_DIR = os.path.join(PATH,"src")
if SCRIPT_DIR not in sys.path:
    sys.path.append(os.path.dirname(SCRIPT_DIR))
from src.utils.cli_handler import CliHandler

class TestCliHandler(unittest.TestCase):
    def testCliHandler(self):
        """Test CliHandler"""
        args = CliHandler().get_args(["charge", "-a", "1", "-y", "2025", "-m" ,  "1", "-s", "PAID"])
        self.assertIsInstance(args, dict)
        self.assertEqual(args["job"], "charge")
        self.assertEqual(args["account"], 1)
        self.assertEqual(args["year"], 2025)
        self.assertEqual(args["month"], 1)
        self.assertEqual(args["status"], "PAID")
    
    def testCliHandlerNoArgs(self):
        """Test CliHandler with no args"""
        args = CliHandler().get_args(["charge"])
        date = datetime.now().replace(day=1)
        end_date = date - timedelta(days=1)
        year_input = end_date.year
        month_input = end_date.month
        self.assertIsInstance(args, dict)
        self.assertEqual(args["job"], "charge")
        self.assertEqual(args["account"], None)
        self.assertEqual(args["year"], year_input)
        self.assertEqual(args["month"], month_input)
        self.assertEqual(args["status"], "UNPAID")

    def testCliHandlerReprocess(self):
        """Test CliHandler reprocess"""
        args = CliHandler().get_args(["reprocess", "-i", "SH-1-1", "-dr"])
        self.assertIsInstance(args, dict)
        self.assertEqual(args["job"], "reprocess")
        self.assertEqual(args["invoice"], "SH-1-1")
        self.assertEqual(args["dry_run"], True)

    def testCliHandlerWrongInputs(self):
        """Test CliHandler with wrong inputs"""
        with self.subTest():
            """Wrong year"""
            self.assertRaises(SystemExit, CliHandler().get_args, ["charge", "-a", "1", "-y", "1899", "-m" ,  "1", "-s", "PAID"])
        with self.subTest():
            """Wrong month"""
            self.assertRaises(SystemExit, CliHandler().get_args, ["charge", "-a", "1", "-y", "2025", "-m" ,  "13", "-s", "PAID"])
        with self.subTest():
            """Wrong status"""
            self.assertRaises(SystemExit, CliHandler().get_args, ["charge", "-a", "1", "-y", "2025", "-m" ,  "1", "-s", "NOT_PAID"])
        with self.subTest():
            """Wrong job"""
            self.assertRaises(SystemExit, CliHandler().get_args, ["bill", "-a", "1", "-y", "2025", "-m" ,  "1", "-s", "PAID"])
        with self.subTest():
            """Wrong reprocess"""
            self.assertRaises(SystemExit, CliHandler().get_args, ["reprocess", "-i", "SH-1-1", "-dr2"])

        