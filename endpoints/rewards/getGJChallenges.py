from lib.enums import Action, CommonError
from lib.exploit_patch import Escape
from lib.log import log
from lib.other import random_string
from lib.security import Security
from lib.xor import XORCipher
from flask import request
from datetime import datetime, timedelta
import time
import random

def do(db):
    person = Security.login_player(db, request)
    if not person["success"]: return CommonError.InvalidRequest
    account_id = person["accountID"]
    user_id = person["userID"]

    chk = XORCipher.cipher(Escape.url_base64_decode(Escape.latin(request.form.get("chk"))[5:].encode()).decode(),19847)
    udid = Escape.text(request.form.get("udid", ""))

    quest_id = round(time.time() / 100000)
    time_left = int((datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)).timestamp()) - int(time.time())

    cursor = db.cursor(dictionary=True)
    cursor.execute('SELECT * FROM quests')
    quests = cursor.fetchall()

    if not quests and len(quests) > 3: return CommonError.InvalidRequest

    random.shuffle(quests)

    quest1 = str(quest_id)+","+str(quests[0]["type"])+","+str(quests[0]["amount"])+","+str(quests[0]["reward"])+","+Escape.dat(quests[0]["name"])
    quest2 = str(quest_id + 1)+","+str(quests[1]["type"])+","+str(quests[1]["amount"])+","+str(quests[1]["reward"])+","+Escape.dat(quests[1]["name"])
    quest3 = str(quest_id + 2)+","+str(quests[2]["type"])+","+str(quests[2]["amount"])+","+str(quests[2]["reward"])+","+Escape.dat(quests[2]["name"])

    string = Escape.url_base64_encode(XORCipher.cipher(random_string(5)+":"+str(user_id)+":"+str(chk)+":"+udid+":"+str(account_id)+":"+str(time_left)+":"+quest1+":"+quest2+":"+quest3, 19847))
    hashstring = Security.generate_third_hash(string)
    return random_string(5)+string+"|"+hashstring

