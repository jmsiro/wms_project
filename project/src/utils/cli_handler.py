import re
import argparse
from ..logs.logs import logger
from datetime import datetime, timedelta

logger = logger.getLogger("INPUT_HANDLER")

class CliHandler():
    def __init__(self):
        pass

    @staticmethod
    def get_args():

        def _verify_year(year):
            try:
                if int(year) >= 1900:
                    return year
                else:
                    raise argparse.ArgumentTypeError("Year must be 1900 or later.")
            except ValueError:
                raise argparse.ArgumentTypeError("Year must be type integer.")

        date = datetime.now().replace(day=1)
        end_date = date - timedelta(days=1)
        year_input = end_date.year
        month_input = end_date.month

        parser = argparse.ArgumentParser(
            prog="ShipHero Billing System",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description="Charge or reprocess customers invoices.",
            epilog="Usage examples:\n\
                ► python main.py charge                         >>>> Create invoice for every account for previous month.\n\
                ► python main.py charge -a 1                    >>>> Create invoice for account 1 for previous month.\n\
                ► python main.py charge -a 1 -y 2025 -m 1       >>>> Create invoice for account 1 for January 2025.\n\
                ► python main.py reprocess -i SH-1-1            >>>> Reprocess invoice SH-1-1 in dry run mode.\n\
                ► python main.py reprocess -i SH-1-1 -dr False  >>>> Reprocess invoice SH-1-1 and commit changes.")
        
        subparsers = parser.add_subparsers(dest="job", required=True, help="Available jobs")

        charge_parser = subparsers.add_parser("charge", description="Create invoices for customers", 
                                              help="Creates invoices in bulk for all accounts from the last previous month or a single invoice for a specified account and date.")
        charge_parser.add_argument("-a", "--account", required=False, type=int, 
                                   help="Account Id (optional).", dest="account")
        charge_parser.add_argument("-y", "--year", required=False, default=year_input, type=_verify_year, 
                                    help="Year (optional). Defaults to the year of the last completed month if not provided.", metavar="INT[1900-]", dest="year")
        charge_parser.add_argument("-m", "--month", required=False, default=month_input, type=int, 
                                    help="Month (optional). Defaults to the month of the last completed month if not provided.", choices=range(1,13), dest="month")
        charge_parser.add_argument("-s", "--status", required=False, default="UNPAID", type=str,
                                   help="Financial status of the invoice.")
        
        reprocess_parser = subparsers.add_parser("reprocess", description="Reprocess an invoice", 
                                                 help="Recalculates an invoice to reflect its new value. Use the dry-run flag to preview changes without saving to the database.")
        reprocess_parser.add_argument("-i", "--invoice", required=True, type=str, 
                                      help="Invoice number to reprocess.", dest="invoice")
        reprocess_parser.add_argument("-dr", "--dry-run", required=False, default=False, action="store_true",
                                      help="Dry Run: Use this flag to preview changes without saving them.", dest="dry_run")

        args = parser.parse_args()
        result = vars(args)

        if args.job == "reprocess":
            match = re.match(r'^SH-\d+-\d+$', result["invoice"])
            if not match:
                logger.error("Invalid invoice number. Exiting...")
                exit(1)
            result['account'] = match.string.split('-')[1]

        return result
            
