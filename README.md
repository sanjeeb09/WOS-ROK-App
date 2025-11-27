# 🤖 Dual Alliance Sentinel (WOS + ROK)

**The Unified Logistics AI for Whiteout Survival & Kingshot.**

This bot runs a **"Dual Core" system**, managing two different Discord servers simultaneously from a single codebase. It acts as the central nervous system for both the Icefield (WOS) and the Kingdom (ROK), handling Support Tickets, Event Automation, Leaderboard Scanning, and Security Verification.

---

## 🛠️ Key Features

### 🐻 Bear Trap Automation
* **Smart Timers:** Automatically counts down to the next trap instance.
* **Auto-Pings:** Alerts the alliance at **6h**, **1h**, **10m**, and **Attack** phases.
* **Visual Logs:** Posts "Victory" embeds automatically when the trap event ends.

### 📸 Leaderboard Scanning (OCR)
* **AI-Powered:** Uses **Google Gemini Vision** to read game screenshots.
* **Instant Results:** Upload an image -> Bot extracts names/damage -> Posts a formatted leaderboard.
* **Reward Calc:** Automatically calculates rewards based on damage tiers.

### 🔗 Smart Verification & Linking
* **Dual API Integration:** Connects to both **WOS** and **ROK** game servers to verify identities.
* **Anti-Imposter:** Links Discord users to specific In-Game IDs to prevent identity theft.
* **Role Management:** Auto-assigns "Verified" roles upon successful linking.

### 🎫 The "Trinity" Ticket System
A fully localized support system with "Smart Routing" that sends tickets to specific channels (`#bugs`, `#suggestions`) and pings the correct officers.

* **❄️ Whiteout Survival (WOS Core):**
    * **Engineering Bay:** For Bugs & Glitches.
    * **Strategic Room:** For Alliance Suggestions.
    * **Disciplinary Council:** For Complaints/Reports.
    * *Includes Rank-based Cooldowns.*

* **👑 Kingshot (ROK Core):**
    * **Royal Armoury:** Blacksmiths handle technical issues.
    * **War Room:** Tacticians review strategy.
    * **High Court:** Royal Guards handle treason/complaints.

---

## ⚙️ Commands

### 🌐 Public Commands
| Command | Description |
| :--- | :--- |
| `/nextbear` | Show the countdown to the next scheduled trap. |
| `/verifywos [ID]` | Check a Whiteout Survival ID. |
| `/verifyrok [ID]` | Check a Rise of Kingdoms ID. |
| `/help` | Show the interactive command menu. |

### 🛡️ Admin Only
| Command | Description |
| :--- | :--- |
| `/linkwos @User [ID]` | Force link a Discord user to a WOS ID. |
| `/linkrok @User [ID]` | Force link a Discord user to a ROK ID. |
| `/setbeartime [Trap] [Time]` | Schedule a trap (Format: `YYYY-MM-DD HH:MM`). |
| `/logss` | Upload screenshots to scan the leaderboard. |
| `/setbearpings` | Configure which roles get pinged for trap alerts. |
| `/setupticket` | Post the permanent Ticket Menu in a channel. |
| `/setupbear` | Post the permanent Bear Info Board. |

---

## 🚀 Deployment (Render.com)

1.  **Fork/Clone** this repository.
2.  Create a **New Web Service** on Render.
3.  Connect your GitHub repository.
4.  **Settings:**
    * **Build Command:** `pip install -r requirements.txt`
    * **Start Command:** `python bot.py`
5.  **Environment Variables (Secrets):**
    * `DISCORD_TOKEN_WOS`: Your Whiteout Survival Bot Token.
    * `DISCORD_TOKEN_ROK`: Your Kingshot Bot Token.
    * `WOS_SECRET`: API Secret for WOS.
    * `ROK_SECRET`: API Secret for ROK.
    * `GOOGLE_API_KEY`: Gemini AI API Key (for OCR).

### 🔋 Uptime (Keep-Alive)
This bot includes a lightweight Flask server (`keep_alive.py`) to prevent sleeping on free tiers.

1.  **Set up a Monitor** (e.g., UptimeRobot).
2.  **Target URL:** `https://your-app-name.onrender.com`
3.  **Interval:** Every 5 minutes.

---
*Forged by BlackHeart.*
