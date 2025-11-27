import os
import json
import google.generativeai as genai
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

# Configure Google Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# ----------------------------------------------------------
# HARD-CODED REWARD TABLES
# ----------------------------------------------------------
REWARDS_ROK = [
    (38_400_000_000, "🔨18, 📦3, 📜15, 🥈100K | 🍞/🪵41.4M, 🪨8.2M, 🔩2.0M"),
    (19_200_000_000, "🔨17, 📦3, 📜14, 🥈95K | 🍞/🪵39.4M, 🪨7.8M, 🔩1.9M"),
    (9_600_000_000,  "🔨16, 📦3, 📜14, 🥈90K | 🍞/🪵37.5M, 🪨7.5M, 🔩1.8M"),
    (4_800_000_000,  "🔨15, 📦3, 📜13, 🥈85K | 🍞/🪵35.8M, 🪨7.1M, 🔩1.7M"),
    (2_400_000_000,  "🔨14, 📦3, 📜13, 🥈80K | 🍞/🪵34.1M, 🪨6.8M, 🔩1.7M"),
    (1_200_000_000,  "🔨13, 📦3, 📜12, 🥈75.6K | 🍞/🪵32.2M, 🪨6.4M, 🔩1.6M"),
    (635_000_000,    "🔨12, 📦2, 📜12, 🥈70K | 🍞/🪵29.9M, 🪨5.9M, 🔩1.5M"),
    (330_000_000,    "🔨11, 📦2, 📜11, 🥈65K | 🍞/🪵27.7M, 🪨5.5M, 🔩1.3M"),
    (175_000_000,    "🔨10, 📦2, 📜11, 🥈60K | 🍞/🪵25.5M, 🪨5.1M, 🔩1.2M"),
    (90_000_000,     "🔨9, 📦2, 📜10, 🥈55K | 🍞/🪵23.2M, 🪨4.6M, 🔩1.1M"),
    (47_000_000,     "🔨8, 📦2, 📜10, 🥈50K | 🍞/🪵21.0M, 🪨4.2M, 🔩1.0M"),
    (20_500_000,     "🔨7, 📦2, 📜9, 🥈47K | 🍞/🪵19.2M, 🪨3.8M, 🔩968K"),
    (8_900_000,      "🔨6, 📦2, 📜9, 🥈43K | 🍞/🪵17.3M, 🪨3.4M, 🔩874K"),
    (3_900_000,      "🔨5, 📦2, 📜8, 🥈40K | 🍞/🪵15.4M, 🪨3.0M, 🔩781K"),
    (1_700_000,      "🔨4, 📦2, 📜8, 🥈35K | 🍞/🪵13.8M, 🪨2.7M, 🔩687K"),
    (745_000,        "🔨3, 📦2, 📜7, 🥈30K | 🍞/🪵11.7M, 🪨2.3M, 🔩593K"),
    (325_000,        "🔨3, 📦1, 📜7, 🥈26K | 🍞/🪵9.9M, 🪨1.9M, 🔩499K"),
    (145_000,        "🔨2, 📦1, 📜6, 🥈22K | 🍞/🪵8.0M, 🪨1.6M, 🔩406K"),
    (62_500,         "🔨2, 📦1, 📜6, 🥈18.5K | 🍞/🪵6.1M, 🪨1.2M, 🔩312K"),
    (27_500,         "🔨1, 📦1, 📜5, 🥈14.5K | 🍞/🪵4.3M, 🪨867K, 🔩218K"),
    (12_000,         "🔨1, 📦1, 📜5, 🥈10K | 🍞/🪵2.4M, 🪨495.5K, 🔩125K"),
    (8_000,          "🔨1, 📦1, 📜4, 🥈9K | 🍞/🪵1.9M, 🪨396.5K, 🔩100K"),
    (5_000,          "🔨1, 📦1, 📜4, 🥈8K | 🍞/🪵1.4M, 🪨297.5K, 🔩75K"),
    (2_500,          "🔨1, 📦1, 📜3, 🥈7K | 🍞/🪵991.5K, 🪨198.5K, 🔩50K"),
    (0,              "🔨1, 📦1, 📜3, 🥈5.5K | 🍞/🪵495.5K, 🪨99K, 🔩25K")
]

