import hashlib
import os
import logging
import yaml

from datetime import datetime, timedelta, date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class Masker:
    @staticmethod
    def mask_phone(phone: str) -> str:
        return f"{'*' * (len(phone) - 4)}{phone[-4:]}"

    @staticmethod
    def mask_name(name: str) -> str:
        return f"{name[0]}{'*' * (len(name) - 2)}{name[-1]}" if len(name) > 2 else name

    @staticmethod
    def mask_address(address: str) -> str:
        parts = address.split()
        if len(parts) > 1:
            masked_parts = [parts[0]] + ["*" * len(part) for part in parts[1:]]
            return " ".join(masked_parts)
        return address

    @staticmethod
    def mask_email(email: str) -> str:
        local, domain = email.split("@")
        return (
            f"{local[0]}{'*' * (len(local) - 2)}{local[-1]}@{domain}"
            if len(local) > 2
            else email
        )

    @staticmethod
    def mask_date(date_value) -> str:
        if isinstance(date_value, date):
            date_value = date_value.strftime("%Y-%m-%d")
        elif not isinstance(date_value, str):
            raise ValueError("Invalid date format")

        parts = date_value.split("-")
        if len(parts) == 3:
            return f"{parts[0]}-**-**"
        return date_value

    @staticmethod
    def _hash_value(value: str) -> str:
        return hashlib.sha256(value.encode()).hexdigest()[
            :10
        ]  # Return first 10 characters of the hash


class Shifter:
    @staticmethod
    def shift_date(date, shift_days: int = 10) -> str:
        shifted_date = date + timedelta(days=shift_days)
        return shifted_date.strftime("%Y-%m-%d")


class DBConnector:
    def __init__(self, dialect, username, password, host, port, database):
        self.dialect = dialect
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.database = database
        self.engine = None
        self.session = None

    def connect(self):
        connection_string = f"{self.dialect}://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        self.engine = create_engine(connection_string)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def execute_query(self, query):
        with self.engine.connect() as connection:
            result = connection.execute(query)
            return result.fetchall()

    def close(self):
        if self.session:
            self.session.close()
        if self.engine:
            self.engine.dispose()


class TestSeeder:
    def __init__(self, dialect="mysql"):

        logging.info("Running TestSeeder ...")

        self.db_config = {
            "user": os.getenv("DATABASE_USER"),
            "password": os.getenv("DATABASE_PASSWORD"),
            "host": os.getenv("DATABASE_HOST"),
            "port": 3306 if dialect == "mysql" else 5432,
            "database": "test_db",
        }

        self.conn = DBConnector(
            dialect,
            self.db_config["user"],
            self.db_config["password"],
            self.db_config["host"],
            self.db_config["port"],
            self.db_config["database"],
        )

    def run_sql(self):
        script_path = "test/test_seed.sql"

        if not os.path.exists(script_path):
            raise FileNotFoundError(f"File {script_path} not found")

        with open(script_path, "r") as file:
            sql_script = file.read()

        for statement in sql_script.split(";"):
            if statement.strip():
                self.conn.execute_query(statement)

        logging.debug(f"Run test script {script_path}")

    def generate_config(self):
        config = {
            "dialect": self.dialect,
            "tables": {
                "users": {
                    "primary_key": "id",
                    "mask_columns": [
                        {"email": "email"},
                        {"phone": "phone"},
                        {"password": "password"},
                        {"address": "address"},
                    ],
                },
                "orders": {
                    "primary_key": "id",
                    "mask_columns": [
                        {"shipping_address": "address"},
                        {"order_date": "date"},
                    ],
                },
            },
        }

        with open("config.preview.yml", "w") as file:
            yaml.dump(config, file, default_flow_style=False)

        logging.debug(f"Generated config file config.preview.yml")

    def run(self):
        try:
            self.conn.connect()
            self.run_sql()
            self.generate_config()
            self.conn.close()
        except Exception as e:
            logging.error("An error occured while running test seeder")
            print(e)
