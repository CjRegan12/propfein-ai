"""Database connection.

Connects with the read-only `propfein_ai_ro` login. That login can only
SELECT from the eval tables, every session is forced read-only, and any
query running longer than 30 seconds is cancelled, so nothing in this repo
can change production data or slow down the live app.
"""

import os

import psycopg
from dotenv import load_dotenv


def connect() -> psycopg.Connection:
    """Open a connection using DATABASE_URL from the local .env file."""
    load_dotenv()  # reads .env in the current folder into environment variables
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise SystemExit(
            "DATABASE_URL is not set. Copy .env.example to .env and fill it in."
        )
    return psycopg.connect(url)
