from .enums import Action, RegisterError
from .exploit_patch import Escape
from .ip import IP
from .log import log
from .security import Security
from .user import get_account_by_user_name
from . import other
import time

def create_user(db, user_name, account_id, IP, bypass_rate_limit=False):
    # rate limit soon

    log_person = {"accountID": account_id, "userID": 0, "userName": user_name, "IP": IP}

    if not bypass_rate_limit: pass

    cursor = db.cursor()
    cursor.execute("INSERT INTO users (isRegistered, extID, userName, IP) VALUES (%s, %s, %s, %s)", (str(account_id).isdigit(), account_id, user_name, IP))
    db.commit()
    user_id = cursor.lastrowid
    log_person["userID"] = user_id

    log(db, log_person, Action.UserCreate, user_id, user_name)

    return user_id


def create_account(db, user_name, password, password_, email, email_):
    ip = IP.get_ip()
    salt = other.random_string(32)

    log_person = {"accountID": 0, "userID": 0, "username": user_name}

    # rate limit soon

    if len(user_name) > 15 or user_name.isdigit() or " " in user_name:
        return {"success": False, "error": RegisterError.InvalidUserName}

    if len(user_name) < 3:
        return {"success": False, "error": RegisterError.UserNameIsTooShort}

    if len(password) < 6:
        return {"success": False, "error": RegisterError.PasswordIsTooShort}

    if password != password_:
        return {"success": False, "error": RegisterError.PasswordsDoNotMatch}

    if not Escape.validate_email(email):
        return {"success": False, "error": RegisterError.InvalidEmail}

    user_name_exists = get_account_by_user_name(db, user_name)

    if user_name_exists:
        return {"success": False, "error": RegisterError.AccountExists}

    gjp2 = Security.gjp2_from_password(password)

    cursor = db.cursor()
    cursor.execute("INSERT INTO accounts (userName, password, email, registerDate, isActive, gjp2, salt) VALUES (%s, %s, %s, %s, %s, %s, %s)", (user_name, Security.hash_password(password), email, time.time(), 1, gjp2, salt))
    db.commit()
    account_id = cursor.lastrowid
    user_id = create_user(db, user_name, account_id, ip, True)
    person = {"accountID": account_id, "userID": user_id, "userName": user_name, "IP": ip}

    log(db, person, Action.AccountRegister, user_name, email, user_id)

    return {"success": True, **person}