REWARDS_WOS = [
    (38_400_000_000, "🪨🔨17, 🧩5, ⚙️22, 🛡️100K | 🍖/🪵41M, 🌑8.2M, ⛏️2.0M"),
    (19_200_000_000, "🪨🔨16, 🧩5, ⚙️21, 🛡️95K | 🍖/🪵39M, 🌑7.8M, ⛏️1.9M"),
    (9_600_000_000,  "🪨🔨15, 🧩5, ⚙️20, 🛡️90K | 🍖/🪵37M, 🌑7.5M, ⛏️1.8M"),
    (4_800_000_000,  "🪨🔨14, 🧩5, ⚙️19, 🛡️85K | 🍖/🪵35M, 🌑7.1M, ⛏️1.7M"),
    (2_400_000_000,  "🪨🔨13, 🧩5, ⚙️18, 🛡️80K | 🍖/🪵34M, 🌑6.8M, ⛏️1.7M"),
    (1_200_000_000,  "🪨🔨12, 🧩5, ⚙️17, 🛡️75.6K | 🍖/🪵32M, 🌑6.4M, ⛏️1.6M"),
    (635_000_000,    "🪨🔨11, 🧩5, ⚙️16, 🛡️70K | 🍖/🪵29M, 🌑5.9M, ⛏️1.5M"),
    (330_000_000,    "🪨🔨10, 🧩5, ⚙️15, 🛡️65K | 🍖/🪵27M, 🌑5.5M, ⛏️1.3M"),
    (175_000_000,    "🪨🔨9, 🧩5, ⚙️14, 🛡️60K | 🍖/🪵25M, 🌑5.1M, ⛏️1.2M"),
    (90_000_000,     "🪨🔨8, 🧩5, ⚙️13, 🛡️55K | 🍖/🪵23M, 🌑4.6M, ⛏️1.1M"),
    (47_000_000,     "🪨🔨7, 🧩5, ⚙️12, 🛡️50K | 🍖/🪵21M, 🌑4.2M, ⛏️1.0M"),
    (20_500_000,     "🪨🔨6, 🧩5, ⚙️11, 🛡️47K | 🍖/🪵19M, 🌑3.8M, ⛏️968K"),
    (8_900_000,      "🪨🔨5, 🧩5, ⚙️10, 🛡️43K | 🍖/🪵17M, 🌑3.4M, ⛏️874K"),
    (3_900_000,      "🪨🔨4, 🧩5, ⚙️9, 🛡️40K | 🍖/🪵15M, 🌑3.0M, ⛏️781K"),
    (1_700_000,      "🪨🔨3, 🧩5, ⚙️8, 🛡️35K | 🍖/🪵13M, 🌑2.7M, ⛏️687K"),
    (745_000,        "🪨🔨2, 🧩5, ⚙️7, 🛡️30K | 🍖/🪵11M, 🌑2.3M, ⛏️593K"),
    (325_000,        "🪨🔨2, 🧩5, ⚙️6, 🛡️26K | 🍖/🪵9.9M, 🌑1.9M, ⛏️499K"),
    (145_000,        "🧩5, ⚙️5, 🛡️22K | 🍖/🪵8.0M, 🌑1.6M, ⛏️406K"),
    (62_500,         "🧩5, ⚙️4, 🛡️18K | 🍖/🪵6.1M, 🌑1.2M, ⛏️312K"),
    (27_500,         "🧩5, ⚙️4, 🛡️14K | 🍖/🪵4.3M, 🌑867K, ⛏️218K"),
    (12_000,         "🧩5, ⚙️3, 🛡️10K | 🍖/🪵2.4M, 🌑495.5K, ⛏️125K"),
    (8_000,          "🧩5, ⚙️3, 🛡️9K | 🍖/🪵1.9M, 🌑396.5K, ⛏️100K"),
    (5_000,          "🧩5, ⚙️2, 🛡️8K | 🍖/🪵1.4M, 🌑297.5K, ⛏️75K"),
    (2_500,          "🧩5, ⚙️2, 🛡️7K | 🍖/🪵991.5K, 🌑198.5K, ⛏️50K"),
    (0,              "🧩5, ⚙️2, 🛡️5.5K | 🍖/🪵495.5K, 🌑99K, ⛏️25K")
]

