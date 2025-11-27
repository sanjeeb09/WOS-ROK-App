import sys
import asyncio

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from keep_alive import keep_alive
import discord
from discord import app_commands
from discord.ext import commands, tasks
import datetime
import time
import os
import re
import io
import tempfile
import aiohttp
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv

# Import our helper modules
from database import (add_link, get_linked_user, get_all_users, check_history, add_history, remove_link, check_discord_link, check_game_id_link, update_stat, get_stat_growth, set_bear_schedule, get_bear_schedule, get_all_schedules, update_bear_status, update_schedule_status, update_schedule_time, delete_schedule, set_ping_config, get_ping_config)
from wos_api import get_wos_profile, redeem_wos_code
from rok_api import get_rok_profile, redeem_rok_code
from ocr_utils import ocr_file, extract_players_from_lines, format_discord_leaderboard_with_rewards, get_reward

load_dotenv()

# 👑 OWNER CONFIGURATION
OWNER_ID = 452873519433383946

# 🖼️ BEAR IMAGE CONFIGURATION
# These URLs are used as thumbnails in the Bear Alert and Info Board embeds.
URL_BEAR_WOS = "https://cdn.discordapp.com/attachments/1438417495680880692/1442178649041403925/jump_icon_40088.png?ex=692525c8&is=6923d448&hm=b6765092c1f5f819aec6660df64dcdf1bb1225f905f18fb58820d8e4d343a3b4&" 
URL_BEAR_ROK = "https://cdn.discordapp.com/attachments/1431717113135104131/1442178809280594095/1375520846407270561.png?ex=692525ee&is=6923d46e&hm=e9bafa5e4900b6eadf2081b21110eb900e630ebf8529c3307eb83aa364f356ca&" 

# ==============================================================================
# 🔔 BEAR TRAP CHANNELS (AUTOMATION)
# ==============================================================================
# Channel: #🐻・bear-alerts (Public/Alliance View)
# Purpose: Bot posts "Incoming (60m)", "Pre-Attack (10m)", and "ATTACK NOW" pings here.
BEAR_NOTIFY_CHANNEL_WOS = 1436577415865569300 
BEAR_NOTIFY_CHANNEL_ROK = 1427864039618252920 

# Channel: #📜・bear-logs (Public/Admin View)
# Purpose: Bot posts the final "Victory" embed here. Admins use !logss here to upload leaderboard screenshots.
BEAR_LOG_CHANNEL_WOS = 1436577418528821371 
BEAR_LOG_CHANNEL_ROK = 1427864040851374150 

# ==============================================================================
# ⚙️ SECTION 1: DUAL CONFIGURATION
# ==============================================================================

# --- 1. WHITEOUT SURVIVAL (WOS) CONFIG ---
TOKEN_WOS = os.getenv('DISCORD_TOKEN_WOS')
CONFIG_WOS = {
    "LOG_CHANNELS": {
        "Bug": 1436611647463489568,        # ID for: ├⚠︰bugs🐛
        "Suggestion": 1436628659413848114, # ID for: ├⚠︰suggestions💡
        "Complaint": 1436628820303286376   # ID for: ╰⚠︰complaints🛡️
    },
    "ROLE_PINGS": {
        "Bug": 1439114820157706351,        # 『⚙️│Tech Support』
        "Suggestion": 1436577296835285012, # 『🔒│Admin』
        "Complaint": 1436783614384800008   # 『👮‍♂️│R4️⃣ - Officer
    },
    "VERIFIED_ROLE": 1436577314589769782,   # 『✅│ Verified』
    "UNVERIFIED_ROLE": 1439271756195041450,  # 『❌│ Unverified』
    
    "CODE_CHANNEL": 1436793435251019887,       # ID for: ꒰≻🥤╏「giveaway-and-code」
    "ADMIN_REDEEM_CHANNEL": 1436577465546834074, # ID for: ├🎁︰redeem-codes
    "LINK_LOG_CHANNEL": 1441470255993192619,     # ID for: #𒆕【📂】wos-link-logs
    
    "TICKET_CATEGORY_NAME": "👮🏻 𝘚𝘜𝘗𝘗𝘖𝘙𝘛 𝘡𝘖𝘕𝘌 👮🏻"
}

# --- 2. KINGSHOT (ROK) CONFIG ---
TOKEN_ROK = os.getenv('DISCORD_TOKEN_ROK')
CONFIG_ROK = {
    "LOG_CHANNELS": {
        "Bug": 1439562618477084803,        # ID for: —͟͞͞🐞・bug-reports
        "Suggestion": 1439562834861097023, # ID for: —͟͞͞💡・suggestions
        "Complaint": 1439562922933092362   # ID for: —͟͞͞🚨・complaints
    },
    "ROLE_PINGS": {
        "Bug": 1439565803816222792,        # [🛠️ Blacksmith] Role
        "Suggestion": 1439567751965577286, # [⚖️ High Council] Role
        "Complaint": 1439568029993275487   # [⚔️ Royal Guard] Role
    },
    "VERIFIED_ROLE": 1410699348320190656,   # [ Verified ✅ ] Role
    "UNVERIFIED_ROLE": 1410699349310046220, # [ Unverified ❌ ] Role
    
    "CODE_CHANNEL": 1417148894240047175,       # ID for: 🎁⤬redeem-code_선물코드
    "ADMIN_REDEEM_CHANNEL": 1441474595516448932, # ID for: —͟͞͞🔐・rok-code-admin
    "LINK_LOG_CHANNEL": 1441475178222846102,     # ID for: 📝⤬rok-link-logs
    
    "TICKET_CATEGORY_NAME": "📬 TICKET STATION"
}

user_cooldowns = {}

