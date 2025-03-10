CREATE DATABASE IF NOT EXISTS testsh;
CREATE DATABASE IF NOT EXISTS testsh_dev;
USE testsh;

create table accounts
(
    id                                 int auto_increment            primary key,
    account_name                       varchar(45)                   not null,
    created_at                         datetime                      not null
)
    charset = utf8mb3;

insert into accounts (account_name, created_at) values
('Juan','2025-01-01T09:00:00'),
('Maria','2025-01-01T09:00:00'),
('Pedro','2025-01-01T09:00:00');

create table shipments
(
    id                                 int auto_increment            primary key,
    account_id                         int                           not null,
    created_at                         datetime                      not null,
    country                            varchar(45)                   not null,
    is_billed                          boolean                       null
)
    charset = utf8mb3;

insert into shipments (account_id, created_at, country) values
(1, '2025-01-01T09:00:00', 'US'),
(1, '2025-01-01T09:00:00', 'CA'),
(1, '2025-01-05T09:00:00', 'US'),
(1, '2025-01-05T10:00:00', 'US'),
(1, '2025-01-05T09:00:00', 'CA'),
(1, '2025-01-05T10:00:00', 'CA'),
(1, '2025-01-10T09:00:00', 'US'),
(1, '2025-01-10T10:00:00', 'US'),
(1, '2025-01-10T11:00:00', 'US'),
(1, '2025-01-10T09:00:00', 'CA'),
(1, '2025-01-10T10:00:00', 'CA'),
(1, '2025-01-10T11:00:00', 'CA'),
(1, '2025-01-15T09:00:00', 'US'),
(1, '2025-01-15T10:00:00', 'US'),
(1, '2025-01-15T11:00:00', 'US'),
(1, '2025-01-15T12:00:00', 'US'),
(1, '2025-01-15T09:00:00', 'CA'),
(1, '2025-01-15T10:00:00', 'CA'),
(1, '2025-01-15T11:00:00', 'CA'),
(1, '2025-01-15T12:00:00', 'CA'),
(1, '2025-01-20T09:00:00', 'US'),
(1, '2025-01-20T10:00:00', 'US'),
(1, '2025-01-20T11:00:00', 'US'),
(1, '2025-01-20T12:00:00', 'US'),
(1, '2025-01-20T13:00:00', 'US'),
(1, '2025-01-20T09:00:00', 'CA'),
(1, '2025-01-20T10:00:00', 'CA'),
(1, '2025-01-20T11:00:00', 'CA'),
(1, '2025-01-20T12:00:00', 'CA'),
(1, '2025-01-20T13:00:00', 'CA'),
(1, '2025-01-25T09:00:00', 'US'),
(1, '2025-01-25T10:00:00', 'US'),
(1, '2025-01-25T11:00:00', 'US'),
(1, '2025-01-25T12:00:00', 'US'),
(1, '2025-01-25T13:00:00', 'US'),
(1, '2025-01-25T14:00:00', 'US'),
(1, '2025-01-25T09:00:00', 'CA'),
(1, '2025-01-25T10:00:00', 'CA'),
(1, '2025-01-25T11:00:00', 'CA'),
(1, '2025-01-25T12:00:00', 'CA'),
(1, '2025-01-25T13:00:00', 'CA'),
(1, '2025-01-25T14:00:00', 'CA'),
(1, '2025-01-30T09:00:00', 'US'),
(1, '2025-01-30T10:00:00', 'US'),
(1, '2025-01-30T11:00:00', 'US'),
(1, '2025-01-30T12:00:00', 'US'),
(1, '2025-01-30T13:00:00', 'US'),
(1, '2025-01-30T14:00:00', 'US'),
(1, '2025-01-30T15:00:00', 'US'),
(1, '2025-01-30T09:00:00', 'CA'),
(1, '2025-01-30T10:00:00', 'CA'),
(1, '2025-01-30T11:00:00', 'CA'),
(1, '2025-01-30T12:00:00', 'CA'),
(1, '2025-01-30T13:00:00', 'CA'),
(1, '2025-01-30T14:00:00', 'CA'),
(1, '2025-01-30T15:00:00', 'CA'),
(2, '2025-01-01T09:00:00', 'US'),
(2, '2025-01-01T09:00:00', 'CA'),
(2, '2025-01-05T09:00:00', 'US'),
(2, '2025-01-05T10:00:00', 'US'),
(2, '2025-01-05T09:00:00', 'CA'),
(2, '2025-01-05T10:00:00', 'CA'),
(2, '2025-01-10T09:00:00', 'US'),
(2, '2025-01-10T10:00:00', 'US'),
(2, '2025-01-10T11:00:00', 'US'),
(2, '2025-01-10T09:00:00', 'CA'),
(2, '2025-01-10T10:00:00', 'CA'),
(2, '2025-01-10T11:00:00', 'CA'),
(2, '2025-01-15T09:00:00', 'US'),
(2, '2025-01-15T10:00:00', 'US'),
(2, '2025-01-15T11:00:00', 'US'),
(2, '2025-01-15T12:00:00', 'US'),
(2, '2025-01-15T09:00:00', 'CA'),
(2, '2025-01-15T10:00:00', 'CA'),
(2, '2025-01-15T11:00:00', 'CA'),
(2, '2025-01-15T12:00:00', 'CA'),
(2, '2025-01-20T09:00:00', 'US'),
(2, '2025-01-20T10:00:00', 'US'),
(2, '2025-01-20T11:00:00', 'US'),
(2, '2025-01-20T12:00:00', 'US'),
(2, '2025-01-20T13:00:00', 'US'),
(2, '2025-01-20T09:00:00', 'CA'),
(2, '2025-01-20T10:00:00', 'CA'),
(2, '2025-01-20T11:00:00', 'CA'),
(2, '2025-01-20T12:00:00', 'CA'),
(2, '2025-01-20T13:00:00', 'CA'),
(2, '2025-01-25T09:00:00', 'US'),
(2, '2025-01-25T10:00:00', 'US'),
(2, '2025-01-25T11:00:00', 'US'),
(2, '2025-01-25T12:00:00', 'US'),
(2, '2025-01-25T13:00:00', 'US'),
(2, '2025-01-25T14:00:00', 'US'),
(2, '2025-01-25T09:00:00', 'CA'),
(2, '2025-01-25T10:00:00', 'CA'),
(2, '2025-01-25T11:00:00', 'CA'),
(2, '2025-01-25T12:00:00', 'CA'),
(2, '2025-01-25T13:00:00', 'CA'),
(2, '2025-01-25T14:00:00', 'CA'),
(2, '2025-01-30T09:00:00', 'US'),
(2, '2025-01-30T10:00:00', 'US'),
(2, '2025-01-30T11:00:00', 'US'),
(2, '2025-01-30T12:00:00', 'US'),
(2, '2025-01-30T13:00:00', 'US'),
(2, '2025-01-30T14:00:00', 'US'),
(2, '2025-01-30T15:00:00', 'US'),
(2, '2025-01-30T09:00:00', 'CA'),
(2, '2025-01-30T10:00:00', 'CA'),
(2, '2025-01-30T11:00:00', 'CA'),
(2, '2025-01-30T12:00:00', 'CA'),
(2, '2025-01-30T13:00:00', 'CA'),
(2, '2025-01-30T14:00:00', 'CA'),
(2, '2025-01-30T15:00:00', 'CA');

