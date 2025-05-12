import os

openai_api_key = os.getenv("OPENAI_API_KEY")
youtube_client_id = os.getenv("YOUTUBE_CLIENT_ID")
youtube_client_secret = os.getenv("YOUTUBE_CLIENT_SECRET")
youtube_refresh_token = os.getenv("YOUTUBE_REFRESH_TOKEN")
heygen_token = os.getenv("HEYGEN_API_TOKEN")
intro_video_url = os.getenv("INTRO_VIDEO_URL")
bgm_url = os.getenv("BGM_URL")

print("OpenAI API key:", openai_api_key)
print("YouTube Upload 준비 완료")
print("인트로 영상 URL:", intro_video_url)
print("BGM URL:", bgm_url)
