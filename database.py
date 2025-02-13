from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

DB_NAME = "expense_tracker_bot"
DB_USER = "anuragprasad"
DB_PASSWORD = "2506"
DB_HOST = "localhost"
DB_PORT = "5432" #default port of postgres

def get_db_connection():
    try:
        DATABASE_URL = f'postgresql+pg8000://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
        engine = create_engine(DATABASE_URL)
        connection = engine.raw_connection()
        return connection
    except SQLAlchemyError as e:
        return None

