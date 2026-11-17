
from sqlalchemy import inspect
from sqlalchemy import text

from api.database import engine
from api.model import Base


def check_schema():
    inspector = inspect(engine)

    print("Connected database:", engine.dialect.name)

    for table_name, model_table in Base.metadata.tables.items():
        actual_columns = {
            column["name"]: column
            for column in inspector.get_columns(table_name)
        }

        expected_columns = set(model_table.columns.keys())
        actual_column_names = set(actual_columns.keys())

        missing = expected_columns - actual_column_names
        extra = actual_column_names - expected_columns

        print(f"\nTable: {table_name}")
        print("Expected columns:", sorted(expected_columns))
        print("Actual columns:", sorted(actual_column_names))
        print("Missing columns:", sorted(missing))
        print("Extra columns:", sorted(extra))

        if missing:
            print("RESULT: MISMATCH")
        else:
            print("RESULT: COLUMN NAMES MATCH")



def test_table_access():
    with engine.connect() as connection:
        users = connection.execute(
            text("SELECT COUNT(*) FROM users")
        ).scalar_one()

        documents = connection.execute(
            text("SELECT COUNT(*) FROM documents")
        ).scalar_one()

    print("\nDatabase access test:")
    print("Users table accessible:", True)
    print("Documents table accessible:", True)
    print("User count:", users)
    print("Document count:", documents)


if __name__ == "__main__":
    check_schema()
    test_table_access()