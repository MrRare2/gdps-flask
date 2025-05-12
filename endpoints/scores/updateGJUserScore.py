from lib.exploit_patch import Escape
from lib.enums import Action, CommonError
from lib.log import log
from lib.security import Security
from lib.user import *
from flask import request

def do(db):
    if "stars" not in request.form or "demons" not in request.form or "icon" not in request.form or "color1" not in request.form or "color2" not in request.form: return CommonError.InvalidRequest
    person = Security.login_player(db, request)
    if not person["success"]: return CommonError.InvalidRequest
    acc_id = person["accountID"]
    user_id = person["userID"]
    user_name = person["userName"]
    ip = person["IP"]

    # automod soon

    stars = Escape.number(request.form.get('stars'))
    demons = Escape.number(request.form.get('demons'))
    icon = Escape.number(request.form.get('icon'))
    color1 = Escape.number(request.form.get('color1'))
    color2 = Escape.number(request.form.get('color2'))
    game_version = Escape.number(request.form.get('gameVersion', 1))
    binary_version = Escape.number(request.form.get('binaryVersion', 1))
    coins = Escape.number(request.form.get('coins', 0))
    icon_type = Escape.number(request.form.get('iconType', 0))
    user_coins = Escape.number(request.form.get('userCoins', 0))
    special = Escape.number(request.form.get('special', 0))
    acc_icon = Escape.number(request.form.get('accIcon', 0))
    acc_ship = Escape.number(request.form.get('accShip', 0))
    acc_ball = Escape.number(request.form.get('accBall', 0))
    acc_bird = Escape.number(request.form.get('accBird', 0))
    acc_dart = Escape.number(request.form.get('accDart', 0))
    acc_robot = Escape.number(request.form.get('accRobot', 0))
    acc_glow = Escape.number(request.form.get('accGlow', 0))
    acc_spider = Escape.number(request.form.get('accSpider', 0))
    acc_explosion = Escape.number(request.form.get('accExplosion', 0))
    diamonds = Escape.number(request.form.get('diamonds', 0))
    moons = Escape.number(request.form.get('moons', 0))
    color3 = Escape.number(request.form.get('color3', 0))
    acc_swing = Escape.number(request.form.get('accSwing', 0))
    acc_jetpack = Escape.number(request.form.get('accJetpack', 0))
    dinfo = Escape.multiple_ids(request.form.get('dinfo', ''))
    dinfow = Escape.number(request.form.get('dinfow', 0))
    dinfog = Escape.number(request.form.get('dinfog', 0))
    sinfo = Escape.multiple_ids(request.form.get('sinfo', ''))
    sinfod = Escape.number(request.form.get('sinfod', 0))
    sinfog = Escape.number(request.form.get('sinfog', 0))

    user = get_user_by_id(db, user_id)

    if dinfo.strip():
        cursor = db.cursor(dictionary=True)
        query = """SELECT IFNULL(easyNormal, 0) as easyNormal,
        IFNULL(mediumNormal, 0) as mediumNormal,
        IFNULL(hardNormal, 0) as hardNormal,
        IFNULL(insaneNormal, 0) as insaneNormal,
        IFNULL(extremeNormal, 0) as extremeNormal,
        IFNULL(easyPlatformer, 0) as easyPlatformer,
        IFNULL(mediumPlatformer, 0) as mediumPlatformer,
        IFNULL(hardPlatformer, 0) as hardPlatformer,
        IFNULL(insanePlatformer, 0) as insanePlatformer,
        IFNULL(extremePlatformer, 0) as extremePlatformer
        FROM (
		(SELECT count(*) AS easyNormal FROM levels WHERE starDemonDiff = 3 AND levelLength != 5 AND levelID IN ("""+str(dinfo)+""") AND starDemon != 0) easyNormal
		JOIN (SELECT count(*) AS mediumNormal FROM levels WHERE starDemonDiff = 4 AND levelLength != 5 AND levelID IN ("""+str(dinfo)+""") AND starDemon != 0) mediumNormal
		JOIN (SELECT count(*) AS hardNormal FROM levels WHERE starDemonDiff = 0 AND levelLength != 5 AND levelID IN ("""+str(dinfo)+""") AND starDemon != 0) hardNormal
		JOIN (SELECT count(*) AS insaneNormal FROM levels WHERE starDemonDiff = 5 AND levelLength != 5 AND levelID IN ("""+str(dinfo)+""") AND starDemon != 0) insaneNormal
		JOIN (SELECT count(*) AS extremeNormal FROM  levels WHERE starDemonDiff = 6 AND levelLength != 5 AND levelID IN ("""+str(dinfo)+""") AND starDemon != 0) extremeNormal
		
		JOIN (SELECT count(*) AS easyPlatformer FROM levels WHERE starDemonDiff = 3 AND levelLength = 5 AND levelID IN ("""+str(dinfo)+""") AND starDemon != 0) easyPlatformer
		JOIN (SELECT count(*) AS mediumPlatformer FROM levels WHERE starDemonDiff = 4 AND levelLength = 5 AND levelID IN ("""+str(dinfo)+""") AND starDemon != 0) mediumPlatformer
		JOIN (SELECT count(*) AS hardPlatformer FROM levels WHERE starDemonDiff = 0 AND levelLength = 5 AND levelID IN ("""+str(dinfo)+""") AND starDemon != 0) hardPlatformer
		JOIN (SELECT count(*) AS insanePlatformer FROM levels WHERE starDemonDiff = 5 AND levelLength = 5 AND levelID IN ("""+str(dinfo)+""") AND starDemon != 0) insanePlatformer
		JOIN (SELECT count(*) AS extremePlatformer FROM levels WHERE starDemonDiff = 6 AND levelLength = 5 AND levelID IN ("""+str(dinfo)+""") AND starDemon != 0) extremePlatformer
        )"""
        cursor.execute(query)
        demons_count = cursor.fetchone()
        all_demons = demons_count["easyNormal"] + demons_count["mediumNormal"] + demons_count["hardNormal"] + demons_count["insaneNormal"] + demons_count["extremeNormal"] + demons_count["easyPlatformer"] + demons_count["mediumPlatformer"] + demons_count["hardPlatformer"] + demons_count["insanePlatformer"] + demons_count["extremePlatformer"] + dinfow + dinfog
        demons_count_diff = min(demons - all_demons, 3)
        dinfo = str(demons_count["easyNormal"] + demons_count_diff) + ',' + str(demons_count["mediumNormal"]) + ',' + str(demons_count["hardNormal"]) + ',' + str(demons_count["insaneNormal"]) + ',' + str(demons_count["extremeNormal"]) + ',' + str(demons_count["easyPlatformer"]) + ',' + str(demons_count["mediumPlatformer"]) + ',' + str(demons_count["hardPlatformer"]) + ',' + str(demons_count["insanePlatformer"]) + ',' + str(demons_count["extremePlatformer"]) + ',' + str(dinfow) + ',' + str(dinfog)
    if sinfo:
        sinfo = sinfo.split(',')
        stars_count = sinfo[0] + ',' + sinfo[1] + ',' + sinfo[2] + ',' + sinfo[3] + ',' + sinfo[4] + ',' + sinfo[5] + ',' + str(sinfod) + ',' + str(sinfog)
        platformer_count = sinfo[6] + ',' + sinfo[7] + ',' + sinfo[8] + ',' + sinfo[9] + ',' + sinfo[10] + ',' + sinfo[11] + ',0'

    cursor = db.cursor()
    cursor.execute(
        "UPDATE users SET gameVersion = %s, userName = %s, coins = %s, stars = %s, demons = %s, icon = %s, color1 = %s, color2 = %s, iconType = %s, userCoins = %s, special = %s, accIcon = %s, accShip = %s, accBall = %s, accBird = %s, accDart = %s, accRobot = %s, accGlow = %s, IP = %s, accSpider = %s, accExplosion = %s, diamonds = %s, moons = %s, color3 = %s, accSwing = %s, accJetpack = %s, dinfo = %s, sinfo = %s, pinfo = %s WHERE userID = %s",
        (
            game_version, user_name, coins, stars, demons, icon, color1, color2,
            icon_type, user_coins, special, acc_icon, acc_ship, acc_ball,
            acc_bird, acc_dart, acc_robot, acc_glow, ip, acc_spider,
            acc_explosion, diamonds, moons, color3, acc_swing, acc_jetpack,
            dinfo, stars_count, platformer_count, user_id
        )
    )

    stars_difference = stars - user['stars']
    coins_difference = coins - user['coins']
    demons_difference = demons - user['demons']
    user_coins_difference = user_coins - user['userCoins']
    diamonds_difference = diamonds - user['diamonds']
    moons_difference = moons - user['moons']

    log(db, person, Action.ProfileStatsChange, stars_difference, coins_difference, demons_difference, user_coins_difference, diamonds_difference, moons_difference)
    if game_version < 20 and not str(account_id).isnumeric() and (stars_difference + coins_difference + demons_difference + user_coins_difference + diamonds_difference + moons_difference) != 0:
        return CommonError.SubmitRestoreInfo

    return str(user_id)
