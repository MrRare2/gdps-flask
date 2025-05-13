from flask import Flask, Blueprint, request
from dashboard import dashboard
from endpoints import *
import conn
import ssl
import threading

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['MAX_FORM_MEMORY_SIZE'] = 16 * 1024 * 1024
#app.config["DEBUG"] = True

main = Blueprint("main", __name__)

try:
    with app.app_context():
        conn.init()
        conn.close()
except Exception as e:
    print("MySQL connection failed...")
    print(e, str(e))
    exit(1)

@app.teardown_appcontext
def server_close(_):
    conn.close()

@app.errorhandler(405)
def err_mnn(x):
    return "-1", 200

@app.errorhandler(500)
def err_ise(x):
    return "-1", 200

@app.after_request
def intercept(req):
    print("server response final:", req.get_data(as_text=True))
    return req

# accounts

@main.route("/getAccountURL.php", methods=["POST"])
def getAccountURL_route():
    return request.scheme+"://"+request.environ.get("SERVER_NAME", "localhost")+":"+request.environ.get("SERVER_PORT", "5000")

@main.route("/accounts/loginGJAccount.php", methods=["POST"])
def loginGJAccount_route():
    db = conn.init()
    return loginGJAccount.do(db)

@main.route("/accounts/registerGJAccount.php", methods=["POST"])
def registerGJAccount_route():
    db = conn.init()
    return registerGJAccount.do(db)

@main.route("/accounts/syncGJAccount.php", methods=["POST"])
@main.route("/accounts/syncGJAccount20.php", methods=["POST"])
@main.route("/accounts/syncGJAccountNew.php", methods=["POST"])
def syncGJAccount_route():
    db = conn.init()
    return syncGJAccount.do(db)

@main.route("/accounts/backupGJAccount.php", methods=["POST"])
@main.route("/accounts/backupGJAccountNew.php", methods=["POST"])
def backupGJComment_route():
    db = conn.init()
    return backupGJAccount.do(db)

# comments

@main.route("/deleteGJAccComment20.php", methods=["POST"])
def deleteGJAccComment_route():
    db = conn.init()
    return deleteGJAccComment.do(db)

@main.route("/deleteGJComment20.php", methods=["POST"])
def deleteGJComment_route():
    db = conn.init()
    return deleteGJComment.do(db)

@main.route("/uploadGJAccComment.php", methods=["POST"])
@main.route("/uploadGJAccComment19.php", methods=["POST"])
@main.route("/uploadGJAccComment20.php", methods=["POST"])
def uploadGJAccComment_route():
    db = conn.init()
    return uploadGJAccComment.do(db)

@main.route("/uploadGJComment.php", methods=["POST"])
@main.route("/uploadGJComment19.php", methods=["POST"])
@main.route("/uploadGJComment20.php", methods=["POST"])
@main.route("/uploadGJComment21.php", methods=["POST"])
def uploadGJComment_route():
    db = conn.init()
    return uploadGJComment.do(db)

@main.route("/getGJAccountComments.php", methods=["POST"])                      
@main.route("/getGJAccountComments20.php", methods=["POST"])
def getGJAccComments_route():
    db = conn.init()
    return getGJAccountComments.do(db)

@main.route("/getGJComments.php", methods=["POST"])
@main.route("/getGJComments20.php", methods=["POST"])
@main.route("/getGJComments21.php", methods=["POST"])
def getGJComment_route():
    db = conn.init()
    return getGJComments.do(db)

# levels

@main.route("/downloadGJLevel.php", methods=["POST"])
@main.route("/downloadGJLevel19.php", methods=["POST"])
@main.route("/downloadGJLevel20.php", methods=["POST"])
@main.route("/downloadGJLevel21.php", methods=["POST"])
@main.route("/downloadGJLevel22.php", methods=["POST"])
def downloadGJLevel_route():
    db = conn.init()
    return downloadGJLevel.do(db)
    #return open('1st.txt', 'r').read()

@main.route("/getGJLevels.php", methods=["POST"])
@main.route("/getGJLevels19.php", methods=["POST"])
@main.route("/getGJLevels20.php", methods=["POST"])
@main.route("/getGJLevels21.php", methods=["POST"])
def getGJLevels_route():
    db = conn.init()
    return getGJLevels.do(db)
    #return open('1stget.txt', 'r').read()

@main.route("/uploadGJLevel.php", methods=["POST"])
@main.route("/uploadGJLevel19.php", methods=["POST"])
@main.route("/uploadGJLevel20.php", methods=["POST"])
@main.route("/uploadGJLevel21.php", methods=["POST"])
def uploadGJLevel_route():
    db = conn.init()
    return uploadGJLevel.do(db)

@main.route("/suggestGJStars.php", methods=["POST"])
@main.route("/suggestGJStars20.php", methods=["POST"])
def suggestGJStars_route():
    db = conn.init()
    return suggestGJStars.do(db)

# misc

@main.route("/requestUserAccess.php", methods=["POST"])
def requestUserAccess_route():
    db = conn.init()
    return requestUserAccess.do(db)

# profiles

@main.route("/getGJUserInfo20.php", methods=["POST"])
def getGJUserInfo_route():
    db = conn.init()
    return getGJUserInfo.do(db)

# rewards

@main.route("/getGJRewards.php", methods=["POST"])
def getGJRewards_route():
    db = conn.init()
    return getGJRewards.do(db)

# scores

@main.route("/updateGJUserScore.php", methods=["POST"])
@main.route("/updateGJUserScore19.php", methods=["POST"])
@main.route("/updateGJUserScore20.php", methods=["POST"])
@main.route("/updateGJUserScore21.php", methods=["POST"])
@main.route("/updateGJUserScore22.php", methods=["POST"])
def updateGJUserScore_route():
    db = conn.init()
    return updateGJUserScore.do(db)

app.register_blueprint(main)
# compat with robtop server endpoints /database/*
app.register_blueprint(main, url_prefix="/database", name="compat")
app.register_blueprint(dashboard, url_prefix="/dashboard", name="dashboard")

# do this only on localhost!!!
def run_http():
    app.run(host='127.0.0.1', port=4999, threaded=True)

def run_https():
    app.run(
        host='127.0.0.1',
        port=5000,
        ssl_context=('cert.pem', 'key.pem'),
        threaded=True
    )

if __name__ == "__main__":
    threading.Thread(target=run_http).start()
    threading.Thread(target=run_https).start()
