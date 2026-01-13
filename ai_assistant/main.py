from flask import Flask
import os
import requests

app = Flask(__name__)

DISCORD_WEBHOOK = os.environ.get("DISCORD_WEBHOOK")

def send_to_discord(message):
    payload = {"content": message}
    r = requests.post(DISCORD_WEBHOOK, json=payload)
    return r.status_code

@app.route("/")
def home():
    return "AI News Assistant is running!"

@app.route("/send")
def send():
    msg = "📰 今日のAIニュースです！（ここに要約が入る）"
    status = send_to_discord(msg)
    return f"Sent to Discord! Status: {status}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
