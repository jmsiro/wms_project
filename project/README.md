# ShipHero Project

- [ShipHero Project](#shiphero-project)
  - [Project Overview](#project-overview)
  - [Features](#features)
  - [Setup Instructions](#setup-instructions)
    - [1. Create a Virtual Environment](#1-create-a-virtual-environment)
    - [2. Activate the Virtual Environment](#2-activate-the-virtual-environment)
    - [3. Install Dependencies](#3-install-dependencies)
    - [4. Set Up Environment Variables](#4-set-up-environment-variables)
    - [5. Set Up the Database](#5-set-up-the-database)
  - [Usage](#usage)
    - [CLI Usage](#cli-usage)
      - [Examples:](#examples)
    - [Main Functions](#main-functions)
      - [`Charge`](#charge)
      - [`Reprocess`](#reprocess)
  - [Running Tests](#running-tests)

## Project Overview
This project is a billing system for ShipHero, designed to handle customer invoicing and reprocessing. It is built with Python and SQLAlchemy and interacts with a MySQL database.

## Features
The system provides two core functionalities:
1. **Charge Customer**:  Generate invoices for all accounts or a specific account for a given billing period.
2. **Reprocess Invoice**: Recalculate and update existing invoices to reflect new rates.

## Setup Instructions

### 1. Create a Virtual Environment
To create a virtual environment, run the following command:
```bash
python -m venv venv
```

### 2. Activate the Virtual Environment
Activate the virtual environment using the following command:
- On Windows:
    ```bash
    .\venv\Scripts\activate
    ```
- On macOS/Linux:
    ```bash
    source venv/bin/activate
    ```

### 3. Install Dependencies
Install the required dependencies using the following command:
```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables
Set up the environment variable for the database connection string. Replace `<your_connection_string>` with your actual MySQL connection string.
```bash
export DATABASE_URL="<your_connection_string>"
```
- On Windows:
    ```bash
    set DATABASE_URL="<your_connection_string>"
    ```

### 5. Set Up the Database
Ensure you have a MySQL database running. Load the tables and sample data from the `database/model.sql` file.

## Usage

### CLI Usage
The application provides a command-line interface (CLI) for charging and reprocessing invoices.

To get help from the CLI, use the following commands:
```bash
python main.py --help
python main.py charge --help
python main.py reprocess --help
```

#### Examples:
- Generate invoices for all accounts for the last closed month:
    ```bash
    python main.py charge
    ```
- Generate an invoice for account 1 for the last closed month:
    ```bash
    python main.py charge -a 1
    ```
- Generate an invoice for account 1 for January 2025:
    ```bash
    python main.py charge -a 1 -y 2025 -m 1
    ```
- Reprocess invoice SH-1-1 in dry-run mode (preview changes without saving):
    ```bash
    python main.py reprocess -i SH-1-1 -dr
    ```
- Reprocess invoice SH-1-1 and save changes:
    ```bash
    python main.py reprocess -i SH-1-1
    `
    
### Main Functions

#### `Charge`
This function generates an invoice to bill a customer for shipments made during the specified billing period.

If no arguments are provided, it creates invoices for all accounts for the last closed month. Alternatively, specific arguments can be passed to generate an invoice for a particular account and period.
Arguments:
- `account_id (optional)`: ID of the customer account to bill.
- `year (optional)`: Billing period year.
- `month (optional)`: Billing period month.
- `status (optional)`: Status of the generated invoice.

#### `Reprocess`
This function recalculates an invoice to update amounts based on shipment type.

Arguments:
- `invoice_number`: Invoice number to reprocess.
- `dry_run`: If True, runs a preview without saving changes; set to False to apply updates.

## Running Tests
To run the tests, use the following command:
```bash
python -m unittest discover <test_directory>
```