import os
import requests
import feedparser
import openai
from dotenv import load_dotenv
from googleapiclient.discovery import build

load_dotenv()

# 환경 변수 불러오기
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
YOUTUBE_CLIENT_ID = os.getenv("YOUTUBE_CLIENT_ID")
YOUTUBE_CLIENT_SECRET = os.getenv("YOUTUBE_CLIENT_SECRET")
YOUTUBE_REFRESH_TOKEN = os.getenv("YOUTUBE_REFRESH_TOKEN")
NEWS_RSS_URL = os.getenv("NEWS_RSS_URL")
INTRO_VIDEO_PATH = os.getenv("INTRO_VIDEO_PATH")

# OpenAI API 설정
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# 1. 뉴스 가져오기
def fetch_news():
    feed = feedparser.parse(NEWS_RSS_URL)
    news_items = []
    for entry in feed.entries[:4]:
        news_items.append({
            "title": entry.title,
            "link": entry.link,
            "summary": entry.summary
        })
    return news_items

# 2. 뉴스 요약
def summarize(news_items):
    combined = "\n".join([f"Title: {item['title']}\nSummary: {item['summary']}" for item in news_items])
    prompt = f"Summarize this into a short, witty, entertaining video script for YouTube Shorts (English):\n{combined}"

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )

    return response.choices[0].message.content.strip()

# 3. 대본 저장
def create_video_script(summary_text):
    with open("output.txt", "w") as f:
        f.write(summary_text)
    print("✅ 대본 저장 완료")

# 4. 메인 실행
if __name__ == "__main__":
    print(">> 뉴스 불러오는 중...")
    news = fetch_news()

    print(">> 뉴스 요약 중...")
    summary = summarize(news)

    print(">> 대본 저장 중...")
    create_video_script(summary)

    print("✅ 모든 작업 완료")
