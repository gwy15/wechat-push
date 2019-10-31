import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, REAL
from sqlalchemy.orm import sessionmaker

Model = declarative_base()


class Message(Model):
    __tablename__ = 'messages'
    id = Column(String, primary_key=True)
    app_id = Column(String)
    template_id = Column(String)
    receiver_id = Column(String)
    created_time = Column(REAL, index=True)
    ip = Column(String)  # use string for now
    UA = Column(String)
    
    errcode = Column(Integer)
    msgid = Column(Integer)

    title = Column(String)
    body = Column(String)
    url = Column(String)


def initDB(dbUrl):
    engine = sqlalchemy.create_engine(dbUrl)
    Model.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()