# ==============================================================================
# 📝 SECTION 2: THEMES & TEXT (TICKET SYSTEM)
# ==============================================================================
THEME_DATA = {
    "WOS": {
        "EMOJIS": {"Bug": "🐛", "Suggestion": "🔥", "Complaint": "🛡️"},
        "EPHEMERAL": {
            "Bug": "🔧 **Engineering Bay Opened!**\nHi {user}, secure line established: {channel}.\nLet's fix those broken gears!",
            "Suggestion": "🔥 **Ignition Sequence Started!**\nHi {user}, drafting table ready: {channel}.\nLet's hear your brilliant ideas!",
            "Complaint": "⚖️ **Council Chamber Cleared!**\nHi {user}, private room: {channel}."
        },
        "INTRO": {
            "Bug": {
                "Title": "🔧 ENGINEERING & BUG REPORT",
                "Desc": (
                    "Hey there {user}! Thank you for taking the time to report a problem!\n\n"
                    "⚠️ **PLEASE READ BEFORE PROCEEDING:**\n"
                    "We **cannot** help with the following (Contact In-Game Support):\n"
                    "1️⃣ Account issues (lost account/binding).\n"
                    "2️⃣ Reports of inappropriate In-Game behavior.\n"
                    "3️⃣ Payment/Refund related issues.\n"
                    "4️⃣ Lost/Missing rewards or items.\n\n"
                    "**🛠️ TROUBLESHOOTING STEPS:**\n"
                    "Before reporting, please try:\n"
                    "• Restarting the game.\n"
                    "• Rebooting your phone.\n\n"
                    "**If your issue is listed above or fixed, click 'End Conversation'.**\n"
                    "Otherwise, answer the bot below!"
                ),
                "Color": discord.Color.red()
            },
            "Suggestion": {
                "Title": "💡 STRATEGIC PLANNING ROOM",
                "Desc": (
                    "Dear Governor {user}! Thank you so much for sharing your suggestion with us!\n\n"
                    "Your ideas are the fuel that keeps our furnace burning. "
                    "We review every spark of genius to make our alliance stronger.\n\n"
                    "**Changed your mind?** You can end this conversation using the button below.\n"
                    "Otherwise, please answer the next couple of questions!"
                ),
                "Color": discord.Color.green()
            },
            "Complaint": {
                "Title": "⚖️ DISCIPLINARY COUNCIL",
                "Desc": (
                    "Greetings Chief {user}. We take peacekeeping seriously.\n\n"
                    "Please provide honest and accurate information regarding the incident. "
                    "False reports may lead to consequences.\n\n"
                    "**Changed your mind?** You can close this ticket using the button below.\n"
                    "If you are ready, please proceed."
                ),
                "Color": discord.Color.blurple()
            }
        },
        "QUESTIONS": {
            "Bug": {
                "In-Game Name": "What is your **In-Game Username**?",
                "Player ID": "What is your **Player ID**? (e.g. 12345678)",
                "Game Version": "What **Game Version** are you on?",
                "Device Model": "Which **Device** are you using?",
                "OS Version": "Which **OS Version**?",
                "Description": "Please describe the **Bug/Glitch**.",
                "Attachment": "Attach a **Screenshot/Video** (or type 'no')."
            },
            "Suggestion": {
                "In-Game Name": "What is your **In-Game Username**?",
                "Player ID": "What is your **Player ID**?",
                "Topic": "What is this suggestion about?",
                "Idea": "Describe your **Spark of Genius** in detail.",
                "Benefit": "How will this help the alliance?",
                "Attachment": "Attach an example image (or type 'no')."
            },
            "Complaint": {
                "In-Game Name": "What is your **In-Game Username**?",
                "Player ID": "What is your **Player ID**?",
                "Offender Name": "Who is this complaint against?",
                "Violation": "What happened?",
                "Time": "When did this happen?",
                "Evidence": "Attach **Proof** (Required). Type 'no' if none."
            }
        }
    },
    "ROK": {
        "EMOJIS": {"Bug": "⚒️", "Suggestion": "📜", "Complaint": "⚔️"},
        "EPHEMERAL": {
            "Bug": "⚔️ **Blacksmith Summoned!**\nHail {user}, workbench secured: {channel}.",
            "Suggestion": "🏰 **War Room Unlocked!**\nMy Lord {user}, strategy table ready: {channel}.",
            "Complaint": "⚖️ **High Court In Session!**\nSharpshooter {user}, private chambers: {channel}."
        },
        "INTRO": {
            "Bug": {
                "Title": "⚒️ THE ROYAL ARMOURY", 
                "Desc": (
                    "Hail, Warrior {user}! Is your equipment jammed?\n\n"
                    "⚠️ **ROYAL DECREE (READ FIRST):**\n"
                    "The Alliance Blacksmiths **cannot** fix:\n"
                    "1️⃣ Lost Accounts or Binding issues.\n"
                    "2️⃣ Refund/Payment disputes.\n"
                    "3️⃣ Missing Rewards.\n"
                    "*(Please contact Official Kingshot Support for these)*\n\n"
                    "**🛠️ BATTLEFIELD REPAIRS:**\n"
                    "• Have you restarted the application?\n"
                    "• Have you cleared your cache?\n\n"
                    "If the issue persists, answer the scribe below."
                ),
                "Color": discord.Color.gold()
            },
            "Suggestion": {
                "Title": "📜 STRATEGY & WAR ROOM", 
                "Desc": (
                    "Greetings, Tactician {user}! The Kingdom needs your strategy.\n\n"
                    "The High Council reviews every battle plan submitted here. "
                    "Your wisdom could lead us to victory!\n\n"
                    "**Changed your mind?** You can retreat using the button below.\n"
                    "Otherwise, present your plans!"
                ),
                "Color": discord.Color.green()
            },
            "Complaint": {
                "Title": "⚖️ HIGH COURT TRIBUNAL", 
                "Desc": (
                    "At ease, {user}. The Royal Guard is listening.\n\n"
                    "We take the Kingdom's laws seriously. "
                    "Please speak the truth. False accusations are considered treason.\n\n"
                    "**Changed your mind?** You can close the chambers using the button below.\n"
                    "If you are ready, state your case."
                ),
                "Color": discord.Color.dark_red()
            }
        },
        "QUESTIONS": {
            "Bug": {
                "In-Game Name": "What is your **Lord Name**?", 
                "Player ID": "What is your **ID**?", 
                "Game Version": "What **Game Version**?",
                "Device Model": "Which **Device**?",
                "OS Version": "Which **OS Version**?",
                "Description": "Describe the **Glitch**:", 
                "Attachment": "Attach **Screenshot** (or type 'no')."
            },
            "Suggestion": {
                "In-Game Name": "What is your **Lord Name**?", 
                "Player ID": "What is your **ID**?",
                "Topic": "What is the **Topic**?", 
                "Idea": "Describe your **Plan**:", 
                "Benefit": "How does this aid the Kingdom?", 
                "Attachment": "Attach **Image** (or type 'no')."
            },
            "Complaint": {
                "In-Game Name": "What is your **Lord Name**?", 
                "Player ID": "What is your **ID**?",
                "Offender": "Who is the **Traitor**?", 
                "Violation": "What was the **Violation**?", 
                "Time": "When did this occur?", 
                "Evidence": "Attach **Proof** (Required)."
            }
        }
    }
}

# ==============================================================================
# 🚀 INITIALIZATION
# ==============================================================================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot_wos = commands.Bot(command_prefix=commands.when_mentioned, intents=intents)
bot_rok = commands.Bot(command_prefix=commands.when_mentioned, intents=intents)
executor = ThreadPoolExecutor(max_workers=4)

