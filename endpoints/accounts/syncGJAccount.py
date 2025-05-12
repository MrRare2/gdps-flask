from lib.enums import Action, BackupError, CommonError
from lib.log import log
from lib.security import Security
from lib.user import get_account_by_id
from flask import request
import os

def do(db):
    person = Security.login_player(db, request)
    if not person["success"]:
        log(db, person, Action.FailedAccountSync, person.get("userName", "Undefined"))
        return CommonError.InvalidArgument
    user_name = person["userName"]
    account_id = person["accountID"]
    account = get_account_by_id(db, account_id)
    save_file = os.path.dirname(os.path.abspath(__file__))+"/../../data/accounts/"+str(account_id)

    if not os.path.exists(save_file): return BackupError.GenericError

    if account["salt"]:
        salt = account["salt"]
        save_data = Security.decrypt_file(save_file, salt)
    else:
        save_data = open(save_file, "r").read()

    if not save_data.strip():
        log(db, person, Action.FailedAccountSync, user_name)
        return BackupError.GenericError

    log(db, person, Action.SuccessfulAccountSync, user_name)
    return save_data+";21;30;a;a"
