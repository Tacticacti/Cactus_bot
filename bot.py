import discord
from discord.ext import tasks, commands
import requests
import json
import os
from dotenv import load_dotenv
import datetime

# Load secrets from a .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
AOC_SESSION = os.getenv('AOC_SESSION_COOKIE')
LEADERBOARD_ID = os.getenv('AOC_LEADERBOARD_ID')
CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID')) # The channel to post in

# Configuration
YEAR = 2025
check_time = datetime.time(hour=8, minute=0, tzinfo=datetime.timezone.utc) # Set your reminder time

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

@tasks.loop(time=check_time)
async def daily_reminder():
    # Only run this loop during Advent (Dec 1 - Dec 25)
    # FIX: Use datetime.timezone and datetime.timedelta
    est = datetime.timezone(datetime.timedelta(hours=-5))
    today = datetime.datetime.now(est) # FIX: Use datetime.datetime.now
    
    if today.month != 12 or today.day > 25:
        return

    data = get_leaderboard_data()
    if not data:
        return

    day_str = str(today.day)
    slacking_members = []

    # Iterate through members to see who hasn't finished today's puzzle
    members = data['members']
    for member_id, details in members.items():
        name = details['name'] or f"Anon #{member_id}"
        
        # Check completion for today
        completion_data = details['completion_day_level']
        
        # If they haven't done part 2 for today
        if day_str not in completion_data or '2' not in completion_data[day_str]:
            slacking_members.append(name)

    channel = bot.get_channel(CHANNEL_ID)
    
    if not slacking_members:
        await channel.send(f"🎉 **Day {day_str} Update:** Everyone has finished! Great job team!")
    else:
        # Create a gently shaming message
        slacker_names = ", ".join(slacking_members)
        await channel.send(
            f"🔔 **Day {day_str} Reminder!**\n"
            f"The puzzle is waiting! These elves still need to earn their stars:\n"
            f"👉 **{slacker_names}**\n"
            f"Go get 'em: https://adventofcode.com/{YEAR}/day/{today.day}"
        )

# --- ADD THIS NEW COMMAND BELOW ---
@bot.command()
async def next(ctx):
    # Advent of Code always unlocks at Midnight EST (UTC-5)
    est = datetime.timezone(datetime.timedelta(hours=-5))
    now = datetime.datetime.now(est)
    
    # Target is the next midnight
    target = (now + datetime.timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Calculate duration
    remaining = target - now
    hours, remainder = divmod(int(remaining.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    
    await ctx.send(f"⏳ **Next Puzzle Unlock:** {hours}h {minutes}m {seconds}s")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    if not daily_reminder.is_running():
        daily_reminder.start()

# 1. Simple connectivity check
@bot.command()
async def test(ctx):
    await ctx.send("🎄 Ho ho ho! The bot is online and listening! 🎅")

# 2. Check if the AoC Cookie is working (without waiting for the daily timer)
@bot.command()
async def check_api(ctx):
    await ctx.send("🔍 Verifying Advent of Code credentials...")
    
    # Try to fetch the data
    url = f"https://adventofcode.com/{YEAR}/leaderboard/private/view/{LEADERBOARD_ID}.json"
    headers = {"Cookie": f"session={AOC_SESSION}"}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        member_count = len(data['members'])
        await ctx.send(f"✅ **Success!** Connected to leaderboard. Found {member_count} members.")
    else:
        await ctx.send(f"❌ **Error!** Could not connect. Status code: {response.status_code}. Check your Session Cookie!")

# Run the bot
bot.run(TOKEN)