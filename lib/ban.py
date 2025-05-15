from .other import *
import time

def get_person_ban(db, person, ban_type):
    return False
    # broken implementation
    account_id = person['accountID']
    user_id = person['userID']
    ip = convert_ip_for_searching(person['IP'])

    cursor = db.cursor()
    cursor.execute(
        'SELECT * FROM bans '
        'WHERE ((person = %s AND personType = 0) '
        'OR (person = %s AND personType = 1) '
        'OR (person = %s AND personType = 2)) '
        'AND banType = %s AND isActive = 1 '
        'ORDER BY expires DESC',
        (account_id, user_id, ip, ban_type)
    )
    ban = cursor.fetchone()

    if ban and ban['expires'] > int(time.time()):
        return ban
    return False

def get_banned_people_query(db, type, add_separator=False):
    query_array = []
    banned_people = get_all_banned_people(db, type)
    ext_ids_string = "','".join(banned_people['accountIDs'])
    user_ids_string = "','".join(banned_people['userIDs'])
    banned_ips_string = "|".join(banned_people['IPs'])
    if ext_ids_string:
        query_array.append("extID NOT IN ('" + ext_ids_string + "')")
    if user_ids_string:
        query_array.append("userID NOT IN ('" + user_ids_string + "')")
    if banned_ips_string:
        query_array.append("IP NOT REGEXP '" + banned_ips_string + "'")
    if query_array:
        query_text = '(' + ' AND '.join(query_array) + ')' + (' AND' if add_separator else '')
    else:
        query_text = ''
    return query_text
