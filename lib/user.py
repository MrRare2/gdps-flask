from .ban import get_banned_people_query 
from .enums import Action, LevelUploadError
from .ip import IP
from .log import log
from . import other
import os
import time

def get_user_by_id(db, user_id):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE userID = %s", (user_id,))
    row = cursor.fetchone()
    return row if row else {**{k: "0" for k in ["isRegistered","userID","extID","userName","stars","demons","icon","color1","color2","color3","iconType","coins","userCoins","special","gameVersion","secret","accIcon","accShip","accBall","accBird","accDart","accRobot","accGlow","accSwing","accJetpack","dinfo","sinfo","pinfo","creatorPoints","IP","lastPlayed","diamonds","moons","orbs","completedLvls","accSpider","accExplosion","chest1time","chest2time","chest1count","chest2count","isBanned","isCreatorBanned"]}, "extID": 0, "userName": "Player", "userID": user_id}

def get_account_by_user_name(db, user_name):
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM accounts WHERE userName LIKE %s LIMIT 1",
        (user_name,)
    )
    return cursor.fetchone()

def get_account_by_id(db, account_id):
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM accounts WHERE accountID = %s",
        (account_id,)
    )
    return cursor.fetchone()

def get_account_by_email(db, email):
    cursor = db.cursor()
    cursor.execute(
        "SELECT * FROM accounts WHERE email LIKE %s ORDER BY registerDate ASC LIMIT 1",
        (email,)
    )
    return cursor.fetchone()

def get_user_id(db, account_id):
    from .accounts import create_user
    cursor = db.cursor()
    cursor.execute("SELECT userID FROM users WHERE extID = %s", (account_id,))
    row = cursor.fetchone()
    user_id = row[0] if row else None

    if not user_id:
        account = get_account_by_id(db, account_id)
        if not account:
            return False

        ip = IP.get_ip()
        user_name = account['userName']
        user_id = create_user(db, user_name, account_id, ip) or 0

    return user_id

def get_account_id(db, user_id):
    cursor = db.cursor()
    cursor.execute("SELECT extID FROM users WHERE userID = %s", (user_id,))
    row = cursor.fetchone()
    return row[0] if row else None

def get_person_roles(db, person):
    if person['accountID'] == 0 or person['userID'] == 0: return False

    role_ids = []
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT roleID FROM roleassign WHERE accountID = %s", (person["accountID"],))
    rows = cursor.fetchall()

    role_ids = [str(row['roleID']) for row in rows]
    role_ids.append('0')

    cursor.execute(f"SELECT * FROM roles WHERE roleID IN ({','.join(role_ids)}) OR isDefault != 0 ORDER BY priority DESC, isDefault ASC");
    roles = cursor.fetchall()

    return roles

def get_person_comment_appearance(db, person):
    if person["accountID"] == 0 or person["userID"] == 0: return {"commentsExtraText": "", "modBadgeLevel": 0, "commentColor": "255,255,255"}

    roles = get_person_roles(db, person)

    if not roles:
        role_appearance = {"commentsExtraText": "", "modBadgeLevel": 0, "commentColor": "255,255,255"}
    else:
        role_appearance = {"commentsExtraText": roles[0].get("commentsExtraText", ""), "modBadgeLevel": roles[0]["modBadgeLevel"], "commentColor": roles[0]["commentColor"]}

    return role_appearance

def update_orbs_and_completed_levels(db, account_id, orbs, levels):
    cursor = db.cursor()
    cursor.execute("UPDATE users SET orbs = %s, completedLvls = %s WHERE extID = %s", (orbs, levels, account_id))
    db.commit()

def get_daily_chests(db, user_id):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT chest1time, chest2time, chest1count, chest2count FROM users WHERE userID = %s", (user_id,))
    return cursor.fetchone()

def retrieve_daily_chest(db, user_id, reward_type):
    cursor = db.cursor()
    cursor.execute("UPDATE users SET chest"+str(reward_type)+"time = %s, chest"+str(reward_type)+"count = chest"+str(reward_type)+"count + 1 WHERE userID = %s", (time.time(), user_id,))
    db.commit()
    return True

