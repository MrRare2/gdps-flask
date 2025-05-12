from lib.enums import Action
from lib.log import log
from lib.security import Security
from flask import request

def do(db):
    person = Security.login_player(db, request)
    if not person["success"]: return person["error"]
    log(db, person, Action.SuccessfulLogin)
    return str(person["accountID"]+","+str(person["userID"]))
