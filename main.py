import groq
import os
import dotenv
import re
from dotenv import load_dotenv
load_dotenv()
from groq import Groq
from fastapi import FastAPI, Form, Response
from database import get_db_connection
from twilio.twiml.messaging_response import MessagingResponse

client = Groq(api_key="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")

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

    response = client.chat.completions.create(
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
        response_data = process_query(user_message)
        reply = f"You have asked a question. The info that you requested: {response_data}" 
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

    response = client.chat.completions.create(
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

def process_query(query: str):
    try:
        connection = get_db_connection()
        if connection is None:
            return {"error": "Database connection failed"}
        
        SYSTEM_PROMPT = f"""
        Convert the user query into a PostgreSQL SQL query.

            Database schema:
            expenses(
                id SERIAL PRIMARY KEY,
                user_id TEXT NOT NULL,
                amount NUMERIC,
                category TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            )

            ### Rules:
            - Use **ONLY** standard PostgreSQL functions.
            - **DO NOT** use non-existent functions like `long_format` or `NUMCACHE`.
            - Ensure the generated query is **valid and executable** in PostgreSQL.
            - **Return only the SQL query** (no explanations or comments).
            - Use **straight single quotes (`'`)** instead of curly quotes (`’`).
            - **DO NOT** generate incorrect SQL syntax, such as `%s` inside `LIKE` clauses.

            ### **Expected Output:**
            - The SQL query should be structured in a way that allows **further processing into human-readable insights**.
            - The query should **group expenses** by category and description where applicable.
            - **Example Queries and Expected Outputs:**
            1. **User Query:** "What is my total spending this month?"
                - **Expected SQL Output:**
                ```sql
                SELECT 
                    category, 
                    description, 
                    SUM(amount) AS total_spent 
                FROM expenses 
                WHERE user_id = 'given_user_id' 
                    AND DATE_TRUNC('month', created_at) = DATE_TRUNC('month', CURRENT_DATE)
                GROUP BY category, description
                ORDER BY total_spent DESC;
                ```
            2. **User Query:** "Show me all food expenses."
                - **Expected SQL Output:**
                ```sql
                SELECT 
                    category, 
                    description, 
                    SUM(amount) AS total_spent 
                FROM expenses 
                WHERE user_id = 'given_user_id' 
                    AND category ILIKE '%food%' 
                GROUP BY category, description
                ORDER BY total_spent DESC;
                ```

            The given user query is: **{query}** 
            """

        response = client.chat.completions.create(
        model="llama-3.2-3b-preview",
            messages=[{"role":"system", "content": SYSTEM_PROMPT},{"role": "user", "content": query}]
        )

        sql_query = response.choices[0].message.content.strip()
        sql_query = sql_query.replace("```sql", "").replace("```", "").strip()

        cursor = connection.cursor()
        query = sql_query.split("\n")[0].strip() 
        
        try:
            cursor.execute(query)
            results = cursor.fetchall()
        except Exception as e:
            print(f"Database Query Execution Error: {e}")
            return {"error": str(e)}


        prompt = f"""
        You are a helpful SQL analyst. I will provide you with the result of a SQL query and I need you to:
        1. Explain what the result means in simple terms and something that can be explained to a layman 
        2. Break down each component of the result
        3. Explain how to interpret the results in human-readable business insights

        Here's the query:
        {results}
        Please provide your analysis in a clear, step-by-step format that a business user can understand. When explaining the results, give examples of how to interpret different possible output values."""
        
        response = client.chat.completions.create(
        model="llama-3.2-3b-preview",
            messages=[{"role": "user", "content": prompt}]
    )

        return response.choices[0].message.content.strip()

    except Exception as e:
        return {"error": str(e)}
