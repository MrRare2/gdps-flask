from lib.exploit_patch import Escape
from lib.enums import Action, CommonError
from lib.log import log
from lib.other import limit_value, fix_level_desc_crash
from lib.user import upload_level
from lib.security import Security
from flask import request

def do(db):
    person = Security.login_player(db, request)
    if not person["success"]: return person["error"]

    game_version = Escape.number(request.form.get('gameVersion'))
    level_id = Escape.number(request.form.get('levelID'))
    level_name = Escape.latin(request.form.get('levelName')) or 'Unnamed level'

    if game_version >= 20:
        raw_desc = request.form.get('levelDesc', '')
        level_desc = Escape.text(Escape.url_base64_decode(raw_desc).decode())
    else:
        raw_desc = request.form.get('levelDesc', '')
        level_desc = Escape.text(raw_desc)

    level_desc = Escape.url_base64_encode(fix_level_desc_crash(level_desc))

    level_length = Escape.number(request.form.get('levelLength', 0))
    audio_track = Escape.number(request.form.get('audioTrack', 0))
    binary_version = Escape.number(request.form.get('binaryVersion', 0))
    auto = limit_value(0, Escape.number(request.form.get('auto', 0)), 1)
    original = Escape.number(request.form.get('original', 0))
    two_player = limit_value(0, Escape.number(request.form.get('twoPlayer', 0)), 1)
    song_id = Escape.number(request.form.get('songID', 0))
    objects = Escape.number(request.form.get('objects', 0))
    coins = limit_value(0, Escape.number(request.form.get('coins', 0)), 3)
    requested_stars = limit_value(0, Escape.number(request.form.get('requestedStars', 0)), 10)

    extra_string = Escape.text(request.form.get('extraString',"29_29_29_40_29_29_29_29_29_29_29_29_29_29_29_29"))
    level_string = Escape.text(request.form.get('levelString', ''))
    level_info = Escape.text(request.form.get('levelInfo', ''))

    unlisted = limit_value(0, Escape.number(request.form.get('unlisted2') or request.form.get('unlisted1') or request.form.get('unlisted', 0)), 2)
    is_ldm  = limit_value(0, Escape.number(request.form.get('ldm', '0')), 1)
    wt = Escape.number(request.form.get('wt', '0'))
    wt2 = Escape.number(request.form.get('wt2', '0'))
    settings_string = Escape.text(request.form.get('settingsString', ''))
    song_ids = Escape.multiple_ids(request.form.get('songIDs', ''))
    sfx_ids = Escape.multiple_ids(request.form.get('sfxIDs', ''))
    ts = Escape.number(request.form.get('ts', '0'))
    password = Escape.number(request.form.get('password', '1' if game_version > 21 else '0'))

    level_details = {
        'gameVersion': game_version,
        'binaryVersion': binary_version,
        'levelDesc': level_desc,
        'levelLength': level_length,
        'audioTrack': audio_track,
        'auto': auto,
        'original': original,
        'twoPlayer': two_player,
        'songID': song_id,
        'objects': objects,
        'coins': coins,
        'requestedStars': requested_stars,
        'extraString': extra_string,
        'levelInfo': level_info,
        'unlisted': unlisted,
        'isLDM': is_ldm,
        'wt': wt,
        'wt2': wt2,
        'settingsString': settings_string,
        'songIDs': song_ids,
        'sfxIDs': sfx_ids,
        'ts': ts,
        'password': password,
    }

    res = upload_level(db, person, level_id, level_name, level_string, level_details)

    if not res["success"]: return CommonError.InvalidRequest

    return res["levelID"]
