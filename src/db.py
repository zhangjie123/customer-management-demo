import os
from typing import Dict, List, Optional, Tuple

import mysql.connector
from dotenv import load_dotenv
from mysql.connector import Error

# Load variables from a local .env file if present.
load_dotenv()

# Basic DB configuration, overridable via environment variables
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "8889")),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "root"),
    "database": os.getenv("DB_NAME", "customer_demo"),
    "auth_plugin": os.getenv("DB_AUTH_PLUGIN"),  # optional, depends on MySQL setup
}


def get_connection():
    """Create a new DB connection; caller is responsible for closing it."""
    return mysql.connector.connect(**{k: v for k, v in DB_CONFIG.items() if v is not None})


def init_db() -> None:
    """Create the customers table and indexes if they don't exist."""
    ddl = """
    CREATE TABLE IF NOT EXISTS customers (
        id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        phone VARCHAR(20) NOT NULL,
        gender ENUM('male', 'female', 'other') NOT NULL DEFAULT 'other',
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        UNIQUE KEY idx_customers_phone (phone),
        KEY idx_customers_name (name),
        KEY idx_customers_created_at (created_at)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """
    indexes = [
        "CREATE UNIQUE INDEX idx_customers_phone ON customers(phone)",
        "CREATE INDEX idx_customers_name ON customers(name)",
        "CREATE INDEX idx_customers_created_at ON customers(created_at)",
    ]

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(ddl)
            for statement in indexes:
                try:
                    cur.execute(statement)
                except Error as exc:
                    # Ignore duplicate index errors to keep init idempotent.
                    if getattr(exc, "errno", None) != 1061:
                        raise
        conn.commit()


def create_customer(data: Dict[str, str]) -> int:
    query = """
        INSERT INTO customers (name, phone, gender)
        VALUES (%s, %s, %s)
    """
    params = (data["name"], data["phone"], data["gender"])
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            conn.commit()
            return cur.lastrowid


def get_customer_by_id(customer_id: int) -> Optional[Dict]:
    query = """
        SELECT id, name, phone, gender, created_at, updated_at
        FROM customers
        WHERE id = %s
    """
    with get_connection() as conn:
        with conn.cursor(dictionary=True) as cur:
            cur.execute(query, (customer_id,))
            row = cur.fetchone()
            return row


def list_customers(page: int, page_size: int) -> Tuple[List[Dict], int]:
    offset = (page - 1) * page_size
    list_query = """
        SELECT id, name, phone, gender, created_at, updated_at
        FROM customers
        ORDER BY created_at DESC, id DESC
        LIMIT %s OFFSET %s
    """
    count_query = "SELECT COUNT(*) AS total FROM customers"

    with get_connection() as conn:
        with conn.cursor(dictionary=True) as cur:
            cur.execute(count_query)
            total = cur.fetchone()["total"]

            cur.execute(list_query, (page_size, offset))
            rows = cur.fetchall()
            return rows, total


def update_customer(customer_id: int, data: Dict[str, str]) -> bool:
    query = """
        UPDATE customers
        SET name = %s, phone = %s, gender = %s
        WHERE id = %s
    """
    params = (data["name"], data["phone"], data["gender"], customer_id)
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            conn.commit()
            return cur.rowcount > 0


def delete_customer(customer_id: int) -> bool:
    query = "DELETE FROM customers WHERE id = %s"
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (customer_id,))
            conn.commit()
            return cur.rowcount > 0
