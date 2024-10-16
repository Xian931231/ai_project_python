from sqlalchemy.orm import Session
from sqlalchemy import select, insert
from db.models import aiModel
from db.schema import aiSchema
from sqlalchemy.sql import func

def getAiEmbeddingList(db: Session, param: dict):
    stmt = select(aiModel.Embedding)

    if "category" in param:
        stmt = stmt.where(aiModel.Embedding.category == param["category"])
    
    if "offset" in param and "limit" in param:
        stmt = stmt.offset(param["offset"]).limit(param["limit"])

    return db.scalars(stmt).all()
    
def addAiEmbedding(db: Session, param: aiSchema.Embedding):
    dbParam = aiModel.Embedding(**param.model_dump())
    dbParam.insert_date = func.now()
    db.add(dbParam)
    db.flush()

    return dbParam

def addAiLearnFile(db: Session, param: aiSchema.LearnFile):
    dbParam = aiModel.LearnFile(**param.model_dump())
    dbParam.insert_date = func.now()
    db.add(dbParam)
    db.flush()
    
    return dbParam

def getAiLearnFileList(db: Session, param: dict):
    stmt = select(aiModel.LearnFile)

    if "ai_embeddion_id" in param:
        stmt = stmt.where(aiModel.LearnFile.ai_embedding_id == param.get("ai_embeddion_id"))

    if "file_kind" in param:
        stmt = stmt.where(aiModel.LearnFile.file_kind == param.get("file_kind"))

    if "offset" in param and "limit" in param:
        stmt = stmt.offset(param["offset"]).limit(param["limit"])

    return db.scalars(stmt).all()

    
