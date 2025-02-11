import os
import sys
import configparser
from src.logs.logs import initialize, logger
from src.database import db

if __name__ == '__main__':

    LOGS_LEVEL = 'INFO'
    initialize(LOGS_LEVEL)
    logger = logger.getLogger("MAIN")
    logger.info("Starting...")

    config_file = 'config.ini'
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), config_file))

    job = sys.argv[1].lower()

    DBDATA = {k:v for k,v in config['DATABASE'].items()}
    dbInstance = db.dbInstance(DBDATA)

    if job == '-charge':
        # I thought on using Year and Month as if the user enter bothe inputs
        # TODO: Automate? - Could use first laborable day of the month
        account_id = 2 or int(input("Enter the account id: ")) # Should be taken from current user
        year_input = 2025 or int(input("Enter the year: "))
        month_input = 1 or int(input("Enter the month: "))

        logger.info("Creating invoice for {0}-{1}. Account Id # {2}".format(year_input, month_input, account_id))

        invoice_data = dbInstance.charge_customer(account_id=account_id, year=year_input, month=month_input, status='UNPAID')
    
    if job == '-reprocess':
        # I thought on using Invoice Number and Dry Run as if the user enter the input
        invoice_number = 'SH-2-24' or input("Enter the invoice number: ")
        dry_run = input("Dry run? (y/n): ").lower()
        if dry_run == 'y':
            message = "Dry run mode enabled."
            dry_run = True
        elif dry_run == 'n':
            message = "Dry run mode disabled."
            dry_run = False
        else:
            logger.error("Invalid input. Exiting...")
            sys.exit(1)
        account_id = invoice_number.split('-')[1] or int(input("Enter the account id: ")) # Should be taken from current user
        
        logger.info("Reprocessing invoice {0}.\nAccount Id # {1}\n{2}".format(invoice_number, account_id, message))
        dbInstance.reprocess_invoice(account_id=account_id, invoice_number=invoice_number, dry_run=dry_run)

    # TODO: Exception management.