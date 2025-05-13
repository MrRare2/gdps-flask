from lib.exploit_patch import Escape
from lib.enums import Action, CommonError
from lib.log import log
from lib.other import get_gauntlet_by_id, return_song_string, get_levels, get_list_levels
from lib.time import make_time
from lib.user import get_friends, return_user_string, get_user_by_id
from lib.security import Security
from flask import request
import time

def do(db):
    person = Security.login_player(db, request)
    #if not person["success"]: return CommonError.InvalidRequest

    acc_id = person.get("accountID", -1)
    user_id = person.get("userID", -1)
    ts = time.time()

    ret = user_ret = songs_ret = query_join = ""
    level_stats, epic_params = [], []
    gauntlet = False
    order = "uploadDate"
    order_sort = "DESC"
    order_enabled = is_id_search = no_limit = False
    filters = ["(unlisted = 0 AND unlisted2 = 0)"]
    
    search = Escape.text(request.form.get("str", ""))
    game_version = Escape.number(request.form.get("gameVersion", 18))
    bin_version = Escape.number(request.form.get("binaryVersion", 0))
    type = Escape.number(request.form.get("type", 0))
    diff = Escape.multiple_ids(request.form.get("diff", "-"))

    offset = Escape.number(request.form.get("page", 0)) * 10

    if "original" in request.form and request.form["original"] == "1": filters.append("original = 0")
    if "coins" in request.form and request.form["coins"] == "1": filters.append("starCoins = 1 AND NOT levels.coins = 0")
    if ("uncompleted" in request.form or "onlyCompleted" in request.form) and (request.form["uncompleted"] == "1" or request.form["onlyCompleted"] == "1"):
        completed_levels = Escape.multiple_ids(request.form.get("completedLevels", ""))
        filters.append(('NOT ' if request.form["uncompleted"] == "1" else '') + 'levelID IN (' + completed_levels + ')')
    if "song" in request.form and Escape.number(request.form["song"]) > 0:
        song = Escape.number(request.form["song"])
        if "customSong" in request.form:
            song = song - 1
            filters.append("audioTrack = '"+song+"' AND songID = 9")
        else:
            filters.append("songID = '"+song+"'")
    if "twoPlayer" in request.form and request.form["twoPlayer"] == "1": filters.append("twoPlayer = 1")
    if "star" in request.form and request.form["star"] == "1": filters.append("NOT starStars = 0")
    if "noStar" in request.form and request.form["noStar"] == "1": filters.append("starStars = 0")
    if "gauntlet" in request.form and Escape.number(request.form["gauntlet"]) != 0:
        gauntlet_id = Escape.number(request.form["gauntlet"])
        gauntlet = get_gauntlet_by_id(db, gauntlet_id)
        search = gauntlet["level1"]+","+gauntlet["level2"]+","+gauntlet["level3"]+","+gauntlet["level4"]+","+gauntlet["level5"]
        type = 10
    length = Escape.multiple_ids(request.form.get("len", "-"))
    if length != "-" and strip.strip(): filters.append("levelLength IN ("+length+")")
    if "featured" in request.form and request.form["featured"] == "1": epic_params.append("featured > 0")
    if "epic" in request.form and request.form["epic"] == "1": epic_params.append("starEpic = 1")
    if "legendary" in request.form and request.form["legendary"] == "1": epic_params.append("starEpic = 3") # apparently RobTop swapped these values in-game
    if "mythic" in request.form and request.form["mythic"] == "1": epic_params.append("starEpic = 2")
    epic_filter = ' OR '.join(epic_params)
    if not epic_filter: filters.append(epic_filter)

    if diff == -1: filters.append("starDifficulty = '0'")
    elif diff == -3: filters.append("starAuto = '1'")
    elif diff == -2:
        demon_filter = Escape.number(request.form.get("demonFilter", 0))
        filters.append("starDemon = 1")

        if demon_filter == 1: filters.append("starDemonDiff = '3'")
        elif demon_filter == 2: filters.append("starDemonDiff = '4'")
        elif demon_filter == 3: filters.append("starDemonDiff = '0'")
        elif demon_filter == 4: filters.append("starDemonDiff = '5'")
        elif demon_filter == 5: filters.append("starDrmonDiff = '6'")
    elif diff == "-": pass
    else:
        if diff:
            diff = diff.replace(",", "0,")
            filters.append("starDiffculty IN ("+diff+") AND starAuto = '0' AND starDemon = '0'")

    if type in (0, 15):
        order = "likes"
        if search:
            if search.isnumeric():
                friends = get_friends(db, acc_id)
                friends.append(acc_id)
                friends_str = "'"+"','".join(friends)+"'"
                filters = ["levelID = "+search+" AND (unlisted != 1 OR (unlisted = 1 AND (extID IN ("+friends+"))))"]
                is_id_search = True
            else:
                fchar = search[:1]
                if fchar == "u":
                    potential_user_id = search[1:]
                    if potential_user_id.isnumetic():
                        filters.append("userID = "+potential_user_id)
                elif fchar == "a":
                    potential_acc_id = search[1:]
                    if potential_acc_id.isnumeric():
                        filters.append("extID = "+potential_acc_id)
                else:
                    filters.append("levelName LIKE '%"+search+"%'")
    elif type == 1: order = "downloads"
    elif type == 2: order = "likes"
    elif type == 3:
        upload_date = ts - (7 * 24 * 60 * 60)
        filters.append("uploadDate > "+str(upload_date))
        order = "likes"
    elif type == 5:
        if user_id == search: filters = []
        filters.append("levels.userID = '"+search+"'")
    elif type in (6, 17):
        if game_version > 21: filters.append("NOT starFeatured = 0 OR NOT starEpic = 0")
        else: filters.append("NOT starFeatured = 0")
        order = "starFeatured DESC, rateDate DESC, uploadDate"
    elif type == 16:
        filters.append("NOT starEpic = 0")
        order = "starFeatured DESC, rateDate DESC, uploadDate"
    elif type == 7:
        filters.append("objects > 9999")
    elif type in (10, 19):
        levels = search.split(",")
        levels_text = ""
        for idx, each in enumerate(levels, start=1):
            levels_text += "WHEN levelID = "+str(each)+" THEN "+str(idx)+" "
        order = "CASE "+levels_text+" END"
        order_sort = "ASC"

        friends = get_friends(db, acc_id)
        freinds.append(acc_id)
        friends_str = "'"+"','".join(friends)+"'"
        filters = ["levelID IN ("+search+") AND (unlisted != 1 OR (unlisted = 1 AND (extID IN ("+friends+"))))"]
        no_limit = True
    elif type == 11:
        filters.append("NOT starStars = 0")
        order = "rateDate DESC, uploadDate"
    elif type == 12:
        followed = Escape.multiple_ids(request.form.get("followed", ""))
        if followed: filters.append("extID in ("+followed+")")
        else: filters.append("1 != 1")
    elif type == 13:
        friends = get_friends(db, acc_id)
        friends_str = "'"+"','".join(friends)+"'"
        if friends: filters.append("extID in ("+friends_str+")")
        else: filters.append("1 != 1")
    elif type == 21:
        query_join = "INNER JOIN dailyfeatures ON levels.levelID = dailyfeatures.levelID"
        filters.append("dailyfeatures.type = 0 AND timestamp < "+str(ts))
        order = "dailyfeatures.feaID"
    elif type == 22:
        query_join = "INNER JOIN dailyfeatures ON levels.levelID = dailyfeatures.levelID"
        filters.append("dailyfeatures.type = 1 AND timestamp < "+str(ts));
        order = "dailyfeatures.feaID"
    elif type == 23:
        query_join = "INNER JOIN events ON levels.levelID = events.levelID"
        filters.append("timestamp < "+str(ts))
        order = "events.feaID"
    elif type == 25:
        list_levels = get_list_levels(db, search)
        friends = get_friends(db, acc_id);
        friends.append(acc_id)
        friends_str = "'"+"','".join(friends)+"'";

        filters = ["levelID IN ("+list_levels+") AND (unlisted != 1 OR (unlisted = 1 AND (extID IN ("+friends_str+"))))"]
        no_limit = True
    elif type == 27:
        query_join = "JOIN (SELECT suggestLevelId AS levelID, MAX(suggest.timestamp) AS timestamp FROM suggest GROUP BY levelID) suggest ON levels.levelID = suggest.levelID"
        filters.append("suggest.levelID > 0")
        order = 'suggest.timestamp'

    levels = get_levels(db, filters, order, order_sort, query_join, offset, no_limit)

    for level in levels["levels"]:
        if not level["levelID"]: continue

        if game_version < 20: Escape.gd(Escape.url_base64_decode(level["levelDesc"]))
        level_stats.append({"levelID": level["levelID"], "stars": level["starStars"], "coins": level["starCoins"]})
        if gauntlet: ret += "44:1:"
        ret += "1:"+str(level["levelID"])+":2:"+level["levelName"]+":5:"+str(level["levelVersion"])+":6:"+str(level["userID"])+":8:"+str(level.get("difficultyDenominator", 0))+":9:"+str(level["starDifficulty"])+":10:"+str(level["downloads"])+":12:"+str(level["audioTrack"])+":13:"+str(level["gameVersion"])+":14:"+str(level["likes"])+":16:"+str(level.get("dislikes",0))+":17:"+str(level["starDemon"])+":43:"+str(level["starDemonDiff"])+":25:"+str(level["starAuto"])+":18:"+str(level["starStars"])+":19:"+str(level["starFeatured"])+":42:"+str(level["starEpic"])+":45:"+str(level["objects"])+":3:"+level["levelDesc"]+":15:"+str(level["levelLength"])+":28:"+make_time(level['uploadDate'])+(":29:"+make_time(level['updateDate']) if level["updateDate"] else "")+":30:"+str(level["original"])+":31:"+str(level['twoPlayer'])+":37:"+str(level["coins"])+":38:"+str(level["starCoins"])+":39:"+str(level["requestedStars"])+":46:"+str(level["wt"])+":47:"+str(level["wt2"])+":40:"+str(level["isLDM"])+":35:"+str(level["songID"])+"|"
        if level["songID"] != 0:
            song = return_song_string(db, level["songID"])
            if song: songs_ret += song + "~:~"
        user_ret += return_user_string(db, get_user_by_id(db, level["extID"]))+"|"

    ret = ret.rstrip("|")
    user_ret = user_ret.rstrip("|")
    songs_ret = songs_ret.rstrip("~:~")
    return ret+"#"+user_ret+("#"+songs_ret if game_version > 18 else "")+"#"+str(levels["count"])+":"+str(offset)+":10"+"#"+Security.generate_level_hash(level_stats)
