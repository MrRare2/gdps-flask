from lib.enums import Action, CommonError
from lib.exploit_patch import Escape
from lib.security import Security
from lib.user import get_user_id
from lib.time import make_time
from flask import request
import time

def do(db):
    person = Security.login_player(db, request)
    #if not person["success"]: return CommonError.InvalidRequest
    account_id = person["accountID"]
    target_acc_id = Escape.latin_no_spaces(request.form.get("accountID"))
    target_user_id = get_user_id(db, target_acc_id)

    if not target_user_id: return CommonError.InvalidArgument

    page = Escape.number(request.form.get("page", 0))

    comments_page = page * 10

    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM acccomments WHERE userID = %s ORDER BY timestamp DESC LIMIT 10 OFFSET %s", (target_user_id, comments_page)
    )
    account_comments = cursor.fetchall()
    cursor.execute("SELECT count(*) FROM acccomments WHERE userID = %s", (target_user_id,))
    row = cursor.fetchone()
    account_comments_count = row["count(*)"] if row else 0
    comments = {"comments": account_comments, "count": account_comments_count}

    ret = ""

    for each in comments["comments"]:
        timestamp = make_time(each["timestamp"])
        likes = str(each["likes"] - each["dislikes"])
        ret += "2~"+each["comment"]+"~3~"+str(each["userID"])+"~4~"+likes+"~5~0~7~"+str(each["isSpam"])+"~9~"+timestamp+"~6~"+str(each["commentID"])+"|"

    ret = ret.rstrip("|")

    ret += "#"+str(comments["count"])+":"+str(comments_page)+":10"
    return ret
