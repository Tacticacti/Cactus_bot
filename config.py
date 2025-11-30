import os
from dotenv import load_dotenv
import datetime

# Load the .env file immediately
load_dotenv()

# Secrets
TOKEN = os.getenv('DISCORD_TOKEN')
AOC_SESSION = os.getenv('AOC_SESSION_COOKIE')
LEADERBOARD_ID = os.getenv('AOC_LEADERBOARD_ID')
CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID', 0)) # Default to 0 if missing to prevent crash

# Constants
YEAR = 2025
# 8:00 AM UTC
CHECK_TIME = datetime.time(hour=8, minute=0, tzinfo=datetime.timezone.utc)