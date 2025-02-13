import groq
from groq import Groq
from fastapi import FastAPI, Form, Response
from database import get_db_connection
from twilio.twiml.messaging_response import MessagingResponse

client = Groq(api_key="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")


def classify_query(message):
    SYSTEM_PROMPT = """ You will be given a message from the user.
    "The message will be something like this: "Hi, I want to add an expense of 1000 rupees for food. Or can be as short as: Spent 250 for coffee. This comes under an instruction and has to be added in the DB"
    "But at the same time, the message can be something like: How much money have I spent in the last 2 days. This classifies as a question."
    "Make sure you classify every message as a question or an instruction."JUST GIVE THE OUTPUT as 'question' or 'instruction' and nothing more or nothing less.
    You have to process the message and classify it as a query(a question) or an instruction.
    Just give the word 'question' if it is a question and 'instruction' if it's an instruction regarding the expenses"""
    response = client.chat.completions.create(
        model="llama-3.2-1b-preview",
        messages=[{"role":"system", "content":SYSTEM_PROMPT},{"role": "user", "content": message}]
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
        reply = f"The info that you requested: {response_data}"
    elif message_category.lower() == 'instruction':
        reply = "The expense has been recorded"
    else:
        reply = "Sorry the message cannot be processed"

    twilio_response = MessagingResponse()
    twilio_response.message(reply)
    return Response(str(twilio_response), media_type="text/xml")


@app.post("/expense/")
def add_expense(query: str):
    connection = get_db_connection()
    if connection is None:
        return {"error": "Failed to connect to the database"}
    cursor = connection.cursor()

    prompt = f"""Convert the following user query into a PostgreSQL SQL query.
    Database schema: expenses(id, user_id, amount, category, description, created_at)
    User query: "{query}"
    Return only the SQL query, without any explanations and no extra characters. """

    response = client.chat.completions.create(
        model="llama-3.2-1b-preview",
        messages=[{
            "role": "user",
            "content": prompt
        }]
    )
    sql_query = response.choices[0].message.content.strip()

    try:
        cursor.execute(sql_query)
        connection.commit()
        return {"message": "Expense added successfully"}
    except Exception as e:
        return {"error": str(e)}
    finally:
        connection.close()


@app.get("/query/")
def process_query(query: str):
    prompt = f"""Convert the following user query into a PostgreSQL SQL query.
    Database schema: expenses(id, user_id, amount, category, description, created_at)
    User query: "{query}"
    Return only the SQL query, without any explanations and no extra characters. """

    response = client.chat.completions.create(
        model="llama-3.2-1b-preview",
        messages=[{
            "role": "user",
            "content": prompt
        }]
    )
    sql_query = response.choices[0].message.content.strip()

    connection = get_db_connection()
    if connection is None:
        return {"error": "Failed to connect to the database"}
    cursor = connection.cursor()
    result = []
    try:
        cursor.execute(sql_query)
        result = cursor.fetchall()
    except Exception as e:
        print(f"Error in fetching the results from the table: {e}")
    finally:
        connection.close()

    return {"user_query": query, "response": result}
