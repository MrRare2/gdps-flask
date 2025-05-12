from lib.enums import Action, BackupError, CommonError
from lib.log import log
from lib.security import Security
from lib.user import get_account_by_id, update_orbs_and_completed_levels
import xml.etree.ElementTree as ET
from flask import request
import os
import re

def do(db):
    person = Security.login_player(db, request)
    if not person["success"]:
        log(db, person, Action.FailedAccountBackup, person.get("userName", "Undefined"))
        return CommonError.InvalidRequest
    user_name = person["userName"]
    save = request.form.get("saveData")
    if not save: return BackupError.SomethingWentWrong

    account_id = person["accountID"]
    user_name = person["userName"]
    account = get_account_by_id(db, account_id)

    save_data = request.form['saveData']
    save_data_array = save_data.split(';')
    save_data_decoded = re.sub(r'(\r\n|\r|\n|( \t)|\t)', '', Security.decode_save_file(save_data_array[0]).decode())
    try:
        ET.fromstring(save_data_decoded)
    except ET.ParseError:
        log(db, person, Action.FailedAccountBackup, len(save_data))
        return CommonError.InvalidRequest

    if save_data_decoded.find('<key>') != -1:
        key_name = 'key'
        string_name = 'string'
    else:
        key_name = 'k'
        string_name = 's'

    save_data_decoded = save_data_decoded.replace('<' + key_name + '>GJA_002</' + key_name + '><' + string_name + '>' + account.get('password') + '</' + string_name + '>', '<' + key_name + '>GJA_002</' + key_name + '><' + string_name + '>:3</' + string_name + '>')
    save_data_decoded = save_data_decoded.replace(
        '<' + key_name + '>GJA_005</' + key_name + '><' + string_name + '>' +
        account.get('gjp2') + '</' + string_name + '>',
        '<' + key_name + '>GJA_005</' + key_name + '><' + string_name + '>:3</' + string_name + '>'
    )

    orbs_section = save_data_decoded.split(
        '</' + string_name + '><' + key_name + '>14</' + key_name + '><' + string_name + '>'
    )[1]
    orbs_str = orbs_section.split('</' + string_name + '>')[0]
    account_orbs = int(orbs_str) if orbs_str else 0

    levels_section = save_data_decoded.split(
        '<' + key_name + '>GS_value</' + key_name + '>'
    )[1]
    official_parts = levels_section.split(
        '</' + string_name + '><' + key_name + '>3</' + key_name + '><' + string_name + '>'
    )
    official_str = official_parts[1].split('</' + string_name + '>')[0]
    account_completed_official_levels = int(official_str) if official_str else 0

    tmp = levels_section.replace('<dict>', '</' + string_name + '>').replace('<d>', '</' + string_name + '>')
    online_parts = tmp.split(
        '</' + string_name + '><' + key_name + '>4</' + key_name + '><' + string_name + '>'
    )
    online_str = online_parts[1].split('</' + string_name + '>')[0]
    account_completed_online_levels = int(online_str) if online_str else 0

    account_levels = account_completed_official_levels + account_completed_online_levels

    levels_data_decoded = Security.decode_save_file(save_data_array[1])
    try:
        ET.fromstring(levels_data_decoded)
    except ET.ParseError:
        log(db, person, Action.FailedAccountBackup, len(save_data))
        return CommonError.InvalidRequest

    save_data = Security.encode_save_file(save_data_decoded) + ';' + save_data_array[1]
    # remove this when that above is properly implemented
    save_data = Security.encode_save_file(sre.sub(r'(\r\n|\r|\n|( \t)|\t)', '', Security.decode_save_file(save_data_array[0]).decode())) + ";" + save_data_array[1]

    update_orbs_and_completed_levels(db, account_id, account_orbs, account_levels)

    file_path = os.path.dirname(os.path.abspath(__file__))+'/../../data/accounts/'+str(account_id)
    if account.get('salt'):
        salt = account['salt']
        save_encrypted = Security.encrypt_data(save_data.encode(), salt)
        with open(file_path, 'w') as f:
            f.write(save_encrypted)
    else:
        with open(file_path, 'w') as f:
            f.write(save_data)

    log(db, person, Action.SuccessfulAccountBackup, user_name, os.path.getsize(file_path), account_orbs, account_levels)
    return CommonError.Success
