from keep_alive import keep_alive  # Import the web server to stay online
import discord
from discord.ext import commands
import asyncio
import datetime
import time
import os
from dotenv import load_dotenv

# Load hidden tokens from the .env file or Render Environment Variables
load_dotenv()

# ==============================================================================
# ⚙️ SECTION 1: DUAL CONFIGURATION
# ==============================================================================

# ------------------------------------------------------------------
# 1. WHITEOUT SURVIVAL (WOS) SETTINGS
# ------------------------------------------------------------------
TOKEN_WOS = os.getenv('DISCORD_TOKEN_WOS')

CONFIG_WOS = {
    # Channels where the bot posts the FINAL completed report.
    "LOG_CHANNELS": {
        "Bug": 1436611647463489568,        # ID for: ├⚠︰bugs🐛
        "Suggestion": 1436628659413848114, # ID for: ├⚠︰suggestions
        "Complaint": 1436628820303286376   # ID for: ╰⚠︰complaints
    },
    # Roles to ping when a report comes in
    "ROLE_PINGS": {
        "Bug": 1439114820157706351,        # Tech Support Role
        "Suggestion": 1436577296835285012, # Admin Role
        "Complaint": 1436783614384800008   # R4 - Officer Role
    },
    # ID for the 'Verified' role (used for cooldown timer logic)
    "VERIFIED_ROLE": 1436577314589769782,
    
    # The Name of the Category where TEMPORARY tickets are created
    "TICKET_CATEGORY_NAME": "👮🏻 𝘚𝘜𝘗𝘗𝘖𝘙𝘛 𝘡𝘖𝘕𝘌 👮🏻" 
}

# ------------------------------------------------------------------
# 2. KINGSHOT (ROK) SETTINGS
# ------------------------------------------------------------------
TOKEN_ROK = os.getenv('DISCORD_TOKEN_ROK')

CONFIG_ROK = {
    # Channels where the bot posts the FINAL completed report.
    "LOG_CHANNELS": {
        "Bug": 1439562618477084803,        # ID for: —͟͞͞🐞・bug-reports
        "Suggestion": 1439562834861097023, # ID for: —͟͞͞💡・suggestions
        "Complaint": 1439562922933092362   # ID for: —͟͞͞🚨・complaints
    },
    # Roles to ping when a report comes in
    "ROLE_PINGS": {
        "Bug": 1439565803816222792,        # [🛠️ Blacksmith] Role
        "Suggestion": 1439567751965577286, # [⚖️ High Council] Role
        "Complaint": 1439568029993275487   # [⚔️ Royal Guard] Role
    },
    # ID for the 'Verified' role
    "VERIFIED_ROLE": 1410699348320190656,  # [ Verified ✅ ] Role
    
    # The Name of the Category where TEMPORARY tickets are created
    "TICKET_CATEGORY_NAME": "📬 TICKET STATION"
}

# Dictionary to track user cooldowns (prevents spam)
user_cooldowns = {}

# ==============================================================================
# 📝 SECTION 2: TEXT, THEMES & QUESTIONS
# ==============================================================================

