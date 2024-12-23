## Prerequisites

- Python 3.12 or higher
- PostgreSQL or MySQL server
- `pip` (Python package installer)

---

## Installation

### 1. Clone the Repository

```sh
git clone git@github.com:iamkuug/anonymize.git
cd anonymize
```

### 2. Create and Activate a Virtual Environment

```sh
python3 -m venv env
source env/bin/activate
```

### 3. Install Dependencies

```sh
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root directory and add your database credentials:

```env
DATABASE_USER=your_db_user
DATABASE_PASSWORD=your_db_password
DATABASE_HOST=your_db_host
DATABASE_PORT=your_db_port
DATABASE_NAME=your_db_name
```

---

## Setting Up the Configuration File

The script requires a configuration file to define the database dialect, batch size, and specific column mappings for anonymization. Below is an example and instructions on how to create it.

### 1. Create the Configuration File

Create a YAML configuration file named `config.yaml` in the project root directory:

```yaml
tables:
    users:
      primary_key: id
      shuffle:
        - email: email  # anonymize email address column
        - phone: phone  # anonymize phone column
        - password: password  # anonymize password column
        - address: address  # anonymize address column
    orders:
      primary_key: id
      shuffle:
        - shipping_address: address  # anonymize address column
        - order_date: date  # anonymize date column
```

### 2. Configuration File Details

- **`batch_size`**: Determines the number of records processed in each batch. Adjust for performance.
- **`tables`**: Defines the tables to anonymize:
  - **`primary_key`**: Specifies the primary key for each table to maintain referential integrity.
  - **`shuffle`**: Maps the column names in the database to their corresponding PII type:
    - **`email`**: Emails
    - **`phone`**: Phone numbers
    - **`password`**: Password fields
    - **`address`**: Addresses
    - **`date`**: Date fields

### 3. Using the Configuration File

The script automatically loads `config.yaml` from the project root. Ensure the file is properly set up before running the script.

## Database Setup

### 1. Ensure Your Database Server is Running

- Start your PostgreSQL or MySQL server.

### 2. Prepare a Test Database (Optional)

For testing in preview mode, create a test database manually:
- Create a database named `test_db` using your preferred SQL dialect.
- Use the `--preview` flag to run the script in preview mode.

Example:

```sql
CREATE DATABASE test_db;
```

---

## Usage

### 1. Run in Preview Mode (Test Database)

Preview mode anonymizes data in a test database without making changes to your production or staging environment.

```sh
python index.py --preview
```

#### Use PostgreSQL in Preview Mode:

```sh
python index.py --preview --postgres
```

### 2. Run with PostgreSQL

Anonymizes data in your configured PostgreSQL database.

```sh
python index.py --postgres
```

### 3. Run Normally (Default to MySQL)

Anonymizes data in your configured MySQL database.

```sh
python index.py
```

---

## Notes

- **Backup Your Data**: Always back up your database before running the anonymization script.
- **Configuration**: Refer to the configuration template to customize which columns are anonymized.