# ----------------------------------------------------------
# AI VISION FUNCTION
# ----------------------------------------------------------
async def ocr_file(filepath: str = None, file_bytes: bytes = None) -> List[Dict]:
    """
    Uses Google Gemini Vision to extract leaderboard data.
    Tries multiple model versions to ensure compatibility.
    """
    # Prepare image data
    image_part = None
    if filepath:
        with open(filepath, "rb") as f:
            image_part = {"mime_type": "image/png", "data": f.read()}
    elif file_bytes:
        image_part = {"mime_type": "image/png", "data": file_bytes}
        
    if not image_part: return []

    # 🚀 TRY MODELS IN ORDER (Based on your available list)
    # Using 2.0 Flash as it is the most modern and fast one you have access to.
    models_to_try = [
        'models/gemini-2.0-flash', 
        'models/gemini-2.0-flash-exp', 
        'models/gemini-flash-latest'
    ]
    
    for model_name in models_to_try:
        try:
            print(f"✨ [Gemini] Sending image to {model_name}...")
            model = genai.GenerativeModel(model_name)
            
            prompt = """
            Analyze this game leaderboard image. 
            Extract a list of players. For each player row found:
            1. Extract the Name (string). Ignore clan tags like [ABC] if possible, but keep the main name.
            2. Extract the Damage/Points (integer). Convert 'M' to millions, 'B' to billions, 'K' to thousands. Remove commas.
            
            Return ONLY valid JSON format like this:
            [
                {"name": "PlayerName", "damage": 12345678},
                {"name": "AnotherPlayer", "damage": 500000}
            ]
            Do not include markdown formatting. Just the raw JSON string.
            """

            response = await model.generate_content_async([prompt, image_part])
            text_response = response.text.strip()
            
            # Clean up potential markdown
            if text_response.startswith("```"):
                text_response = text_response.strip("`").replace("json\n", "").replace("json", "")

            # Parse JSON
            players = json.loads(text_response)
            return players # If successful, return and stop trying other models

        except Exception as e:
            error_msg = str(e)
            if "404" in error_msg and "not found" in error_msg:
                print(f"⚠️ [Gemini] Model {model_name} not found. Trying next...")
                continue # Try next model
            else:
                print(f"❌ [Gemini Error on {model_name}] {e}")
                if "API key" in error_msg: return []
                continue

    return []

# ----------------------------------------------------------
# UTILS
# ----------------------------------------------------------
def extract_players_from_lines(raw_data) -> List[Dict]:
    """
    Sorts the structured data returned by Gemini.
    """
    if isinstance(raw_data, list) and len(raw_data) > 0 and isinstance(raw_data[0], dict):
        raw_data.sort(key=lambda x: x.get("damage", 0), reverse=True)
        return raw_data
    return []

def get_reward(damage: int, game: str) -> str:
    table = REWARDS_WOS if game.upper() == "WOS" else REWARDS_ROK
    for threshold, reward in table:
        if damage >= threshold: return reward
    return table[-1][1]

def format_discord_leaderboard_with_rewards(players: List[Dict], game: str) -> str:
    lines = []
    medals = ["🥇", "🥈", "🥉"]
    nums = ["4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    
    for idx, p in enumerate(players, start=1):
        if idx <= 3: medal = medals[idx-1]
        elif idx <= 10: medal = nums[idx-4]
        else: medal = f"**#{idx}**"

        dmg_val = p.get('damage', 0)
        name_val = p.get('name', 'Unknown')
        
        dmg_str = f"{dmg_val:,}"
        reward = get_reward(dmg_val, game)
        
        lines.append(f"{medal} | **{name_val}** — {dmg_str} dmg")
        lines.append(f"   🎁 Reward: {reward}")
        lines.append("") 
        
        if idx >= 25: break 
        
    return "\n".join(lines)