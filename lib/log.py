import time

def safe_int(val):
    try:
        return int(val)
    except (ValueError, TypeError):
        return 0

def log(db, person, type, val1="", val2="", val3="", val4="", val5="", val6=""):
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO actions (account, type, timestamp, value, value2, value3, value4, value5, value6, IP) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
        (
            person["accountID"],
            type,
            int(time.time()),
            val1,
            val2,
            safe_int(val3),
            safe_int(val4),
            safe_int(val5),
            safe_int(val6),
            person.get("IP", "")
        )
    )
    db.commit()
    return cursor.lastrowid

def log_mod(db, person, type, val1="", val2="", val3="", val4="", val5="", val6="", val7=""):
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO modactions (account, type, timestamp, value, value2, value3, value4, value5, value6, value7, IP) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
        (
            person["accountID"],
            type,
            int(time.time()),
            val1,
            val2,
            safe_int(val3),
            val4,
            safe_int(val5),
            safe_int(val6),
            val7,
            person.get("IP", "")
        )
    )
    db.commit()
    return cursor.lastrowid
