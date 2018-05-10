# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect, url_for, session, make_response, jsonify
from flask_oauthlib.client import OAuth
from pymongo import MongoClient
from pymongo import Connection
from urllib2 import Request, urlopen, URLError
import gridfs, datetime
from gridfs.errors import NoFile
from bson.objectid import ObjectId
from werkzeug import secure_filename

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['GOOGLE_ID'] = "1047595356269-lhvbbepm5r2dpt1bpk01f4m5e78vavk2.apps.googleusercontent.com"
app.config['GOOGLE_SECRET'] = "61w2EkT-lKN8eUkSRUBWIxMx"
app.debug = True
app.secret_key = 'development'
oauth = OAuth(app)
client = MongoClient('localhost', 27017)
db = client.OpenJournal

google = oauth.remote_app(
    'google',
    consumer_key=app.config.get('GOOGLE_ID'),
    consumer_secret=app.config.get('GOOGLE_SECRET'),
    request_token_params={
        'scope': 'email'
    },
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)

@app.route("/")
def home():
    return render_template('main.html')

@app.route("/main_comunity_detail", methods=['GET', 'POST'])
def getWriting():
    id = request.args.get("id")
    bulletin = db.Bulletin
    hit = 0
    data = bulletin.find({"_id": ObjectId(id)})
    for document in data:
        if document['_id'] == ObjectId(id):
            hit = document['hits']
    bulletin.update({"_id": ObjectId(id)},{"$set": {"hits":hit+1}})
    data = bulletin.find({"_id": ObjectId(id)})
    return render_template('main_comunity_detail.html',data = data)

@app.route('/oauth', methods=['GET', 'POST'])
def index():
    if 'google_token' in session:
        me = google.get('userinfo')
        return render_template('authorization.html', name=me.data['name'])
    else:
        return redirect(url_for('login'))

@app.route('/login')
def login():
    return google.authorize(callback=url_for('authorized', _external=True))

@app.route('/commentEnroll', methods=['POST'])
def commentEnroll():
    if 'google_token' in session:
        if request.method == 'POST':
            bulletin = db.Bulletin
            me = google.get('userinfo')
            userName = me.data['name']
            now = datetime.datetime.now()
            currentTime = str(now.strftime("%Y.%m.%d %H:%M"))
            commentContent = request.form['comment']
            objectId = request.form['objectId']
            data = bulletin.find({"_id": ObjectId(objectId)})
            commentNum = 0
            for document in data:
                if document['_id'] == ObjectId(objectId):
                    commentNum = document['commentNum']
            commentDict = {'commentNum':commentNum+1, 'userName':userName, 'Time':currentTime, 'comment':commentContent}
            bulletin.update({"_id": ObjectId(objectId)},{"$push": {"commentDicts":commentDict}})
            bulletin.update({"_id": ObjectId(objectId)},{"$set": {"commentNum":commentNum+1}})
            return "댓글 등록"
        else:
            return "post형태의 데이터 전송이 아닙니다."
    else:
        return "로그인이 필요한 기능입니다."

def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/files/<oid>')
def serve_gridfs_file(oid):
    try:
        file = fs.get(ObjectId(oid))
        response = make_response(file.read())
        response.mimetype = file.content_type
        return response
    except NoFile:
        abort(404)

@app.route("/main_enroll")
def mainEnroll():
    return render_template('main_enroll.html')

@app.route("/main_comunity")
def mainComunity():
    client = MongoClient('localhost', 27017)
    db = client.OpenJournal
    collection = db.Bulletin
    rows = collection.find().sort("writingNum",-1)
    client.close()
    return render_template('main_comunity.html', data=rows)

@app.route("/main_enroll_for_check_journal")
def mainEnrollForCheckJournal():
    return render_template('main_enroll_for_check_journal.html')

@app.route("/main_comunity_write")
def mainComunityWrite():
    return render_template('main_comunity_write.html')

@app.route('/logout', methods = ['POST', 'GET'])
def logout():
    session.pop('google_token', None)
    return render_template('main.html')

