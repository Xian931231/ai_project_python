import os
from dotenv import load_dotenv

load_dotenv()

os.system("poetry install --no-root")
# os.system(f"poetry run uvicorn main:app --reload --port {os.getenv('SERVER_PORT')}")
os.system(f"cd src; nohup poetry run uvicorn main:app --reload --port {os.getenv('SERVER_PORT')} 1> /dev/null 2>&1 &")