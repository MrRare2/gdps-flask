from lib.enums import Action, CommonError
from lib.exploit_patch import Escape
from lib.log import log
from lib.security import Security
from flask import request

def do(db):
    person = Security.login_player(db, request)
    if not person["success"]: return CommonError.InvalidRequest
    comment_id = Escape.number(str(request.form.get("commentID", "-1")))
    
    account_id = person["accountID"]
    user_name = person["userName"]
    user_id = person["userID"]

    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM acccomments WHERE userID = %s AND commentID = %s", (user_id, comment_id))
    comment = cursor.fetchone()
    if not comment: return CommonError.InvalidRequest

    cursor.execute("DELETE FROM acccomments WHERE commentID = %s", (comment_id,))
    db.commit()

    log(db, person, Action.AccountCommentDeletion, user_name, comment["comment"], account_id, comment["commentID"], comment["likes"], comment["dislikes"])

    return CommonError.Success
