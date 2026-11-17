
from api.database import engine

with engine.connect() as connection:
    result = connection.exec_driver_sql(
        "PRAGMA foreign_keys"
    ).scalar()

    print("Foreign keys enabled:", result)

    assert result == 1, "Foreign keys are not enabled!"

print("Foreign-key connection test completed.")
