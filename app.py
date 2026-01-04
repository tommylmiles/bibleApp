from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import requests
import re

app = Flask(__name__)

BIBLE_API_URL = "https://bible-api.com/"

STOP_WORDS = {
    "i", "am", "is", "are", "the", "a", "an", "and", "or",
    "to", "of", "in", "on", "for", "with", "that", "this",
    "today", "very", "feeling", "feel", "my", "me"
}

def extract_keywords(message):
    words = re.findall(r"\b[a-z]+\b", message.lower())
    return [word for word in words if word not in STOP_WORDS]

def get_bible_verse(keywords):
    for word in keywords:
        response = requests.get(
            BIBLE_API_URL,
            params={
                "search": word,
                "translation": "kjv"
            }
        )

        if response.status_code == 200:
            data = response.json()
            if "verses" in data and data["verses"]:
                verse = data["verses"][0]
                return (
                    f'{verse["book_name"]} '
                    f'{verse["chapter"]}:{verse["verse"]} - '
                    f'{verse["text"].strip()}'
                )
    return None

@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    incoming_msg = request.values.get("Body", "")
    response = MessagingResponse()

    keywords = extract_keywords(incoming_msg)
    verse = get_bible_verse(keywords)

    if verse:
        response.message(verse)
    else:
        response.message(
            "I couldn’t find a verse for that message. "
            "Try words like hope, fear, love, or strength."
        )

    return str(response)

if __name__ == "__main__":
    app.run()
