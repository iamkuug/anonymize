import psycopg2.extras
import yaml
import mysql.connector
import os
import logging
import json
import coloredlogs
import psycopg2

from dotenv import load_dotenv
from utils import Masker, TestSeeder, Shifter
from tabulate import tabulate
from termcolor import colored



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
        elif dialect == "postgres":
            return psycopg2.connect(
                host=os.getenv("DATABASE_HOST"),
                user=os.getenv("DATABASE_USER"),
                password=os.getenv("DATABASE_PASSWORD"),
                dbname=os.getenv("DATABASE_NAME")
            )
        else:
            logging.error("Database dialect not supported. Add appropriate property to your config.yml")
        
    
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
            return Shifter.shift_date(value)
        else:
            logging.error(f"Unknown mask type: {mask_type}")
            return value

    @staticmethod
    def anonymize_data(conn, table_name, column_meta, batch_size=100):
        logging.info(f"Anonymizing {table_name} table ...")

        primary_key = column_meta["primary_key"] if column_meta.get("primary_key") else "id"
        mask_columns = column_meta["mask_columns"]
        column_op_mappings = {list(col.keys())[0]: list(col.values())[0] for col in mask_columns}

        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) if isinstance(conn, psycopg2.extensions.connection) else conn.cursor(dictionary=True)
        columns = ",".join(column_op_mappings.keys())
        offset = 0


        if not Anonymizer.get_user_consent(cursor, table_name, primary_key, columns, column_op_mappings, batch_size):
            return

        total_anoynmized_rows = []        

        while True:
            sql = f"SELECT {primary_key}, {columns} FROM {table_name} LIMIT {batch_size} OFFSET {offset}"
            logging.debug(f"Executing: {sql}")
            cursor.execute(sql)
            result = cursor.fetchall()

            if not result:
                break

            anonymized_result = [
                {**{primary_key: row[primary_key]}, **{col: Anonymizer.apply_masking(column_op_mappings[col], row[col]) for col in column_op_mappings.keys()}}
                for row in result
            ]

            total_anoynmized_rows.extend(anonymized_result)
            offset += batch_size

        # Preview the updates
        headers = list(total_anoynmized_rows[0].keys())
        preview_data = [[row[col] for col in headers] for row in total_anoynmized_rows[:15]]

        print(colored("Preview:", 'red'))
        print(tabulate(preview_data, headers=headers, tablefmt="grid"))

        consent = input(colored("Are you sure you want to commit these changes? (yes/no): ", 'red'))
        if consent.lower() == 'yes':
            for row in total_anoynmized_rows:
                set_clause = ", ".join([f"{col} = %s" for col in column_op_mappings.keys()])
                update_sql = f"UPDATE {table_name} SET {set_clause} WHERE {primary_key} = %s"
                cursor.execute(update_sql, [row[col] for col in column_op_mappings.keys()] + [row[primary_key]])

            conn.commit()
            logging.debug("DONE")
        else:
            logging.info("Update aborted")

    
    @staticmethod
    def get_user_consent(cursor, table_name, primary_key, columns, column_op_mappings, batch_size):
        # Fetch total number of rows in the table
        cursor.execute(f"SELECT COUNT(*) AS total FROM {table_name}")
        total_rows = cursor.fetchone()["total"]

        # Fetch a sample row
        cursor.execute(f"SELECT {primary_key}, {columns} FROM {table_name} LIMIT 1")
        sample_row = cursor.fetchone()

        if not sample_row:
            logging.warning(f"Abort '{table_name}' table has no rows")
            return False

        # Anonymize the sample row
        sample_anon_row = {**{primary_key: sample_row[primary_key]}, **{col: Anonymizer.apply_masking(column_op_mappings[col], sample_row[col]) for col in column_op_mappings.keys()}}

        # Display the sample row before and after anonymization
        headers = list(sample_row.keys())
        original_row = [sample_row[col] for col in headers]
        anonymized_row = [sample_anon_row[col] for col in headers]

        # Color code the rows
        original_row_colored = [colored(str(item), 'red') for item in original_row]
        anonymized_row_colored = [colored(str(item), 'green') for item in anonymized_row]

        table_data = [["Original"] + original_row_colored, ["Anonymized"] + anonymized_row_colored]

        logging.info("Sample row before and after anonymization:")
        print(tabulate(table_data, headers=[""] + headers, tablefmt="grid"))

        # Prompt the user for consent
        consent = input(f"The table '{table_name}' has {total_rows} rows. The anonymization will be performed in batches of {batch_size} rows. Do you want to proceed with the update? (yes/no): ")
        if consent.lower() != 'yes':
            logging.info("Update aborted by user.")
            return False
        return True

    @staticmethod
    def run():
        config = Anonymizer.load_config()
        conn = Anonymizer.connect_to_db(config["dialect"])
        table_data = config.get("tables")

        logging.debug(f"Using {config["dialect"].upper()} dialect")

        if conn:
            for table_name, column_meta in table_data.items():
                Anonymizer.anonymize_data(conn, table_name, column_meta)
            conn.close()

if __name__ == "__main__":
    load_dotenv()
    
    log_styles = {
        'debug': {'color': 'green'},
        'info': {'color': 'blue'},
        'warning': {'color': 'yellow'},
        'error': {'color': 'red'},
        'critical': {'color': 'magenta', 'bold': True}
    }

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


    logging = logging.getLogger(__name__)

    coloredlogs.install(
        level='DEBUG',
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level_styles=log_styles
    )

    # seeder = TestSeeder()
    # seeder.run()
    Anonymizer.run()
