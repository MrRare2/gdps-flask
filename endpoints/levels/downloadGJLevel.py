from lib.exploit_patch import Escape
from lib.enums import Action, CommonError
from lib.log import log
from lib.other import add_dl_to_level, get_level_by_id, get_daily_level
from lib.time import make_time
from lib.user import get_user_by_id
from lib.security import Security
from lib.xor import XORCipher
from flask import request
import gzip
import os

def do(db):
    person = Security.login_player(db, request)
    #if not person["success"]: return CommonError.InvalidRequest
    
    if not request.form.get("levelID", "").isnumeric(): return CommonError.InvalidRequest

    level_id = Escape.multiple_ids(request.form.get("levelID"))
    game_version = Escape.number(request.form.get("gameVersion", 1))
    extras = request.form.get("extras")

    fea_id = 0
    if int(level_id) < 0:
        daily = get_daily_level_id(db, level_id)
        if not daily: return CommonError.InvalidRequest

    level = get_level_by_id(db, level_id)

    add_dl_to_level(db, person, level_id)

    upload_date = make_time(level["uploadDate"])
    if level["updateDate"]: update_date = make_time(level["updateDate"])
    else: update_date = None
    level_desc = Escape.url_base64_decode(level["levelDesc"])

    try: level_string = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data', 'levels', str(level["levelID"])), 'r').read()
    except: level_string = level["levelString"]

    password = xor_pass = level["password"]
    if game_version > 18:
        if level_string[:3] == "kS1":
            level_string = Escape.url_base64_encode(gzip.compress(level_string.encode()))
        if game_version > 19:
            if password != 0: xor_pass = Escape.url_base64_encode(XORCipher.cipher(str(password), 26364))
            level_desc = Escape.url_base64_encode(level_desc)

    ret = "1:"+str(level["levelID"])+":2:"+level["levelName"]+":3:"+str(level_desc)+":4:"+str(level_string)+":5:"+str(level["levelVersion"])+":6:"+str(level["userID"])+":8:"+str(level.get("difficultyDenominator",0))+":9:"+str(level["starDifficulty"])+":10:"+str(level["downloads"])+":11:1:12:"+str(level["audioTrack"])+":13:"+str(level["gameVersion"])+":14:"+str(level["likes"])+":16:"+str(level.get("dislikes", 0))+":17:"+str(level["starDemon"])+":43:"+str(level["starDemonDiff"])+":25:"+str(level["starAuto"])+":18:"+str(level["starStars"])+":19:"+str(level["starFeatured"])+":42:"+str(level["starEpic"])+":45:"+str(level["objects"])+":15:"+str(level["levelLength"])+":30:"+str(level["original"])+":31:"+str(level['twoPlayer'])+":28:"+upload_date+(":29:"+update_date if update_date else '')+":35:"+str(level["songID"])+":36:"+str(level["extraString"])+":37:"+str(level["coins"])+":38:"+str(level["starCoins"])+":39:"+str(level["requestedStars"])+":46:"+str(level["wt"])+":47:"+str(level["wt2"])+":48:"+str(level["settingsString"])+":40:"+str(level["isLDM"])+":27:"+str(xor_pass)+":52:"+str(level["songIDs"])+":53:"+str(level["sfxIDs"])+":57:"+str(level['ts'])
    if fea_id: ret += ":41:"+feaID
    if extras: ret += ":26:"+str(level["levelInfo"])

    ret += "#"+Security.generate_first_hash(level_string);
    some_string = str(level["userID"])+","+str(level["starStars"])+","+str(level["starDemon"])+","+str(level["levelID"])+","+str(level["starCoins"])+","+str(level["starFeatured"])+","+str(password)+","+str(fea_id)
    ret += "#"+Security.generate_second_hash(some_string);
    if fea_id: ret += "#"+get_user_string(get_user_by_id(db, level["extID"]));

    return ret
