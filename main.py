import os

print("CWD:", os.getcwd())
print("FILES:", os.listdir())

import time
import requests
import feedparser
import schedule
import threading
from flask import Flask
from openai import OpenAI

app = Flask(__name__)

DISCORD_WEBHOOK = os.environ.get("DISCORD_WEBHOOK")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

RSS_FEEDS = [
    "https://www.theverge.com/rss/index.xml",
    "https://gigazine.net/news/rss_2.0/",
]

def fetch_news():
    articles = []
    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries[:3]:
            articles.append({
                "title": entry.title,
                "link": entry.link,
                "summary": entry.get("summary", "")
            })
    return articles[:5]

def summarize_news(articles):
    text = ""
    for i, a in enumerate(articles, 1):
        text += f"{i}. {a['title']}\n{a['summary']}\n\n"

    prompt = f"""
以下のニュースを日本語で簡潔に要約してください。
各ニュースは以下の形式で：

【番号】タイトル
要約：〇〇

{text}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content

def send_to_discord(message):
    payload = {"content": message}
    r = requests.post(DISCORD_WEBHOOK, json=payload)
    return r.status_code

def daily_job():
    try:
        news = fetch_news()
        summary = summarize_news(news)
        msg = f"🧠 今日のAIニュース\n\n{summary}"
        send_to_discord(msg)
        print("Posted to Discord")
    except Exception as e:
        print("Error:", e)

schedule.every().day.at("07:30").do(daily_job)

@app.route("/")
def home():
    return "AI News Assistant is running!"

@app.route("/send")
def manual_send():
    daily_job()
    return "Sent manually!"

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(30)

# 🔥 gunicorn でもスケジューラが動くようにする
threading.Thread(target=run_scheduler, daemon=True).start()
