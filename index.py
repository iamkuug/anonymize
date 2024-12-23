import yaml
import os
import logging
import argparse
import coloredlogs
import pymysql

from utils import Masker, TestSeeder, Shifter, DBConnector, Shuffler, Checker
from tabulate import tabulate
from termcolor import colored
from dotenv import load_dotenv

pymysql.install_as_MySQLdb()


class Anonymizer:

    def __init__(self, dialect, is_preview=False):
        self.config = None
        self.is_preview = is_preview
        self.dialect = dialect

        self.db_config = {
            "user": os.getenv("DATABASE_USER"),
            "password": os.getenv("DATABASE_PASSWORD"),
            "host": os.getenv("DATABASE_HOST"),
            "port": 3306 if self.dialect == "mysql" else 5432,
            "database": "test_db" if self.is_preview else os.getenv("DATABASE_NAME"),
        }

        print(self.db_config)

        self.conn = DBConnector(
            self.dialect,
            self.db_config["user"],
            self.db_config["password"],
            self.db_config["host"],
            self.db_config["port"],
            self.db_config["database"],
        )

        self.load_config()
        self.conn.connect()

    def load_config(self):
        if self.is_preview:
            with open("config.preview.yml", "r") as file:
                self.config = yaml.safe_load(file)
            return

        with open("config.yml", "r") as file:
            self.config = yaml.safe_load(file)

    def apply_shuffle(self, shuffle_type, value):

        shuffler = Shuffler()
        if shuffle_type == "email":
            return shuffler.shuffle_email(value)
        elif shuffle_type == "phone":
            return shuffler.shuffle_phone(value)
        elif shuffle_type == "password":
            return Masker._hash_value(value)
        elif shuffle_type == "address":
            return shuffler.shuffle_address(value)
        elif shuffle_type == "date":
            return Shifter.shift_date(value)
        else:
            logging.error(f"Unknown shuffle type: {shuffle_type}")
            return value

    def anonymize_data(self, table_name, column_meta, batch_size=10):
        logging.info(f"Anonymizing {table_name} table ...")

        primary_key = (
            column_meta["primary_key"] if column_meta.get("primary_key") else "id"
        )
        shuffle_columns = column_meta["shuffle"]

        column_op_mappings = {
            list(col.keys())[0]: list(col.values())[0] for col in shuffle_columns
        }

        columns = ",".join(column_op_mappings.keys())
        offset = 0

        if not self.get_initial_preview_consent(
            table_name, primary_key, columns, column_op_mappings, batch_size
        ):
            return

        all_anonymized_rows = []

        while True:
            select_stmnt = f"SELECT {primary_key}, {columns} FROM {table_name} LIMIT {batch_size} OFFSET {offset}"
            logging.debug(f"Executing: {select_stmnt}")

            batch = [
                record._asdict() for record in self.conn.execute_query(select_stmnt)
            ]

            if not batch:
                break

            batch_anonymized = [
                {
                    **{primary_key: row[primary_key]},
                    **{
                        col: self.apply_shuffle(column_op_mappings[col], row[col])
                        for col in column_op_mappings.keys()
                    },
                }
                for row in batch
            ]

            all_anonymized_rows.extend(batch_anonymized)
            offset += batch_size

        self.get_final_preview_consent(
            all_anonymized_rows, table_name, primary_key, column_op_mappings
        )

    def get_initial_preview_consent(
        self, table_name, primary_key, columns, column_op_mappings, batch_size
    ):
        total_rows = self.conn.execute_query(
            f"SELECT COUNT(*) AS total FROM {table_name}", fetch_one=True
        )._asdict()["total"]

        sample_row = self.conn.execute_query(
            f"SELECT {primary_key}, {columns} FROM {table_name} LIMIT 1", fetch_one=True
        )._asdict()

        if not sample_row:
            logging.warning(f"Abort '{table_name}' table has no rows")
            return False

        sample_anon_row = {
            **{primary_key: sample_row[primary_key]},
            **{
                col: self.apply_shuffle(column_op_mappings[col], sample_row[col])
                for col in column_op_mappings.keys()
            },
        }

        headers = list(sample_row.keys())
        original_row = [sample_row[col] for col in headers]
        anonymized_row = [sample_anon_row[col] for col in headers]

        original_row_colored = [colored(str(item), "red") for item in original_row]
        anonymized_row_colored = [
            colored(str(item), "green") for item in anonymized_row
        ]

        table_data = [
            ["Original"] + original_row_colored,
            ["Anonymized"] + anonymized_row_colored,
        ]

        logging.info("Sample row before and after anonymization:")
        print(tabulate(table_data, headers=[""] + headers, tablefmt="grid"))

        consent = input(
            f"The table '{table_name}' has {total_rows} rows. The anonymization will be performed in batches of {batch_size} rows. Do you want to proceed with the update? (yes/no): "
        )
        if consent.lower() != "yes":
            logging.info("Update aborted by user.")
            return False
        return True

    def get_final_preview_consent(
        self, all_anonymized_rows, table_name, primary_key, column_op_mappings
    ):
        headers = list(all_anonymized_rows[0].keys())
        preview_data = [
            [row[col] for col in headers] for row in all_anonymized_rows[:15]
        ]

        print(colored("Preview:", "red"))
        print(tabulate(preview_data, headers=headers, tablefmt="grid"))

        consent = input(
            colored("Are you sure you want to commit these changes? (yes/no): ", "red")
        )

        if consent.lower() == "yes":
            for row in all_anonymized_rows:
                set_clause = ", ".join(
                    [f"{col} = :{col}" for col in column_op_mappings.keys()]
                )
                update_stmnt = f"UPDATE {table_name} SET {set_clause} WHERE {primary_key} = :{primary_key}"

                params = {col: row[col] for col in column_op_mappings.keys()}
                params[primary_key] = row[primary_key]

                self.conn.execute_update(update_stmnt, params)
            logging.debug("DONE")
        else:
            logging.info("Update Aborted")

    def run(self):
        logging.debug(f"Using {self.dialect} dialect")
        table_data = self.config.get("tables")
        batch_size = self.config.get("batch_size")

        for table_name, column_meta in table_data.items():
            self.anonymize_data(table_name, column_meta, batch_size)

        logging.info("COMPLETED")

    def __del__(self):
        self.conn.close()
        preview_config_path = "config.preview.yml"
        if os.path.exists(preview_config_path):
            try:
                os.remove(preview_config_path)
                logging.debug(
                    f"File {preview_config_path} has been removed successfully."
                )
            except PermissionError:
                logging.debug(
                    f"Permission denied: Unable to remove {preview_config_path}"
                )
            except OSError as e:
                logging.debug(
                    f"Error occurred while removing {preview_config_path}: {e}"
                )
        else:
            print(f"File {preview_config_path} does not exist.")


if __name__ == "__main__":
    try:
        load_dotenv()

        parser = argparse.ArgumentParser(description="Run the main application.")
        parser.add_argument(
            "--preview", action="store_true", help="Run in preview mode"
        )
        parser.add_argument(
            "--postgres", action="store_true", help="Use PostgreSQL database"
        )
        args = parser.parse_args()

        log_styles = {
            "debug": {"color": "green"},
            "info": {"color": "blue"},
            "warning": {"color": "yellow"},
            "error": {"color": "red"},
            "critical": {"color": "magenta", "bold": True},
        }

        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        logging = logging.getLogger(__name__)

        coloredlogs.install(
            level="DEBUG",
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            level_styles=log_styles,
        )

        anonymizer = None

        if args.preview:
            seeder = TestSeeder("postgresql" if args.postgres else "mysql")
            seeder.run()

            anonymizer = Anonymizer(
                dialect="postgresql" if args.postgres else "mysql", is_preview=True
            )
        else:
            Checker.check_config()
            anonymizer = Anonymizer(dialect="postgresql" if args.postgres else "mysql")

        anonymizer.run()
    except Exception as e:
        logging.error("An error occurred while running the anonymizer")
        print(e)
