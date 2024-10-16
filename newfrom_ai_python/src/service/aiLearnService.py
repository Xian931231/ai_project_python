import os, re, json
from fastapi import UploadFile
from sqlalchemy.orm import Session
from db.crud import aiCrud
from db.schema import aiSchema
from utils import calcUtil, pdfUtil
from operator import itemgetter
from . import openaiService, s3Service
from dotenv import load_dotenv
load_dotenv()

# 시스템 메시지 생성 = 모델 판별
def createSystemMessage(db: Session):
    modelResponse = aiCrud.getAiEmbeddingList(db, {"category": "MODEL"})

    message = "답변 시에는 아래에 정의된 모델에 대해서만 답변할 수 있습니다. \n\n모델 종류(콤마[,]로 구분): \n"

    for response in modelResponse:
        message += ", ".join(json.loads(response.text_value))

    message += "\n"

    return message

# 시스템 메시지 생성 - 답변 양식
def createStreamSystemMessage():
    message = ("다음과 같은 답변 형식으로 작성해주세요."
    "\n\n1. \"안녕하세요. 인공지능 고객상담사입니다.\" 인사말 건네기"
    "\n2. 질문에 대한 답변 하기"
    "\n\n답변 형식은 다음 코드 블럭 안의 내용과 같으며, 실제 답변 시 코드 블럭(```)은 제거해주세요"
    "\n\n```"
    "\n안녕하세요. AI 인공지능 상담사입니다."
    "\n\n[답변]"
    "\n```"
    "\n\n답변의 내용은 2000자 이내로 출력해주세요.")
    
    return message

# 사용자 메시지 생성
def createUserMessage(results: list[dict], question: str, quetsionType: str = None):
    introduction = ""

    # 요약 정보, 상세 정보
    if quetsionType == "SUMMARY":
        introduction = '다음 질문에 답변하려면 아래의 Section 데이터만 사용하고, 내용을 요약해서 500자 내로 답변해주세요. "**"과 같은 마크다운 형식 없이 텍스트로만 답변해주세요.'
    elif quetsionType == "DETAIL":
        introduction = '다음 질문에 답변하려면 아래의 Section 데이터만 사용하고, 내용을 상세하게 답변해주세요.'
    else:
        introduction = '다음 질문에 답변하려면 아래의 Section 데이터만 사용하여 답변해주세요. 만약 적절한 답변을 찾을 수 없는 경우, 반드시 "X" 라고만 답변하고, 답변 가능한 내용이면 반드시 "O" 라고만 답변해주세요.'

    query = f"\n\nQuestion(사용자 질문): {question}"
    message = introduction
    message += f"{query}"

    section = "\n\nSection(참고할 데이터): "
    for result in results:
        section += "\n"
        section += re.sub("\n", "", result["text"])

    message += section
    

    return message

#db 임베딩 데이터와 사용자 질문의 임베딩 데이터의 유사도 분석 및 유사성 높은 데이터 리턴
def getRelevantEmbeddingText(db: Session, question: str, topN: int = 5):
    try:
        # 사용자 질문 임베딩    
        queryEmbeddingResponse = openaiService.getEmbeddingText([question])

        queryEmbedding = list(map(lambda data: data.embedding, queryEmbeddingResponse.data))[0]

        #DB의 데이터 읽어옴
        dbAiEmbeddingList = aiCrud.getAiEmbeddingList(db, {"category": "MANUAL"})
        
        resultList = []  
        for dbAiEmbedding in dbAiEmbeddingList:
            dbTextList = json.loads(dbAiEmbedding.text_value)
            dbEmbeddingList = list(map(lambda data: data["embedding"], json.loads(dbAiEmbedding.vector_value)["data"]))

            for index, text in enumerate(dbTextList):
                resultList.append({
                    "id": dbAiEmbedding.id,
                    "page": index + 1,
                    "text": text,
                    "vector_value": calcUtil.cosineSimilarity(queryEmbedding, dbEmbeddingList[index])    
                })

        return sorted(resultList, key=itemgetter("vector_value"), reverse=True)[0:topN]

    except Exception:
        raise

# gpt에게 질문
def verifySyntax(db: Session, embeddingList: list[dict], question: str):
    systemMsg = createSystemMessage(db)
    userMsg = createUserMessage(embeddingList, question, None)
    responseMsg = openaiService.askQuestionToGPT(systemMsg, userMsg)

    if responseMsg == "X":
        return False

    return True


