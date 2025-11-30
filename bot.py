import discord
from discord.ext import tasks, commands
from discord import app_commands
import requests
import json
import os
from dotenv import load_dotenv
import datetime

# Load secrets
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
AOC_SESSION = os.getenv('AOC_SESSION_COOKIE')
LEADERBOARD_ID = os.getenv('AOC_LEADERBOARD_ID')
CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID'))

# Configuration
YEAR = 2025
check_time = datetime.time(hour=8, minute=0, tzinfo=datetime.timezone.utc)

# Setup Bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

def get_leaderboard_data():
    url = f"https://adventofcode.com/{YEAR}/leaderboard/private/view/{LEADERBOARD_ID}.json"
    headers = {"Cookie": f"session={AOC_SESSION}"}
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"Error fetching data: {response.status_code}")
        return None
    return response.json()

# --- THE BACKGROUND TASK ---
@tasks.loop(time=check_time)
async def daily_reminder():
    # Define EST timezone (UTC-5)
    est = datetime.timezone(datetime.timedelta(hours=-5))
    today = datetime.datetime.now(est)
    
    if today.month != 12 or today.day > 25:
        return

    data = get_leaderboard_data()
    if not data:
        return

    day_str = str(today.day)
    slacking_members = []

    members = data['members']
    for member_id, details in members.items():
        name = details['name'] or f"Anon #{member_id}"
        completion_data = details['completion_day_level']
        
        if day_str not in completion_data or '2' not in completion_data[day_str]:
            slacking_members.append(name)

    channel = bot.get_channel(CHANNEL_ID)
    
    if not slacking_members:
        await channel.send(f"🎉 **Day {day_str} Update:** Everyone has finished! Great job team!")
    else:
        slacker_names = ", ".join(slacking_members)
        await channel.send(
            f"🔔 **Day {day_str} Reminder!**\n"
            f"The puzzle is waiting! These elves still need to earn their stars:\n"
            f"👉 **{slacker_names}**\n"
            f"Go get 'em: https://adventofcode.com/{YEAR}/day/{today.day}"
        )

# --- SLASH COMMANDS ---

@bot.tree.command(name="test", description="Check if the bot is alive")
async def test(interaction: discord.Interaction):
    # We use interaction.response.send_message instead of ctx.send
    await interaction.response.send_message("🎄 Ho ho ho! The bot is online and listening! 🎅")

@bot.tree.command(name="check_api", description="Verify Advent of Code credentials")
async def check_api(interaction: discord.Interaction):
    await interaction.response.send_message("🔍 Verifying Advent of Code credentials...", ephemeral=True)
    
    url = f"https://adventofcode.com/{YEAR}/leaderboard/private/view/{LEADERBOARD_ID}.json"
    headers = {"Cookie": f"session={AOC_SESSION}"}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        member_count = len(data['members'])
        # We use followup.send because we already replied once
        await interaction.followup.send(f"✅ **Success!** Connected to leaderboard. Found {member_count} members.")
    else:
        await interaction.followup.send(f"❌ **Error!** Status code: {response.status_code}. Check your Session Cookie!")

@bot.tree.command(name="next", description="Countdown to the next puzzle unlock")
async def next(interaction: discord.Interaction):
    est = datetime.timezone(datetime.timedelta(hours=-5))
    now = datetime.datetime.now(est)
    
    target = (now + datetime.timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    
    remaining = target - now
    hours, remainder = divmod(int(remaining.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    
    await interaction.response.send_message(f"⏳ **Next Puzzle Unlock:** {hours}h {minutes}m {seconds}s")

# --- ON READY (SYNC COMMANDS) ---
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    
    # This syncs the commands with Discord
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

    if not daily_reminder.is_running():
        daily_reminder.start()

bot.run(TOKEN)