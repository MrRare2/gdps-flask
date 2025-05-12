from lib.dailyconf import *
from lib.enums import Action, CommonError
from lib.exploit_patch import Escape
from lib.log import log
from lib.other import random_string
from lib.user import get_daily_chests, retrieve_daily_chest
from lib.security import Security
from lib.xor import XORCipher
from flask import request
import time
import random

def do(db):
    person = Security.login_player(db, request)
    if not person["success"]: return CommonError.InvalidRequest
    account_id = person["accountID"]
    user_id = person["userID"]

    cur = time.time()
    small_chest = big_chest = "0,0,0,0"

    reward_type = Escape.number(request.form.get("rewardType", 0))
    chk = XORCipher.cipher(Escape.url_base64_decode(Escape.latin(request.form.get("chk"))[5:].encode()).decode(),59182)
    udid = Escape.text(request.form.get("udid", ""))

    chests_time = get_daily_chests(db, user_id)

    small_chest_count = chests_time["chest1count"]
    big_chest_count = chests_time["chest2count"]
    small_chest_time = cur - chests_time["chest1time"]
    big_chest_time = cur - chests_time["chest2time"]

    small_chest_left = max(0, small_wait - small_chest_time)
    big_chest_left = max(0, big_wait - big_chest_time)

    small_chest_items = small_items
    big_chest_items = big_items

    small_chest = str(random.randint(small_min_orbs, small_max_orbs))+","+str(random.randint(small_min_diamonds, small_max_diamonds))+","+str(random.choice(small_items))+","+str(random.randint(small_min_keys, small_max_keys))
    big_chest = str(random.randint(big_min_orbs, big_max_orbs))+","+str(random.randint(big_min_diamonds, big_max_diamonds))+","+str(random.choice(big_items))+","+str(random.randint(big_min_keys, big_max_keys))

    if reward_type == 1:
        if small_chest_left > 0: return CommonError.InvalidRequest

        small_chest_count += 1
        retrieve_daily_chest(db, user_id, 1)
        small_chest_left = small_wait
    elif reward_type == 2:
        if big_chest_left > 0: return CommonError.InvalidRequest

        big_chest_count += 1
        retrieve_daily_chest(db, user_id, 2)

    string = Escape.url_base64_encode(XORCipher.cipher(random_string(5)+":"+str(user_id)+":"+str(chk)+":"+str(udid)+":"+str(account_id)+":"+str(small_chest_left)+":"+small_chest+":"+str(small_chest_count)+":"+str(big_chest_left)+":"+big_chest+":"+str(big_chest_count)+":"+str(reward_type), 59182))
    hashstring = Security.generate_fourth_hash(string)
    return random_string(5)+string+"|"+hashstring

