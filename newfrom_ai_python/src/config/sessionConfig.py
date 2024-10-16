import os
from fastapi import FastAPI, Request
from starlette.middleware.sessions import SessionMiddleware
from utils import sessionUtil, cookieUtil
from dotenv import load_dotenv
load_dotenv()

EXPIRE_SECONDS = eval(os.getenv("SESSION_EXPIRE_SECONDS"))
EXCEED_COUNT = int(os.getenv("SESSION_EXCEED_COUNT"))
SECRET_KEY = os.getenv("SESSION_SECRET_KEY")

def setSession(app: FastAPI):
    # 세션 아이디 생성
    @app.middleware("http")
    async def createSession(request: Request, call_next):
        sid = sessionUtil.createSession(request)
        response = await call_next(request)
        if sid:
            cookieUtil.setCookei(response = response, key = "SID", value = sid)
        return response

    # 세션을 사용하기 위한 미들웨어 추가
    app.add_middleware(
        SessionMiddleware,
        secret_key = SECRET_KEY,
        max_age = EXPIRE_SECONDS,
        https_only = True,
    )
