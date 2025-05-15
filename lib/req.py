import requests

gj_headers = {
    "User-Agent": "", # don't set this (whe using RobTop's servers so Cloudflare don't block your request) (https://wyliemaster.github.io/gddocs/#/endpoints/generic?id=sending-requests)
}

extra_payload = {
    # 2.207
    "gameVersion": "22",
    "binaryVersion": "45",
}

class Secret:
    Common = "Wmfd2893gb7"
    Account = "Wmfv3899gc9"
    Level = "Wmfv2898gc9"

def request_data(url, endpoint, payload, secret, method="POST", headers=gj_headers, params={}, pre_add_payloads=True, follow_redirects=False, bytestring=False):
    final_payload = {**payload, **extra_payload} if pre_add_payload else payload
    if secret: final_payload.update({"secret": secret})
    resp = requests.request(method, url+"/"+endpoint, data=final_payload, params=params, headers=headers, allow_redirects=follow_redirects)
    return resp.status_code, (resp.content if bytestring else resp.content.encode())
