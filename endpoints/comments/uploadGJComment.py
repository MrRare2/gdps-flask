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
    level_id = Escape.multiple_ids(str(request.form.get("levelID","-1")))
    game_version = Escape.number(str(request.form.get("gameVersion", "0")))
    comment = Escape.text(request.form.get("comment"))
    percent = Escape.number(request.form.get("percent", 0))

    if not comment.strip(): return CommonError.InvalidRequest

    if int(game_version) >= 20: comment = Escape.url_base64_decode(comment)

    # add filtering soon
    # basic max length filter
    if len(comment) > 100:
        comment = comment[:100]

    if person["accountID"] == 0 or person["userID"] == 0: return CommonError.InvalidRequest

    comment = Escape.url_base64_encode(comment)

    cursor = db.cursor()
    cursor.execute("INSERT INTO comments (userID, userName, comment, levelID, percent, timestamp) VALUES (%s, %s, %s, %s, %s, %s)", (person["userID"], person["userName"], comment, level_id, percent, time.time()))
    db.commit()

    log(db, person, Action.CommentUpload, person["userName"], comment, cursor.lastrowid, level_id)

    # add automod soon

    return str(cursor.lastrowid)
