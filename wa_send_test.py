import twilio
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client

account_sid = 'AC4b1490bbda3d24711d3194d0ed023d82'
auth_token = '91eb2a571b74bb7fcd2134d1faa7d68a'
client = Client(account_sid, auth_token)

def send_message(name,message):
    message = client.messages.create(
  from_='whatsapp:+14155238886',
  content_sid='HX6fba352dbcad742d3050700c10b01107',
  content_variables=f'{{"1": "{name}", "2": "{message}"}}',
  to='whatsapp:+918939889107'
)
    return message.sid


send_message()