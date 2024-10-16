import os
import redis as rd
from dotenv import load_dotenv
load_dotenv()

HOST = os.getenv("REDIS_HOST")
PORT = os.getenv("REDIS_PORT")

redisPool = rd.ConnectionPool(
     host = HOST,
     port = PORT,
     decode_responses = True
)
redis = rd.Redis.from_pool(redisPool)
