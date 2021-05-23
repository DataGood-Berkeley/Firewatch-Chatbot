"""
Point of entry for the Firewatch Chatbot 
"""

# Import Statements 
import random
from flask import Flask, request
from pymessenger.bot import Bot

# Defining App 
app = Flask(__name__)
# We don't want to store the access token on repo so we'll put it in the gitignore prior to committing 
ACCESS_TOKEN = 'your_access_token'
VERIFY_TOKEN = 'your_token_verification'
bot = Bot(ACCESS_TOKEN)

# Defining Endpoints 
@app.route("/", methods=['GET', 'POST'])

def receive_message(): 
    if request.method == "GET": 
        token_sent = request.args.get("hub.verify_token")
        return verify_fb_token(token_sent)  
    else:
        output = request.get_json()
        for event in output['entry']:
            messaging = event['messaging']
            for message in messaging:
                if message.get('message'):
                    #Facebook Messenger ID for user so we know where to send response back to
                    recipient_id = message['sender']['id']
                    if message['message'].get('text'):
                        response_sent_text = get_message()
                        send_message(recipient_id, response_sent_text)
                    #if user sends us a GIF, photo,video, or any other non-text item
                    if message['message'].get('attachments'):
                        response_sent_nontext = get_message()
                        send_message(recipient_id, response_sent_nontext)
    return "Message Processed"

def verify_fb_token(token_sent):
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'


#chooses a random message to send to the user
def get_message():
    sample_responses = ["Test 1", "Test 2", "Test 3", "Test 4"]
    # return selected item to the user
    return random.choice(sample_responses)

def send_message(recipient_id, response):
    bot.send_text_message(recipient_id, response)
    return "success"

if __name__ == "__main__":
    app.run()
