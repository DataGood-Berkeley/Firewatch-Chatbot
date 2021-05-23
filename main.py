"""
Point of entry for the Firewatch Chatbot 
"""

#import statements
from tokens.py import VERIFY_TOKEN, PAGE_TOKEN, ANSWERS_URL
import json
import requests
import pandas as pd
import spacy
from google.colab import auth
auth.authenticate_user()
import gspread
from oauth2client.client import GoogleCredentials
gc = gspread.authorize(GoogleCredentials.get_application_default())
from bottle import debug, request, route, run

# Initialize Variables 
GRAPH_URL = "https://graph.facebook.com/v2.6"

#FROM MODEL
wb = gc.open_by_url(ANSWERS_URL)
sheet = wb.sheet1
data = sheet.get_all_values()

#creating the df
df = pd.DataFrame(data)
df.columns = df.iloc[0]
df = df.iloc[1:]

#text preprocessing
from string import punctuation

df['Question'] = df['Question'].str.replace('/',' ').str.lower()
df['Question'] = [''.join([i for i in text if i not in punctuation]) for text in df['Question']]

## Stopwords
#add our own stopwords
nlp = spacy.load("en_core_web_sm")
nlp.Defaults.stop_words |= {'wildfire',"wildfires","fire","what","how","nt"}
df['no_stopwords'] = df['Question'].apply(lambda x: ' '.join([word for word in x.split() if word not in nlp.Defaults.stop_words]))

#tokenize questions
def tokenize(text):   
    tokens = []
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    for token in doc:
        tokens.append(token.lemma_)
    return tokens
df['Lemmas'] = [tokenize(i) for i in df['no_stopwords']]

#most frequently used words
from collections import Counter
# Most common overall
# Most common per category
# Words that appear similarly in all categories
df["Large Category"].unique()
#content = {[token for row in df['Question'] for token in row.split()]}
#freq = Counter(content)
#freq.most_common(10)
for category in df["Large Category"].unique():
  print(category)
  tmp = df[df["Large Category"]==category]["Lemmas"]
  content = [token for row in tmp for token in row]
  freq = Counter(content)
  freq_table = pd.DataFrame(freq.most_common(10))
  freq_table[1] = freq_table[1]/len(content) * 100
  display(freq_table)
print("All")
content = [token for row in df["Lemmas"] for token in row]
freq = Counter(content)
freq_table = pd.DataFrame(freq.most_common(10))
freq_table[1] = freq_table[1]/len(content) * 100


# remove links
df['no_links'] = df['Question'].str.replace(r'https?://[A-Za-z0-9./]+', '')
df['no_links']


def send_to_messenger(ctx):
    url = "{0}/me/messages?access_token={1}".format(GRAPH_URL, PAGE_TOKEN)
    response = requests.post(url, json=ctx)

@route('/chat', method=["GET", "POST"])
def bot_endpoint():
    if request.method.lower() == 'get':
        verify_token = request.GET.get('hub.verify_token')
        hub_challenge = request.GET.get('hub.challenge')
        if verify_token == VERIFY_TOKEN:
            url = "{0}/me/subscribed_apps?access_token={1}".format(GRAPH_URL, PAGE_TOKEN)
            response = requests.post(url)
            return hub_challenge
    else:
        body = json.loads(request.body.read())
        user_id = body['entry'][0]['messaging'][0]['sender']['id']
        page_id = body['entry'][0]['id']
        message_text = body['entry'][0]['messaging'][0]['message']['text']
        # we just echo to show it works
        # use your imagination afterwards
        if user_id != page_id:
            ctx = {
                'recipient': {
                    'id': user_id,
                },
                'message': {
                    'text': message_text,
                }
            }
            response = send_to_messenger(ctx)
        return ''

debug(True)
run(reloader=True, port=5000)