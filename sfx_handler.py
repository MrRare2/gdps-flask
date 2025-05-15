from lib.exploit_patch import Escape
from flask import request

def do(db, file):
    file = file.strip()
    if file in ["sfxlibrary.dat"]:
        dat_file = "standalone.dat" if requests.args.get("dashboard") else "gdps.dat"
        # not implemented yet
        return "-1"
    elif file in ["sfxlibrary_version.txt"]:
        # not implemented yet
        return "-1"
    else:
        return "-1"

