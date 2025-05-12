from lib.exploit_patch import Escape
from lib.enums import Action, CommonError, Permission
from lib.log import log
from lib.other import get_level_by_id, rate_level, send_level
from lib.user import check_perm
from lib.security import Security
from flask import request

def do(db):
    person = Security.login_player(db, request)
    if not person["success"]: return CommonError.InvalidRequest

    level_id = Escape.number(request.form["levelID"])
    stars = Escape.number(request.form["stars"])
    feature = Escape.number(request.form["feature"])

    level = get_level_by_id(db, level_id)
    if not level: return CommonError.InvalidRequest

    if check_perm(db, person, Permission.actionRateStars):
        rate_level(db, level_id, person,  stars, stars, 1 if level["coins"] else 0, feature)
        return CommonError.Success
    elif check_perm(db, person, Permission.actionSuggestRating):
        send_level(db, level_id, person, stars, stars, feature)
        return CommonError.Success

    return CommonError.InvalidRequest
