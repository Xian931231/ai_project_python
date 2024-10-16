from pydantic import BaseModel

class Embedding(BaseModel):
    category: str
    text_value: str
    vector_value: str = None
    
class LearnFile(BaseModel):
    id: int = None
    ai_embedding_id: int
    file_path: str
    file_name: str
    file_ext: str
    file_size: int
    file_kind: str