def is_person_blocked(db, account_id, target_id):
    if account_id == target_id: return False
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT count(*) FROM blocks WHERE (person1 = %s AND person2 = %s) OR (person1 = %s AND person2 = %s)", (account_id, target_id, target_id, account_id))
    return cursor.fetchone()["count(*)"] > 0


def is_friends(db, account_id, target_id):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT count(*) FROM friendships WHERE (person1 = %s AND person2 = %s) OR (person1 = %s AND person2 = %s)", (account_id, target_id, target_id, account_id))
		
    return cursor.fetchone()["count(*)"] > 0

def get_friend_request(db, acc_id, target_acc_id):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM friendreqs WHERE accountID = %s AND toAccountID = %s", (acc_id, target_acc_id))

    return cursor.fetchone()

def make_clan_username(db, account_id):
    user = get_user_by_id(db, account_id)
    return user["userName"]

def get_rank(x, y, z):
    return 1 # implement soon

def return_user_string(db, user):
    user['userName'] = make_clan_username(db, user['extID'])
    return (
        "1:" + user['userName'] +
        ":2:" + str(user['userID']) +
        ":13:" + str(user['coins']) +
        ":17:" + str(user.get('userCoins', 0)) +
        ":10:" + str(user.get('color1', 0)) +
        ":11:" + str(user.get('color2', 0)) +
        ":51:" + str(user.get('color3', 0)) +
        ":3:" + str(user.get('stars', 0)) +
        ":46:" + str(user.get('diamonds', 0)) +
        ":52:" + str(user.get('moons', 0)) +
        ":4:" + str(user.get('demons', 0)) +
        ":8:" + str(user.get('creatorPoints', 0)) +
        ":18:" + str(user.get('messagesState', 0)) +
        ":19:" + str(user.get('friendRequestsState', 0)) +
        ":50:" + str(user.get('commentsState', 0)) +
        ":20:" + user.get('youtubeurl', '') +
        ":21:" + str(user.get('accIcon', 0)) +
        ":22:" + str(user.get('accShip', 0)) +
        ":23:" + str(user.get('accBall', 0)) +
        ":24:" + str(user.get('accBird', 0)) +
        ":25:" + str(user.get('accDart', 0)) +
        ":26:" + str(user.get('accRobot', 0)) +
        ":28:" + str(user.get('accGlow', 0)) +
        ":43:" + str(user.get('accSpider', 0)) +
        ":48:" + str(user.get('accExplosion', 0)) +
        ":53:" + str(user.get('accSwing', 0)) +
        ":54:" + str(user.get('accJetpack', 0)) +
        ":30:" + str(user.get('rank', 0)) +
        ":16:" + str(user['extID']) +
        ":31:" + str(user.get('friendsState', 0)) +
        ":44:" + user.get('twitter', '') +
        ":45:" + user.get('twitch', '') +
        ":49:" + str(user.get('badge', 0)) +
        ":55:" + user.get('dinfo', '') +
        ":56:" + user.get('sinfo', '') +
        ":57:" + user.get('pinfo', '') + user.get('incomingRequestText', "") +
        ":29:" + str(user.get('isRegistered', 0))
    )

def return_friendships_string(db, person, user, is_blocks):
    if not is_blocks:
        if user['person2'] == user['extID']:
            user_new = user['isNew1']
        else:
            user_new = user['isNew2']
        can_message = 0 if can_send_message(person, user['extID']) else 2
    else:
        user_new = user.get('isNew')
        can_message = None
    user['userName'] = make_clan_username(db, user['extID'])
    return (
        "1:" + user['userName'] +
        ":2:" + str(user['userID']) +
        ":9:" + user['icon'] +
        ":10:" + user['color1'] +
        ":11:" + user['color2'] +
        ":14:" + user['iconType'] +
        ":15:" + user['special'] +
        ":16:" + str(user['extID']) +
        ("" if is_blocks else ":18:" + str(can_message)) +
        ":41:" + str(user_new)
    )

