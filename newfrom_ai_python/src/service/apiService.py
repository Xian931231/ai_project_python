import openai
import redis
import uuid
from fastapi import UploadFile, WebSocket, WebSocketDisconnect
from exception.validation import InvalidParamException, ExceedAiReqException, UnanswerableAiException
from sqlalchemy.orm import Session
from config import sessionConfig
from config.redisConfig import redis
from . import openaiService, aiLearnService
from dotenv import load_dotenv
load_dotenv()

# text to speech
def tts(param: dict):
    text = param["text"]
    path = ""
    if text and not text.isspace():
        path = openaiService.text2Speech(text)

    return path

# 모델 및 질문에 답변 가능한지 확인
def verifyQuestion(db: Session, param: dict):
    question = param["question"]
    embeddingList = aiLearnService.getRelevantEmbeddingText(db, question, 7)
    result = aiLearnService.verifySyntax(db, embeddingList, question)

    return {"result": result}

# 텍스트 데이터 학습
def textLearn(db: Session, param: dict):
    text = param["text"]
    result = aiLearnService.addTextLearn(db, text)

    return {"result": result}
    

# pdf 파일 학습
def fileLearn(db: Session, file: UploadFile, videoLink: str, videoName: str):
    if file.content_type != "application/pdf":
        return {"result": False, "mimeType": True}
    
    result = aiLearnService.addPdfDocument(db, file, videoLink, videoName)

    return {"result": result}

# 모델 학습
def modelLearn(db: Session, param: dict):
    text = param["text"]   
    result = aiLearnService.modelLearn(db, text)

    return {"result": result}

# 소켓 통신
async def aiWebSocket(db: Session, websocket: WebSocket):
    try:
        headers = []
        sid = websocket.cookies.get("SID", None)

        # 쿠키에 SID가 있는지 확인 후 없으면 쿠키에 SID를 넣어준다.
        if sid is None:
            sid = str(uuid.uuid4())
            headers.append(
                ("Set-Cookie".encode("utf-8"), f"SID={sid}; Path=/; Max-Age={sessionConfig.EXPIRE_SECONDS}".encode("utf-8"))
            )

        await websocket.accept(headers = headers)

        # 사용량 체크
        usage = redis.get(sid)
        if usage is None:
            redis.set(sid, 0)
        elif int(usage) > sessionConfig.EXCEED_COUNT:
            raise ExceedAiReqException()

        while True:
            receiveData = await websocket.receive_json()

            # 파라미터 체크
            if not "question" in receiveData:
                raise InvalidParamException()
            
            response = {}
            question = receiveData["question"]
            questionType = receiveData.get("question_type", None) # SUMMARY, DETAIL, DOCUMENT, VIDEO

            embeddingList = aiLearnService.getRelevantEmbeddingText(db, question, 7)
            # result = aiLearnService.verifySyntax(db, embeddingList, question)

            # if not result:
            #     # 모델 및 답변할 수 없는 질문일 때 처리
            #     raise UnanswerableAiException()
                
            # user content 생성
            userMsg = aiLearnService.createUserMessage(embeddingList, question, questionType)    
            if questionType == "DOCUMENT" or questionType == "VIDEO":
                response = aiLearnService.getFileInfo(db, embeddingList, questionType)

                await websocket.send_json({
                    "result": True,
                    "data": response
                })
                break

            # gpt 질의
            for chunk in openai.chat.completions.create(
                model = "gpt-4-turbo-preview",
                messages = [
                    {
                        "role": "system",
                        "content": aiLearnService.createStreamSystemMessage()
                    },
                    {
                        "role": "user",
                        "content": userMsg
                    },
                ],
                stream = True,
                temperature = 0,
                max_tokens = 2000,
            ):
                sendData = {}
                choices = chunk.choices[0]
                delta = choices.delta

                if delta.role and delta.role == "assistant":
                    # 응답 시작
                    sendData["type"] = "start"
                elif choices.finish_reason == None:
                    # 응답 메시지
                    sendData["type"] = "answer"
                    sendData["content"] = delta.content
                else: 
                    # 응답 종료
                    sendData["type"] = "end"

                await websocket.send_json({
                    "result": True,
                    "data": sendData,
                })         
            break

    except ExceedAiReqException as EARE:
        await websocket.send_json(EARE.getResult())
    except InvalidParamException as IPE:
        await websocket.send_json(IPE.getResult())
    except UnanswerableAiException as UAE:
        await websocket.send_json(UAE.getResult())
    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        # 사용량 1증가
        usage = int(redis.get(sid))
        redis.set(sid, usage + 1)
        redis.expire(sid, sessionConfig.EXPIRE_SECONDS)
        await websocket.close()