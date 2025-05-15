from lib.exploit_patch import Escapr
from flask import request

def do(db):
    file = request.args.get("request", "").strip()
    if file in ["musiclibrary.dat", "musiclibrary_02.dat"]:
        dat_file = "standalone.dat" if requests.args.get("dashboard") else "gdps.dat"
        # not implemented yet
        return "-1"
    elif file in ["musiclibrary_version.txt", "musiclibrary_version_02.txt"]:
        # not implemented yet
        return "-1"
    else:
        return "-1"

