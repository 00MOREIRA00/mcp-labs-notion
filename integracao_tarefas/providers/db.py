import sqlite3 
from collections.abc import Generator

DATABASE_PATH = "database.db"

def get_connection() -> Generator[sqlite3.Connection, None, None]: 
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    try:
        yield connection
    finally:
        connection.close()