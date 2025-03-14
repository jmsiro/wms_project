# ShipHero Project

- [ShipHero Project](#shiphero-project)
  - [Project Overview](#project-overview)
  - [Features](#features)
  - [Requirements](#requirements)
  - [Setup Instructions](#setup-instructions)
    - [1. Clone the Repository](#1-clone-the-repository)
    - [2. Environment Configuration](#2-environment-configuration)
    - [3. Docker Compose Up](#3-docker-compose-up)
    - [4. Database Initialization](#4-database-initialization)
  - [Usage](#usage)
    - [Executing Commands](#executing-commands)
      - [Option 1: From the Host Machine](#option-1-from-the-host-machine)
      - [Option 2: Inside the Application Container](#option-2-inside-the-application-container)
    - [CLI Commands](#cli-commands)
      - [Examples](#examples)
    - [Main Functions](#main-functions)
      - [`Charge`](#charge)
      - [`Reprocess`](#reprocess)
      - [`Rates`](#rates)
  - [Testing](#testing)
    - [Running Tests](#running-tests)
  - [Database](#database)
    - [Database Schema](#database-schema)
    - [Test Database](#test-database)

## Project Overview
This project is a billing system for ShipHero, designed to handle customers invoicing and reprocessing. It is is a command-line application built with Python and SQLAlchemy and interacts with a MySQL database.

## Features
The system provides three core functionalities:
1. **Invoice Generation**:  Generates invoices for all accounts or a specific account for a specified billing period.
2. **Invoice Reprocessing**: Recalculates and updates existing invoices to adjust amounts based on current shipment rates.
3. **Rates Management**: Allows updating and creating rates for specific accounts

## Requirements

-   Docker
-   Docker Compose

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <repository_url>
cd <repository_directory>
```

### 2. Environment Configuration
Create a `.env` file in the root directory with the following variables:

```
MYSQL_ROOT_PASSWORD=<your_mysql_root_password>
MYSQL_DATABASE=testsh
```

Replace `<your_mysql_root_password>` with your desired MySQL root password.

### 3. Docker Compose Up
Run the following command to build and start the services:

```bash
docker-compose up --build
```

This command builds the application image and starts the `app`, `redis`, and `db` services as defined in the `docker-compose.yml` file.

### 4. Database Initialization
The MySQL database initializes automatically on startup by executing the SQL scripts located in the `docker_db/initdb.d` directory. This sets up the necessary tables and sample data. The models.sql file contains the database schema.

## Usage

### Executing Commands

You can execute commands in two ways:

#### Option 1: From the Host Machine

Run commands directly from your host machine, interacting with the Docker container. Use the following structure:

```bash
docker exec -it project_app python main.py <command> <options>
```

#### Option 2: Inside the Application Container

Access the application container's bash shell and run commands from there:

```bash
docker exec -it project_app bash
```

Once inside the container, you can run the commands directly:

```bash
python main.py <command> <options>
```

### CLI Commands

The application provides a command-line interface (CLI) for charging, reprocessing invoices, and managing rates.

To get help from the CLI, use the following commands:

**From the Host Machine:**

```bash
docker exec -it project_app python main.py --help
docker exec -it project_app python main.py charge --help
docker exec -it project_app python main.py reprocess --help
docker exec -it project_app python main.py rates --help
```

**Inside the Application Container:**

```bash
python main.py --help
python main.py charge --help
python main.py reprocess --help
python main.py rates --help
```

#### Examples

**From the Host Machine:**

-   Generate invoices for all accounts for the last closed month:
    ```bash
    docker exec -it project_app python main.py charge
    ```

-   Generate an invoice for account 1 for the last closed month:
    ```bash
    docker exec -it project_app python main.py charge -a 1
    ```

-   Generate an invoice for account 1 for January 2025:
    ```bash
    docker exec -it project_app python main.py charge -a 1 -y 2025 -m 1
    ```

-   Reprocess invoice SH-1-1 in dry-run mode (preview changes without saving):
    ```bash
    docker exec -it project_app python main.py reprocess -i SH-1-1 -dr
    ```

-   Reprocess invoice SH-1-1 and save changes:
    ```bash
    docker exec -it project_app python main.py reprocess -i SH-1-1
    ```

-   Update rates for account 1 setting national rate to 15 and international rate to 30:
    ```bash
    docker exec -it project_app python main.py rates -a 1 -n 15 -i 30 -uc
    ```

**Inside the Application Container:**

-   Generate invoices for all accounts for the last closed month:
    ```bash
    python main.py charge
    ```

-   Generate an invoice for account 1 for the last closed month:
    ```bash
    python main.py charge -a 1
    ```

-   Generate an invoice for account 1 for January 2025:
    ```bash
    python main.py charge -a 1 -y 2025 -m 1
    ```

-   Reprocess invoice SH-1-1 in dry-run mode (preview changes without saving):
    ```bash
    python main.py reprocess -i SH-1-1 -dr
    ```

-   Reprocess invoice SH-1-1 and save changes:
    ```bash
    python main.py reprocess -i SH-1-1
    ```

-   Update rates for account 1 setting national rate to 15 and international rate to 30:
    ```bash
    python main.py rates -a 1 -n 15 -i 30 -uc
    ```

### Main Functions

#### `Charge`

This function generates an invoice to bill a customer for shipments made during the specified billing period.

If no arguments are provided, it creates invoices for all accounts for the last closed month. Alternatively, specific arguments can be passed to generate an invoice for a particular account and period.

Arguments:

-   `account_id (optional)`: ID of the customer account to bill.
-   `year (optional)`: Billing period year.
-   `month (optional)`: Billing period month.
-   `status (optional)`: Status of the generated invoice.

#### `Reprocess`

This function recalculates an invoice to update amounts based on shipment type.

Arguments:

-   `invoice_number`: Invoice number to reprocess.
-   `dry_run`: If True, runs a preview without saving changes; set to False to apply updates.

#### `Rates`

This function gets or modifies rates for an account.

Arguments:

-   `account_id`: ID of the customer account.
-   `national`: National rate.
-   `international`: International rate.
-   `update_create`: If True, updates or creates rates for the account.

## Testing

### Running Tests

To run the tests, you can choose to execute the commands from the host machine or inside the application container.

**From the Host Machine:**
```bash
docker exec -it project_app python -m unittest discover ./tests
```

**Inside the Application Container:**
First, access the application container:
```bash
docker exec -it project_app bash
```
Then, navigate to the tests directory and run the tests:
```bash
cd project/tests
python -m unittest discover .
```
This command discovers and runs all test files in the current directory.

## Database

### Database Schema

The database schema is defined in `docker_db/initdb.d/models.sql`. It includes the following tables:

-   `accounts`: Stores account information.
-   `shipments`: Stores shipment details.
-   `shipment_types`: Stores shipment types.
-   `rates`: Stores rates for different shipment types.
-   `invoices`: Stores invoice information.
-   `invoice_items`: Stores individual invoice items.

### Test Database

The test environment uses a separate database named `testsh_dev`. The test setup and teardown scripts (`test_setUp.sql` and `test_tearDown.sql`) are used to initialize and clean up the test database before and after running tests.