def return_friend_requests_string(db, person, user):
    user['userName'] = make_clan_username(db, user['extID'])
    return (
        "1:" + user['userName'] +
        ":2:" + str(user['userID']) +
        ":9:" + user['icon'] +
        ":10:" + user['color1'] +
        ":11:" + user['color2'] +
        ":14:" + user['iconType'] +
        ":15:" + user['special'] +
        ":16:" + str(user['extID']) +
        ":32:" + str(user['ID']) +
        ":35:" + user['comment'] +
        ":41:" + str(user['isNew']) +
        ":37:" + str(user['uploadTime'])
    )

def get_leaderboard(db, type, person, moderators_list_in_global, leaderboard_min_stars, count):
    account_id = person["accountID"]
    user_id = person["userID"]
    user_name = person["userName"]
    user = get_user_by_id(db, user_id)
    rank = 0
    cursor = db.cursor(dictionary=True)
    if type == 'top':
        query_text = get_banned_people_query(db, 0, True)
        sql = "SELECT * FROM users WHERE " + query_text + " stars + moons >= %s ORDER BY stars + moons DESC, userName ASC LIMIT 100"
        cursor.execute(sql, (leaderboard_min_stars,))
    elif type == 'creators':
        query_text = get_banned_people_query(db, 1, True)
        sql = "SELECT * FROM users WHERE " + query_text + " creatorPoints > 0 ORDER BY creatorPoints DESC, userName ASC LIMIT 100"
        cursor.execute(sql)
    elif type == 'relative':
        if moderators_list_in_global:
            sql = (
                "SELECT * FROM users"
                " INNER JOIN roleassign ON "
                "(users.extID = roleassign.person AND roleassign.personType = 0) OR "
                "(users.userID = roleassign.person AND roleassign.personType = 1)"
                " INNER JOIN roles ON roleassign.roleID = roles.roleID"
                " ORDER BY roles.priority DESC, users.userName ASC"
            )
            cursor.execute(sql)
        else:
            query_text = get_banned_people_query(db, 0, True)
            half = count // 2
            sql = (
                "SELECT leaderboards.* FROM ("
                "(SELECT * FROM users WHERE " + query_text + " stars + moons <= %s ORDER BY stars + moons DESC LIMIT " + str(half) + ")"
                " UNION "
                "(SELECT * FROM users WHERE " + query_text + " stars + moons >= %s ORDER BY stars + moons ASC LIMIT " + str(half) + ")"
                ") as leaderboards"
                " ORDER BY leaderboards.stars + leaderboards.moons DESC, leaderboards.userName ASC"
            )
            total = user["stars"] + user["moons"]
            cursor.execute(sql, (total, total))
            rank = max(0, get_user_rank(db, user["stars"], user["moons"], user_name) - half)
    elif type == 'friends':
        friends = get_friends(account_id)
        friends.append(account_id)
        friends_string = "'" + "','".join(friends) + "'"
        sql = "SELECT * FROM users WHERE extID IN (" + friends_string + ") ORDER BY stars + moons DESC, userName ASC"
        cursor.execute(sql)
    elif type == 'week':
        query_text = get_banned_people_query(db, 0, True)
        sql = (
            "SELECT users.*, SUM(actions.value) AS stars, SUM(actions.value2) AS coins, SUM(actions.value3) AS demons"
            " FROM actions"
            " INNER JOIN users ON actions.account = users.extID"
            " WHERE type = '9' AND " + query_text + " timestamp > %s AND stars > 0"
            " GROUP BY account ORDER BY stars DESC, userName ASC LIMIT 100"
        )
        cursor.execute(sql, (int(time.time()) - 604800,))
    result = cursor.fetchall()
    return {"rank": rank, "leaderboard": result}

