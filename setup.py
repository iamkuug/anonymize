import mysql.connector
from mysql.connector import errorcode

# Database configuration
config = {
    'user': 'nginze',
    'password': 'Guuk12jona@',
    'host': 'localhost',
    'database': 'anony',
}

# Seed data
seed_data = {
    'users': [
        (1, 'John Doe', 'john@example.com', 'password123', '1234567890'),
        (2, 'Jane Smith', 'jane@example.com', 'password456', '0987654321'),
        (3, 'Alice Johnson', 'alice.johnson@example.com', 'password789', '1122334455'),
        (4, 'Bob Brown', 'bob.brown@example.com', 'securePass1', '6677889900'),
        (5, 'Charlie Davis', 'charlie.davis@example.com', 'Pa$$w0rd!', '2233445566'),
        (6, 'Emily White', 'emily.white@example.com', 'white1234', '4455667788'),
        (7, 'David Black', 'david.black@example.com', 'blackHorse9', '9988776655'),
        (8, 'Grace Green', 'grace.green@example.com', 'Greeny!', '3344556677'),
        (9, 'Henry Clark', 'henry.clark@example.com', 'HClark42', '5566778899'),
        (10, 'Ivy Adams', 'ivy.adams@example.com', 'Adams2023', '7788990011'),
        (11, 'Jack Cooper', 'jack.cooper@example.com', 'Jacky!', '9900112233'),
        (12, 'Lily Evans', 'lily.evans@example.com', 'Evans123', '1233214567'),
        (13, 'Michael Harris', 'michael.harris@example.com', 'MHarris!', '7894561230'),
        (14, 'Natalie Brown', 'natalie.brown@example.com', 'Nats456', '3216549870'),
        (15, 'Oscar Thomas', 'oscar.thomas@example.com', 'Osc4rTh!', '6549873210'),
    ],
    'orders': [
        (1, '123 Main St', '2023-01-01', 1),
        (2, '456 Elm St', '2023-02-01', 2),
        (3, '789 Oak St', '2023-03-01', 3),
        (4, '101 Pine St', '2023-04-01', 4),
        (5, '202 Birch St', '2023-05-01', 5),
        (6, '303 Cedar St', '2023-06-01', 6),
        (7, '404 Maple St', '2023-07-01', 7),
        (8, '505 Walnut St', '2023-08-01', 8),
        (9, '606 Ash St', '2023-09-01', 9),
        (10, '707 Chestnut St', '2023-10-01', 10),
        (11, '808 Spruce St', '2023-11-01', 11),
        (12, '909 Poplar St', '2023-12-01', 12),
        (13, '1001 Sycamore St', '2024-01-01', 13),
        (14, '1102 Redwood St', '2024-02-01', 14),
        (15, '1203 Fir St', '2024-03-01', 15),
    ],
}

# Connect to the database

def seed():
    try:
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()

        # Drop existing tables
        cursor.execute("DROP TABLE IF EXISTS orders")
        cursor.execute("DROP TABLE IF EXISTS users")

        # Create tables
        cursor.execute("""
            CREATE TABLE users (
                id INT PRIMARY KEY,
                name VARCHAR(255),
                email VARCHAR(255),
                password VARCHAR(255),
                phone VARCHAR(20)
            )
        """)
        cursor.execute("""
            CREATE TABLE orders (
                id INT PRIMARY KEY,
                shipping_address VARCHAR(255),
                order_date DATE,
                userId INT,
                FOREIGN KEY (userId) REFERENCES users(id)
            )
        """)

        # Insert seed data
        cursor.executemany("""
            INSERT INTO users (id, name, email, password, phone)
            VALUES (%s, %s, %s, %s, %s)
        """, seed_data['users'])
        cursor.executemany("""
            INSERT INTO orders (id, shipping_address, order_date, userId)
            VALUES (%s, %s, %s, %s)
        """, seed_data['orders'])

        # Commit changes
        cnx.commit()

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    else:
        cursor.close()
        cnx.close()