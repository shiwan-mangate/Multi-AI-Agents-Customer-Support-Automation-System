from sqlalchemy import text
from database.postgres import engine

try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT version();"))

        for row in result:
            print(row)

    print("\nDatabase connection successful!")

except Exception as e:
    print(f"Connection failed: {e}")