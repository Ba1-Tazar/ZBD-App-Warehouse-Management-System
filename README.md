# Warehouse Management System (WMS) API

This project is an advanced extension of a FastAPI application developed during database laboratory sessions. It serves as a comprehensive Warehouse Management System, focusing on relational data integrity, automated transaction logging, and advanced reporting.

## 🚀 Key Features & Requirements Met

- **Extended Database Schema**: Implementation of 4 additional tables beyond the base user system: `suppliers`, `locations`, `products`, and `warehouse_logs`.
- **Relational Mapping**: Full implementation of One-to-Many (1:N) relationships using Tortoise ORM.
- **Advanced SQL & Aggregation**: Custom reporting module using raw SQL with `JOIN`, `GROUP BY`, and `SUM` for real-time financial valuation.
- **Database Iterators (Cursors)**: High-efficiency reporting via async generators and database cursors to minimize memory footprint.
- **ACID Transactions**: Atomic stock adjustments that guarantee a log entry is created for every quantity change.
- **Role-Based Access Control (RBAC)**: Distinct permissions for standard users (viewing/operating) and administrators (management/reporting).

## 🛠 Tech Stack

- **Backend**: FastAPI (Python)
- **ORM**: Tortoise ORM
- **Database**: PostgreSQL
- **Security**: OAuth2 with Password Hashing

## 📊 Database Schema (ERD)

<img width="1503" height="607" alt="ZBD - App - Project - ERD - Diagram" src="https://github.com/user-attachments/assets/25b46c6b-e880-4853-a885-e4d7844837bb" />

### Database Schema Details

The database is built on **PostgreSQL** using **Tortoise ORM**. Below is a detailed description of the table structures and their business logic:

#### 1. Core & Inventory Tables
* **Users**: Stores administrative and staff credentials. Includes an `is_admin` flag to control access to financial reports and stock management.
* **Suppliers**: Maintains a directory of vendors. This table is linked to `products` to track the source of every item in the warehouse.
* **Locations**: Represents physical warehouse slots (Zone and Shelf). This allows for precise inventory tracking and prevents placement errors.
* **Products**: The central hub for inventory data, storing SKUs, prices, and current stock levels. It acts as a bridge between suppliers and physical locations.

#### 2. Audit & Logging
* **Warehouse Logs**: This is an immutable audit trail table. It records every stock movement, linking the specific **Product**, the **User** who performed the action, and a timestamp. 
    * *Technical Note*: Entries are managed via **ACID transactions** to ensure data consistency between the `products` and `warehouse_logs` tables.

#### 3. Implemented Relationships
* **1:N (One-to-Many)**: 
    * `Suppliers` -> `Products`: A vendor provides multiple items.
    * `Locations` -> `Products`: A shelf can hold various products.
    * `Users` -> `Warehouse Logs`: An employee can perform many actions.
    * `Products` -> `Warehouse Logs`: A single product has a full movement history.

### Entities:
- **Users**: Authentication and administrative flags.
- **Suppliers**: Vendor information and contact details.
- **Locations**: Physical warehouse structure (Zones and Shelves).
- **Products**: Central inventory tracking (SKU, Price, Quantity).
- **Warehouse Logs**: Immutable audit trail of all inventory movements.

## 🏗 Project Architecture

The project follows a **Layered Architecture** to ensure clean code and separation of concerns:

1. **Models Layer (`user/model.py`)**: Defines database entities and Pydantic schemas.
2. **Service Layer (`inventory/service.py`)**: Contains business logic, complex SQL queries, and transactional operations.
3. **Controller Layer (`inventory/controller.py`)**: Manages API routing, request validation, and dependency injection for security.

<img width="281" height="416" alt="image" src="https://github.com/user-attachments/assets/c4cc9f3c-1d9c-4df6-844e-77ab3bc5b4b2" />

## 🚦 Getting Started

### Prerequisites
- Python 3.9+
- PostgreSQL database

### Installation
1. Clone the repository.
2. Install dependencies: `pip install fastapi "tortoise-orm[asyncpg]" uvicorn pydantic "passlib[bcrypt]"`.
3. Configure your database URL in `main.py`.
4. Run the application: `uvicorn main:app --reload`.

### Testing with Swagger
Access the interactive documentation at: `http://127.0.0.1:8000/docs`
