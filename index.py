import yaml
import mysql.connector
import os
import logging
import json
from dotenv import load_dotenv
from utils import Masker, TestSeeder

class Anonymizer:
    @staticmethod
    def load_config():
        with open("config.yml", "r") as file:
            return yaml.safe_load(file)

    @staticmethod
    def connect_to_db(dialect):
        if dialect == "mysql":
            return mysql.connector.connect(
                host=os.getenv("DATABASE_HOST"),
                user=os.getenv("DATABASE_USER"),
                password=os.getenv("DATABASE_PASSWORD"),
                database=os.getenv("DATABASE_NAME")
            )
        else:
            logging.error("Database dialect not supported. Add appropriate property to your config.yml")
            return None
        
    
    @staticmethod
    def apply_masking(mask_type, value):
        if mask_type == 'email':
            return Masker.mask_email(value)
        elif mask_type == 'phone':
            return Masker.mask_phone(value)
        elif mask_type == 'password':
            return Masker._hash_value(value)
        elif mask_type == 'address':
            return Masker.mask_address(value)
        elif mask_type == 'date':
            return Masker.mask_date(value)
        else:
            logging.error(f"Unknown mask type: {mask_type}")
            return value

    @staticmethod
    def anonymize_data(conn, table_name, column_meta, batch_size=100):
        primary_key = column_meta["primary_key"] if column_meta.get("primary_key") else "id"
        mask_columns = column_meta["mask_columns"]
        column_op_mappings = {list(col.keys())[0]: list(col.values())[0] for col in mask_columns}

        cursor = conn.cursor(dictionary=True)
        columns = ",".join(column_op_mappings.keys())
        offset = 0

        while True:
            sql = f"SELECT {primary_key}, {columns} FROM {table_name} LIMIT {batch_size} OFFSET {offset}"
            cursor.execute(sql)
            result = cursor.fetchall()

            if not result:
                break

            anonymized_result = [
                {col: Anonymizer.apply_masking(column_op_mappings[col], row[col]) for col in column_op_mappings.keys()}
                for row in result
            ]

            for row, anon_row in zip(result, anonymized_result):
                set_clause = ", ".join([f"{col} = %s" for col in column_op_mappings.keys()])
                update_sql = f"UPDATE {table_name} SET {set_clause} WHERE {primary_key} = %s"
                cursor.execute(update_sql, [anon_row[col] for col in column_op_mappings.keys()] + [row[primary_key]])

            conn.commit()
            offset += batch_size

        logging.debug(f"Anonymized {table_name} table")

    @staticmethod
    def run():
        config = Anonymizer.load_config()
        conn = Anonymizer.connect_to_db(config["dialect"])
        table_data = config.get("tables")

        if conn:
            for table_name, column_meta in table_data.items():
                Anonymizer.anonymize_data(conn, table_name, column_meta)
            conn.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    load_dotenv()
    seeder = TestSeeder()
    seeder.run()
    Anonymizer.run()
