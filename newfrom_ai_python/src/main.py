from fastapi import FastAPI
from routers import apiRouter
from db.models import aiModel
from config.dbConfig import engine
from config import sessionConfig

aiModel.Base.metadata.create_all(bind=engine)

app = FastAPI()

sessionConfig.setSession(app)

app.include_router(apiRouter.router, prefix = "/api")

@app.get("/")
async def index():
     return {"result", "ok"}

