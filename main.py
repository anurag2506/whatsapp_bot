from fastapi import FastAPI
import psycopg2 # type: ignore
from groq import Groq
from whatsapp_bot.database import get_db_connection

app = FastAPI()

@app.get("/") # Get route at the homepage
def home():
    return {"message":"Expense tracker bot is running"}

@app.post("/expense")
def add_expense(id: int, amount: float, category:str, description:str = None):
    connection = get_db_connection()
    cursor = connection.cursor()
    
Groq(api_key="")
@app.get("/query")
def process_query(query:str):
    g

