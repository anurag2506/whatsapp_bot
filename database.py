from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

DB_NAME = "expense_tracker_bot"
DB_USER = "anuragprasad"
DB_PASSWORD = "2506"
DB_HOST = "localhost"
DB_PORT = "5432" #default port of postgres

try:
    DATABASE_URL = f'postgresql+pg8000://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    engine = create_engine(DATABASE_URL)
    with engine.connect() as connection:
        print("Database connection successful!")
except SQLAlchemyError as e:
    print(f"Database connection failed: {str(e)}")