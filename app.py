from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import requests

app = Flask(__name__)

BIBLE_API_URL = "https://bible-api.com/"

def get_bible_verse(query):
    """
    Query Bible API using keywords from user message
    """
    response = requests.get(
        f"{BIBLE_API_URL}{query}",
        params={"translation": "kjv"}
    )

    if response.status_code != 200:
        return None

    data = response.json()

    if "verses" not in data or not data["verses"]:
        return None

    verse = data["verses"][0]
    return f'{verse["book_name"]} {verse["chapter"]}:{verse["verse"]} - {verse["text"].strip()}'

@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    incoming_msg = request.values.get("Body", "").lower()
    response = MessagingResponse()

    # Clean input for API search
    search_query = incoming_msg.replace(" ", "+")

    verse = get_bible_verse(search_query)

    if verse:
        response.message(verse)
    else:
        response.message(
            "I couldn’t find a verse matching that message. "
            "Try words like *hope*, *fear*, *love*, or *strength*."
        )

    return str(response)

if __name__ == "__main__":
    app.run()
