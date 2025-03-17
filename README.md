# B2Broker-Wallet API

This project is a production-ready Django REST API server built using Django Rest Framework (DRF) with JSON:API specification support. It implements two models:

- **Wallet**: Stores a wallet with a label and balance. The balance is automatically updated by summing related transaction amounts. The wallet balance must never become negative.
- **Transaction**: Represents a deposit or withdrawal with a unique transaction ID (`txid`) and an amount (positive for deposits, negative for withdrawals). The creation, update, or deletion of a transaction updates the associated wallet's balance.

---

## Tech Stack

- **Python**: 3.11+
- **Django**: 4.x
- **Django Rest Framework**
- **djangorestframework-jsonapi** (for JSON:API compliance)
- **PostgreSQL** as the database
- **Docker & Docker Compose** for containerization and ease of setup
- **drf-spectacular** for API documentation (Swagger/OpenAPI)
- **flake8** for linting

---


## Features

- **CRUD** features for wallets and transactions
- **Pagination, Filtering & Sorting**: The API endpoints support standard JSON:API pagination, filtering, and sorting parameters.
- **Logging & Testing**: Comprehensive unit and integration tests cover wallet and transaction operations.
- **Dockerized Setup**: Run the entire stack (Django app and PostgreSQL) via Docker Compose.
- **Swagger Documentation**: Interactive API docs available at `/docs/swagger/`.

---

## Data Models


### Wallet Model

The **Wallet** model represents a financial wallet that holds a balance derived from related transactions.

#### Fields

- **id**
  - **Type:** AutoField (Primary Key)
  - **Description:** A unique identifier for each wallet.

- **label**
  - **Type:** CharField (max_length=100)
  - **Description:** A human-readable label or name for the wallet.
  - **Database Index:**  
    An index is created on this field to optimize search queries and sorting by label.

- **balance**
  - **Type:** DecimalField (max_digits=36, decimal_places=18)
  - **Description:** The wallet’s current balance, computed as the sum of all related transaction amounts.
  - **Business Rule:**  
    - The balance should **never be negative**. Custom logic in the model (or during transaction processing) prevents any transaction that would result in a negative balance.

#### Database Indexes for Wallet

- **Index on `label`:**  
  Improves performance when filtering or ordering wallets by their label.

---

### Transaction Model

The **Transaction** model represents an individual financial operation that affects a wallet’s balance. Transactions may be deposits (positive amounts) or withdrawals (negative amounts).

#### Fields

- **id**
  - **Type:** AutoField (Primary Key)
  - **Description:** A unique identifier for each transaction.

- **wallet**
  - **Type:** ForeignKey to the Wallet model
  - **Description:** The wallet that the transaction is associated with.
  - **Database Index:**  
    An index on the foreign key improves performance when filtering transactions by wallet.

- **txid**
  - **Type:** CharField (max_length=255, unique=True)
  - **Description:** A unique transaction identifier.
  - **Database Index:**  
    The uniqueness constraint automatically creates a unique index to ensure that each transaction is uniquely identifiable.

- **amount**
  - **Type:** DecimalField (max_digits=36, decimal_places=18)
  - **Description:** The transaction amount.
  - **Business Rule:**  
    - Positive values indicate deposits.
    - Negative values indicate withdrawals.
    - The creation, update, or deletion of a transaction updates the associated wallet’s balance.
    - A transaction is not allowed if it would cause the wallet’s balance to become negative.

#### Database Indexes for Transaction

- **Index on `wallet`:**  
  Speeds up lookups and filtering of transactions by the wallet.
- **Unique Index on `txid`:**  
  Ensures that duplicate transactions are not allowed.

---

### Business Logic and Data Integrity

- **Wallet Balance Integrity:**  
  The wallet’s balance is computed as the sum of all transaction amounts related to that wallet. Custom logic in the model's `save()` and `delete()` methods (or using signals) ensures that a wallet’s balance never becomes negative.

