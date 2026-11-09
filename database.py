"""MySQL connection and parameterized query helpers."""
import os
import mysql.connector
from mysql.connector import Error


def get_connection():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', '3306')),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        database=os.getenv('DB_NAME', 'job_tracker'),
        connection_timeout=5,
    )


def query(sql, params=(), *, one=False):
    """Read-only helper; always close cursor and connection."""
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params)
        return cursor.fetchone() if one else cursor.fetchall()
    finally:
        if cursor is not None:
            cursor.close()
        conn.close()


def execute(sql, params=()):
    """Execute an INSERT / UPDATE / DELETE; return affected-row count or insert ID."""
    conn = get_connection()
    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()
        return cursor.lastrowid if sql.lstrip().upper().startswith('INSERT') else cursor.rowcount
    except Error:
        conn.rollback()
        raise
    finally:
        if cursor is not None:
            cursor.close()
        conn.close()
