from datetime import datetime
from app import db
class DBFileInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    parentid = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(64), nullable=False)
    hashname = db.Column(db.String(16), nullable=False)
    uploadtime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    #def __init__(self, isfolder, name, path, uploadtime):
    #    self.isfolder = isfolder
    #    self.name = name
    #    self.path = path
    #    self.uploadtime = uploadtime

    def __repr__(self):
        return "<User(id.'%s', f.'%s', n.'%s')>" % (self.id, self.isfolder, self.name)

class DBFilePath(db.Model):
    __tablename__ = 'file_tree'
    #__table_args__ = {}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    parentid = db.Column(db.Integer, nullable=True)
    name = db.Column(db.String(128), nullable=False)
    path = db.Column(db.String(128), nullable=True)

    #def __init__(self, fileid, parentid):
    #    self.fileid = fileid
    #    self.parentid = parentid

    def __repr__(self):
        return "<DBFileTree(id.'%s', pid.'%s', n.'%s')>" % (self.id, self.parentid, self.path)