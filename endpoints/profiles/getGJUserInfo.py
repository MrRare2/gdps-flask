from lib.exploit_patch import Escape
from lib.enums import Action, CommonError
from lib.log import log
from lib.security import Security
from lib.time import make_time
from lib.user import *
from flask import request
import math

def do(db):
    person = Security.login_player(db, request)
    if not person["success"]: return CommonError.InvalidRequest
    account_id = person["accountID"]
    target_acc_id = Escape.latin_no_spaces(request.form.get("targetAccountID"))
    target_user_id = get_user_id(db, target_acc_id)
    if not target_user_id: return CommonError.InvalidRequest

    is_blocked = is_person_blocked(db, account_id, target_acc_id)
    if is_blocked: return CommonError.InvalidRequest

    user = get_user_by_id(db, target_user_id)
    account = get_account_by_id(db, target_acc_id)

    # check ban soon
    user["rank"] = get_rank(user["stars"], user["moons"], user["userName"])
    user["creatorPoints"] = math.floor(user["creatorPoints"])
    user["messagesState"] = account["mS"]
    user["friendRequestsState"] = account["frS"]
    user["commentsState"] = account["cS"]
    user["youtubeurl"] = account["youtubeurl"]
    user["twitter"] = account["twitter"]
    user["twitch"] = account["twitch"]
    
    user_appearance = get_person_comment_appearance(db, {"accountID": target_acc_id, "userID": target_user_id, "IP": user["IP"]})
    user["badge"] = user_appearance["modBadgeLevel"]
    if account_id == target_acc_id:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT count(*) FROM friendreqs WHERE toAccountID = %s AND isNew = 1", (account_id,))
        requests_count = cursor.fetchone()["count(*)"]
        cursor.execute("SELECT count(*) FROM messages WHERE toAccountID = %s AND isNew = 0", (account_id,))
        messages_count = cursor.fetchone()["count(*)"]
        cursor.execute("SELECT count(*) FROM friendships WHERE (person1 = %s AND isNew1 = 1) OR (person2 = %s AND isNew2 = 1)", (account_id, account_id))
        friend_requests_count = cursor.fetchone()["count(*)"]

        user["incomingRequestsText"] = ":38:"+str(messages_count)+":39:"+str(requests_count)+":40:"+str(friend_requests_count)
    else:
        is_friend = is_friends(db, account_id, target_acc_id)
        if is_friend: user["friendsState"] = 1
        else:
            incoming_fr = get_friend_request(db, target_acc_id, account_id)
            if incoming_fr:
                req_time = make_time(incoming_fr["uploadDate"])
                user["incomingRequestText"] = ":32:"+str(incoming_fr["ID"])+":35:"+incoming_fr["comment"]+":37:"+req_time
            else: user["friendState"] = 4

    return return_user_string(db, user)
