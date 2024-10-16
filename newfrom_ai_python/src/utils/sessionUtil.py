import uuid
from config.redisConfig import redis
from fastapi import Request
from config import sessionConfig
from dotenv import load_dotenv
load_dotenv()

# 세션 있는지 확인
def isExistSessionId(request: Request):
    if request.cookies.get("SID", None) is None:
        return False
    return True

# 세션 생성
def createSession(request: Request):
    if isExistSessionId(request) == False:
        sid = str(uuid.uuid4())        
        request.session["SID"] = sid
        
        # 레디스에 저장
        redis.set(sid, 0)
        redis.expire(sid, sessionConfig.EXPIRE_SECONDS)

        print("===================== Create Session ====================")  
        print(f"Session ID: {sid}")

        return sid
    return None

        