def is_able_to_upload_level(db, person, level_name, level_desc):
    # Must be logged in
    if person['accountID'] == 0 or person['userID'] == 0:
        return {'success': False}

    user_id = person['userID']
    ip = person['IP']

    # Check bans
    if Library.get_person_ban(db, person, 2):
        return {'success': False, 'error': CommonError.Banned}

    # Global rate limit
    if not Security.check_rate_limits(person, 0):
        return {'success': False, 'error': LevelUploadError.TooFast}

    # Per-user rate limit
    if not Security.check_rate_limits(person, 1):
        return {'success': False, 'error': LevelUploadError.TooFast}

    # Filter violations in name or description
    if (Security.check_filter_violation(person, level_name, 3) or
        Security.check_filter_violation(person, level_desc, 3)):
        return {'success': False, 'error': CommonError.Filter}

    # Automod global disable
    if Automod.is_levels_disabled(0):
        return {'success': False, 'error': CommonError.Automod}

    return {'success': True}


def upload_level(db, person, level_id, level_name, level_string, level_details):
    if person['accountID'] == 0 or person['userID'] == 0:
        return {'success': False, 'error': LoginError.WrongCredentials}

    account_id = person['accountID']
    user_id = person['userID']
    ip = person['IP']

    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT updateLocked, starStars "
        "FROM levels "
        "WHERE levelID = %s AND userID = %s AND isDeleted = 0",
        (level_id, user_id)
    )
    existing = cursor.fetchone()

    if existing:
        if (existing['updateLocked'] or
            (existing['starStars'] > 0)
        ):
            return {'success': False, 'error': LevelUploadError.UploadingDisabled}

        try:
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'levels', str(level_id)), 'w') as f:
                f.write(level_string)
        except IOError:
            return {'success': False, 'error': LevelUploadError.FailedToWriteLevel}

        cursor.execute(
            """
            UPDATE levels SET
              gameVersion   = %(gameVersion)s,
              binaryVersion = %(binaryVersion)s,
              levelDesc     = %(levelDesc)s,
              levelVersion  = levelVersion + 1,
              levelLength   = %(levelLength)s,
              audioTrack    = %(audioTrack)s,
              auto          = %(auto)s,
              original      = %(original)s,
              twoPlayer     = %(twoPlayer)s,
              songID        = %(songID)s,
              objects       = %(objects)s,
              coins         = %(coins)s,
              requestedStars= %(requestedStars)s,
              extraString   = %(extraString)s,
              levelString   = "",
              levelInfo     = %(levelInfo)s,
              unlisted      = %(unlisted)s,
              IP            = %(IP)s,
              isLDM         = %(isLDM)s,
              wt            = %(wt)s,
              wt2           = %(wt2)s,
              settingsString= %(settingsString)s,
              songIDs       = %(songIDs)s,
              sfxIDs        = %(sfxIDs)s,
              ts            = %(ts)s,
              password      = %(password)s,
              updateDate    = %(timestamp)s
            WHERE levelID = %(levelID)s
            """,
            {
                **level_details,
                'levelID': level_id,
                'IP': ip,
                'timestamp': int(time.time()),
            }
        )
        db.commit()

        log(db, person, Action.LevelChange, level_name, level_details['levelDesc'], level_id)
        return {'success': True, 'levelID': str(level_id)}

    cursor.execute(
        "SELECT levelID, updateLocked, starStars "
        "FROM levels "
        "WHERE levelName LIKE %s AND userID = %s AND isDeleted = 0 "
        "ORDER BY levelID DESC LIMIT 1",
        (level_name, user_id)
    )
    existing = cursor.fetchone()

    if existing:
        lvl_id = existing['levelID']
        if (existing['updateLocked'] or
            (not rated_levels_updates
             and existing['starStars'] > 0
             and lvl_id not in rated_levels_updates_exceptions)
        ):
            return {'success': False, 'error': LevelUploadError.UploadingDisabled}

        try:
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'levels', str(lvl_id)), 'w') as f:
                f.write(level_string)
        except IOError:
            return {'success': False, 'error': LevelUploadError.FailedToWriteLevel}

        cursor.execute(
            """
            UPDATE levels SET
              gameVersion   = %(gameVersion)s,
              binaryVersion = %(binaryVersion)s,
              levelDesc     = %(levelDesc)s,
              levelVersion  = levelVersion + 1,
              levelLength   = %(levelLength)s,
              audioTrack    = %(audioTrack)s,
              auto          = %(auto)s,
              original      = %(original)s,
              twoPlayer     = %(twoPlayer)s,
              songID        = %(songID)s,
              objects       = %(objects)s,
              coins         = %(coins)s,
              requestedStars= %(requestedStars)s,
              extraString   = %(extraString)s,
              levelString   = "",
              levelInfo     = %(levelInfo)s,
              unlisted      = %(unlisted)s,
              IP            = %(IP)s,
              isLDM         = %(isLDM)s,
              wt            = %(wt)s,
              wt2           = %(wt2)s,
              settingsString= %(settingsString)s,
              songIDs       = %(songIDs)s,
              sfxIDs        = %(sfxIDs)s,
              ts            = %(ts)s,
              password      = %(password)s,
              updateDate    = %(timestamp)s
            WHERE levelID = %(levelID)s AND isDeleted = 0
            """,
            {
                **level_details,
                'levelID': lvl_id,
                'IP': ip,
                'timestamp': int(time.time()),
            }
        )
        db.commit()

        log(db, Action.LevelChange, level_name, level_details['levelDesc'], lvl_id)
        return {'success': True, 'levelID': str(lvl_id)}

    timestamp = int(time.time())
    new_filename = f"{user_id}_{timestamp}"
    try:
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'levels', new_filename), 'w') as f:
            f.write(level_string)
    except IOError:
        return {'success': False, 'error': LevelUploadError.FailedToWriteLevel}

    cursor.execute(
        """
        INSERT INTO levels
          (userID, extID, gameVersion, binaryVersion, levelName,
           levelDesc, levelVersion, levelLength, audioTrack, auto,
           original, twoPlayer, songID, objects, coins, requestedStars,
           extraString, levelString, levelInfo, unlisted, unlisted2, IP,
           isLDM, wt, wt2, settingsString, songIDs, sfxIDs, ts, password,
           uploadDate, updateDate,
           userName, secret, hostname)
        VALUES
          (%s, %s, %s, %s, %s,
           %s, 1, %s, %s, %s,
           %s, %s, %s, %s, %s, %s,
           %s, '', %s, %s, %s, %s,
           %s, %s, %s, %s, %s,
           %s, %s, %s, %s, 0,
           %s, %s, %s)
        """,
        (
            user_id, account_id,
            level_details['gameVersion'],
            level_details['binaryVersion'],
            level_name,
            level_details['levelDesc'],
            level_details['levelLength'],
            level_details['audioTrack'],
            level_details['auto'],
            level_details['original'],
            level_details['twoPlayer'],
            level_details['songID'],
            level_details['objects'],
            level_details['coins'],
            level_details['requestedStars'],
            level_details['extraString'],
            level_details['levelInfo'],
            level_details['unlisted'],
            level_details['unlisted'],
            ip,
            level_details['isLDM'],
            level_details['wt'],
            level_details['wt2'],
            level_details['settingsString'],
            level_details['songIDs'],
            level_details['sfxIDs'],
            level_details['ts'],
            level_details['password'],
            timestamp,
            person["userName"],
            get_account_by_id(db, account_id)["auth"],
            ip,
        )
    )
    db.commit()

    new_level_id = cursor.lastrowid
    os.rename(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'levels', new_filename),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'levels', str(new_level_id))
    )

    log(db, person, Action.LevelUpload, level_name, level_details['levelDesc'], new_level_id)

    return {'success': True, 'levelID': str(new_level_id)}

def get_friends(db, acc_id):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT person1, person2 FROM friendships WHERE person1 = %s OR person2 = %s", (acc_id, acc_id))
    friends = cursor.fetchall()
    ret = []
    for friend in friends: ret.append(friend["person1"] if friend["person2"] == acc_id else friend["person1"])

    return ret

def is_account_admin(db, person):
    return bool(get_account_by_id(db, person["accountID"]).get("isAdmin", False))

def check_perm(db, person, permission):
    if person['accountID'] == 0 or person['userID'] == 0: return False

    if is_account_admin(db, person): return True

    roles = get_person_roles(db, person)
    if not roles: return False

    for each in roles:
        if each[permission] == 1: return True
        elif each[permission] == 2: return False

    return False