THEME_DATA = {
    "WOS": {
        "EMOJIS": {"Bug": "🐛", "Suggestion": "🔥", "Complaint": "🛡️"},
        "EPHEMERAL": {
            "Bug": "🔧 **Engineering Bay Opened!**\nHi {user}, secure line established: {channel}.",
            "Suggestion": "🔥 **Ignition Sequence Started!**\nHi {user}, drafting table ready: {channel}.",
            "Complaint": "⚖️ **Council Chamber Cleared!**\nHi {user}, private room: {channel}."
        },
        "INTRO": {
            "Bug": {
                "Title": "🔧 ENGINEERING & BUG REPORT",
                "Desc": "Greetings Chief {user}! You've spotted a glitch in the system?\n\n**Troubleshooting:** Have you tried restarting the game?\nIf not, please answer the questions below.",
                "Color": discord.Color.red()
            },
            "Suggestion": {
                "Title": "🔥 STRATEGIC PLANNING ROOM",
                "Desc": "Welcome {user}! Your ideas keep the furnace burning.\nPlease describe your suggestion in detail so the Chiefs can review it.",
                "Color": discord.Color.green()
            },
            "Complaint": {
                "Title": "⚖️ DISCIPLINARY COUNCIL",
                "Desc": "Greetings {user}. We take peace seriously.\nPlease provide honest information regarding the violation.",
                "Color": discord.Color.blurple()
            }
        },
        "QUESTIONS": {
            "Bug": {
                "In-Game Name": "What is your **In-Game Username**? (e.g. WhiteoutKing)",
                "Player ID": "What is your **Chief ID**? (e.g. 12345678)",
                "Device Model": "Which **Device** are you using? (e.g. iPhone 14)",
                "Description": "Please describe the **Glitch/Bug** in detail.",
                "Attachment": "Attach a **Screenshot/Video** (or type 'no')."
            },
            "Suggestion": {
                "In-Game Name": "What is your **In-Game Username**? (e.g. WhiteoutKing)",
                "Topic": "What is this suggestion about? (e.g. Event Schedule)",
                "Idea": "Describe your **Spark of Genius** in detail.",
                "Benefit": "How will this help the Alliance?",
                "Attachment": "Attach an example image (or type 'no')."
            },
            "Complaint": {
                "In-Game Name": "What is your **In-Game Username**? (e.g. WhiteoutKing)",
                "Offender": "Who is this complaint against? (Name or ID)",
                "Violation": "Which rule was broken? (e.g. Tile Hitting)",
                "Time": "When did this happen? (e.g. 10 mins ago)",
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
                "Desc": "Hail, Warrior {user}! Is your equipment jammed?\n\n**Troubleshooting:** Have you checked your connection?\nIf the issue persists, report to the Blacksmith below.",
                "Color": discord.Color.gold()
            },
            "Suggestion": {
                "Title": "📜 STRATEGY & WAR ROOM",
                "Desc": "Greetings, Tactician {user}! The Kingdom needs your strategy.\nThe High Council reviews every battle plan submitted here.",
                "Color": discord.Color.green()
            },
            "Complaint": {
                "Title": "⚖️ HIGH COURT TRIBUNAL",
                "Desc": "At ease, {user}. We take the Kingdom's laws seriously.\nFalse accusations are treason. Please speak the truth.",
                "Color": discord.Color.dark_red()
            }
        },
        "QUESTIONS": {
            "Bug": {
                "In-Game Name": "What is your **Lord/Lady Name**? (e.g. KingSlayer)",
                "Player ID": "What is your **Kingdom ID**? (e.g. 98765432)",
                "Device Model": "Which **Device** are you playing on? (e.g. Android)",
                "Description": "Describe the **Glitch/Bug** in detail.",
                "Attachment": "Attach a **Screenshot/Video** (or type 'no')."
            },
            "Suggestion": {
                "In-Game Name": "What is your **Lord/Lady Name**? (e.g. KingSlayer)",
                "Topic": "What is this strategy about? (e.g. Bear Trap time)",
                "Idea": "Describe your **Battle Plan** in detail.",
                "Benefit": "How will this strengthen the Kingdom?",
                "Attachment": "Attach an example image (or type 'no')."
            },
            "Complaint": {
                "In-Game Name": "What is your **Lord/Lady Name**? (e.g. KingSlayer)",
                "Offender": "Who is the **Traitor** (Offender)?",
                "Violation": "Which **Law** was broken?",
                "Time": "When did this occur?",
                "Evidence": "Attach **Proof** (Required). Type 'no' if none."
            }
        }
    }
}

# ==============================================================================
# 🤖 SECTION 3: SHARED LOGIC (CLASSES)
# ==============================================================================

class TicketLauncher(discord.ui.View):
    """The Main Menu buttons that appear in #help-desk."""
    def __init__(self, bot_type):
        super().__init__(timeout=None)
        self.bot_type = bot_type
        self.emojis = THEME_DATA[bot_type]["EMOJIS"]
        
        # Create buttons dynamically based on the theme
        self.add_item(self.create_button("Bug", discord.ButtonStyle.red, "btn_bug", self.emojis["Bug"]))
        self.add_item(self.create_button("Suggestion", discord.ButtonStyle.green, "btn_sug", self.emojis["Suggestion"]))
        self.add_item(self.create_button("Complaint", discord.ButtonStyle.blurple, "btn_com", self.emojis["Complaint"]))

    def create_button(self, label, style, custom_id, emoji):
        button = discord.ui.Button(label=label, style=style, custom_id=f"{self.bot_type}_{custom_id}", emoji=emoji)
        async def callback(interaction):
            await self.handle_ticket(interaction, label)
        button.callback = callback
        return button

    async def handle_ticket(self, interaction, ticket_type):
        user = interaction.user
        # 60-second Global Cooldown to prevent spamming buttons
        if user.id in user_cooldowns and time.time() - user_cooldowns[user.id] < 60:
             await interaction.response.send_message("⏳ Please wait a moment before opening another ticket.", ephemeral=True)
             return
             
        user_cooldowns[user.id] = time.time()
        await interaction.response.defer(ephemeral=True)
        await create_ticket(interaction, ticket_type, self.bot_type)

