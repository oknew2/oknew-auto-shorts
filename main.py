import os
import openai
import requests
import json
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

# 환경변수 불러오기
openai.api_key = os.getenv("OPENAI_API_KEY")
YOUTUBE_CLIENT_ID = os.getenv("YOUTUBE_CLIENT_ID")
YOUTUBE_CLIENT_SECRET = os.getenv("YOUTUBE_CLIENT_SECRET")
YOUTUBE_REFRESH_TOKEN = os.getenv("YOUTUBE_REFRESH_TOKEN")
HEYGEN_API_TOKEN = os.getenv("HEYGEN_API_TOKEN")
INTRO_VIDEO_URL = os.getenv("GOOGLE_DRIVE_INTRO_VIDEO_URL")
BACKGROUND_MUSIC_URL = os.getenv("BACKGROUND_MUSIC_URL")

# 1. 기사 요약 (예시 기사 사용)
article = "삼성전자가 새로운 갤럭시 시리즈를 공개했다. 사용자 경험 향상과 배터리 효율 개선이 주목받고 있다."
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": f"다음 기사를 5초 내외 영상용 멘트로 요약해줘:\n{article}"}]
)
summary = response['choices'][0]['message']['content']
print("요약 완료:", summary)

# 2. Heygen으로 영상 생성
headers = {"Authorization": f"Bearer {HEYGEN_API_TOKEN}", "Content-Type": "application/json"}
payload = {
    "video_title": "Auto Shorts",
    "script": summary,
    "voice_id": "6f8e6dd5eae949b5b3d598b15827aa54",  # 예시 voice ID
    "avatar_id": "5f55c3b14cf58e001faedc65",         # 예시 avatar ID
    "aspect_ratio": "9:16"
}
res = requests.post("https://api.heygen.com/v1/video/generate", headers=headers, json=payload)
video_url = res.json().get("data", {}).get("url")
print("영상 생성 완료:", video_url)

# 3. 영상 다운로드
video_filename = "shorts.mp4"
with open(video_filename, "wb") as f:
    f.write(requests.get(video_url).content)

# 4. YouTube 업로드
creds_data = {
    "client_id": YOUTUBE_CLIENT_ID,
    "client_secret": YOUTUBE_CLIENT_SECRET,
    "refresh_token": YOUTUBE_REFRESH_TOKEN,
    "token_uri": "https://oauth2.googleapis.com/token"
}
creds = Credentials.from_authorized_user_info(info=creds_data)

youtube = build('youtube', 'v3', credentials=creds)
request_body = {
    "snippet": {
        "title": "AI 자동 생성 Shorts",
        "description": "자동 요약 + 생성 + 업로드",
        "tags": ["AI", "Shorts", "Auto"],
        "categoryId": "24"
    },
    "status": {"privacyStatus": "public"}
}
media = MediaFileUpload(video_filename, resumable=True, mimetype='video/*')
response = youtube.videos().insert(part="snippet,status", body=request_body, media_body=media).execute()
print("업로드 완료:", response.get("id"))
