from lib.accounts import create_user
from lib.enums import CommonError
from lib.exploit_patch import Escape
from lib.ip import IP
from lib.log import safe_int
from lib.req import Secret, request_data
from lib.user import get_account_by_id, get_user_id
from lib.xor import XORCipher
from flask import Blueprint, request, render_template_string, redirect, url_for
from urllib.parse import urlparse
import base64
import conn
import os
import time
import zlib

dashboard = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard.route("/")
def dashboard_main():
    return "not implemented yet"

@dashboard.route('/reupload_lvl', methods=['GET', 'POST'])
def reupload_lvl():
    if request.method == 'POST':
        db = conn.init()
        level_id = Escape.number(request.form.get('level_id', "-1"))
        base = Escape.text(request.form.get("base", "http://www.boomlings.com/database"))
        try: p_url = urlparse(base)
        except: return "Invslid URL"
        db = conn.init()
        code, data = request_data(base, "downloadGJLevel22.php", {"levelID": level_id}, Secret.Common)
        if code != 200 or data == "-1" or data == "": return "Cannot retreive data from server"
        level = data.split("#")[0]
        level_parts = level.split(":")
        level_dict = dict(zip(level_parts[::2], level_parts[1::2]))
        if level_dict.get("4","") == "": return CommonError.InvalidRequest
        upload_date = time.time()
        if p_url.netloc == request.host.split(":")[0]: return "You are attempting to re-upload from the target server"
        cursor = db.cursor()
        cursor.execute("SELECT count(*) FROM levels WHERE originalReup = %s OR original = %s", (level_id, level_id))
        result = cursor.fetchone()
        if result and result[0] != 0: return "Level has already been reuploaded"
        lvl_str = level_dict["4"]
        game_version = level_dict.get("13", "")
        if lvl_str[:2] == "eJ":
            lvl_str = zlib.decompress(base64.urlsafe_b64decode(lvl_str), 15 | 32)
            if int(game_version) > 18: game_version = 18
        hostname = IP.get_ip()
        two_player = level_dict.get("31")
        song_id = level_dict.get("35")
        coins = level_dict.get("37")
        req_star = level_dict.get("39")
        extra_string = level_dict.get("36", "")
        star_stars = level_dict.get("18", 0)
        is_ldm = safe_int(level_dict.get("40"))
        password = level_dict.get("27")
        if password != "0": password = XORCipher.cipher(Escape.url_base64_decode(password).decode(), 26364)
        star_coins = 0
        star_diff = 0
        star_demon = 0
        star_auto = 0
        if p_url.netloc == "www.boomlings.com" and star_stars != 0:
            star_coins = safe_int(level_dict.get("38", 0))
            star_diff = safe_int(level_dict.get("9", 0))
            star_demon = safe_int(level_dict.get("17", 0))
            star_auto = safe_int(level_dict.get("25", 0))
        else: star_stars = 0
        target_user_id = level_dict.get("6")
        cursor.execute("SELECT accountID, userID FROM links WHERE targetUserID=%s AND server=%s", (target_user_id, p_url.netloc))
        result = cursor.fetchone()
        if result is None:
            # you can change these
            user_id = "15"
            ext_id = "15"
        else:
            info = result[0]
            user_id = info["userID"]
            ext_id = info["accountID"]
        level_dict["2"] = Escape.text(level_dict["2"])
        cursor.execute("INSERT INTO levels (levelName, gameVersion, binaryVersion, userName, levelDesc, levelVersion, levelLength, audioTrack, auto, password, original, twoPlayer, songID, objects, coins, requestedStars, extraString, levelString, levelInfo, secret, uploadDate, updateDate, originalReup, userID, extID, unlisted, hostname, starStars, starCoins, starDifficulty, starDemon, starAuto, isLDM, songIDs, sfxIDs, ts) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (
            level_dict["2"], game_version, "40", "Reupload", level_dict["3"], level_dict["5"], level_dict["15"], level_dict["12"], "0", password, level_dict["1"], two_player, song_id, "0", coins, req_star, extra_string, "", "", "", upload_date, upload_date, level_dict["1"], user_id, ext_id, "0", hostname, star_stars, star_coins, star_diff, star_demon, star_auto, is_ldm, level_dict.get("52", ""), level_dict.get("53", ""), safe_int(level_dict.get("57", time.time()))
        ))
        db.commit()
        reup_lvl_id = cursor.lastrowid
        try:
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'levels', str(reup_lvl_id)), 'w') as f:
                f.write(lvl_str.decode() if isinstance(lvl_str, bytes) else lvl_str)
        except IOError:return "Can't write level data"
        return CommonError.Success
    return render_template_string("""
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Reupload Level</title>
</head>
<body>
    <h1>Reupload Level</h1>
    <form method="post" action="{{ url_for('dashboard.reupload_lvl') }}">
        <label for="level_id">Level ID:</label>
        <input type="text" id="level_id" name="level_id" required>
        <button type="submit">Submit</button>
    </form>
</body>
</html>
""")
