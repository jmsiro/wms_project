# ShipHero Backend Take Home Project

ShipHero WMS is a fully featured Warehouse Management System designed for DTC brands and 3PL providers running their own warehouse and shipping operations.
The goal of this project is to write two jobs described in the Requirements section.

## Before you start working on the project please read these recommendations:


* Please read the whole project specification carefully and ask all the questions you feel would help you to do the most accurate solution you can, there's no such thing as a stupid question!
* We respect the time you decide to spent doing this test, that's why we want to recommend you to submit **only** the things explicitly asked for in this spec, there's no such thing as extra points for features out of the scope. **Quality is critical so please define how you would test and validate the changes. Bonus if you can explain how to automate the test.**
* You're always welcome to propose and discuss any improvements you find.
* Please return the exercise as soon as you can and in no more than  **2 days** once you begin.

NOTE: If AI is suspected/used, candidate will be immediately disqualified from consideration. 


## Requirements


### As ShipHero, I’d like to charge my customers for their shipping operations, so my business is profitable
ShipHero customers ship national and international orders. At the beginning of each month, we must generate an invoice to charge them for their shipping operations.

We must support shipment default rates, AND specific customers could have their own rates.
Invoices could have three different statuses: UNPAID, PAID, and VOIDED. The default status of an invoice is UNPAID.

Here’s an example of a simple rate sheet:

| Customer | National | International
|--------|------------|--------------
| Default price | 10 | 25
| 1 | 5 | 20

The rate sheet defines which price should be applied according to the customer and the type of shipment

The invoice must show:
* Invoice number (e.g. SH-{customer_id}-{invoice_id})
* Issued date (e.g. February 01, 2025)
* Billing period (e.g. January 01, 2025 - January 31, 2025)
* Invoice items grouped by day and type of shipment
* * Description (e.g. National shipment)
* * Quantity of shipments (e.g. 5)
* * Unit price (e.g. 10)
* * Amount (e.g. 50)

Acceptance criteria: once this process has been completed, we expect to have the data in the database to generate an invoice file to send to the customers. Note: It’s out of the scope of this requirement to generate an invoice file.

### As ShipHero, I’d like to be able to reprocess invoices, so I can amend incorrect charges
Rates could change depending on the time of the year. Partners such as USPS, Fedex, and Canada Post provide these rates. Sometimes, our finance team receives these rates late, and invoices are generated with outdated rates.

We need a mechanism to reprocess invoices. Since we usually want to validate differences between invoices before updating the invoice, it must provide a dry run feature that should work the following way

* dry_run=True: returns the difference in the charges by shipment without committing changes in the database
* dry_run=False: returns the difference in the charges by shipment and commits the changes in the database

Only UNPAID invoices can be reprocessed with dry_run=False. For invoices with other statuses, even if we cannot reprocess them, it’s good to allow reprocessing with dry_run=True to understand the difference between the current charge and what should have been charged.

Acceptance criteria: once this process has been completed, depending on the configuration, we expectect to have the difference in the charges by shipment. It's out of the scope of this requirement to build a CRUD to manage rates, we can manually update the records in the rates table for testing purposes.

## Tables

model.sql contains the database model plus some data to process

![Database Diagram](./database/diagram.png?raw=true)

### shipments

| Column | Description
|--------|-------------
| id | Unique identifier
| account_id | Unique identifier of the customer account
| created_at | Date when the order was shipped
| country | Country code by alpha-2
| is_billed | Indicates wether the shipment is billed or not

### rates

| Column | Description
|--------|-------------
| id | Unique identifier
| account_id | Unique identifier of the customer account
| shipment_type | Type of the shipment
| price | Price of the shipment
| created_at | Date when the rate was created
| updated_at | Date of the last time the rate was updated

### invoices

| Column | Description
|--------|-------------
| id | Unique identifier
| account_id | Unique identifier of the customer account
| issued_at | Date when the invoice was created
| invoice_number | External unique identifier
| status | Status of the invoice
| amount | Total amount of the invoice

### invoice_items

| Column | Description
|--------|-------------
| id | Unique identifier
| invoice_id | Unique identifier of the invoice where the item belong
| description | Information about the items in the invoice. E.g.: National shipment
| quantity | Number of items
| unit_price | Price of a single item
| amount | Total amount of the items

## How to submit your solution?
Please open a PR with your changes so we can review it and give you some feedback if there's place for it, your PR must have:
* A description of your solution and design decisions you made or anything you think it's worthwhile to mention.  Use the GitHub PR description for this
* The code for your solution

## How to communicate with us?
We're going to invite you to our Slack channel as a guest, in this channel, all the people involved in the interviewing process will be present. You can post your questions or anything related to the process and we'll answer as soon as possible.

## What comes after this project?
We'll be scheduling a call to ask questions about the project, your solution and the general experience.

**Good luck!**


