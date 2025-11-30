import discord
from discord import app_commands
from discord.ext import commands
import datetime
import config
from utils import aoc

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="test", description="Check if the bot is alive")
    async def test(self, interaction: discord.Interaction):
        await interaction.response.send_message("🎄 Ho ho ho! The bot is online and listening! 🎅")

    @app_commands.command(name="next", description="Countdown to the next puzzle unlock")
    async def next(self, interaction: discord.Interaction):
        # Timezone logic
        est = datetime.timezone(datetime.timedelta(hours=-5))
        now = datetime.datetime.now(est)
        
        # Target is next midnight
        target = (now + datetime.timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        
        remaining = target - now
        hours, remainder = divmod(int(remaining.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        
        await interaction.response.send_message(f"⏳ **Next Puzzle Unlock:** {hours}h {minutes}m {seconds}s")

    @app_commands.command(name="check_api", description="Verify Advent of Code credentials")
    async def check_api(self, interaction: discord.Interaction):
        await interaction.response.send_message("🔍 Verifying Advent of Code credentials...", ephemeral=True)
        
        data = aoc.get_leaderboard_data()
        
        if data:
            member_count = len(data.get('members', {}))
            await interaction.followup.send(f"✅ **Success!** Connected to leaderboard. Found {member_count} members.")
        else:
            await interaction.followup.send("❌ **Error!** Could not connect. Check console logs.")

# This function is required to load the Cog
async def setup(bot):
    await bot.add_cog(General(bot))