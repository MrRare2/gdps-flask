from lib.enums import Action, CommonError
from lib.exploit_patch import Escape
from lib.log import log
from lib.other import random_string, get_vault_code, is_vault_code_used, use_vault_code
from lib.security import Security
from lib.xor import XORCipher
from flask import request
import time

def do(db):
    person = Security.login_player(db, request)
    if not person["success"]: return CommonError.InvalidRequest
    reward_key = Escape.latin(request.form.get("rewardKey", 0))
    chk = XORCipher.cipher(Escape.url_base64_decode(Escape.latin(request.form.get("chk"))[5:].encode()).decode(),59182)
    vault_code = get_vault_code(db, reward_key)
    if not vault_code or vault_vode["uses"] == 0 and (vault_code["duration"] != 0 and vault_code["duration"] <= time.time()): return CommonError.InvalidRequest
    if is_vault_code_used(db, person, vault_code["rewardID"]): return CommonError.InvalidRequest
    use_vault_code(db, person, vault_code, reward_key)
    string = Escape.url_base64_encode(XORCipher.cipher(random_string(5)+":"+str(chk)+":"+str(vault_code["rewardID"])+":"+str(vault_code["rewards"]), 59182))
    hashstring = Security.generate_fourth_hash(string)
    return random_string(5)+string+"|"+hashstring

