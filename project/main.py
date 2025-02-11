import os
import sys
import time
import configparser
from src.database import db

if __name__ == '__main__':
    config_file = 'config.ini'
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), config_file))

    DBDATA = {k:v for k,v in config['DATABASE'].items()}
    dbInstance = db.dbInstance(DBDATA)

    # TODO: Automate - Could use first laborable day of the month
    invoice_date = "{year}-{month}-01".format(year=2025, month=2)

    dbInstance.charge_customer(account_id=1, date=invoice_date, status='PAID')

    # TODO: Exception management. Logs?