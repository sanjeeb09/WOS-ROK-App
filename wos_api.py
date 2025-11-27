import hashlib
import time
import os
import asyncio
import requests # Using standard requests for stability
from dotenv import load_dotenv

load_dotenv()

SECRET = os.getenv('WOS_SECRET') 
URL_PLAYER = 'https://wos-giftcode-api.centurygame.com/api/player'

HEADERS = {
    "accept": "application/json",
    "content-type": "application/x-www-form-urlencoded",
    "origin": "https://wos-giftcode.centurygame.com",
    "referer": "https://wos-giftcode.centurygame.com/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def _sign(raw_string):
    """Signs the raw query string directly."""
    return hashlib.md5((raw_string + SECRET).encode('utf-8')).hexdigest()

def _fetch_wos_sync(user_id):
    """Standard requests logic running in a thread."""
    t = int(time.time() * 1000)
    
    # Manually build the body to ensure order matches signature
    raw_data = f"fid={user_id}&time={t}"
    signature = _sign(raw_data)
    payload = f"sign={signature}&{raw_data}"
    
    try:
        response = requests.post(URL_PLAYER, data=payload, headers=HEADERS)
        return response.json()
    except Exception as e:
        print(f"[WOS Connection Error] {e}")
        return None

async def get_wos_profile(user_id):
    """Async wrapper for the sync function."""
    # Run the blocking request in a separate thread
    data = await asyncio.to_thread(_fetch_wos_sync, user_id)
    
    if data:
        # DEBUG: This will print the actual response in your terminal
        print(f"[WOS API DEBUG] Response: {data}")
        
        if data.get("msg") == "success":
            player_data = data.get("data", {})
            return {
                "name": player_data.get("nickname", "Unknown"),
                "kingdom": player_data.get("kid", "Unknown"),
                "profilePhoto": player_data.get("avatar_image", ""),
                "level": player_data.get("stove_lv", "Unknown") 
            }
        else:
            print(f"[WOS API Fail] Message: {data.get('msg')} | Error: {data.get('err_code')}")
            
    return None

async def redeem_wos_code(user_id, code):
    return {"msg": "Auto-Redeem unavailable for WOS (Captcha Required)."}