# ==============================================================================
# 🤖 TICKET SYSTEM (VIEWS)
# ==============================================================================
class TicketLauncher(discord.ui.View):
    def __init__(self, bot_type):
        super().__init__(timeout=None)
        self.bot_type = bot_type
        self.emojis = THEME_DATA[bot_type]["EMOJIS"]
        self.add_item(self.create_btn("Bug", discord.ButtonStyle.red, "btn_bug", self.emojis["Bug"]))
        self.add_item(self.create_btn("Suggestion", discord.ButtonStyle.green, "btn_sug", self.emojis["Suggestion"]))
        self.add_item(self.create_btn("Complaint", discord.ButtonStyle.blurple, "btn_com", self.emojis["Complaint"]))

    def create_btn(self, label, style, custom_id, emoji):
        btn = discord.ui.Button(label=label, style=style, custom_id=f"{self.bot_type}_{custom_id}", emoji=emoji)
        async def cb(interaction): await self.handle(interaction, label)
        btn.callback = cb
        return btn

    async def handle(self, interaction, ticket_type):
        """Central logic to check cooldowns and create tickets."""
        user = interaction.user
        user_id = user.id
        
        # 1. Determine Configuration based on Bot Type
        config = CONFIG_WOS if self.bot_type == "WOS" else CONFIG_ROK
        verified_role_id = config["VERIFIED_ROLE"]
        
        # 2. --- TIERED COOLDOWN LOGIC ---
        limit = 600 # Default: 10 Minutes for everyone else
        
        if user.id == interaction.guild.owner_id:
            limit = 60  # 1 Minute for Owner
        elif user.guild_permissions.administrator:
            limit = 120 # 2 Minutes for Admins
        elif discord.utils.get(user.roles, id=verified_role_id):
            limit = 300 # 5 Minutes for Verified Members

        # 3. Check if user is on cooldown
        if user_id in user_cooldowns:
            last_time = user_cooldowns[user_id]
            if time.time() - last_time < limit:
                remaining = int(limit - (time.time() - last_time))
                minutes = remaining // 60
                seconds = remaining % 60
                
                title = "Chief" if self.bot_type == "WOS" else "My Lord"
                await interaction.response.send_message(
                    f"❄️ **Chill out, {title}!**\nBased on your rank, you must wait **{minutes}m {seconds}s**.", 
                    ephemeral=True
                )
                return

        # 4. Save current time and proceed
        user_cooldowns[user_id] = time.time()
        await interaction.response.defer(ephemeral=True)
        await create_ticket(interaction, ticket_type, self.bot_type)

class TicketControls(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="End Conversation", style=discord.ButtonStyle.grey, emoji="🔒")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Closing ticket...")
        await asyncio.sleep(2)
        try: await interaction.channel.delete()
        except: pass

