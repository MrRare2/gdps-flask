from lib.enums import Action, CommonError
from lib.exploit_patch import Escape
from lib.log import log
from lib.security import Security
from lib.user import get_user_by_id
from flask import request

def do(db):
    person = Security.login_player(db, request)
    if not person["success"]: return CommonError.InvalidRequest
    comment_id = Escape.number(str(request.form.get("commentID","-1")))
    
    account_id = person["accountID"]
    user_id = person["userID"]

    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM comments WHERE commentID = %s", (comment_id,))
    comment = cursor.fetchone()
    if not comment or str(comment["userID"]) != str(user_id): return CommonError.InvalidRequest

    user = get_user_by_id(db, comment["userID"])

    cursor.execute("DELETE FROM comments WHERE commentID = %s", (comment_id,))
    db.commit()

    log(db, person, Action.CommentDeletion, person["userName"], comment["comment"], user["extID"], comment["likes"] - comment["dislikes"], comment["levelID"])

    return CommonError.Success
