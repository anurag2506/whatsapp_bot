import groq
import os
import re
from groq import Groq
from fastapi import FastAPI, Form, Response
from database import get_db_connection
from twilio.twiml.messaging_response import MessagingResponse

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def classify_query(message):
    SYSTEM_PROMPT = """You are an expert in language comprehension, trained to classify user messages as either a 'question' or an 'instruction'.
    
    **Classification Rules:**
    - If the message contains words like **"How", "What", "Why", "When", "Where", "Which", "Who", "Whom"** or a question mark (?), then it is a 'question'. 
    - If the message **asks for information** (e.g., "How much did I spend?"), classify it as 'question'.
    - If the message **commands an action** (e.g., "Show my expenses", "Add expense"), classify it as 'instruction'.
    
    **Examples:**
    - "How much money did I spend on clothing?" → **question**
    - "What is my total expense?" → **question**
    - "List all my expenses" → **question**
    - "Add 500 to my expenses under food" → **instruction**
    
    **Important:**  
    - You MUST return ONLY one word: **"question"** or **"instruction"**.  
    - Any incorrect prediction will result in a loss of your job!  
    - There is no ambiguity—every message fits into one of these two categories."""

    response = groq_client.chat.completions.create(
        model="llama-3.2-3b-preview",
            messages=[{"role":"system", "content": SYSTEM_PROMPT},{"role": "user", "content": message}]
        )

    return response.choices[0].message.content.strip()

app = FastAPI()


@app.get("/")
def home():
    return {"message": "Expense tracker bot is running"}


@app.post("/whatsapp/")
def process_input_message(
    From: str = Form(...),
    Body: str = Form(...)
):
    sender = From
    user_message = Body

    message_category = classify_query(user_message)
    if message_category.lower() == 'question':
        response_data = process_user_request(user_message, sender)
        reply = f"The info that you requested: {response_data}" 
    elif message_category.lower() == 'instruction':
        reply = add_expense(user_message,sender)
        reply = reply["message"]
    else:
        reply = "Sorry the message cannot be processed"

    twilio_response = MessagingResponse()
    twilio_response.message(reply)
    return Response(str(twilio_response), media_type="text/xml")


def add_expense(query: str, user_id: str):
    connection = get_db_connection()
    if connection is None:
        return {"error": "Failed to connect to the database"}
    
    cursor = connection.cursor()

    prompt = f"""Convert the following user query into a PostgreSQL SQL INSERT statement.
    Database schema: expenses(id SERIAL PRIMARY KEY, user_id TEXT NOT NULL, amount NUMERIC, category TEXT, description TEXT, created_at TIMESTAMP DEFAULT NOW())
    Rules:
    - The INSERT statement **must include `user_id = '{user_id}'`**.
    - Do NOT include `id` (PostgreSQL will auto-generate it).
    - Ensure `created_at` uses `NOW()` if not provided.
    - The query should be a valid `INSERT` statement for PostgreSQL.
    - Return ONLY the raw SQL query, with NO explanations, formatting, or extra characters.

    User query: "{query}"
    """

    response = groq_client.chat.completions.create(
        model="llama-3.2-3b-preview",
        messages=[{"role": "user", "content": prompt}]
    )

    # Clean the response
    sql_query = response.choices[0].message.content.strip()
    sql_query = sql_query.replace("```sql", "").replace("```", "").strip() 

    try:
        cursor.execute(sql_query)
        connection.commit()
        return {"message": "Expense added successfully"}
    except Exception as e:
        return {"error": str(e)}
    finally:
        cursor.close()
        connection.close()


def process_user_request(query: str, user_id:str):
    try:
        connection = get_db_connection()
        if connection is None:
            return "Unable to connect to database. Please try again."
        
        SYSTEM_PROMPT = """Convert the user query to a PostgreSQL query following these rules:
        - Table: expenses(id, user_id, amount, category, description, created_at)
        - Always include category, SUM(amount), and date-based filters where relevant
        - Group by category for aggregate queries
        - Use standard PostgreSQL date functions
        - Return only the SQL query without formatting
        - Make sure that the SQL query is fetching data from the expenses table which otherwise would throw an error
        
        Common patterns:
        - Monthly spending: DATE_TRUNC('month', created_at) = DATE_TRUNC('month', CURRENT_DATE)
        - Category search: category ILIKE '%keyword%'
        - Time range: created_at BETWEEN date1 AND date2
        - Make sure to be precise on the timings by fetching the created_at data from the expenses table"""
        

        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-specdec",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": query}
            ],
            max_tokens=150
        )

        sql_query = response.choices[0].message.content.strip()
        sql_query = re.sub(r'```sql|```', '', sql_query).strip()
        
        cursor = connection.cursor()
        try:
            cursor.execute(sql_query)
            results = cursor.fetchall()
            
            if not results:
                return "No expenses found for your query."

            analysis_prompt = f"""Analyze these expense results in simple terms:
            - Total amounts per category
            
            Results: {results}"""

            analysis_response = groq_client.chat.completions.create(
                model="llama-3.3-70b-specdec",
                messages=[{"role": "user", "content": analysis_prompt}],
                max_tokens=200
            )

            return analysis_response.choices[0].message.content.strip()

        except Exception as db_error:
            if "syntax error" in str(db_error).lower():
                return "I couldn't understand your query. Please try rephrasing it."
            elif "does not exist" in str(db_error).lower():
                return "Sorry, I couldn't find that information in your expenses."
            else:
                return f"There was an error processing your query: {str(db_error)}"

        finally:
            cursor.close()
            connection.close()

    except Exception as e:
        return f"An error occurred: {str(e)}"
    
