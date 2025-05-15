from lib.exploit_patch import Escape
from lib.enums import Action, CommonError
from lib.log import log
from lib.other import get_song_by_id, save_ng, return_song_string
from lib.security import Security
from flask import request

def do(db):
    person = Security.login_player(db, request)
    if not person["success"]: return CommonError.InvalidRequest
    
    song_id = Escape.number(request.form.get("songID", "-1"))

    song = get_song_by_id(db, song_id)
    if not song:
        song = save_ng(db, song_id)
        if not song: return CommonError

    if song["isDisabled"]: return CommonError.Disabled

    return return_song_string(db, song_id)
