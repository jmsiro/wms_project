import os
from src.logs.logs import initialize, logger
from src.database import db
from src.utils.cli_handler import CliHandler
from src.services.billing import BillingService
from src.services.reprocess import BillReprocessor

if __name__ == "__main__":

    LOGS_LEVEL = "INFO"
    initialize(LOGS_LEVEL)
    logger = logger.getLogger("MAIN")
    logger.info("Billing System Starting...")
    
    connection_string = os.environ["CONN"]
    db_instance = db.DbInstance(connection_string)

    args = CliHandler().get_args()
    if args["job"] == "charge":
        billing = BillingService(db_instance)
        account, year, month, status = args["account"], args["year"], args["month"], args["status"]
        # If no account is specified, bill all
        if account:
            logger.info(f"Creating invoice for Account ID #{account} for period {year}-{month}")
            billed = billing.charge_customer(account_id=account, year=year, month=month, status=status)
        else:
            logger.info(f"Creating invoices for all accounts for period {year}-{month}")
            billed = billing.charge_all(year=year, month=month)

    if args["job"] == 'reprocess':
        reprocessor = BillReprocessor(db_instance)
        account, invoice, dry_run = args["account"], args["invoice"], args["dry_run"]
        msg = "Dry Run" if dry_run else "Commit changes"
        logger.info(f"Reprocessing invoice {invoice}.\nAccount Id # {account}\nMode: {msg}")
        reprocessed = reprocessor.reprocess_invoice(account_id=account, invoice_number=invoice, dry_run=dry_run)