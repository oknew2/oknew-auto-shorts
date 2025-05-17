import os
import requests
import feedparser
import openai
from dotenv import load_dotenv

# 환경 변수 불러오기
load_dotenv()

# OpenAI API 키 설정
openai.api_key = os.getenv("OPENAI_API_KEY")

# 뉴스 불러오기
def fetch_news():
    feed = feedparser.parse(os.getenv("NEWS_RSS_URL"))
    news_items = []
    for entry in feed.entries[:4]:
        news_items.append({
            "title": entry.title,
            "link": entry.link,
            "summary": entry.summary
        })
    return news_items

# 뉴스 요약
def summarize(news_items):
    combined = "\n".join(
        [f"Title: {item['title']}\nSummary: {item['summary']}" for item in news_items]
    )
    prompt = f"Summarize this into a short, witty, entertaining video script for YouTube Shorts (English):\n{combined}"

    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()

# 결과 저장
def create_video_script(summary_text):
    with open("output.txt", "w") as f:
        f.write(summary_text)
    print(">> 대본 저장 완료")

# 메인 실행
if __name__ == "__main__":
    print(">> 뉴스 불러오는 중...")
    news = fetch_news()

    print(">> 뉴스 요약 중...")
    summary = summarize(news)

    print(">> 대본 저장 중...")
    create_video_script(summary)

    print("✅ 모든 작업 완료")
