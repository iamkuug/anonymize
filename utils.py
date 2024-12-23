import hashlib
import os
import logging
import random
import yaml

from datetime import datetime, timedelta, date
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from urllib.parse import quote_plus


class Checker:
    @staticmethod
    def check_config():
        logging.debug("Checking config file ...")

        with open("config.yml", "r") as file:
            config = yaml.safe_load(file)

        if "batch_size" not in config:
            logging.critical("Critical: 'batch_size' not found in config.yml")
            raise Exception("Batch size not found in config.yml")

        if "tables" not in config:
            logging.critical("Critical: 'tables' not found in config.yml")
            raise Exception("Tables not found in config.yml")

        for table_name, table_config in config["tables"].items():
            if "primary_key" not in table_config:
                logging.warning(
                    f"Warning: 'primary_key' not specified for table '{table_name}', using 'id' by default"
                )
            elif table_config["primary_key"] is None:
                logging.warning(
                    f"Warning: 'primary_key' specified as None for table '{table_name}', using 'id' by default"
                )
        


class Shuffler:
    def __init__(self):
        self._common_names = ['James', 'John', 'Robert', 'Michael', 'William', 'David', 'Mary', 'Patricia', 'Jennifer', 'Linda']
        self._last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis']
    
    def _get_seed(self, text: str) -> int:
        return int(hashlib.md5(text.encode()).hexdigest(), 16)
    
    def shuffle_name(self, name: str) -> str:
        seed = self._get_seed(name)
        random.seed(seed)
        parts = name.split()
        return f"{random.choice(self._common_names)} {random.choice(self._last_names)}"
    
    def shuffle_email(self, email: str) -> str:
        local, domain = email.split('@')
        seed = self._get_seed(email)
        random.seed(seed)
        chars = list(local)
        random.shuffle(chars)
        return f"{''.join(chars)}@{domain}"
    
    def shuffle_phone(self, phone: str) -> str:
        digits = ''.join(filter(str.isdigit, phone))
        seed = self._get_seed(phone)
        random.seed(seed)
        shuffled = ''.join(random.sample(digits, len(digits)))
        return f"+{shuffled}" if phone.startswith('+') else shuffled
    
    def shuffle_date(self, date: str) -> str:
        if '-' not in date:
            return date
        year, month, day = date.split('-')
        seed = self._get_seed(date)
        random.seed(seed)
        new_month = str(random.randint(1, 12)).zfill(2)
        new_day = str(random.randint(1, 28)).zfill(2)
        return f"{year}-{new_month}-{new_day}"
    
    def shuffle_address(self, address: str) -> str:
        seed = self._get_seed(address)
        random.seed(seed)
        parts = address.split()
        return ' '.join(''.join(random.sample(part, len(part))) for part in parts)

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
        try:
            connection_string = f"{self.dialect}://{self.username}:{quote_plus(self.password)}@{self.host}:{self.port}/{self.database}"
            self.engine = create_engine(connection_string)
            Session = sessionmaker(bind=self.engine)
            self.session = Session()
        except Exception as e:
            raise Exception(e)

    def execute_query(self, query, params=None, fetch_one=False):
        try:
            query = text(query)

            if not self.engine:
                self.connect()

            if params:
                if isinstance(params, list):
                    params = [tuple(params)]
                result = self.session.execute(query, params)
            else:
                result = self.session.execute(query)

            if fetch_one:
                return result.fetchone()
            else:
                return result.fetchall()

        except Exception as e:
            raise Exception(e)

    def execute_update(self, query, params=None):
        try:
            query = text(query)

            if not self.engine:
                self.connect()

            if params:
                result = self.session.execute(query, params)
            else:
                result = self.session.execute(query)

            self.session.commit()

        except Exception as e:
            self.session.rollback()
            raise Exception(e)

    def execute_insert(self, query, params=None):
        try:
            query = text(query)

            if not self.engine:
                self.connect()

            if params:
                result = self.session.execute(query, params)
            else:
                result = self.session.execute(query)

            self.session.commit()

            return result.lastrowid
        except Exception as e:
            self.session.rollback()
            raise Exception(e)

    def close(self):
        if self.session:
            self.session.close()
        if self.engine:
            self.engine.dispose()


class TestSeeder:
    def __init__(self, dialect="mysql"):

        logging.info("Running TestSeeder ...")

        self.dialect = dialect
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
        script_path = (
            "test/test_seed_mysql.sql"
            if self.dialect == "mysql"
            else "test/test_seed_postgresql.sql"
        )

        if not os.path.exists(script_path):
            raise FileNotFoundError(f"File {script_path} not found")

        with open(script_path, "r") as file:
            sql_script = file.read()

        for statement in sql_script.split(";"):
            if statement.strip():
                self.conn.execute_insert(statement)

        logging.debug(f"Run test script {script_path}")

    def generate_config(self):
        config = {
            "batch_size": 10,
            "tables": {
                "users": {
                    "primary_key": "id",
                    "shuffle": [
                        {"email": "email"},
                        {"phone": "phone"},
                        {"password": "password"},
                        {"address": "address"},
                    ],
                },
                "orders": {
                    "primary_key": "id",
                    "shuffle": [
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
        except Exception as e:
            logging.error("An error occured while running test seeder")
            print(e)
        finally:
            self.conn.close()
