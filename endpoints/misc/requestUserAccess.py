from lib.exploit_patch import Escape
from lib.enums import Action, CommonError
from lib.log import log
from lib.user import get_person_comment_appearance
from lib.security import Security
from flask import request

def do(db):
    person = Security.login_player(db, request)
    if not person["success"]: return CommonError.InvalidRequest
    badge = get_person_comment_appearance(db, person)["modBadgeLevel"]
    return str(badge)