- **Atomic Updates:**  
  Database transactions (atomic blocks and row-level locking) are used when updating the wallet’s balance. This prevents race conditions and ensures data consistency.

- **Optimized Queries:**  
  The use of indexes on key fields (`label`, `txid`, and the `wallet` foreign key) improves performance for filtering, sorting, and lookup operations, ensuring that the API remains responsive even as data grows.

---

## Installation

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

### Local Installation (Without Docker)

1. **Clone the Repository:**

   ```bash
   git clone <your-repo-url> b2broker-wallet
   cd b2broker-wallet

2. **Create and Activate a Virtual Environment**
    ```bash
   python -m venv venv
   source venv/bin/activate
   
3. **Install dependenices**
    ```bash
   pip install -r requirements.txt
   
4. Ensure you have a PostgreSQL instance running and update your api/settings.py (or use environment variables) with your PostgreSQL credentials.

5. **Apply Migrations**
    ```Bash
   python manage.py makemigrations
   python manage.py migrate  

   Note: Sometimes django cannot automatically detect  
   so use explicit:
   
   python manage.py makemigrations wallet
   python manage.py migrate wallet
   
6. **Run the server**
   ```bash
   python manage.py runserver
The API is available at http://127.0.0.1:8000/

## Running with Docker Compose

1. **Build and Start Containers**
   ```bash
   docker-compose up --build
2. **Access the API**
   * The API is available at http://localhost:8000/
   * Swagger documentation is available at http://localhost:8000/docs/swagger/

3. **Stop the Containers**
   ```bash
   docker-compose down
   
---

## Testing 

Project contains both unit and integration tests under `wallets/tests` folder
**You can run them inside the container with**:

```docker-compose exec web python manage.py test```  

### Manual testing examples
To manually test the API endpoints with Postman, use the following sample request bodies and endpoints. All requests must include the headers:

* `Accept: application/vnd.api+json`
* For POST, PATCH, PUT requests, also include:
  * `Content-Type: application/vnd.api+json`

#### Wallet endpoints
1. Create Wallet
   * **Method**: POST
   * **URL**: `http://localhost:8000/api/wallets/`
   * **Request Body**:
      ```json
     {
          "data": {
          "type": "Wallets",
          "attributes": {
            "label": "New Wallet"
          }
        }
     }
      ```
   
   * **Expected Response:**
     A 201 Created response with the new wallet data in the `"data"` key.


2. Retrieve a Wallet:
    * **Method**: GET
    * **URL**: `http://localhost:8000/api/wallets/{wallet_id}/`
    * **Expected Response:**
      A 200 OK response with the wallet data.

And other crud methods: Update and Delete ...


#### Transaction endpoints:
1. Create a Deposit Transaction
   * **Method**: Post
   * **URL**: `http://localhost:8000/api/transactions/`
   * **Request Body**:
     ```json
        {
          "data": {
              "type": "Transactions",
              "attributes": {
                    "txid": "tx101",
                    "amount": "50.00"
              },
              "relationships": {
                "wallet": {
                    "data": { "type": "Wallets", "id": "{wallet_id}" }
                }
              }
          }
       }
     ```
   * **Expected Response:**  
     A 201 Created response. The wallet’s balance should update accordingly (e.g., if the wallet initially had 100.00, it will become 150.00).

And some other CRUD methods...

### Sorting and Pagination examples
1. Sort Wallets by Label (Ascending)
    * **Method**: GET  
    * **URL**: http://localhost:8000/api/wallets/?sort=label  
    * **Request Body**: None  
    * **Expected Outcome**: The list of wallets is sorted alphabetically in ascending order by the label.  

2. Transactions Pagination Example
    * **Method**: GET
    * **URL**: `http://localhost:8000/api/transactions/?page[number]=2&page[size]=5`
    * **Request Body**: None
    * **Expected Outcome**:  
      The API returns the second page with up to 5 transactions. Pagination details and navigation links should be present in the response.  

## Licence  
This project is licensed under the MIT License. Feel free to modify and adapt for your use case.
