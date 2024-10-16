import os
import uuid
from openai import OpenAI
from io import BytesIO
from service import s3Service
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(
    api_key = os.getenv("OPENAI_API_KEY")
)

def text2Speech(text: str):
    try:
        s3Path = f"/speech/{uuid.uuid4()}.mp3"

        response = client.audio.speech.create(
            model = "tts-1",   
            voice = "nova",
            input = text,
            speed = 1
        )
        s3Service.uploadFile(BytesIO(response.read()), s3Path)

    except Exception:
        raise

    return f"{os.getenv("S3_URL")}{os.getenv("S3_DEFAULT_PATH")}{s3Path}"

# gpt에게 질문
def askQuestionToGPT(systemMsg: str, userMsg: str):
    try:
        response = client.chat.completions.create(
            model = "gpt-4-0125-preview",
            messages = [
                {
                    "role": "system",
                    "content": systemMsg
                },
                {
                    "role": "user",
                    "content": userMsg
                },
            ],
            max_tokens = 100
        )
    except Exception:
        raise

    return response.choices[0].message.content

# 임베딩
def getEmbeddingText(textList: list):
    try:
        reponse = client.embeddings.create(
            model = "text-embedding-3-small",
            input = textList
        )
    except Exception:
        raise

    return reponse


