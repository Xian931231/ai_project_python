from PyPDF2 import PdfReader
from typing import IO

# pdf 페이지별 텍스트를 리스트에 저장 후 리턴
def convertPDFToText(stream: IO):
    reader = PdfReader(stream)
    pages = reader.pages
    
    pageTextList = []

    for page in pages:
        extractText = page.extract_text()
        pageTextList.append(extractText)

    stream.seek(0)

    return pageTextList
    