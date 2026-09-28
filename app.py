from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import database
import chatbot

# setup instructions:
# 1. pip install flask twilio
# 2. make a twilio account and setup whatsapp sandbox
# 3. run this file, then use ngrok to expose port 5000
# 4. put the ngrok url + /webhook in the twilio sandbox settings
# 5. send a message on whatsapp to test

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    msg = request.form.get('Body', '')
    sender = request.form.get('From', '')

    reply = chatbot.get_response(sender, msg)

    resp = MessagingResponse()
    resp.message(reply)
    return str(resp)

@app.route('/', methods=['GET'])
def home():
    return 'WhatsApp assistant is running.'

if __name__ == '__main__':
    database.init_db()
    # print("starting server...")
    app.run(debug=True, port=5000)