
import getpass
import psycopg

password = getpass.getpass("Enter your Supabase database password: ")

try:
    with psycopg.connect(
        host="aws-1-ap-south-1.pooler.supabase.com",
        port=5432,
        dbname="postgres",
        user="postgres.xcplkgyvcelxijewmucv",
        password=password,
        connect_timeout=10,
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            print("Connection successful!")
            print(cursor.fetchone()[0])

except Exception as error:
    print("Connection failed:", type(error).__name__)
    print(error)
