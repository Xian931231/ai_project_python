from . import router
from fastapi import Depends, UploadFile, WebSocket, Form
from config.dbConfig import get_db
from service import apiService

@router.post("/tts", response_model = str)
def tts(param: dict):
    return apiService.tts(param)

@router.post("/verify/question", response_model = dict)
def verifyQuestion(param: dict, db = Depends(get_db)):
    return apiService.verifyQuestion(db, param)
    
@router.post("/learn/text", response_model = dict)
def textLearn(param: dict, db = Depends(get_db)):
    return apiService.textLearn(db, param)

@router.post("/learn/file", response_model = dict)
def fileLearn(learn_file: UploadFile, video_name: str = Form(default = None), video_link: str = Form(default = None), db = Depends(get_db)):
    return apiService.fileLearn(db, learn_file, video_link, video_name)

@router.post("/learn/model", response_model = dict)
def modelLearn(param: dict, db = Depends(get_db)):
    return apiService.modelLearn(db, param)

# 웹 소캣
@router.websocket("/ws")
async def aiWebSocket(websocket: WebSocket, db = Depends(get_db)):
    return await apiService.aiWebSocket(db, websocket)
    

