import hashlib
import mysql.connector
import os
import logging

from mysql.connector import errorcode
from datetime import datetime, timedelta, date


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
            masked_parts = [parts[0]] + ['*' * len(part) for part in parts[1:]]
            return ' '.join(masked_parts)
        return address

    @staticmethod
    def mask_email(email: str) -> str:
        local, domain = email.split('@')
        return f"{local[0]}{'*' * (len(local) - 2)}{local[-1]}@{domain}" if len(local) > 2 else email

    @staticmethod
    def mask_date(date_value) -> str:
        if isinstance(date_value, date):
            date_value = date_value.strftime('%Y-%m-%d')
        elif not isinstance(date_value, str):
            raise ValueError("Invalid date format")

        parts = date_value.split('-')
        if len(parts) == 3:
            return f"{parts[0]}-**-**"
        return date_value

    @staticmethod
    def _hash_value(value: str) -> str:
        return hashlib.sha256(value.encode()).hexdigest()[:10]  # Return first 10 characters of the hash

class Shifter:
    @staticmethod
    def shift_date(date, shift_days: int = 10) -> str:
        shifted_date = date + timedelta(days=shift_days)
        return shifted_date.strftime("%Y-%m-%d")


class TestSeeder:
    def __init__(self):
        
        self.db_config = {
            'user': os.getenv('DATABASE_USER'),
            'password': os.getenv('DATABASE_PASSWORD'),
            'host': os.getenv('DATABASE_HOST'),
            'database': "anony"
        }
        logging.info("Running TestSeeder ...")
        self.conn = None
        self.cursor = None

    def connect(self):
        try:
            self.conn = mysql.connector.connect(**self.db_config)
            self.cursor = self.conn.cursor()
            logging.debug("Connected to test database")
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                logging.critical("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                logging.warning("Test database does not exist, creating database ...")
                self.create_database()
                self.connect()
            else:
                logging.error(err)

    def create_database(self):
        try:
            temp_config = self.db_config.copy()
            temp_config.pop('database')
            self.conn = mysql.connector.connect(**temp_config)
            self.cursor = self.conn.cursor()
            self.cursor.execute(f"CREATE DATABASE {self.db_config['database']}")
            logging.debug(f"Database {self.db_config['database']} created successfully")
        except mysql.connector.Error as err:
            logging.critical(f"Failed to create database: {err}")
        finally:
            self.disconnect()

    def disconnect(self):
        if self.conn:
            self.cursor.close()
            self.conn.close()
            logging.debug("Connection to test database closed")

    def wipe_data(self):
        self.cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        self.cursor.execute("SHOW TABLES;")
        tables = self.cursor.fetchall()
        for table in tables:
            self.cursor.execute(f"TRUNCATE TABLE {table[0]};")
        self.cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        self.conn.commit()
        logging.debug("Previous test data wiped")

    def seed_data(self):
        self.cursor.execute("""
            INSERT INTO users (id, email, phone, password, address) VALUES
            (1, 'john.doe@example.com', '1234567890', 'password123', '123 Main St'),
            (2, 'jane.doe@example.com', '0987654321', 'password456', '456 Elm St');
        """)
        self.cursor.execute("""
            INSERT INTO orders (id, shipping_address, order_date, userId) VALUES
            (1, '123 Main St', '2023-01-01', 1),
            (2, '456 Elm St', '2023-01-02', 2);
        """)
        self.conn.commit()
        logging.debug("Dummy data inserted")

    def run(self):
        self.connect()
        self.wipe_data()
        self.seed_data()
        self.disconnect()
    




