from .exploit_patch import Escape
from .enums import Action, ModeratorAction
from .log import log, log_mod
from .req import request_data, Secret
from .song_servers import libraries
import base64
import json
import os
import random
import string
import time

def random_string(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def get_first_mentioned_level(text):
    if isinstance(text, bytes): text = text.decode()
    words = text.split()
    for word in words:
        if not word.startswith("#"):
            continue
        level_id = word[1:]
        if level_id.isdigit():
            return int(level_id)
    return False

def convert_ip_for_searching(ip, is_search=False):
    parts = ip.split('.')
    if len(parts) < 3:
        return ip
    return '.'.join(parts[:3]) if is_search else '.'.join(parts[:3] + ['0'])

def limit_value(x, y, z):
    return sorted([x, int(y), z], reverse=True)[1]

def fix_level_desc_crash(raw_desc):
    if '<c' in raw_desc:
        tags_start = raw_desc.count('<c')
        tags_end  = raw_desc.count('</c>')
        if tags_start > tags_end:
            raw_desc += '</c>' * (tags_start - tags_end)

    return raw_desc

def get_friends(db, acc_id):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT person1, person2 FROM friendships WHERE person1 = %s OR person2 = %s", (acc_id, acc_id))
    friends = cursor.fetchall()

    array = []

    for friend in friends:
        array.append(friend["person1"] if  friend["person2"] == acc_id else friend["person2"])

    return array

def get_gauntlet_by_id(db, g_id):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM gauntlets WHERE ID = %s", (g_id,))
    return cursor.fetchone()

def get_list_levels(db, l_id):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT listlevels FROM lists WHERE listID = %s", (l_id,))
    return cursor.fetchone()

def get_level_by_id(db, level_id):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM levels WHERE levelID = %s AND isDeleted = 0", (level_id,))
    return cursor.fetchone()

def get_daily_level(db, **kwargs):
    pass

def get_levels(db, filters, order, order_sorting, query_join, offset, no_limit=False):
    cursor = db.cursor(dictionary=True)
    large_query = "SELECT * FROM levels "+query_join+" WHERE ("+(") AND (".join(str(x) for x in filters if x.strip()) if len(filters) > 0 else "")+") AND isDeleted = 0 "+("ORDER BY "+order+" "+order_sorting if order else "")+" "+("LIMIT 10 OFFSET "+str(offset) if offset else '')
    cursor.execute(large_query)
    levels = cursor.fetchall()

    cursor.execute("SELECT count(*) FROM levels "+query_join+" WHERE ("+" ) AND ( ".join(str(x) for x in filters if x.strip())+") AND isDeleted = 0")
    row = cursor.fetchone()

    return {"levels": levels, "count": row["count(*)"] if row else 0}

def get_list_levels(db, list_id):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT listlevels FROM lists WHERE listID = :listID", (list_id,))
    return cursor.fetchone()

def get_library_song_info(db, song_id, type="music"):
    return False # impl later

def get_song_by_id(db, song_id, col="*"):
    cursor = db.cursor(dictionary=True)
    local_song = True
    cursor.execute("SELECT * FROM songs WHERE ID = %s", (song_id,))
    song = cursor.fetchone()

    if not song:
        song = get_library_song_info(db, song_id)
        local_song = False

    if not song: return False

    song["isLocalSong"] = local_song

    if col != "*": return song[col]
    else: return song

def return_song_string(db, song_id):
    library_song = False
    extra_song_string = ""
    song = get_song_by_id(db, song_id)
    if not song:
        library_song = True
        song = get_library_song_info(db, song_id)

    if not song: return ""

    dl_link = song["download"]

    if library_song:
        artist_names = []
        artists = song["artists"].split(".")

        if len(artists) > 0:
            for artist_id in artists:
                data = get_library_artist_info(artist_id)
                if not data: continue
                artists_names.append(str(artist_id)+","+data["name"])

        artists_names = ",".join(artist_names)
        extra_song_string += "~|~9~|~"+str(song["priorityOrder"])+"~|~11~|~"+song["ncs"]+"~|~12~|~"+song["artists"]+"~|~13~|~"+str(1 if song["new"] else 0)+"~|~14~|~"+str(song["new"])+"~|~15~|~"+artists_names
    return "1~|~"+str(song["ID"])+"~|~2~|~"+song["name"].replace("#","")+"~|~3~|~"+str(song["authorID"])+"~|~4~|~"+song["authorName"]+"~|~6~|~"+str(song["size"])+"~|~6~|~~|~10~|~"+dl_link+"~|~7~|~~|~8~|~1"+extra_song_string

def save_ng(db, song_id):
    payload = {"songID": song_id}
    code, resp = request_data("http://www.boomlings.com/database", "getGJSongInfo.php", payload, Secret.Common)
    if code != 200 or resp == "-1" or not resp.strip(): return False
    resp_l = resp.split("~|~")
    result = dict(zip(resp_l[::2], resp_l[1::2]))
    cursor = db.cursor()
    cursor.execute("INSERT INTO songs (ID, name, authorID, authorName, size, download) VALUES (%s, %s, %s, %s, %s, %s)", (song_id, result["2"], result["3"], result["4"], result["5"], result["10"]))
    db.commit()
    return get_song_by_id(db, song_id)

def generate_dat_file(db, main_server_time, type=0):
    library, servers, server_ids, types = {"folders": {}, "tags": {}}, [], {}, []
    types = ["sfx", "music"]
    for each in libraries:
        if each[2] is not None:
            servers["s"+str(each[0])] = each[2]
        server_ids[each[2]] = each[0]

    if types[type] == "sfx":
        if each[3] != 1:
            library['folders'][customLib[0] + 1] = {'name': Escape.dat(customLib[1]), 'type': 1, 'parent': 1}
    else:
        if each[3] != 0:
            library['tags'][customLib[0]] = {'ID': customLib[0], 'name': Escape.dat(customLib[1])}

    ids_path = os.path.join(os.path.dirname(__file__), "..", types[type], "ids.json")
    idsConverter = json.loads(open(ids_path).read()) if os.path.exists(ids_path) else {"count": (len(each) + 2 if type == 0 else 8000000),"IDs": [],"originalIDs": []}
    skip_sfx_path = os.path.join(os.path.dirname(__file__), "..", "config", "skipSFXIDs.json")
    skipSFXIDs = json.loads(open(skip_sfx_path).read()) if os.path.exists(skip_sfx_path) else {}

    for key, server in servers:
        if not os.path.exists(os.path.join(os.path.dirname(__file__), "..", types[type], key + ".dat")): continue
        res = bits = None
        try:
            res = zlib.decompress(Escape.url_base64_decode(open(os.path.join(os.path.dirname(__file__), "..", types[type], key + ".dat"), "rw").read()))
        except:
            os.remove(os.path.join(os.path.dirname(__file__), "..", types[type], key + ".dat"))
            continue

        res = res.decode().split("|")
        if type == 0:
            for i in range(len(res)):
                pass
        else:
            version = main_server_time
            x = 0
            for data in res:
                data = data.rstrip(";")
                music = data.split(";")
                for m_str in music:
                    song = m_str.split(",")
                    pass
    # partial implementation

def update_libraries(db, token, expires, main_server_time, type=0):
    servers, times = {}, []

    types = ["sfx", "music"]
    for library in libraries:
        if (types[type] == "sfx" and library[3] == 1) or (types[type] == "music" and library[3] == 0): continue
        if library[2].strip(): servers.update({"s"+str(library[0]): library[2]})

    updated_lib = False
    for key, server in servers.items():
        version_url = server + '/' + types[type] + '/' + types[type] + 'library_version' + ('_02' if types[type] == 'music' else '') + '.txt'
        data_url = server + '/' + types[type_] + '/' + types[type] + 'library' + ('_02' if types[type] == 'music' else '') + '.dat'
        old_version = open(os.path.join(os.path.dirname(__file__), '..', types[type_], f"{key}.txt"), "r").read().split(",") if os.path.exists(os.path.join(os.path.dirname(__file__), '..', '..', types[type_], f"{key}.txt")) else [0, 0]

        time.append(int(old_version[1]))
        if int(old_version[1]) + 600 > time.time():
            _, new_version = request_data(str(version_url), "", {}, None, method="GET", params={"token": token, "expires": expires}, pre_add_payloads=False, follow_redirects=True)
            new_version = Escape.number(new_version)
        if new_version > old_version[0] or not old_version[0]:
            open(os.path.join(os.path.dirname(__file__), '..', types[type_], f"{key}.txt"), "w").write(str(newVersion) + ', ' + str(int(time.time())))

            code, dat = request_data(data_url, "", {}, None, method="GET", params={"token": token, "expires": expires, "dashboard": "1"}, pre_add_payloads=False, follow_redirects=True, bytestring=True)
            if code == 200:
                open(os.path.join(os.path.dirname(__file__), '..', types[type_], f"{key}.dat"), "wb").write(dat.encode())
                updated_lib = True

    if os.path.exists(os.path.join(os.path.dirname(__file__), '..', types[type_], "gdps.txt")): old_version = open(os.path.join(os.path.dirname(__file__), '..', types[type_], "gdps.txt"), "r").read()
    else:
        old_version = 0
        open(os.path.join(os.path.dirname(__file__), '..', types[type_], "gdps.txt"), "w").write(str(main_server_time))
    
    times.append(main_server_time)
    if old_version < main_server_time or updated_lib: generate_dat_file(db, sorted(times, reverse=True)[0], type)

def add_dl_to_level(db, person, level_id):
    if person.get("accountID", -1) == 0 or person.get("userID", -1) == 0: return False
    cursor = db.cursor()
    cursor.execute("UPDATE levels SET downloads = downloads + 1 WHERE levelID = %s AND isDeleted = 0", (level_id,))
    db.commit()
    return True

def get_level_difficulty(difficulty):
    difficulty_str = str(difficulty).lower()

    if difficulty_str in ["1", "auto"]:
        return {"name": "Auto", "difficulty": 50, "auto": 1, "demon": 0}
    elif difficulty_str in ["2", "easy"]:
        return {"name": "Easy", "difficulty": 10, "auto": 0, "demon": 0}
    elif difficulty_str in ["3", "normal"]:
        return {"name": "Normal", "difficulty": 20, "auto": 0, "demon": 0}
    elif difficulty_str in ["4", "5", "hard"]:
        return {"name": "Hard", "difficulty": 30, "auto": 0, "demon": 0}
    elif difficulty_str in ["6", "7", "harder"]:
        return {"name": "Harder", "difficulty": 40, "auto": 0, "demon": 0}
    elif difficulty_str in ["8", "9", "insane"]:
        return {"name": "Insane", "difficulty": 50, "auto": 0, "demon": 0}
    elif difficulty_str in ["10", "demon", "harddemon", "hard_demon", "hard demon"]:
        return {"name": "Hard Demon", "difficulty": 60, "auto": 0, "demon": 1}
    elif difficulty_str in ["easydemon", "easy_demon", "easy demon"]:
        return {"name": "Easy Demon", "difficulty": 70, "auto": 0, "demon": 3}
    elif difficulty_str in ["mediumdemon", "medium_demon", "medium demon"]:
        return {"name": "Medium Demon", "difficulty": 80, "auto": 0, "demon": 4}
    elif difficulty_str in ["insanedemon", "insane_demon", "insane demon"]:
        return {"name": "Insane Demon", "difficulty": 90, "auto": 0, "demon": 5}
    elif difficulty_str in ["extremedemon", "extreme_demon", "extreme demon"]:
        return {"name": "Extreme Demon", "difficulty": 100, "auto": 0, "demon": 6}
    else:
        return {"name": "N/A", "difficulty": 0, "auto": 0, "demon": 0}

def next_featured_id(db):
    cursor = db.cursor()
    cursor.execute("SELECT starFeatured FROM levels WHERE isDeleted = 0 ORDER BY starFeatured DESC LIMIT 1")
    ret = cursor.fetchone()
    if ret is not None and ret[0] is not None: return ret[0] + 1
    return 1

def send_level(db, level_id, person, difficulty, stars, featured_value):
    pass

def rate_level(db, level_id, person, difficulty, stars, verify_coins, featured_value):
    if person['accountID'] == 0 or person['userID'] == 0: return False

    level = get_level_by_id(db, level_id)

    real_difficulty = get_level_difficulty(difficulty)

    if featured_value: 
        epic = featured_value - 1
        featured = level.get("starFeatured", next_featured_id(db))
    else:
        epic = 0
        featured = 0

    star_coins = 1 if verify_coins != 0 else 0
    star_demon = 1 if real_difficulty["demon"] != 0 else 0
    demon_diff = real_difficulty["demon"]

    cursor = db.cursor()
    cursor.execute("UPDATE levels SET starDifficulty = %s, difficultyDenominator = 10, starStars = %s, starFeatured = %s, starEpic = %s, starCoins = %s, starDemon = %s, starDemonDiff = %s, starAuto = %s, rateDate = %s WHERE levelID = %s AND isDeleted = 0", (real_difficulty["difficulty"], stars, featured, epic, star_coins, star_demon, demon_diff, real_difficulty["auto"], time.time(), level_id))

    log_mod(db, person, ModeratorAction.LevelRate, real_difficulty["difficulty"], stars, level_id, featured_value, star_coins)
    return real_difficulty["name"]

def get_vault_code(db, code):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM vaultcodes WHERE code = %s", (base64.b64encode(code.encode()).decode(),))
    return cursor.fetchone()

def is_vault_code_used(db, person, reward_id):
    if person["accountID"] == 0 or person["userID"] == 0: return True

    cursor = db.cursor()
    cursor.execute("SELECT count(*) FROM actions WHERE type = 38 AND value = %s AND account = %s", (reward_id, person["accountID"]))
    return cursor.fetchone()[0] > 0

def use_vault_code(db, person, vault_code, code):
    if person["accountID"] == 0 or person["userID"] == 0: return True

    if vault_code["uses"] == 0: return False

    cursor = db.cursor()
    cursor.execute("UPDATE vaultcodes SET uses = uses - 1 WHERE rewardID = %s", (vault_code["rewardID"],))
    db.commit()

    log(db, person["accountID"], person["ID"], Action.VaultCodeUse, vault_code["rewardID"], vault_code["rewards"], code)
