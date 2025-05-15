import hashlib
import bcrypt
import base64
import os
import time
import gzip
from flask import request
from lib.exploit_patch import Escape
from lib.xor import XORCipher
from lib.ban import get_person_ban
from lib.enums import LoginError, Action
from lib.ip import IP
from lib.log import log
import lib.user as user
import lib.secconf as secconf
import lib.other as other
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding

class Security:
    @staticmethod
    def gjp2_from_password(password):
        return hashlib.sha1((password + "mI29fmAnxgTs").encode("utf-8")).hexdigest()

    @staticmethod
    def hash_password(password):
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    @staticmethod
    def login_to_account_with_id(db, account_id, key, login_type):
        ip = IP.get_ip()
        account = user.get_account_by_id(db, account_id)
        if not account:
            return {
                "success": False,
                "error": LoginError.WrongCredentials,
                "accountID": str(account_id),
                "IP": ip
            }

        if login_type == 1:
            if not bcrypt.checkpw(key.encode("utf-8"), account["password"].encode("utf-8")):
                return {
                    "success": False,
                    "error": LoginError.WrongCredentials,
                    "accountID": str(account_id),
                    "IP": ip
                }
        elif login_type == 2:
            if not key == account["gjp2"]:
                return {
                    "success": False,
                    "error": LoginError.WrongCredentials,
                    "accountID": str(account_id),
                    "IP": ip
                }

        if account["isActive"] == "0":
            return {
                "success": False,
                "error": LoginError.AccountIsNotActivated,
                "accountID": str(account_id),
                "IP": ip
            }

        user_id = user.get_user_by_id(db, account_id)["userID"]

        if not account.get("salt") and os.urandom(1):
            salt_value = Security.random_string(32)
            Security.assign_salt_to_account(db, account_id, salt_value)
            data_path = os.path.join("data", "accounts", account_id)
            if os.path.exists(data_path):
                self.encrypt_file(data_path, salt_value)

        user_name = account["userName"]
        Security.update_last_played(db, user_id)

        udid = request.form.get("udid", "")
        if udid:
            Security.assign_udid_to_registered_account(db, user_id, udid, user_name)

        return {
            "success": True,
            "accountID": str(account_id),
            "userID": str(user_id),
            "userName": str(user_name),
            "IP": ip
        }

    def login_to_account_with_username(self, db, user_name, key, login_type):
        account_id = user.get_account_id_with_username(db, user_name)
        if not account_id:
            return {
                "success": False,
                "error": LoginError.WrongCredentials,
                "accountID": "0"
            }
        return self.login_to_account_with_id(db, account_id, key, login_type)

    @staticmethod
    def assign_salt_to_account(db, account_id, salt):
        cursor = db.cursor()
        try:
            cursor.execute(
                "UPDATE accounts SET salt = %s WHERE accountID = %s" % (salt, account_id)
            )
            db.commit()
            return True
        except:
            db.rollback()
            return False

    @staticmethod
    def get_main_cipher_method():
        try:
            _ = algorithms.ChaCha20
            return "chacha20"
        except:
            return "aes-128-cbc"

    def encrypt_file(self, file_path, salt):
        with open(file_path, "rb") as f:
            data = f.read()
        encrypted = Security.encrypt_data(data, salt)
        with open(file_path, "wb") as f:
            f.write(encrypted.encode("utf-8"))

    @staticmethod
    def encrypt_data(data, salt):
        method = Security.get_main_cipher_method()
        key_bytes = salt.encode("utf-8")

        if method == "chacha20":
            nonce = b"\0" * 16
            cipher = Cipher(
                algorithms.ChaCha20(key_bytes.ljust(32, b"\0"), nonce),
                mode=None
            )
            encryptor = cipher.encryptor()
            encrypted = encryptor.update(data)
        else:
            iv = b"\0" * 16
            key16 = key_bytes[:16].ljust(16, b"\0")
            cipher = Cipher(algorithms.AES(key16), modes.CBC(iv))
            encryptor = cipher.encryptor()
            padder = padding.PKCS7(128).padder()
            padded = padder.update(data) + padder.finalize()
            encrypted = encryptor.update(padded) + encryptor.finalize()

        return base64.b64encode(encrypted).decode("utf-8")

    @staticmethod
    def decrypt_file(file_path, salt):
        with open(file_path, "rb") as f:
            encoded = f.read()
        return Security.decrypt_data(encoded.decode("utf-8"), salt)

    @staticmethod
    def decrypt_data(data_str, salt):
        method = Security.get_main_cipher_method()
        encrypted = base64.b64decode(data_str)
        key_bytes = salt.encode("utf-8")

        if method == "chacha20":
            nonce = b"\0" * 16
            cipher = Cipher(
                algorithms.ChaCha20(key_bytes.ljust(32, b"\0"), nonce),
                mode=None
            )
            decryptor = cipher.decryptor()
            decrypted = decryptor.update(encrypted)
        else:
            iv = b"\0" * 16
            key16 = key_bytes[:16].ljust(16, b"\0")
            cipher = Cipher(algorithms.AES(key16), modes.CBC(iv))
            decryptor = cipher.decryptor()
            padded = decryptor.update(encrypted) + decryptor.finalize()
            unpadder = padding.PKCS7(128).unpadder()
            decrypted = unpadder.update(padded) + unpadder.finalize()

        return decrypted.decode("utf-8")

    @staticmethod
    def get_login_type():
        if "gjp2" in request.form:
            return {"key": request.form["gjp2"], "type": 2}
        if "password" in request.form or "gjp" in request.form:
            if "gjp" in request.form:
                decoded = Escape.url_base64_decode(request.form["gjp"])
                key = XORCipher.cipher(decoded, 37526)
            else:
                key = request.form["password"]
            return {"key": key, "type": 1}
        return False

    @staticmethod
    def login_player(db, req):
        ip = IP.get_ip()
        account_id = None

        if Security.is_too_many_attempts():
            log_person = {
                "accountID": Escape.number(request.form.get("accountID", 0)),
                "userID": 0,
                "userName": "",
                "IP": ip
            }
            log(db, log_person, Action.FailedLogin)
            Security.check_rate_limits(log_person, 5)
            return {
                "success": False,
                "error": LoginError.WrongCredentials,
                "accountID": Escape.number(request.form.get("accountID", 0)),
                "IP": ip
            }

        if request.form.get("uuid") and any(request.form.get(k) for k in ("password", "gjp", "gjp2", "auth")):
            user_id = Escape.number(request.form["uuid"])
            account_id = user.get_account_id(db, user_id)
        elif not any(request.form.get(k) for k in ("password", "gjp", "gjp2", "auth")):
            if not secconf.unregistered_submissions:
                return {
                    "success": True,
                    "accountID": "0",
                    "userID": "0",
                    "userName": "Undefined",
                    "IP": ip
                }

            udid = request.form.get("udid", "")
            user_name = Escape.latin(request.form.get("userName", "Undefined"))
            account_id = Escape.number(request.form.get("accountID", 0))

            if not request.form.get("uuid") and account_id:
                user_id = user.get_user_id(db, account_id)
            else:
                user_id = Escape.number(request.form.get("uuid", 0))

            verify_udid = Security.verify_udid(db, user_id, udid, user_name)
            if not verify_udid:
                log_person = {
                    "accountID": 0,
                    "userID": user_id,
                    "userName": user_name,
                    "IP": ip
                }
                if udid:
                    log.log_action(db, log_person, Action.FailedLogin)
                    Security.check_rate_limits(log_person, 5)
                return {
                    "success": True,
                    "accountID": str(verify_udid.get("unregisteredID", "0")),
                    "userID": str(verify_udid.get("userID", "0")),
                    "userName": str(verify_udid.get("userName", "Undefined")),
                    "IP": ip
                }
        elif request.form.get("userName"):
            user_name = Escape.latin(request.form["userName"])
            account = user.get_account_by_user_name(db, user_name)
            if not account:
                return {
                    "success": False,
                    "error": LoginError.GenericError,
                    "accountID": account_id,
                    "IP": ip
                }
            account_id = account["accountID"]
        else:
            account_id = Escape.number(request.form.get("accountID", 0))

        login_info = Security.get_login_type()
        if not login_info:
            log_person = {
                "accountID": account_id,
                "userID": user.get_user_id(db, account_id),
                "userName": "",
                "IP": ip
            }
            Security.check_rate_limits(log_person, 5)
            return {
                "success": False,
                "error": LoginError.GenericError,
                "accountID": account_id,
                "IP": ip
            }

        result = Security.login_to_account_with_id(
            db,
            account_id,
            login_info["key"],
            login_info["type"],
        )
        if not account_id: account_id = 0
        if not result["success"]:
            log_person = {
                "accountID": account_id,
                "userID": user.get_user_by_id(db, account_id),
                "userName": "",
                "IP": ip
            }
            log(db, log_person, Action.FailedLogin)
            Security.check_rate_limits(log_person, 5)
            return {
                "success": False,
                "error": result["error"],
                "accountID": account_id,
                "IP": ip
            }

        auth = Security.get_auth_token(db, account_id)
        person = {
            "success": True,
            "accountID": result["accountID"],
            "userID": result["userID"],
            "userName": result["userName"],
            "IP": result["IP"],
            "auth": auth
        }

        if get_person_ban(db, person, 4):
            return True

        return person

    @staticmethod
    def is_too_many_attempts():
        return False  

    @staticmethod
    def check_rate_limits(*args, **kwargs):
        pass

    @staticmethod
    def update_last_played(db, user_id):
        cursor = db.cursor()
        cursor.execute("UPDATE users SET lastPlayed = %s WHERE userID = %s", (time.time(), user_id))

    @staticmethod
    def assign_udid_to_registered_account(db, user_id, udid, user_name):
        pass

    @staticmethod
    def verify_udid(db, user_id, udid, user_name):
        return True 

    @staticmethod
    def get_auth_token(db, account_id):
        account = user.get_account_by_id(db, account_id)
        token = account.get("auth")
        if not token:
            token = Security.assign_auth_token(db, account_id)
        return token

    @staticmethod
    def assign_auth_token(db, account_id):
        auth = other.random_string(16)

        cursor = db.cursor()
        cursor.execute("UPDATE accounts SET auth = %s WHERE accountID = %s", (auth, account_id))

        db.commit()

        return auth

    @staticmethod
    def encode_save_file(save_data):
        return Escape.url_base64_encode(gzip.compress(save_data.encode()))

    @staticmethod
    def decode_save_file(save_data):
        return gzip.decompress(Escape.url_base64_decode(save_data))

    @staticmethod
    def generate_level_hash(level_stats):
        hash_ = ""
        for each in level_stats:
            id_ = str(each["levelID"])
            hash_ += id_[0]+id_[len(id_)-1]+str(each["stars"])+str(each["coins"])
        return hashlib.sha1((hash_ + "xI25fpAapCQg").encode("utf-8")).hexdigest()  

    @staticmethod
    def generate_first_hash(level_string):
        salt = "xI25fpAapCQg"
        length = len(level_string)
        if length < 41:
            return hashlib.sha1((level_string + salt).encode("utf-8")).hexdigest()
        m = length // 40
        hash_chars = list("?" * 40 + salt)
        for i in range(40):
            hash_chars[i] = level_string[i * m]
        return hashlib.sha1("".join(hash_chars).encode("utf-8")).hexdigest()

    @staticmethod
    def generate_second_hash(level_string):
        return hashlib.sha1((level_string + "xI25fpAapCQg").encode("utf-8")).hexdigest()

    @staticmethod
    def generate_third_hash(level_string):
        return hashlib.sha1((level_string + "oC36fpYaPtdg").encode("utf-8")).hexdigest()

    @staticmethod
    def generate_fourth_hash(level_string):
        return hashlib.sha1((level_string + "pC26fpYaQCtg").encode("utf-8")).hexdigest()
