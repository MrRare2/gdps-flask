from lib.enums import Action, CommonError, RegisterError
from lib.exploit_patch import Escape
from lib.accounts import create_account
from flask import request

def do(db):
    user_name = Escape.latin_no_spaces(request.form.get("userName"))
    password = request.form.get("password")
    email = Escape.text(request.form.get("email"))

    if not user_name.strip() or not password.strip() or not email.strip(): return CommonError.InvalidArgument

    status = create_account(db, user_name, password, password, email, email)
    if not status["success"]: return status["error"]
    return RegisterError.Success
