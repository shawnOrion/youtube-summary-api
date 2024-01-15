from fastapi import FastAPI, HTTPException
from youtube_transcript_api import YouTubeTranscriptApi
from dotenv import load_dotenv
import re
import os
from openai import OpenAI
load_dotenv()
openai_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

client = OpenAI(
    api_key=openai_key  # Replace with your actual API key
)


@app.get("/create-summary/")
async def create_summary(url: str):
    video_id = extract_youtube_video_id(url)
    if video_id == "Error: Invalid YouTube URL or Video ID not found":
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")

    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    transcript_text = ' '.join([t['text'] for t in transcript])
    summary = text_to_summary(transcript_text)

    return {"summary": summary}


def extract_youtube_video_id(url):
    # Regular expression pattern
    pattern = r'^.*(youtu\.be\/|v\/|u\/\w\/|embed\/|watch\?v=|\&v=)([^#\&\?]*).*'

    # Matching the URL with the pattern
    match = re.match(pattern, url)

    # Check if a match is found and the second group (video ID) is of length 11
    if match and len(match.group(2)) == 11:
        return match.group(2)
    else:
        return "Error: Invalid YouTube URL or Video ID not found"


def text_to_summary(text):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "given a youtube transcript, generate an educational summary of the video. key sections: introduction, main arguments(series of bullet points), brief summary",
            },
            {
                "role": "user",
                "content": text,
            }
        ],
        model="gpt-4-1106-preview",
    )
    return chat_completion.choices[0].message.content
