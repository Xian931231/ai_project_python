from sqlalchemy import Column, TEXT, BigInteger, VARCHAR, TIMESTAMP, CHAR, ForeignKey
from config.dbConfig import Base

class Embedding(Base):
    __tablename__ = "ai_embedding"
    id = Column("id", BigInteger, primary_key=True)
    category = Column("category", VARCHAR(20))
    text_value = Column("text_value", TEXT)
    vector_value = Column("vector_value", TEXT)
    insert_date = Column("insert_date", TIMESTAMP)

class LearnFile(Base):
    __tablename__ = "ai_learn_file"
    id = Column("id", BigInteger, primary_key=True)
    ai_embedding_id = Column("ai_embedding_id", BigInteger, ForeignKey("ai_embedding.id"))
    file_path = Column("file_path", VARCHAR(250))
    file_name = Column("file_name", VARCHAR(200))
    file_ext = Column("file_ext", VARCHAR(5))
    file_size = Column("file_size", BigInteger)
    file_kind = Column("file_kind", CHAR(1))
    insert_date = Column("insert_date", TIMESTAMP)