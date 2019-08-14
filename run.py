from app import db, app
from models import DBFileInfo, DBFilePath
from flask import request, redirect, render_template, send_file
from werkzeug.utils import secure_filename
import os
import hashlib
from time import time

FORBIDEN_EXTS = ['php', 'asp', 'py']
UPLOAD_ROUTE = 'files'

def hash_sha128(d):
        return hashlib.sha1((d+str(time())).encode()).hexdigest()

def file_ext_check(name):
        nvec=name.rsplit('.', 1)
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
                return redirect('/dir/'+str(folderid))
        else:
                return "No File"

def getlastpathidstrp1():
        return str(db.session.query(DBFilePath.id).order_by(DBFilePath.id.desc()).limit(1).first()[0]+1)

def addfolder(foldername, parentfolder):
        oldpath = db.session.query(DBFilePath.path, DBFilePath.idpath).filter_by(id=parentfolder).first()
        if not oldpath or oldpath == None:
                return False
        newpath = str(oldpath[0])+'.'+foldername
        newidpath = str(oldpath[1])+'.'+getlastpathidstrp1()
        newfolder = DBFilePath(parentid=parentfolder, name=foldername, path=newpath, idpath=newidpath)
        db.session.add(newfolder)
        db.session.commit()
        return True

@app.route('/createfolder/<int:folderid>')
def createfolder(folderid):
        name = request.args.get('foldername')
        if not name:
                return "No folder name"
        addfolder(str(name), folderid)
        return redirect('/dir/'+str(folderid))

def getfiles(directory):
        out = []
        tmp = db.session.query(DBFileInfo).filter_by(parentid=int(directory)).all()
        for f in tmp:
                out.append({'filename':f.name, 'datet':f.uploadtime, 'fid':f.id})
        return out

def getfolders(folderid):
        return db.session.query(DBFilePath).filter_by(parentid=folderid).all()

def getcurrentpath(directory):
        ls = db.session.query(DBFilePath).filter_by(id=directory)
        if ls.count() == 0:
                return []
        to = ls.first()
        t = to.path
        path = ('' if t == None else str(t)).split('.')
        t = to.idpath
        idpath = ('' if t == None else str(t)).split('.')
        return list(zip(path, idpath))

@app.route('/dir/<int:folderid>')
def directoryview(folderid):
        proute = getcurrentpath(folderid)
        folders = getfolders(folderid)
        files = getfiles(folderid)
        llen = len(proute)
        print(proute)
        if llen == 0:
                return render_template('directory.html', fid=folderid, path=None, lastpath=None, folders=(None if len(folders) == 0 else folders), files=(None if len(files) == 0 else files))
        else:
                last = proute[llen-1]
                left = None
                if llen == 2:
                        left = [proute[0]]
                elif llen > 2:
                        left = proute[0:llen-1]
                return render_template('directory.html', fid=folderid, path=left, lastpath=last, folders=(None if len(folders) == 0 else folders), files=(None if len(files) == 0 else files))

@app.route('/download/<int:fileid>')
def downloadfile(fileid):
        file = db.session.query(DBFileInfo).filter_by(id=fileid).first()
        if file == None:
                return '404 Not Found'
        output = send_file(os.path.join(UPLOAD_ROUTE,file.hashname), as_attachment=True)
        output.headers[0] = (output.headers[0][0],output.headers[0][1].replace(file.hashname, file.name, 1),)
        
        return output

app.run(port=5000, debug=True)