# ShipHero Project

- [ShipHero Project](#shiphero-project)
  - [Description](#description)
  - [Usage](#usage)
  - [Configuration](#configuration)

## Description
The project includes two main jobs:
1. **Charge Customer**: Creates invoices to charge the customer for the shipments made in the billed period.
2. **Reprocess Invoice**: Reprocesses an invoice to get new amounts per shipment type.

## Usage
1. **Charge Customer**:
    ```sh
    python main.py -charge
    ```
    The user will be prompted to enter the account ID, year, and month as if where using the actual app.
    - The bill period will be the entire month inputed by the user.
    - The issue date will be the first day of the following month from the billed one.
    - When trying to generate an already existing bill, the system will fail. The constraint used id the Account ID and Date, which was selected to avoid modifying the given data structure.
    - The returned value is a dictionary with the following structure:  {"data": {}, "message": ""}
      - "data" will be the actual data that was registered after billing, according with the task. Or None if something went wrong within the process.
      - "message" will described the result of the process.

2. **Reprocess Invoice**:
    ```sh
    python main.py -reprocess
    ```
    The user will be prompted to enter the account ID, invoice number and whether to perform a dry run as if where using the actual app.
    - The invoice number is created using the account ID and the invoice ID, being that a unique combination, the system uses it instead of the period.
    - Disabling Dry Run for PAID bills will not make the system fails, but no update will be done to the bill. 
    - The returned value is a dictionary with the following structure:  {"data": {}, "message": ""}
      - "data" will display the old and new amounts for the bill as well as if there was a difference between what was billed and the reprocess and wether the bill was updated or not.
      - "message" will described the result of the process.

## Configuration
The project uses a configuration file to set up database connection parameters. A sample configuration file is provided:
```ini
[DATABASE]
host = 
port = 
user = 
password = 
database =
```
The name of the file must be change to **config.ini**
In **model.sql** there is the database structure needed to run the jobs along with sample data for testing.