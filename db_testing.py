from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

DB_NAME = "expense_tracker_bot"
DB_USER = "anuragprasad"
DB_PASSWORD = "2506"
DB_HOST = "localhost"
DB_PORT = "5432"

try:
    DATABASE_URL = f'postgresql+pg8000://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        )
        print("\nTables in your database:")
        tables = result.fetchall()
        if tables:
            for table in tables:
                print(table[0])
                columns = connection.execute(
                    text(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table[0]}'")
                )
                print("Columns:")
                for col in columns:
                    print(f"  - {col[0]} ({col[1]})")
                print()
        else:
            print("No tables found in the database.")
            
except SQLAlchemyError as e:
    print(f"Database error: {str(e)}")