from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import json
import random
import re

app = Flask(__name__)

# Load BBE Bible JSON once at startup
with open("en_bbe.json", "r", encoding="utf-8") as f:
    bbe_data = json.load(f)

# Words to ignore
STOP_WORDS = {
    "i", "am", "is", "are", "the", "a", "an", "and", "or",
    "to", "of", "in", "on", "for", "with", "that", "this",
    "today", "very", "feeling", "feel", "my", "me"
}

def extract_keywords(message):
    """Extract meaningful words from a message"""
    words = re.findall(r"\b[a-z]+\b", message.lower())
    return [word for word in words if word not in STOP_WORDS]

def find_verses(keywords):
    """Search the BBE JSON for verses containing any of the keywords"""
    matches = []

    for book, chapters in bbe_data.items():
        for chapter_num, verses in chapters.items():
            for verse_num, verse_text in verses.items():
                verse_text_lower = verse_text.lower()
                if any(word in verse_text_lower for word in keywords):
                    matches.append(f"{book} {chapter_num}:{verse_num} - {verse_text.strip()}")

    return matches

@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    incoming_msg = request.values.get("Body", "")
    response = MessagingResponse()

    keywords = extract_keywords(incoming_msg)
    if not keywords:
        response.message("Please send a word or sentence describing your feeling or request.")
        return str(response)

    matching_verses = find_verses(keywords)

    if matching_verses:
        verse = random.choice(matching_verses)
        response.message(verse)
    else:
        response.message("I couldn’t find a matching verse. Try words like hope, fear, love, or strength.")

    return str(response)

if __name__ == "__main__":
    app.run()
