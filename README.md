# 🎄 Advent of Code Discord Bot

A festive Discord bot written in Python that tracks your private **Advent of Code** leaderboard. It sends daily reminders to players who haven't completed the day's puzzle and includes utility commands to track the event schedule.

## ✨ Features

* **Daily "Shame" Reminder:** Automatically checks the leaderboard every day at **8:00 AM UTC**. If a member hasn't completed Part 2 of the daily puzzle, they get tagged in the chat.
* **Slash Commands:** Modern, easy-to-use Discord commands (`/`).
* **Countdown:** Check exactly how much time is left until the next puzzle unlocks.
* **Secure:** Uses environment variables to keep your Session Cookie and Tokens safe.

## 🛠️ Prerequisites

* Python 3.8 or higher
* A Discord Bot Token
* An Advent of Code Account (and Private Leaderboard)

## ⚙️ Installation & Setup

### 1. Clone or Download
Download this repository to your local machine.

### 2. Install Dependencies
Open your terminal/command prompt in the project folder and run:
```bash
python -m pip install discord.py requests python-dotenv
````

### 3\. Configure Secrets (.env)

Create a file named `.env` in the root folder. **Do not upload this file to GitHub\!**
Add the following lines:

```env
DISCORD_TOKEN=your_discord_bot_token
AOC_SESSION_COOKIE=your_aoc_session_cookie
AOC_LEADERBOARD_ID=your_private_leaderboard_id
DISCORD_CHANNEL_ID=your_discord_channel_id
```

#### 🕵️ How to find your AOC\_SESSION\_COOKIE:

1.  Go to [adventofcode.com](https://adventofcode.com) and log in.
2.  Right-click the page \> **Inspect**.
3.  Go to the **Application** tab (you might need to click `>>` to see it).
4.  Expand **Cookies** \> `https://adventofcode.com`.
5.  Copy the value of the `session` row.

## 🚀 Usage

Run the bot locally:

```bash
python bot.py
```

### Commands

| Command | Description |
| :--- | :--- |
| `/next` | Shows a countdown timer to the next puzzle unlock (Midnight EST). |
| `/check_api` | Verifies that the bot can connect to the AoC Leaderboard successfully. |
| `/test` | Simple connectivity check to ensure the bot is online. |

## ☁️ Deployment (Discloud)

This bot is ready for **Discloud** hosting.

1.  Make sure `discloud.config` is present in the folder:
    ```text
    NAME=AoCBot
    TYPE=bot
    MAIN=bot.py
    RAM=100
    AUTORESTART=true
    VERSION=latest
    APT=tools
    ```
2.  Upload the files to Discloud.
3.  **Important:** Add your `.env` variables manually in the **Vars** tab of your Discloud dashboard (or upload the `.env` file via the Explorer tab).
4.  Ensure the "Start Command" in settings is set to `python bot.py`.

## 🤝 Contributing

Feel free to fork this project and add features like:

  * Leaderboard graphs/images.
  * Automatic role assignment based on stars.
  * "First to solve" announcements.

## ⚖️ Disclaimer

This project is not affiliated with Advent of Code or Eric Wastl. Please respect the [Advent of Code automation guidelines](https://www.reddit.com/r/adventofcode/wiki/faqs/automation) (request data max once every 15 minutes).

```
```