class ConfirmView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.value = None
    @discord.ui.button(label="Yes, Submit", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = True; self.stop(); await interaction.response.defer()
    @discord.ui.button(label="No, Revise", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = False; self.stop(); await interaction.response.defer()

async def create_ticket(interaction, ticket_type, bot_type):
    guild = interaction.guild
    config = CONFIG_WOS if bot_type == "WOS" else CONFIG_ROK
    cat = discord.utils.get(guild.categories, name=config["TICKET_CATEGORY_NAME"])
    if not cat: cat = await guild.create_category(config["TICKET_CATEGORY_NAME"])
    overwrites = {guild.default_role: discord.PermissionOverwrite(read_messages=False),
                  interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                  guild.me: discord.PermissionOverwrite(read_messages=True)}
    channel_name = f"{ticket_type.lower()}-{interaction.user.name}"
    ticket_channel = await guild.create_text_channel(channel_name, category=cat, overwrites=overwrites)
    msg = THEME_DATA[bot_type]["EPHEMERAL"][ticket_type].format(user=interaction.user.mention, channel=ticket_channel.mention)
    await interaction.followup.send(msg, ephemeral=True)
    asyncio.create_task(run_interview(ticket_channel, interaction.user, ticket_type, bot_type))

async def run_interview(channel, user, ticket_type, bot_type):
    data = THEME_DATA[bot_type]["INTRO"][ticket_type]
    embed = discord.Embed(title=data["Title"], description=data["Desc"].format(user=user.mention), color=data["Color"])
    await channel.send(embed=embed, view=TicketControls())
    questions = THEME_DATA[bot_type]["QUESTIONS"][ticket_type]
    answers = {}
    captured_attachment = None 
    bot_instance = bot_wos if bot_type == "WOS" else bot_rok
    def check(m): return m.author == user and m.channel == channel

    for field, question in questions.items():
        try: await channel.send(f"🔹 **{field}:** {question}")
        except: return
        while True:
            try:
                msg = await bot_instance.wait_for('message', check=check, timeout=300)
                if "ID" in field and not msg.content.isdigit():
                     await channel.send("⚠️ **Invalid ID.** Numbers only."); continue
                if msg.attachments:
                    captured_attachment = msg.attachments[0]
                    answers[field] = "*(Image Attached)*"
                else: answers[field] = msg.content
                break
            except asyncio.TimeoutError: 
                try: await channel.delete(); return
                except: pass
            except: return
    summary = "\n".join([f"**{k}:** {v}" for k, v in answers.items()])
    embed = discord.Embed(title=f"{ticket_type} Summary", description=summary, color=discord.Color.gold())
    view = ConfirmView()
    try: await channel.send(embed=embed, view=view)
    except: return
    await view.wait()
    if view.value:
        config = CONFIG_WOS if bot_type == "WOS" else CONFIG_ROK
        log_channel = bot_instance.get_channel(config["LOG_CHANNELS"][ticket_type])
        if log_channel:
            log_embed = discord.Embed(title=f"📄 New {ticket_type}", color=discord.Color.green(), timestamp=datetime.datetime.now())
            log_embed.set_author(name=f"{user.name} ({user.id})", icon_url=user.display_avatar.url)
            for k, v in answers.items(): log_embed.add_field(name=k, value=v, inline=False)
            role_id = config["ROLE_PINGS"].get(ticket_type)
            if role_id: await log_channel.send(f"<@&{role_id}>")
            if captured_attachment:
                file = await captured_attachment.to_file()
                log_embed.set_image(url=f"attachment://{file.filename}")
                await log_channel.send(embed=log_embed, file=file)
            else: await log_channel.send(embed=log_embed)
        try: await channel.send("✅ Submitted! Closing..."); await asyncio.sleep(4); await channel.delete()
        except: pass
    else:
        try: await channel.send("❌ Cancelled."); await channel.delete()
        except: pass

# ==============================================================================
# 🛠️ SHARED LOGIC HELPERS
# ==============================================================================
def is_admin(interaction: discord.Interaction) -> bool:
    return interaction.user.guild_permissions.administrator

async def log_link_action(interaction, user, game_id, game_type, action="link"):
    config = CONFIG_WOS if game_type == "WOS" else CONFIG_ROK
    log_channel = interaction.guild.get_channel(config["LINK_LOG_CHANNEL"])
    
    # Manage Roles based on logic
    try:
        v_role = interaction.guild.get_role(config["VERIFIED_ROLE"])
        u_role = interaction.guild.get_role(config["UNVERIFIED_ROLE"])
        if action == "link":
            if u_role and u_role in user.roles: await user.remove_roles(u_role)
            if v_role: await user.add_roles(v_role)
    except: pass # Ignore permission errors for roles

    if log_channel:
        theme_color = 0x00F7FF if game_type == "WOS" else 0xD4AF37
        game_emoji = "❄️" if game_type == "WOS" else "👑"
        desc_text = "Link Established Successfully" if action == "link" else "Link Terminated"

        embed = discord.Embed(
            title=f"📂 Database Updated | {game_type}", 
            description=f"**{desc_text}**", 
            color=theme_color,
            timestamp=datetime.datetime.now()
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(name="👤 Discord User", value=f"{user.mention}\n`{user.id}`", inline=True)
        embed.add_field(name=f"{game_emoji} Game ID", value=f"```yaml\n{game_id}\n```", inline=True)
        embed.set_footer(text=f"Authorized by {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
        
        await log_channel.send(embed=embed)

async def verify_logic(interaction, user_id, game_type):
    await interaction.response.defer()
    
    if game_type == "WOS":
        # WOS Logic
        data = await get_wos_profile(user_id)
        
        # FIX: The API now handles "msg" check internally. 
        # If 'data' exists, it is valid.
        if data: 
            name = data.get('name')
            img = data.get("profilePhoto")
            level = data.get("level", "Unknown")
            state_info = f"#{data.get('kingdom', '???')}"
            
            embed = discord.Embed(title="❄️ Survivor Detected", color=0x00F7FF)
            embed.set_thumbnail(url=img)
            embed.add_field(name="👤 Chief Name", value=f"**{name}**", inline=True)
            embed.add_field(name="🔥 Furnace Lv", value=f"**{level}**", inline=True)
            embed.add_field(name="🌐 State", value=f"**{state_info}**", inline=True)
            embed.add_field(name="\u200b", value=f"Type `/linkwos @User {user_id}` to grant verified status.", inline=False)
            embed.set_footer(text="Whiteout Survival Database", icon_url=URL_BEAR_WOS)
            
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send("❌ **Signal Lost.** ID not found on the tundra.")
            
    else: 
        # ROK Logic
        data = get_rok_profile(user_id)
        
        if data: 
            name = data.get('name')
            img = data.get("profilePhoto")
            level = data.get('level', 'Unknown')
            kingdom = f"#{data.get('kingdom', '???')}"
            
            embed = discord.Embed(title="👑 Monarch Identified", color=0xD4AF37)
            embed.set_thumbnail(url=img)
            embed.add_field(name="⚔️ Ruler Name", value=f"**{name}**", inline=True)
            embed.add_field(name="🏰 Castle Lv", value=f"**{level}**", inline=True)
            embed.add_field(name="🚩 Kingdom", value=f"**{kingdom}**", inline=True)
            embed.add_field(name="\u200b", value=f"Type `/linkrok @User {user_id}` to grant noble status.", inline=False)
            embed.set_footer(text="Kingshot Royal Registry", icon_url=URL_BEAR_ROK)
            
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send("❌ **Unknown Subject.** ID not found in the records.")

async def process_leaderboard_slash(interaction, images, game_type, trap_choice):
    await interaction.response.defer()
    valid_images = [img for img in images if img and img.content_type.startswith("image/")]
    all_players = []
    status_msg = await interaction.followup.send(f"👀 Scanning {len(valid_images)} image(s)...")
    
    try:
        for img in valid_images:
            data = await ocr_file(file_bytes=await img.read())
            if data: all_players.extend(data)
        
        if not all_players: return await status_msg.edit(content="⚠️ Scan Failed.")
        
        merged = {}
        for p in all_players:
            n, d = p.get("name", "Unknown").strip(), p.get("damage", 0)
            merged[n] = max(merged.get(n, 0), d)
        
        final = sorted([{"name": k, "damage": v} for k, v in merged.items()], key=lambda x: x["damage"], reverse=True)
        total = sum(p["damage"] for p in final)
        top_10 = final[:10]
        
        title = f"🏆 {game_type} Bear {'Trap ' + str(trap_choice) if trap_choice else 'Results'}"
        color = 0x00F7FF if game_type == "WOS" else 0xD4AF37
        formatted = format_discord_leaderboard_with_rewards(top_10, game_type)
        
        embed = discord.Embed(title=title, color=color, timestamp=datetime.datetime.now())
        embed.description = f"**Date:** <t:{int(time.time())}:F>\n\n{formatted}"
        embed.add_field(name="🔥 Alliance Total Damage", value=f"**{total:,}** (Sum of {len(final)} players)", inline=False)
        embed.set_footer(text=f"Scanned by {interaction.user.display_name} • Top 10 Shown")
        await status_msg.edit(content=None, embed=embed)
    except Exception as e: await interaction.followup.send(f"❌ Error: {e}")

async def set_bear_time_logic(interaction, trap_num, time_str, game_type):
    if not is_admin(interaction): return await interaction.response.send_message("⛔ Admin only.", ephemeral=True)
    try:
        if time_str.isdigit(): target = int(time_str)
        else: target = int(datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M").replace(tzinfo=datetime.timezone.utc).timestamp())
        while target < int(time.time()): target += 172800 
        
        uid = f"{game_type.lower()}_{trap_num}"
        existing = [x for x in get_all_schedules() if x[0] == uid]
        vid = existing[0][5] if existing and existing[0][5] else None
        
        if not vid:
            for c in interaction.guild.voice_channels:
                if c.name.startswith(f"🐻 {game_type} {trap_num}"): vid = c.id; break
        
        if vid:
            try: await interaction.guild.get_channel(vid).edit(name=f"🐻 {game_type} {trap_num}: Updating...")
            except: vid = None
            
        if not vid:
            vc = await interaction.channel.category.create_voice_channel(f"🐻 {game_type} {trap_num} Timer", overwrites={interaction.guild.default_role: discord.PermissionOverwrite(connect=False)})
            vid = vc.id
            
        set_bear_schedule(game_type, trap_num, target, interaction.channel_id, vid)
        
        time_diff = target - int(time.time())
        if time_diff > 0:
             d, h, m = int(time_diff//86400), int((time_diff%86400)//3600), int((time_diff%3600)//60)
             try: await interaction.guild.get_channel(vid).edit(name=f"🐻 {game_type} {trap_num}: {d}d {h}h {m}m" if d>0 else f"🐻 {game_type} {trap_num}: {h}h {m}m")
             except: pass

        color = 0x00F7FF if game_type == "WOS" else 0xD4AF37
        embed = discord.Embed(title=f"🐻 {game_type} Bear Scheduled", color=color)
        embed.set_thumbnail(url=URL_BEAR_WOS if game_type == "WOS" else URL_BEAR_ROK)
        embed.add_field(name=f"Trap {trap_num}", value=f"<t:{target}:F>\n(<t:{target}:R>)")
        await interaction.response.send_message(embed=embed)
        if not bear_trap_loop.is_running(): bear_trap_loop.start()
    except Exception as e: await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)

async def cancel_bear_logic(interaction, bear_id):
    if not is_admin(interaction): return await interaction.response.send_message("⛔ Admin only.", ephemeral=True)
    if bear_id == "none": return await interaction.response.send_message("⚠️ No active traps.", ephemeral=True)
    
    row = next((x for x in get_all_schedules() if x[0] == bear_id), None)
    if row:
        if delete_schedule(bear_id):
            msg = f"🗑️ Cancelled `{bear_id}`."
            if row[5]:
                try: await interaction.guild.get_channel(row[5]).delete(); msg += " (VC Deleted)"
                except: msg += " (VC not found)"
            await interaction.response.send_message(msg)
        else: await interaction.response.send_message("❌ DB Error", ephemeral=True)
    else: await interaction.response.send_message("❌ ID Not Found", ephemeral=True)

async def bear_autocomplete(interaction, current, game_type):
    return [app_commands.Choice(name=f"Trap {x[2]}", value=x[0]) for x in get_all_schedules() if x[1] == game_type and current.lower() in x[0].lower()] or [app_commands.Choice(name="None", value="none")]

async def set_bear_pings_logic(interaction, phase, action, value, game_type):
    if not is_admin(interaction): return await interaction.response.send_message("⛔ Admin only.", ephemeral=True)
    
    # Logic to interpret the input
    final_setting = "0"
    
    if action == "toggle":
        if value.lower() in ["true", "on", "1", "yes", "enable"]: final_setting = "true"
        else: final_setting = "0"
    else:
        # For "Set Role", we try to extract a Role ID or number
        if value.lower() in ["true", "everyone", "@everyone"]: final_setting = "true"
        elif value.isdigit(): final_setting = value
        elif value.startswith("<@&") and value.endswith(">"): final_setting = value[3:-1] # Extract ID from mention
        else: final_setting = value # Fallback
        
    set_ping_config(game_type, phase, final_setting)
    
    display_val = "✅ ON" if final_setting == "true" else "❌ OFF" if final_setting == "0" else f"<@&{final_setting}>"
    await interaction.response.send_message(f"⚙️ **Configuration Updated**\nPhase: `{phase}`\nSetting: {display_val}")
async def ping_value_autocomplete(interaction, current: str):
    # Provides suggestions based on what might be needed
    suggestions = [
        app_commands.Choice(name="Toggle: On (Enable)", value="true"),
        app_commands.Choice(name="Toggle: Off (Disable)", value="false"),
        app_commands.Choice(name="Set: No Ping (0)", value="0"),
        app_commands.Choice(name="Set: Everyone (@everyone)", value="true"),
    ]
    return [s for s in suggestions if current.lower() in s.name.lower()]    

async def list_bears_logic(interaction, game_type):
    if not is_admin(interaction): return await interaction.response.send_message("⛔ Admin only.", ephemeral=True)
    
    # Check explicitly before deferring to avoid stuck state
    res = [x for x in get_all_schedules() if x[1] == game_type]
    if not res: 
        return await interaction.response.send_message("💤 No bears scheduled.", ephemeral=True)

    await interaction.response.defer()
    
    color = 0x00F7FF if game_type == "WOS" else 0xD4AF37
    img = URL_BEAR_WOS if game_type == "WOS" else URL_BEAR_ROK
    
    embed = discord.Embed(title=f"🐻 {game_type} Scheduled Bears", color=color)
    embed.set_thumbnail(url=img)
    
    for r in res: 
        # r = [id, type, trap_num, time, ch_id, vc_id, status]
        embed.add_field(name=f"🆔 `{r[0]}` (Trap {r[2]})", value=f"<t:{r[3]}:F> (<t:{r[3]}:R>)", inline=False)
        
    await interaction.followup.send(embed=embed)

async def setup_info_logic(interaction, game_type):
    if not is_admin(interaction): return await interaction.response.send_message("⛔ Admin only.", ephemeral=True)
    color, img = (0x00F7FF, URL_BEAR_WOS) if game_type == "WOS" else (0xD4AF37, URL_BEAR_ROK)
    embed = discord.Embed(title=f"🐻 {game_type} Bear Attack Notifications", color=color)
    embed.set_thumbnail(url=img)
    
    verify_cmd = f"/verify{game_type.lower()}"
    link_cmd = f"/link{game_type.lower()}"
    unlink_cmd = f"/unlink{game_type.lower()}"
    
    embed.description = (
        "📢 **This channel posts upcoming Bear attack phases!**\n\n"
        "⏰ **Alert** — 6 hours before (Optional)\n"
        "🔔 **Incoming** — 60 minutes before\n"
        "🎯 **Pre-Attack** — 10 minutes before impact\n"
        "⚔️ **Attack** — when the Bear arrives\n"
        "🏆 **Victory** — Event End & Logs\n\n"
        "**Public Slash Commands:**\n"
        f"⏰ `/nextbear` (See timer)\n\n"
        "**Admin Slash Commands:**\n"
        f"🗓️ `/setbeartime` [Trap] [Time]\n"
        f"🚫 `/cancelbear` [Select ID]\n"
        f"📸 `/logss` [Upload Image]\n"
        f"⚙️ `/setbearpings` [Phase] [Setting]"
    )
    embed.set_footer(text=f"{game_type} Bot • Bear Alerts • UTC", icon_url=img)
    
    await interaction.response.send_message("✅ Info Board Posted!", ephemeral=True)
    await interaction.channel.send(embed=embed)

class HelpPaginator(discord.ui.View):
    def __init__(self, embeds):
        super().__init__(timeout=60); self.embeds = embeds; self.curr = 0; self.btns()
    def btns(self): self.children[0].disabled = self.curr==0; self.children[1].disabled = self.curr==len(self.embeds)-1
    @discord.ui.button(label="◀️", style=discord.ButtonStyle.secondary)
    async def p(self, i, b): self.curr-=1; self.btns(); await i.response.edit_message(embed=self.embeds[self.curr], view=self)
    @discord.ui.button(label="▶️", style=discord.ButtonStyle.secondary)
    async def n(self, i, b): self.curr+=1; self.btns(); await i.response.edit_message(embed=self.embeds[self.curr], view=self)

async def help_logic(interaction, game_type):
    color = 0x00F7FF if game_type == "WOS" else 0xD4AF37
    emoji = "❄️" if game_type == "WOS" else "👑"
    
    embed = discord.Embed(title=f"{emoji} {game_type} Command Center", description="Available automated commands.", color=color)
    
    # Public Section
    embed.add_field(name="🌐 Public Commands", value=(
        f"**/nextbear**\nCheck countdown for the next Trap.\n"
        f"**/verify{game_type.lower()} [ID]**\nSearch the database for your Game Profile.\n"
        f"**/help**\nShow this menu."
    ), inline=False)
    
    # Admin Section
    if is_admin(interaction):
        embed.add_field(name="🛡️ Admin Administration", value=(
            f"**/link{game_type.lower()} [User] [ID]** - Link Discord User to Game ID.\n"
            f"**/unlink{game_type.lower()} [User] [ID]** - Remove link.\n"
            f"**/listbears** - View all active schedules.\n"
            f"**/logss** - Scan leaderboard screenshots.\n"
            f"**/setbeartime** - Schedule a trap manually.\n"
            f"**/cancelbear** - Delete a scheduled trap.\n"
            f"**/setbearpings** - Configure alert roles."
        ), inline=False)
        
        embed.add_field(name="⚙️ Setup", value=(
            f"**/setupbear** - Post the Info Board.\n"
            f"**/setupticket** - Post the Support Ticket Menu."
        ), inline=False)

    embed.set_footer(text=f"{game_type} Alliance Bot System")
    await interaction.response.send_message(embed=embed, ephemeral=True)

# ==============================================================================
# ❄️ WOS COMMANDS COG
# ==============================================================================
class WOSCommands(commands.Cog):
    def __init__(self, bot): self.bot = bot; self.game = "WOS"

    @app_commands.command(name="verifywos", description="Verify your WOS profile")
    async def verifywos(self, interaction: discord.Interaction, user_id: str):
        await verify_logic(interaction, user_id, "WOS")

    @app_commands.command(name="linkwos", description="[Admin] Link a Discord user to WOS ID")
    async def linkwos(self, interaction: discord.Interaction, user: discord.Member, game_id: str):
        if not is_admin(interaction): return await interaction.response.send_message("⛔ Admin only.", ephemeral=True)
        add_link(user.id, game_id, "WOS")
        await interaction.response.send_message(f"✅ Linked {user.mention} to ID `{game_id}` (WOS)", ephemeral=True)
        await log_link_action(interaction, user, game_id, "WOS", "link")

    @app_commands.command(name="unlinkwos", description="[Admin] Unlink a Discord user")
    async def unlinkwos(self, interaction: discord.Interaction, user: discord.Member, game_id: str):
        if not is_admin(interaction): return await interaction.response.send_message("⛔ Admin only.", ephemeral=True)
        if remove_link(user.id, game_id, "WOS"): 
            await interaction.response.send_message(f"🗑️ Unlinked {user.mention}.", ephemeral=True)
            await log_link_action(interaction, user, game_id, "WOS", "unlink")
        else: await interaction.response.send_message("❌ Link not found.", ephemeral=True)

    @app_commands.command(name="nextbear", description="Show countdown to next WOS bear")
    async def nextbear(self, interaction: discord.Interaction):
        schedules = get_all_schedules()
        res = [x for x in schedules if x[1] == "WOS" and x[3] > time.time()]
        if not res: await interaction.response.send_message(f"💤 No WOS bear scheduled yet.")
        else:
            upcoming = sorted(res, key=lambda x: x[3])[0]
            await interaction.response.send_message(f"🐻 **Next WOS Bear (Trap {upcoming[2]}):** <t:{upcoming[3]}:F> (<t:{upcoming[3]}:R>)")

    @app_commands.command(name="logss", description="[Admin] Scan WOS leaderboard screenshots (Max 5)")
    @app_commands.describe(screenshot="First image", screenshot2="Optional", screenshot3="Optional", screenshot4="Optional", screenshot5="Optional", trap="Select Trap 1 or 2")
    @app_commands.choices(trap=[app_commands.Choice(name="Trap 1", value=1), app_commands.Choice(name="Trap 2", value=2)])
    async def logss(self, interaction: discord.Interaction, trap: app_commands.Choice[int], screenshot: discord.Attachment, screenshot2: discord.Attachment = None, screenshot3: discord.Attachment = None, screenshot4: discord.Attachment = None, screenshot5: discord.Attachment = None):
        if not is_admin(interaction): return await interaction.response.send_message("⛔ Admin only.", ephemeral=True)
        await process_leaderboard_slash(interaction, [screenshot, screenshot2, screenshot3, screenshot4, screenshot5], "WOS", trap.value)

    @app_commands.command(name="setbeartime", description="[Admin] Schedule WOS Bear Trap (YYYY-MM-DD HH:MM)")
    @app_commands.choices(trap=[app_commands.Choice(name="Trap 1", value=1), app_commands.Choice(name="Trap 2", value=2)])
    async def setbeartime(self, interaction: discord.Interaction, trap: app_commands.Choice[int], time_str: str):
        await set_bear_time_logic(interaction, trap.value, time_str, "WOS")

    @app_commands.command(name="cancelbear", description="[Admin] Cancel active WOS bear trap")
    async def cancelbear(self, interaction: discord.Interaction, bear_id: str):
        await cancel_bear_logic(interaction, bear_id)
    
    @cancelbear.autocomplete('bear_id')
    async def cancelbear_autocomplete(self, interaction: discord.Interaction, current: str):
        return await bear_autocomplete(interaction, current, "WOS")

    @app_commands.command(name="setbearpings", description="[Admin] Configure notifications")
    @app_commands.choices(phase=[
        app_commands.Choice(name="Warning (6h)", value="warning_6h"), 
        app_commands.Choice(name="Incoming (60m)", value="incoming"), 
        app_commands.Choice(name="Pre-Attack (10m)", value="pre_attack"), 
        app_commands.Choice(name="Attack (Start)", value="attack")
    ], action=[
        app_commands.Choice(name="Toggle (On/Off)", value="toggle"), 
        app_commands.Choice(name="Set Role", value="set")
    ])
    @app_commands.autocomplete(value=ping_value_autocomplete) # <--- ADD THIS LINE
    async def setbearpings(self, interaction: discord.Interaction, phase: app_commands.Choice[str], action: app_commands.Choice[str], value: str):
        await set_bear_pings_logic(interaction, phase.value, action.value, value, self.game)

    @app_commands.command(name="listbears", description="[Admin] List scheduled WOS bears")
    async def listbears(self, interaction: discord.Interaction):
        await list_bears_logic(interaction, "WOS")

    @app_commands.command(name="setupticket", description="[Admin] Post WOS Ticket Menu")
    async def setupticket(self, interaction: discord.Interaction):
        if not is_admin(interaction): return await interaction.response.send_message("⛔ Admin only.", ephemeral=True)
        desc = "**Your eyes and ears are the lifeblood of our city.**\n\n🐛 **BUGS & GLITCHES**\nSpotted something broken? The tech survivors will thaw it out.\n\n🔥 **SPARKS OF GENIUS**\nHave a brilliant idea to improve the alliance? Share your brainwave!\n\n🛡️ **PEACEKEEPERS**\nFound someone breaking the peace? Report it here securely."
        embed = discord.Embed(title="Greetings, Chiefs! 👋", description=desc, color=discord.Color.blue())
        embed.set_footer(text="TOGETHER WE SURVIVE")
        await interaction.response.send_message("✅ Ticket Menu Posted!", ephemeral=True)
        await interaction.channel.send(embed=embed, view=TicketLauncher("WOS"))

    @app_commands.command(name="setupbear", description="[Admin] Post WOS Info Board")
    async def setupbear(self, interaction: discord.Interaction):
        await setup_info_logic(interaction, "WOS")

    @app_commands.command(name="help", description="Show WOS commands")
    async def help(self, interaction: discord.Interaction):
        await help_logic(interaction, "WOS")

# ==============================================================================
# 👑 ROK COMMANDS COG
# ==============================================================================
class ROKCommands(commands.Cog):
    def __init__(self, bot): self.bot = bot; self.game = "ROK"

    @app_commands.command(name="verifyrok", description="Verify your ROK profile")
    async def verifyrok(self, interaction: discord.Interaction, user_id: str):
        await verify_logic(interaction, user_id, "ROK")

    @app_commands.command(name="linkrok", description="[Admin] Link a Discord user to ROK ID")
    async def linkrok(self, interaction: discord.Interaction, user: discord.Member, game_id: str):
        if not is_admin(interaction): return await interaction.response.send_message("⛔ Admin only.", ephemeral=True)
        add_link(user.id, game_id, "ROK")
        await interaction.response.send_message(f"✅ Linked {user.mention} to ID `{game_id}` (ROK)", ephemeral=True)
        await log_link_action(interaction, user, game_id, "ROK", "link")

    @app_commands.command(name="unlinkrok", description="[Admin] Unlink a Discord user")
    async def unlinkrok(self, interaction: discord.Interaction, user: discord.Member, game_id: str):
        if not is_admin(interaction): return await interaction.response.send_message("⛔ Admin only.", ephemeral=True)
        if remove_link(user.id, game_id, "ROK"): 
            await interaction.response.send_message(f"🗑️ Unlinked {user.mention}.", ephemeral=True)
            await log_link_action(interaction, user, game_id, "ROK", "unlink")
        else: await interaction.response.send_message("❌ Link not found.", ephemeral=True)

    @app_commands.command(name="nextbear", description="Show countdown to next ROK bear")
    async def nextbear(self, interaction: discord.Interaction):
        schedules = get_all_schedules()
        res = [x for x in schedules if x[1] == "ROK" and x[3] > time.time()]
        if not res: await interaction.response.send_message(f"💤 No ROK bear scheduled yet.")
        else:
            upcoming = sorted(res, key=lambda x: x[3])[0]
            await interaction.response.send_message(f"🐻 **Next ROK Bear (Trap {upcoming[2]}):** <t:{upcoming[3]}:F> (<t:{upcoming[3]}:R>)")

    @app_commands.command(name="logss", description="[Admin] Scan ROK leaderboard screenshots")
    @app_commands.describe(screenshot="First image", screenshot2="Optional", screenshot3="Optional", screenshot4="Optional", screenshot5="Optional", trap="Select Trap 1 or 2")
    @app_commands.choices(trap=[app_commands.Choice(name="Trap 1", value=1), app_commands.Choice(name="Trap 2", value=2)])
    async def logss(self, interaction: discord.Interaction, trap: app_commands.Choice[int], screenshot: discord.Attachment, screenshot2: discord.Attachment = None, screenshot3: discord.Attachment = None, screenshot4: discord.Attachment = None, screenshot5: discord.Attachment = None):
        if not is_admin(interaction): return await interaction.response.send_message("⛔ Admin only.", ephemeral=True)
        await process_leaderboard_slash(interaction, [screenshot, screenshot2, screenshot3, screenshot4, screenshot5], "ROK", trap.value)

    @app_commands.command(name="setbeartime", description="[Admin] Schedule ROK Bear Trap")
    @app_commands.choices(trap=[app_commands.Choice(name="Trap 1", value=1), app_commands.Choice(name="Trap 2", value=2)])
    async def setbeartime(self, interaction: discord.Interaction, trap: app_commands.Choice[int], time_str: str):
        await set_bear_time_logic(interaction, trap.value, time_str, "ROK")

    @app_commands.command(name="cancelbear", description="[Admin] Cancel active ROK bear trap")
    async def cancelbear(self, interaction: discord.Interaction, bear_id: str):
        await cancel_bear_logic(interaction, bear_id)

    @cancelbear.autocomplete('bear_id')
    async def cancelbear_autocomplete(self, interaction: discord.Interaction, current: str):
        return await bear_autocomplete(interaction, current, "ROK")

    @app_commands.command(name="setbearpings", description="[Admin] Configure notifications")
    @app_commands.choices(phase=[
        app_commands.Choice(name="Warning (6h)", value="warning_6h"), 
        app_commands.Choice(name="Incoming (60m)", value="incoming"), 
        app_commands.Choice(name="Pre-Attack (10m)", value="pre_attack"), 
        app_commands.Choice(name="Attack (Start)", value="attack")
    ], action=[
        app_commands.Choice(name="Toggle (On/Off)", value="toggle"), 
        app_commands.Choice(name="Set Role", value="set")
    ])
    @app_commands.autocomplete(value=ping_value_autocomplete) # <--- ADD THIS LINE
    async def setbearpings(self, interaction: discord.Interaction, phase: app_commands.Choice[str], action: app_commands.Choice[str], value: str):
        await set_bear_pings_logic(interaction, phase.value, action.value, value, self.game)

    @app_commands.command(name="listbears", description="[Admin] List scheduled ROK bears")
    async def listbears(self, interaction: discord.Interaction):
        await list_bears_logic(interaction, "ROK")

    @app_commands.command(name="setupticket", description="[Admin] Post ROK Ticket Menu")
    async def setupticket(self, interaction: discord.Interaction):
        if not is_admin(interaction): return await interaction.response.send_message("⛔ Admin only.", ephemeral=True)
        desc = "**Greetings, Sharpshooters!** 🏹\nThe Kingdom needs your eyes and honor.\n\n⚒️ **THE ROYAL ARMOURY (Bugs)**\nSpotted a jammed rifle? Our Blacksmiths will repair it immediately.\n\n📜 **THE WAR ROOM (Suggestions)**\nHave a battle plan to improve the server? The High Council is listening.\n\n⚔️ **THE HIGH COURT (Complaints)**\nWitnessed treason or unauthorized attacks? The Royal Guard will serve justice."
        embed = discord.Embed(title="Royal Command Station 🛡️", description=desc, color=discord.Color.gold())
        embed.set_footer(text="LONG LIVE THE KING")
        await interaction.response.send_message("✅ Ticket Menu Posted!", ephemeral=True)
        await interaction.channel.send(embed=embed, view=TicketLauncher("ROK"))

    @app_commands.command(name="setupbear", description="[Admin] Post ROK Info Board")
    async def setupbear(self, interaction: discord.Interaction):
        await setup_info_logic(interaction, "ROK")

    @app_commands.command(name="help", description="Show ROK commands")
    async def help(self, interaction: discord.Interaction):
        await help_logic(interaction, "ROK")

# ==========================================
# 🎁 AUTO-REDEEM (Restored Text Commands)
# ==========================================
def extract_code(text):
    match = re.search(r'\b(?:Code|Gift Code|CdK)\s*[:\-]\s*([A-Za-z0-9]{3,})', text, re.IGNORECASE)
    return match.group(1) if match else None

@bot_wos.command()
@commands.has_permissions(administrator=True)
async def redeemall(ctx, code: str):
    if ctx.channel.id != CONFIG_WOS["ADMIN_REDEEM_CHANNEL"]: return
    await ctx.send(f"⚠️ **Auto-Redeem Unavailable:** Whiteout Survival requires manual Captcha.\nActive Code: `{code}`\nLink: https://wos-giftcode.centurygame.com/")

@bot_rok.command()
@commands.has_permissions(administrator=True)
async def redeemall(ctx, code: str):
    if ctx.channel.id != CONFIG_ROK["ADMIN_REDEEM_CHANNEL"]: return
    status_msg = await ctx.send(f"⏳ **Initiating ROK Mass Redeem protocol for `{code}`...**\nGenerating report...")
    users = get_all_users("ROK")
    success, skipped, failed = 0, 0, 0
    report_buffer = io.StringIO()
    report_buffer.write(f"--- MISSION REPORT: ROK ---\nCODE: {code}\nTIME: {datetime.datetime.now()}\n\n")
    for game_id, discord_id in users:
        if check_history(game_id, code, "ROK"):
            skipped += 1
            report_buffer.write(f"[⏭️ SKIPPED] ID: {game_id} | Reason: Code already used (in DB)\n")
            continue
        res = redeem_rok_code(game_id, code)
        is_success = (res.get("status") == "success") or (res.get("msg") == "success")
        if is_success:
            add_history(game_id, code, "ROK"); success += 1
            report_buffer.write(f"[✅ SUCCESS] ID: {game_id} | Reward Claimed\n")
        elif res and "received" in str(res).lower():
            add_history(game_id, code, "ROK"); skipped += 1
            report_buffer.write(f"[⏭️ SKIPPED] ID: {game_id} | Reason: Game said 'Already Received'\n")
        else:
            failed += 1
            error_msg = res.get('msg') or res.get('error') or str(res)
            report_buffer.write(f"[❌ FAILED ] ID: {game_id} | Error: {error_msg}\n")
        await asyncio.sleep(2)
    embed = discord.Embed(title="🏰 ROK Redeem Complete", color=discord.Color.gold())
    embed.add_field(name="Code", value=code)
    embed.add_field(name="✅ Success", value=str(success), inline=True)
    embed.add_field(name="⏭️ Skipped", value=str(skipped), inline=True)
    embed.add_field(name="❌ Failed", value=str(failed), inline=True)
    embed.set_footer(text="Check the attached file for failure reasons.")
    report_buffer.seek(0)
    file = discord.File(io.BytesIO(report_buffer.getvalue().encode()), filename=f"ROK_Report_{code}.txt")
    await status_msg.delete()
    await ctx.send(embed=embed, file=file)

# ==============================================================================
# 🐻 FEATURE: BEAR TRAP LOOP (AUTO)
# ==============================================================================
@tasks.loop(minutes=1)
async def bear_trap_loop():
    current_time = int(time.time())
    schedules = get_all_schedules()
    for row in schedules:
        unique_id, game_type, trap_num, next_time, channel_id, voice_id, status = row
        bot_instance = bot_wos if game_type == "WOS" else bot_rok
        time_diff = next_time - current_time
        
        if voice_id:
            try:
                vc = bot_instance.get_channel(voice_id)
                if vc:
                    if time_diff > 0:
                        days = int(time_diff // 86400)
                        hours = int((time_diff % 86400) // 3600)
                        mins = int((time_diff % 3600) // 60)
                        time_str = f"{days}d {hours}h {mins}m" if days > 0 else f"{hours}h {mins}m"
                        new_name = f"🐻 {game_type} {trap_num}: {time_str}"
                    elif time_diff > -1800: new_name = f"⚔️ {game_type} {trap_num}: ACTIVE!"
                    else: new_name = f"💤 {game_type} {trap_num}: Sleeping"
                    if vc.name != new_name: await vc.edit(name=new_name)
            except: pass

        channel = bot_instance.get_channel(channel_id)
        if not channel: continue

        phase = None
        if 21540 <= time_diff <= 21600 and status == "scheduled": phase = "warning_6h"
        elif 3540 <= time_diff <= 3600 and status == "scheduled": phase = "incoming"
        elif 540 <= time_diff <= 600 and status == "scheduled": phase = "pre_attack"
        elif -30 <= time_diff <= 30 and status == "scheduled": phase = "attack"
        
        if phase:
            setting = get_ping_config(game_type, phase)
            if setting != "0":
                ping = "@everyone" if setting == "true" else f"<@&{setting}>" if setting.isdigit() else ""
                msgs = {
                    "warning_6h": f"⏰ **REMINDER:** {game_type} Trap {trap_num} in **6 Hours.**",
                    "incoming": f"🔔 **INCOMING:** {game_type} Trap {trap_num} in **60 Minutes!**",
                    "pre_attack": f"⚠️ **PRE-ATTACK:** {game_type} Trap {trap_num} in **10 Minutes!** Get online!",
                    "attack": f"⚔️ **ATTACK:** The Bear is here! **JOIN RALLY NOW!**"
                }
                await channel.send(f"{msgs[phase]} {ping} <t:{next_time}:R>")
                if phase == "attack": update_schedule_status(unique_id, "active")

        if time_diff < -1800 and status == "active":
            log_id = BEAR_LOG_CHANNEL_WOS if game_type == "WOS" else BEAR_LOG_CHANNEL_ROK
            log_ch = bot_instance.get_channel(log_id)
            if log_ch:
                color = 0x00F7FF if game_type == "WOS" else 0xD4AF37
                embed = discord.Embed(title=f"🏆 Victory! {game_type} Bear {trap_num} Slain", color=color)
                embed.add_field(name="Completed", value=f"<t:{next_time+1800}:F>", inline=False)
                embed.add_field(name="Admins", value=f"Upload ranking screenshot via `/logss`.", inline=False)
                await log_ch.send(embed=embed)
            new_time = next_time + 172800 
            update_schedule_time(unique_id, new_time)
            await channel.send(f"🔄 **Auto-Schedule:** {game_type} Trap {trap_num} reset for <t:{new_time}:F>.")

# --- LISTENER (WOS) ---
@bot_wos.event
async def on_message(message):
    await bot_wos.process_commands(message)

# --- LISTENER (ROK) ---
@bot_rok.event
async def on_message(message):
    await bot_rok.process_commands(message)
    if message.channel.id == CONFIG_ROK["CODE_CHANNEL"] and not message.author.bot:
        detected_code = extract_code(message.content)
        if detected_code:
            admin_channel = bot_rok.get_channel(CONFIG_ROK["ADMIN_REDEEM_CHANNEL"])
            if admin_channel:
                embed = discord.Embed(title="🆕 New ROK Code Detected!", description=f"**{detected_code}**", color=discord.Color.gold())
                embed.add_field(name="Original Msg", value=message.content[:200])
                embed.add_field(name="Action", value=f"Type `?redeemall {detected_code}` to distribute.")
                await admin_channel.send(embed=embed)

# ==============================================================================
# 🚀 MAIN EXECUTION & SETUP
# ==============================================================================
@bot_wos.event
async def on_ready():
    # REMOVED: sys.stdout.reconfigure (It's already done in main)
    print('❄️ WOS Bot Online', flush=True) # Added flush=True
    await bot_wos.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Bear Timers 🐻"))
    bot_wos.add_view(TicketLauncher("WOS"))
    await bot_wos.add_cog(WOSCommands(bot_wos))
    try: 
        synced = await bot_wos.tree.sync()
        print(f"❄️ Synced {len(synced)} WOS Commands", flush=True)
    except Exception as e: 
        print(e, flush=True)
    
    if not bear_trap_loop.is_running():
        bear_trap_loop.start()

@bot_rok.event
async def on_ready():
    # REMOVED: sys.stdout.reconfigure
    print('👑 ROK Bot Online', flush=True) # Added flush=True
    await bot_rok.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Kingdom Chat 👑"))
    bot_rok.add_view(TicketLauncher("ROK"))
    await bot_rok.add_cog(ROKCommands(bot_rok))
    try: 
        synced = await bot_rok.tree.sync()
        print(f"👑 Synced {len(synced)} ROK Commands", flush=True)
    except Exception as e: 
        print(e, flush=True)

async def main():
    # Keep this ONE line here. It covers everything.
    sys.stdout.reconfigure(encoding='utf-8')
    
    # Slight delay to ensure logs don't overlap perfectly
    await asyncio.gather(
        bot_wos.start(TOKEN_WOS), 
        bot_rok.start(TOKEN_ROK)
    )

if __name__ == "__main__":
    keep_alive()
    try: 
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Force stopping...", flush=True)
        os._exit(0)