create  table shipment_types
(
	id                                 int auto_increment            primary key,
    name                     		   varchar(40)                   not null
)
    charset = utf8mb3;
    
insert into shipment_types (name) values
('NATIONAL'),
('INTERNATIONAL');

create table rates
(
    id                                 int auto_increment            primary key,
    account_id                         int                           null,
    shipment_type_id                   int  						 not null,
    price                              decimal(4, 2)                 not null,
    created_at                         datetime                      not null,
    updated_at                         datetime                      null
)
    charset = utf8mb3;

insert into rates (account_id, shipment_type_id, price, created_at) values
(null, 1, 10, current_timestamp),
(null, 2, 25, current_timestamp),
(1, 1, 5, current_timestamp),
(1, 2, 20, current_timestamp);

create table invoices
(
    id                                 int auto_increment            primary key,
    account_id                         int                           not null,
    issued_at                          datetime                      not null,
    invoice_number                     varchar(128)                  not null,
    status                             enum('UNPAID', 'PAID', 'VOIDED')  not null,
    amount                             decimal(9, 2)                 not null
)
    charset = utf8mb3;

ALTER TABLE invoices ADD UNIQUE `unique_invoice`(account_id, issued_at);

insert into invoices (account_id, issued_at, invoice_number, status, amount) values
(1, '2025-02-01 00:00:00', 'SH-1-1', 'UNPAID', 700.00);

create table invoice_items
(
    id                                 int auto_increment            primary key,
    invoice_id                         int                           not null,
    shipment_type_id                   int                           not null,
    description                        varchar(128)                  not null,
    quantity                           int                           not null,
    unit_price                         decimal(9, 2)                 not null,
    amount                             decimal(9, 2)                 not null
)
    charset = utf8mb3;
    
INSERT INTO invoice_items (invoice_id, shipment_type_id, description, quantity, unit_price, amount) VALUES
(1, 1, 'National shipments of 2025-01-01', 1, 5.0, 5.0),
(1, 2, 'International shipment of 2025-01-01', 1, 20.0, 20.0),
(1, 1, 'National shipments of 2025-01-05', 2, 5.0, 10.0),
(1, 2, 'International shipment of 2025-01-05', 2, 20.0, 40.0),
(1, 1, 'National shipments of 2025-01-10', 3, 5.0, 15.0),
(1, 2, 'International shipment of 2025-01-10', 3, 20.0, 60.0),
(1, 1, 'National shipments of 2025-01-15', 4, 5.0, 20.0),
(1, 2, 'International shipment of 2025-01-15', 4, 20.0, 80.0),
(1, 1, 'National shipments of 2025-01-20', 5, 5.0, 25.0),
(1, 2, 'International shipment of 2025-01-20', 5, 20.0, 100.0),
(1, 1, 'National shipments of 2025-01-25', 6, 5.0, 30.0),
(1, 2, 'International shipment of 2025-01-25', 6, 20.0, 120.0),
(1, 1, 'National shipments of 2025-01-30', 7, 5.0, 35.0),
(1, 2, 'International shipment of 2025-01-30', 7, 20.0, 140.0);