class TicketControls(discord.ui.View):
    """The 'End Conversation' button inside the ticket."""
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="End Conversation", style=discord.ButtonStyle.grey, emoji="🔒")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Closing ticket...")
        await asyncio.sleep(2)
        await interaction.channel.delete()

class ConfirmView(discord.ui.View):
    """The Yes/No buttons after interview."""
    def __init__(self):
        super().__init__(timeout=None)
        self.value = None

    @discord.ui.button(label="Yes, Submit", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = True
        self.stop()
        await interaction.response.defer()

    @discord.ui.button(label="No, Revise", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = False
        self.stop()
        await interaction.response.defer()

# ==============================================================================
# 🧠 SECTION 4: TICKET GENERATION & INTERVIEW LOGIC
# ==============================================================================

async def create_ticket(interaction, ticket_type, bot_type):
    """Creates the private channel in the correct category."""
    guild = interaction.guild
    config = CONFIG_WOS if bot_type == "WOS" else CONFIG_ROK
    
    cat_name = config["TICKET_CATEGORY_NAME"]
    category = discord.utils.get(guild.categories, name=cat_name)
    if not category:
        category = await guild.create_category(cat_name)

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        guild.me: discord.PermissionOverwrite(read_messages=True)
    }
    
    channel_name = f"{ticket_type.lower()}-{interaction.user.name}"
    ticket_channel = await guild.create_text_channel(channel_name, category=category, overwrites=overwrites)
    
    msg_text = THEME_DATA[bot_type]["EPHEMERAL"][ticket_type]
    await interaction.followup.send(msg_text.format(user=interaction.user.mention, channel=ticket_channel.mention), ephemeral=True)
    
    try:
        await run_interview(ticket_channel, interaction.user, ticket_type, bot_type)
    except Exception as e:
        print(f"Error in interview: {e}")

async def run_interview(channel, user, ticket_type, bot_type):
    """Runs the Q&A loop inside the private channel."""
    data = THEME_DATA[bot_type]["INTRO"][ticket_type]
    embed = discord.Embed(title=data["Title"], description=data["Desc"].format(user=user.mention), color=data["Color"])
    await channel.send(embed=embed, view=TicketControls())
    
    questions = THEME_DATA[bot_type]["QUESTIONS"][ticket_type]
    answers = {}
    captured_attachment = None 
    bot_instance = bot_wos if bot_type == "WOS" else bot_rok

    def check(m): return m.author == user and m.channel == channel

    for field, question in questions.items():
        await channel.send(f"🔹 **{field}:** {question}")
        while True:
            try:
                msg = await bot_instance.wait_for('message', check=check, timeout=300)
                
                # Validation: If field contains "ID", ensure it's numbers only
                if "ID" in field and not msg.content.isdigit():
                     await channel.send("⚠️ **Invalid ID.** Numbers only, please.")
                     continue
                
                if msg.attachments:
                    captured_attachment = msg.attachments[0]
                    answers[field] = "*(Image Attached)*"
                else:
                    answers[field] = msg.content
                break
            except asyncio.TimeoutError:
                await channel.delete()
                return

    summary = "\n".join([f"**{k}:** {v}" for k, v in answers.items()])
    embed = discord.Embed(title=f"{ticket_type} Summary", description=summary, color=discord.Color.gold())
    view = ConfirmView()
    await channel.send(embed=embed, view=view)
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
            
            # --- IMAGE FIX: EMBED THE ATTACHMENT INSIDE THE BOX ---
            if captured_attachment:
                file = await captured_attachment.to_file()
                log_embed.set_image(url=f"attachment://{file.filename}")
                await log_channel.send(embed=log_embed, file=file)
            else:
                await log_channel.send(embed=log_embed)

        await channel.send("✅ Submitted! Closing...")
        await asyncio.sleep(4)
        await channel.delete()
    else:
        await channel.send("❌ Cancelled. Closing...")
        await asyncio.sleep(4)
        await channel.delete()

# ==============================================================================
# 🚀 SECTION 5: STARTUP & COMMANDS
# ==============================================================================

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot_wos = commands.Bot(command_prefix="!", intents=intents)
bot_rok = commands.Bot(command_prefix="?", intents=intents)

@bot_wos.event
async def on_ready():
    print(f'❄️ WOS Bot: {bot_wos.user} is Online')
    await bot_wos.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="the Furnace 🔥"))
    bot_wos.add_view(TicketLauncher("WOS"))