# 텍스트 데이터 학습
def addTextLearn(db: Session, text: str):
    try:
        textArr = text.split("\n\n")
        textEmbeddingResponse = openaiService.getEmbeddingText(text)

        addEmbedding = aiSchema.Embedding(
            category = "MANUAL", 
            text_value = json.dumps(textArr, ensure_ascii = False), 
            vector_value = json.dumps(textEmbeddingResponse.model_dump(), ensure_ascii = False)
        )
        aiCrud.addAiEmbedding(db, addEmbedding)
        db.commit()
    except:
        db.rollback()
        return False

    return True

# pdf 파일 학습
def addPdfDocument(db: Session, file: UploadFile, videoLink: str, videoName: str):
    try:
        fileName = file.filename
        fileExt = fileName[fileName.rfind(".") + 1:]
        
        with file.file as pdfFile:
            # pdf > text변환 
            pdfTextList = pdfUtil.convertPDFToText(pdfFile)

            pdfEmbeddingResponse = openaiService.getEmbeddingText(pdfTextList)

            addEmbedding = aiSchema.Embedding(
                category = "MANUAL", 
                text_value = json.dumps(pdfTextList, ensure_ascii = False), 
                vector_value = json.dumps(pdfEmbeddingResponse.model_dump(), ensure_ascii = False)
            )
            # db 임베딩 저장
            result = aiCrud.addAiEmbedding(db, addEmbedding)
            filePath = f"/{result.id}/{file.filename}"

            # db 저장 학습 파일
            pdfFileParam = aiSchema.LearnFile(
                ai_embedding_id = result.id,
                file_path = f"{os.getenv("S3_DEFAULT_PATH")}{filePath}",
                file_name = fileName,
                file_ext = fileExt,
                file_size = file.size,
                file_kind = "D" 
            )
            aiCrud.addAiLearnFile(db, pdfFileParam)

            if videoLink and not videoLink.isspace() and videoName and not videoName.isspace():
                # 동영상 파일 저장
                videoFileParam = aiSchema.LearnFile(
                    ai_embedding_id = result.id,
                    file_path = videoLink,
                    file_name = videoName,
                    file_ext = "link",
                    file_size = file.size,
                    file_kind = "M" 
                )
                aiCrud.addAiLearnFile(db, videoFileParam)

            s3Service.uploadFile(pdfFile, filePath, None)

        db.commit()
    except:
        db.rollback()
        return False

    return True

# 모델 학습
def modelLearn(db: Session, text: str):
    try:
        textArr = text.split("\n")
        
        addEmbedding = aiSchema.Embedding(
            category = "MODEL", 
            text_value = json.dumps(textArr, ensure_ascii = False), 
        )
        aiCrud.addAiEmbedding(db, addEmbedding)

        db.commit()
    except:
        return False
    
    return True

def getFileInfo(db: Session, embeddingList: list[dict], questionType: str):
    response = {}
    if questionType == "VIDEO":
        fileData = getFileData(db, embeddingList, questionType)

        if fileData is None:
            return {
                "content": None,
                "file_path": None
            }
        audioData = getFileResponseText(questionType)
        response["content"] = audioData["text"]
        response["file_path"] = fileData["file_path"]

    elif questionType == "DOCUMENT":
        fileData = getFileData(db, embeddingList, questionType)

        if fileData is None:
            return {
                "content": None,
                "doc_page": None,
                "file_path": None
            }
        audioData = getFileResponseText(questionType)

        response["content"] = audioData["text"]
        response["dic_page"] = fileData["file_page"]
        response["file_path"] = f"{os.getenv("S3_URL")}{fileData["file_path"]}"

    return response

# db에서 문서와 동영상 데이터를 가져옴
def getFileData(db: Session, embeddionList: list[dict], questionType: str):
    param = {
        "ai_embeddion_id": embeddionList[0]["id"],
        "file_kind": "D"
    }

    if questionType != "DOCUMENT":
        param["file_kind"] = "M"

    aiLearnFileList = aiCrud.getAiLearnFileList(db, param)

    if len(aiLearnFileList) == 0:
        return None
    
    return {
        "file_id": aiLearnFileList[0].id,
        "file_path": aiLearnFileList[0].file_path,
        "file_name": aiLearnFileList[0].file_name,
        "file_size": aiLearnFileList[0].file_size,
        "file_page": embeddionList[0]["page"]
    }
    
# 문서, 동영상 응답 텍스트
def getFileResponseText(questionType):
    text = "링크를 클릭하시면 메뉴얼 문서를 다운로드하거나, 바로 보실 수 있습니다."

    if questionType != "DOCUMENT":
        text = "관련 동영상을 안내드립니다. 클릭하시면 동영상이 실행됩니다."
    
    return {
        "text": text
    }
