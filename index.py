import yaml
import pymysql
import os
import json
import logging

from dotenv import load_dotenv
from setup import seed
from utils import shift, mask, op

#Load env
load_dotenv()

#Load configuration file
with open("config.yml", "r") as file:
    config = yaml.safe_load(file)

db_flavour = os.getenv("DATABASE_FLAVOUR")
conn = None

try:
    if db_flavour == "mysql":
        conn = pymysql.connect(
            host = os.getenv("DATABASE_HOST"),
            user = os.getenv("DATABASE_USER"),
            password = os.getenv("DATABASE_PASSWORD"),
            database= os.getenv("DATABASE_NAME"),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
    else:
        logging.error("Database flavour not supported")
except:
    logging.error("Error connecting to database")

def anonymize_data(table_name, column_op_mappings, batch_size=100):
    with conn.cursor() as cursor:
        columns = ",".join(column_op_mappings.keys())
        sql = f"SELECT {columns} FROM {table_name}"
        cursor.execute(sql)

        result = cursor.fetchall()


    conn.commit()


def main():
    seed()
    for table_name, column_op_mappings in config["tables"].items():
        anonymize_data(table_name, column_op_mappings) 
        
main()


