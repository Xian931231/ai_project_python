import boto3
import os
from dotenv import load_dotenv
load_dotenv()

BUTKET_NAME = os.getenv("S3_BUCKET_NAME")
DEFAULT_PATH = os.getenv("S3_DEFAULT_PATH")

session = boto3.Session(profile_name = "newfrom_ai")
s3Client = session.client("s3")

defaultExtraArgs = {
    "ContentDisposition": "inline" 
}

def uploadFile(file, filePath: str, extraArgs: dict = None):
    fullPath = f"{DEFAULT_PATH}{filePath}"
    if extraArgs is not None:
        defaultExtraArgs.update(extraArgs)

    s3Client.upload_fileobj(file, BUTKET_NAME, fullPath, ExtraArgs = defaultExtraArgs)
