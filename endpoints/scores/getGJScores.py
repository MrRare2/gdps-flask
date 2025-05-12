from lib.exploit_patch import Escape
from lib.enums import Action, CommonError
from lib.log import log
from lib.security import Security
from lib.user import *
from flask import request

def do(db):
    person = Security.login_player(db, request)
    if not person["success"]: CommonError.InvalidRequest

    stars = diamonds = 
