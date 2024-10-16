import os
from fastapi import Response
from dotenv import load_dotenv
load_dotenv()

EXPIRE = eval(os.getenv("SESSION_EXPIRE_SECONDS"))
HTTPONLY = True

def setCookei(response: Response, key: str, value: any, expires: int = EXPIRE, httponly: bool = HTTPONLY):
    response.set_cookie(
        key = key,
        value = value,
        expires = expires,
        httponly = httponly,
    )