@bot_rok.event
async def on_ready():
    print(f'🏰 ROK Bot: {bot_rok.user} is Online')
    await bot_rok.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="the Throne 👑"))
    bot_rok.add_view(TicketLauncher("ROK"))

# --- SETUP COMMAND: WHITE OUT ---
@bot_wos.command()
async def setup(ctx):
    desc = """
    **Your eyes and ears are the lifeblood of our city.**
    
    🐛 **BUGS & GLITCHES**
    Spotted something broken? The tech survivors will thaw it out.
    
    🔥 **SPARKS OF GENIUS (Suggestions)**
    Have a brilliant idea to improve the alliance? Share your brainwave!
    
    🛡️ **ALLIANCE PEACEKEEPERS (Complaints)**
    Found someone breaking the peace? Report it here securely.
    """
    embed = discord.Embed(title="Greetings, Chiefs! 👋", description=desc, color=discord.Color.blue())
    embed.set_footer(text="TOGETHER WE SURVIVE")
    await ctx.send(embed=embed, view=TicketLauncher("WOS"))

# --- SETUP COMMAND: KINGSHOT ---
@bot_rok.command()
async def setup(ctx):
    desc = """
    **Greetings, Sharpshooters!** 🏹
    The Kingdom needs your eyes, your strategies, and your honor.
    
    ⚒️ **THE ROYAL ARMOURY (Bugs)**
    Spotted a jammed rifle? Our Blacksmiths will repair it immediately.
    
    📜 **THE WAR ROOM (Suggestions)**
    Have a battle plan to improve the server? The High Council is listening.
    
    ⚔️ **THE HIGH COURT (Complaints)**
    Witnessed treason or unauthorized attacks? The Royal Guard will serve justice.
    """
    embed = discord.Embed(title="Royal Command Station 🛡️", description=desc, color=discord.Color.gold())
    embed.set_footer(text="LONG LIVE THE KING")
    await ctx.send(embed=embed, view=TicketLauncher("ROK"))

# --- FORCE CLOSE COMMAND: WOS ---
@bot_wos.command()
@commands.has_permissions(manage_channels=True)
async def close(ctx):
    """Force closes a WOS ticket instantly. Admin only."""
    if "bug-" in ctx.channel.name or "suggestion-" in ctx.channel.name or "complaint-" in ctx.channel.name:
        await ctx.send("⛔ **Force Closing Ticket...**")
        await asyncio.sleep(2)
        await ctx.channel.delete()

# --- FORCE CLOSE COMMAND: ROK ---
@bot_rok.command()
@commands.has_permissions(manage_channels=True)
async def close(ctx):
    """Force closes a ROK ticket instantly. Admin only."""
    if "bug-" in ctx.channel.name or "suggestion-" in ctx.channel.name or "complaint-" in ctx.channel.name:
        await ctx.send("⛔ **Force Closing Ticket...**")
        await asyncio.sleep(2)
        await ctx.channel.delete()

# ==============================================================================
# 🔄 MAIN EXECUTION LOOP
# ==============================================================================

async def main():
    if not TOKEN_WOS or not TOKEN_ROK:
        print("❌ Error: Missing DISCORD_TOKEN_WOS or DISCORD_TOKEN_ROK in .env")
        return
    
    # Run both bots simultaneously in the same event loop
    await asyncio.gather(
        bot_wos.start(TOKEN_WOS),
        bot_rok.start(TOKEN_ROK)
    )

if __name__ == "__main__":
    keep_alive() # Start the Flask server
    asyncio.run(main()) # Start the Discord Bots