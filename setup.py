from app import db
from models import DBFileInfo, DBFilePath

db.create_all()
db.session.add(DBFilePath(id=0,name='ROOT', path='ROOT', idpath='0'))