@app.route('/login/authorized')
def authorized():
    resp = google.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['google_token'] = (resp['access_token'], '')
    me = google.get('userinfo')

    userId = me.data['email']
    userName = me.data['name']
    doc = {'user_id': userId, 'user_name': userName}

    client = MongoClient('localhost', 27017)
    db = client.OpenJournal
    collection = db.Oauth_Users
    cursor = collection.find({"user_id": userId}) #회원등록이 되 있는지 검색, 회원 정보가 있다면 session에 로그인 정보 추가 후 이동
    for document in cursor:
        if document['user_id'] == userId:
            return render_template('authorization.html', name=me.data['name'])

    collection.insert(doc)
    client.close()
    return "구글계정으로 처음 로그인. db에 oauth정보 추가"

@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')

@app.route('/enroll')
def enroll():
   return render_template('enroll.html')

#일반회원 가입. 데이터베이스에 User등록
@app.route('/enrollUser', methods=['POST'])
def enrollUser():
    if request.method == 'POST':
        userId = request.form['user_id']
        userName = request.form['user_name']
        userPw = request.form['user_pw']
        fame = 0
        doc = {'user_id': userId, 'user_name': userName, 'user_pw': userPw, 'user_fame': fame}
        client = MongoClient('localhost', 27017)
        db = client.OpenJournal
        collection = db.Users
        cursor = collection.find({"user_id": userId}) #회원등록이 되 있는지 검색
        for document in cursor:
            if document['user_id'] == userId:
                return "이미 회원 가입 되었습니다."
	collection.insert(doc)
	client.close()
	return render_template("main.html")
    else:
	return "잘못된 데이터 수신 에러 입니다."

"""쿠키 설정"""
@app.route('/login2')
def login2():
   return render_template('login2.html')

@app.route('/setcookie', methods = ['POST', 'GET'])
def setcookie():
   if request.method == 'POST':
	user = request.form['nm']
 	resp = make_response(render_template('readcookie.html'))
	resp.set_cookie('userID', user)
   	return resp

@app.route('/getcookie')
def getcookie():
   name = request.cookies.get('userID')
   return '<h1>welcome '+name+'</h1>'

@app.route('/enrollPaper', methods=['POST'])
def enrollPaper():
    if 'google_token' in session:
        if request.method == 'POST':
            me = google.get('userinfo')
            userId = me.data['email']
            mainCategory = request.form['mainCat']
            subCategory = request.form['subCat']
            writer = request.form['name']
            title = request.form['title']
            abstract = request.form['abstract']
            hits = 0
            doc = {'user_id': userId, 'writer':writer,
                   'mainCategory':mainCategory, 'subCategory':subCategory,
                   'title':title, 'abstract':abstract, 'hits':hits}
            client = MongoClient('localhost', 27017)
            db = client.OpenJournal
            fs = gridfs.GridFS(db)
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                fild_id = fs.put(file, content_type=file.content_type, filename=filename)
                #return redirect(url_for('serve_gridfs_file', oid=str(oid)))
            collection = db.PaperInformation
            collection.insert(doc)
            client.close()
            return render_template('main_enroll.html')
    else:
        return "로그인 안돼있음"

@app.route('/enrollWriting', methods=['POST', 'GET'])
def enrollWriting():
    if 'google_token' in session:
        if request.method == 'POST':
            me = google.get('userinfo')
            userName = me.data['name']
            mainCategory = request.form['mainCat']
            subCategory = request.form['subCat']
            title = request.form['title']
            contents = request.form['contents']
            hits = 0
            like = 0
            writingNum = 0
            client = MongoClient('localhost', 27017)
            db = client.OpenJournal
            collection = db.BulletinNum
            bulletinCollection = db.Bulletin
            cursor = collection.find_one({"_id": ObjectId("5af1836db79ff2818f02efb0")})
            writingNum = int(cursor['writingNum']+1)
            now = datetime.datetime.now()
            commentNum = 0
            currentTime = str(now.strftime("%Y.%m.%d %H:%M"))
            doc = {'userName': userName, 'mainCategory':mainCategory, 'subCategory':subCategory,
                   'title':title, 'contents':contents, 'hits':hits, 'writingNum':writingNum,
                   'time':currentTime, 'commentNum':commentNum}
            bulletinCollection.insert(doc)
            collection.update({"_id": ObjectId("5af1836db79ff2818f02efb0")}, {"_id": ObjectId("5af1836db79ff2818f02efb0"),
            'writingNum':writingNum})
            client.close()
            return mainComunity()
    else:
        return "로그인 안돼있음"

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
