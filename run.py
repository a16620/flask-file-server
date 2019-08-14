from app import db, app
from models import DBFileInfo, DBFilePath
from flask import request, redirect, render_template
from werkzeug.utils import secure_filename
import os
import hashlib

FORBIDEN_EXTS = ['php', 'asp', 'py']
UPLOAD_ROUTE = ''

def hash_sha128(d):
        return hashlib.sha1(d.encode()).hexdigest()

def file_ext_check(name):
        nvec=name.rsplite('.', 1)
        if len(nvec) == 2:
                return (nvec[1] not in FORBIDEN_EXTS)
        else:
                return True

@app.route('/upload/<int:folderid>', methods=['GET', 'POST'])
def uploadfile(folderid):
    if request.method == 'POST':
        file = request.files['file']
        if file and file_ext_check(file.filename):
                file_name = secure_filename(file.filename)
                hs_name = hash_sha128(file_name)
                fpath = os.path.join(UPLOAD_ROUTE, hs_name)
                file.save(fpath)
                fi = DBFileInfo(name=file_name, parentid=folderid, hashname=hs_name)
                db.session.add(fi)
                db.session.commit()
                return redirect('/dir/'+folderid)
        else:
                return "No File"

def getfiles(directory):
        out = db.session.query(DBFileInfo).filter_by(parentid=int(directory)).all()
        return out

def getfolders(folderid):
        return db.session.query(DBFilePath).filter_by(parentid=folderid).all()

def getcurrentpath(directory):
        ls = db.session.query(DBFilePath).filter_by(id=directory)
        if ls.count() == 0:
                return []
        t = ls.first().path
        return ('' if t == None else str(t)).split('.')

@app.route('/dir/<int:folderid>')
def directoryview(folderid):
        proute = getcurrentpath(folderid)
        folders = getfolders(folderid)
        files = getfiles(folderid)
        llen = len(proute)
        if llen == 0:
                return render_template('directory.html', fid=folderid, path=None, lastpath=None, folders=(None if len(folders) == 0 else folders), files=(None if len(files) == 0 else files))
        else:
                last = proute[llen-1]
                left = None
                if llen >= 2:
                        left = proute[0:llen-2]
                return render_template('directory.html', fid=folderid, path=left, lastpath=last, folders=(None if len(folders) == 0 else folders), files=(None if len(files) == 0 else files))

app.run(debug=True)