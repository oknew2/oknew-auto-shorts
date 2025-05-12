import os
import openai
import requests
import time
import json

# 환경변수 불러오기
openai.api_key = os.getenv("OPENAI_API_KEY")
youtube_client_id = os.getenv("YOUTUBE_CLIENT_ID")
youtube_client_secret = os.getenv("YOUTUBE_CLIENT_SECRET")
youtube_refresh_token = os.getenv("YOUTUBE_REFRESH_TOKEN")
heygen_token = os.getenv("HEYGEN_API_TOKEN")
intro_url = os.getenv("INTRO_VIDEO_URL")
bgm_url = os.getenv("BACKGROUND_MUSIC_URL")

# 1. 뉴스 기사 수집 (네이버 뉴스 예시)
def get_latest_news():
    from bs4 import BeautifulSoup
    import feedparser
    rss = feedparser.parse("https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko")
    link = rss.entries[0].link
    res = requests.get(link)
    soup = BeautifulSoup(res.text, "html.parser")
    paragraphs = soup.find_all("p")
    text = "\n".join(p.text for p in paragraphs if len(p.text) > 30)
    return text[:2000]

# 2. 요약 (ChatGPT)
def summarize(text):
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "뉴스를 짧고 재미있는 유튜브 숏츠 대본으로 요약해줘."},
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message.content.strip()

# 3. Heygen으로 영상 생성
def create_heygen_video(script):
    url = "https://api.heygen.com/v1/video.generate"
    headers = {
        "Authorization": f"Bearer {heygen_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "script": script,
        "voice": "en_us_001",  # 한글 지원 음성으로 변경 가능
        "avatar_id": "default_avatar_1"  # 기본 아바타
    }
    res = requests.post(url, headers=headers, json=payload)
    video_id = res.json()["data"]["video_id"]
    return video_id

# 4. Heygen 영상 다운로드
def download_heygen_video(video_id):
    url = f"https://api.heygen.com/v1/video.status?video_id={video_id}"
    headers = {"Authorization": f"Bearer {heygen_token}"}
    for _ in range(30):
        res = requests.get(url, headers=headers)
        status = res.json()["data"]["status"]
        if status == "done":
            return res.json()["data"]["download_url"]
        time.sleep(5)
    return None

# 5. YouTube 업로드 (단순 업로드 예시)
def upload_to_youtube(video_url, title):
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    creds = Credentials(
        None,
        refresh_token=youtube_refresh_token,
        client_id=youtube_client_id,
        client_secret=youtube_client_secret,
        token_uri="https://oauth2.googleapis.com/token"
    )
    youtube = build("youtube", "v3", credentials=creds)

    # 영상 다운로드
    video_data = requests.get(video_url).content
    with open("final.mp4", "wb") as f:
        f.write(video_data)

    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": "자동 생성된 영상입니다.",
                "tags": ["뉴스", "요약", "AI Shorts"],
                "categoryId": "25"
            },
            "status": {"privacyStatus": "public"}
        },
        media_body="final.mp4"
    )
    response = request.execute()
    return response["id"]

# 실행 흐름
news = get_latest_news()
summary = summarize(news)
video_id = create_heygen_video(summary)
video_url = download_heygen_video(video_id)
if video_url:
    youtube_id = upload_to_youtube(video_url, "오늘의 AI 뉴스 요약")
    print("업로드 완료! https://youtube.com/watch?v=" + youtube_id)
else:
    print("영상 생성 실패")
