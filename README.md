🤖 Dual Alliance Sentinel ([WOS] + [ROK])

**The Unified Logistics AI for Whiteout Survival & Kingshot.**

This bot runs a "Dual Core" system, managing two different Discord servers simultaneously from a single codebase. It handles Support Tickets, Moderation Logging, and Server Logistics for both the Icefield and the Kingdom.

## 🛠️ Features

### ❄️ Whiteout Survival (WOS) Core
* **Trinity Ticket System:** Engineering (Bugs), Strategic Room (Suggestions), Disciplinary Council (Complaints).
* **Smart Routing:** Auto-sorts tickets to specific channels (`#bugs`, `#suggestions`).
* **Role Pings:** Tags Tech Support, Admins, or R4 Officers based on the ticket type.
* **Cooldowns:** Rank-based rate limiting.

### 🏰 Kingshot (ROK) Core
* **Royal Command Station:** The Armoury (Bugs), War Room (Strategy), High Court (Complaints).
* **Theme:** Fully localized with Kingdom/Medieval terminology.
* **Ephemeral UI:** Private interactions to keep channels clean.
* **Force Close:** Admin commands to instantly shut down tickets.

## 🚀 Deployment (Render.com)

1.  **Fork/Clone** this repository.
2.  Create a **New Web Service** on Render.
3.  Connect your GitHub repository.
4.  **Settings:**
    * **Build Command:** `pip install -r requirements.txt`
    * **Start Command:** `python bot.py`
5.  **Environment Variables:**
    * `DISCORD_TOKEN_WOS`: Your Whiteout Survival Bot Token.
    * `DISCORD_TOKEN_ROK`: Your Kingshot Bot Token.

## 🔋 Uptime (Cron-job)
This bot includes a lightweight Flask server (`keep_alive.py`).
To keep it running 24/7 on the Free Tier:
1.  Set up a Cron-job (e.g., cron-job.org).
2.  Target URL: `https://your-app-name.onrender.com`
3.  Interval: Every 5 minutes.

---
*Forged by Sanjeeb.*
