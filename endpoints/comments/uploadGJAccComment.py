from lib.enums import Action, CommonError
from lib.exploit_patch import Escape
from lib.log import log
from lib.security import Security
from lib.user import get_account_by_id
from flask import request
import time

def do(db):
    person = Security.login_player(db, request)
    if not person["success"]: return CommonError.InvalidRequest
    account_id = person["accountID"]
    game_version = Escape.number(str(request.form.get("gameVersion", "0")))
    comment = Escape.text(request.form.get("comment"))

    if not comment.strip(): return CommonError.InvalidRequest

    if int(game_version) >= 20: comment = Escape.url_base64_decode(comment)

    account = get_account_by_id(db, account_id)
    # add filtering soon
    # basic max length filter
    if len(comment) > 100:
        comment = comment[:100]

    if person["accountID"] == 0 or person["userID"] == 0: return CommonError.InvalidRequest

    comment = Escape.url_base64_encode(comment)

    cursor = db.cursor()
    cursor.execute("INSERT INTO acccomments (userID, userName, comment, timestamp) VALUES (%s, %s, %s, %s)", (person["userID"], person["userName"], comment, time.time()))
    db.commit()

    log(db, person, Action.AccountCommentUpload, person["userName"], comment, cursor.lastrowid)

    # add automod soon

    return str(cursor.lastrowid)
