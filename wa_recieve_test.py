from twilio.rest import Client

account_sid = 'AC4b1490bbda3d24711d3194d0ed023d82'
auth_token = '91eb2a571b74bb7fcd2134d1faa7d68a '
client = Client(account_sid, auth_token)

message = client.messages.create(
  from_='whatsapp:+14155238886',
  body='Your appointment is coming up on July 21 at 3PM',
  to='whatsapp:+918939889107'
)

print(message.sid)