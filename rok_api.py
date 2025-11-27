import hashlib
import time
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()
SECRET = os.getenv('ROK_SECRET') 
URL_PLAYER = 'https://kingshot-giftcode.centurygame.com/api/player'
URL_REDEEM = 'https://kingshot-giftcode.centurygame.com/api/gift_code'
HEADERS = {
    "Content-Type": "application/x-www-form-urlencoded", 
    "Origin": "https://ks-giftcode.centurygame.com", 
    "Referer": "https://ks-giftcode.centurygame.com/", 
    "User-Agent": "Mozilla/5.0"
}

def _sign(params):
    sorted_keys = sorted(params.keys())
    query_list = [f"{k}={params[k]}" for k in sorted_keys]
    query_string = "&".join(query_list)
    raw = query_string + SECRET
    return hashlib.md5(raw.encode('utf-8')).hexdigest()

def get_rok_profile(user_id):
    t = int(time.time() * 1000)
    params = {"fid": str(user_id), "time": str(t)}
    params["sign"] = _sign(params)
    try:
        res = requests.post(URL_PLAYER, data=params, headers=HEADERS)
        data = res.json()
        
        if data.get("msg") == "success":
            player_data = data.get("data", {})
            
            # DEBUG: Print raw data to confirm structure if needed
            print(f"[ROK API DEBUG] Data found: {player_data}")

            # FIX: The log showed 'stove_lv' holds the castle level
            lvl = player_data.get("stove_lv")
            if lvl is None:
                lvl = player_data.get("level") # Fallback just in case
            
            return {
                "name": player_data.get("nickname", "Unknown"), 
                "kingdom": player_data.get("kid", "Unknown"), 
                "profilePhoto": player_data.get("avatar_image", ""), 
                "level": str(lvl) if lvl is not None else "Unknown"
            }
        return None
    except Exception as e: 
        print(f"[ROK Error] {e}")
        return None

def redeem_rok_code(user_id, code):
    t = int(time.time() * 1000)
    params = {"captcha_code": "", "cdk": str(code), "fid": str(user_id), "time": str(t)}
    params["sign"] = _sign(params)
    try:
        res = requests.post(URL_REDEEM, data=params, headers=HEADERS)
        return res.json()
    except Exception as e: return {"msg": f"Connection Error: {str(e)}"}