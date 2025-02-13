from fastapi import FastAPI
import psycopg2 # type: ignore
import groq
from groq import Groq
from whatsapp_bot.database import get_db_connection

def classify_query(message):
    prompt = f""" You will be given a message from the user.
    You have to process the message:{message} and classify it as a query(a question) or an instruction
    Just give the word 'question' if it is a question and 'instruction' if its an instruction regarding the expenses"""
    
    response = groq.client.completions.create(
        model = "llama-8b-32k",
        messages = [{"role": "user", "content": prompt}]
    )
    return response.choices[0].message["content"].strip()

app = FastAPI()

@app.get("/") # Get route at the homepage
def home():
    return {"message":"Expense tracker bot is running"}

@app.post("/expense/")
def add_expense(query:str):
    connection = get_db_connection()
    cursor = connection.cursor()
    
    prompt = f"""Convert the following user query into a PostgreSQL SQL query.
    Database schema: expenses(id, user_id, amount, category, description, created_at)
    User query: "{query}"
    Return only the SQL query, without any explanations and no extra characters. """
    
    response = groq.client.completions.create(
        model = "llama3-8b-32k",
        messages = [{"role": "user", "content":prompt}]
    )
    sql_query = response.choices[0].message["content"].strip()
    
Groq(api_key="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")
@app.get("/query/")
def process_query(query:str):
    
    # The input query wil be in natural language and will have to be converted into a sql query:
    prompt = f"""Convert the following user query into a PostgreSQL SQL query.
    Database schema: expenses(id, user_id, amount, category, description, created_at)
    User query: "{query}"
    Return only the SQL query, without any explanations and no extra characters. """
    
    response = groq.client.completions.create(
        model = "llama3-8b-32k",
        messages = [{"role": "user", "content":prompt}]
    )
    sql_query = response.choices[0].message["content"].strip()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(sql_query)
    result = cursor.fetchall()
    conn.close()
    
    return {"user_query": query, "response":result}

    
    

