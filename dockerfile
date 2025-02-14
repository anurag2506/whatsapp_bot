FROM python:3.12-slim

WORKDIR /whatsapp_bot

COPY . .

RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y ngrok

# Make the script executable
RUN chmod +x start.sh

EXPOSE 8000

# Run the script
CMD ["./start.sh"]
