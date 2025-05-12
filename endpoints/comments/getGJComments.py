from lib.enums import Action, CommonError, CommentsError
from lib.exploit_patch import Escape
from lib.security import Security
from lib.user import get_account_id, get_user_by_id, get_person_comment_appearance
from lib.time import make_time
from lib.other import get_first_mentioned_level
from flask import request
import time

def do(db):
    person = Security.login_player(db, request)
    #if not person["success"]: return CommonError.InvalidRequest
    bin_version = Escape.number(request.form.get("binaryVersion", 0))
    game_version = Escape.number(request.form.get("gameVersion", 0))
    sort_mode = "comments.likes - comments.dislikes" if request.form.get("mode") else "comments.timestamp"
    count = Escape.number(request.form.get("count", 10))
    page = Escape.number(request.form.get("page", 0))

    if "levelID" in request.form:
        display_level_id = False
        level_id = Escape.multiple_ids(request.form.get("levelID"))

        if int(level_id) > 0:
            # check user can see comments soon
            cursor = db.cursor(dictionary=True)
            cursor.execute(f"SELECT *, levels.userID AS creatorUserID FROM levels INNER JOIN comments ON comments.levelID = levels.levelID WHERE levels.levelID = %s AND levels.isDeleted = 0 ORDER BY {sort_mode} DESC LIMIT 10 OFFSET {page}", (level_id,))
            comments = cursor.fetchall()

            cursor.execute("SELECT count(*) FROM levels INNER JOIN comments ON comments.levelID = levels.levelID WHERE levels.levelID = %s AND levels.isDeleted = 0", (level_id,))
            row = cursor.fetchone()
            comment_count = row["count(*)"] if row else 0
        else:
            list_id = level_id * -1
            # check user can see comments soon
            cursor = db.cursor(dictionary=True)
            cursor.execute(f"SELECT *, lists.accountID AS creatorAccountID FROM lists INNER JOIN comments ON comments.levelID = (lists.listID * -1) WHERE lists.listID = %s ORDER BY {sort_mode} DESC LIMIT 10 OFFSET {page}", (list_id,))
            comments = cursor.fetchall()

            cursor.execute("SELECT count(*) FROM lists INNER JOIN comments ON comments.levelID = (lists.listID * -1) WHERE lists.listID = :listID", (list_id,))
            row = cursor.fetchall()
            comment_counts = row["count(*)"] if row else 0
    elif "userID" in request.form:
        display_level_id = True
        target_user_id = Escape.number(request.form.get("userID"))
        # check if user can see comments soon
        cursor = db.cursor(dictionary=True)
        cursor.execute(f"SELECT *, levels.userID AS creatorUserID FROM levels INNER JOIN comments ON comments.levelID = levels.levelID WHERE comments.userID = %s AND levels.unlisted = 0 AND levels.unlisted2 = 0 AND levels.isDeleted = 0 ORDER BY {sort_mode} DESC LIMIT 10 OFFSET {page}", (target_user_id,))
        comments = cursor.fetchall()

        cursor.execute("SELECT count(*) FROM levels INNER JOIN comments ON comments.levelID = levels.levelID WHERE comments.userID = %s AND levels.unlisted = 0 AND levels.unlisted2 = 0 AND levels.isDeleted = 0", (target_user_id,))
        row = cursor.fetchone()
        comment_count = row["count(*)"] if row else 0
		
    else: return CommonError.InvalidRequest

    if len(comments) <= 0: return CommentsError.NothingFound

    ret = users_ret = person_ret = ""

    for each in comments:
        extra = []
        creator_rating = {"1": "Liked by creator", "-1": "Disliked by creator"}
        if not each["extID"]:
            each["extID"] = get_account_id(each["userID"])
        if each["userID"] == each["creatorUserID"] or each["extID"] == each["creatorAccountID"]: extra.append("Creator")
        elif each["commentRating"]: extra.append(creator_rating[each["creatorRating"]])
        each["comment"] = Escape.url_base64_decode(each["comment"])
        show_level_id = each["commentID"] if display_level_id else get_first_mentioned_level(each["comment"])
        comment_text = Escape.gd(each["comment"]) if game_version < 20 else Escape.url_base64_encode(each["comment"])
        likes = each["likes"] - each["dislikes"]

        user = get_user_by_id(db, each["userID"])
        # clan soon?
        if bin_version > 31:
            player = {"accountID": user["extID"], "userID": user["userID"], "IP": user["IP"]}
            appearance = get_person_comment_appearance(db, player)
            if not appearance["commentsExtraText"]: extra.append(appearance["commentsExtraText"])
            person_ret += "~11~"+str(appearance['modBadgeLevel'])+"~12~"+str(appearance['commentColor'])+":1~"+str(user['userName'])+"~7~1~9~"+str(user['icon'])+"~10~"+str(user['color1'])+"~11~"+str(user['color2'])+"~14~"+str(user['iconType'])+"~15~"+str(user['special'])+"~16~"+str(user['extID'])
        else:
            users_ret += str(user["userID"])+":"+str(user["userName"])+":"+str(user["extID"])+"|"
        timestamp = make_time(each["timestamp"])
        if show_level_id: ret += "1~"+str(show_level_id)+"~"
        ret += "2~"+comment_text+"~3~"+str(each["userID"])+"~4~"+str(likes)+"~5~0~7~"+str(each["isSpam"])+"~9~"+timestamp+"~6~"+str(each["commentID"])+"~10~"+str(each["percent"])+person_ret
        ret += "|"
    
    ret = ret.rstrip("|")
    if bin_version < 32:
        ret += "#"+users_ret.rstrip("|")

    ret += "#"+str(comment_count)+":"+str(page)+":"+str(len(comments))
    return ret
