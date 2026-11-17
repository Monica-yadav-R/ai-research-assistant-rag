
import os
from pathlib import Path
from urllib.parse import urlsplit, unquote

import psycopg
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env", override=True)

database_url = os.getenv("SUPABASE_DATABASE_URL")

if not database_url:
    raise RuntimeError("SUPABASE_DATABASE_URL was not found.")

parsed = urlsplit(database_url)

try:
    with psycopg.connect(
        host=parsed.hostname,
        port=parsed.port,
        dbname=parsed.path.lstrip("/"),
        user=parsed.username,
        password=unquote(parsed.password or ""),
        connect_timeout=10,
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            result = cursor.fetchone()

    print("Supabase connection successful!")
    print("PostgreSQL version:", result[0])

except Exception as error:
    print("Supabase connection failed.")
    print("Error type:", type(error).__name__)
    print("Error:", str(error))
