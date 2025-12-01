import discord
from discord import app_commands
from discord.ext import commands, tasks
import datetime
import config
from utils import aoc, storage

class Scheduler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.daily_reminder.start() # Start the loop immediately when loaded
        self.daily_leaderboard.start() # Start the new loop

    def cog_unload(self):
        self.daily_reminder.cancel() # Stop loop if this file is unloaded
        self.daily_leaderboard.cancel()

    async def run_mission_check(self, manual_interaction=None):
        # Timezone logic (UTC-5 for EST)
        est = datetime.timezone(datetime.timedelta(hours=-5))
        today = datetime.datetime.now(est)

        # Check if it's Advent Season
        # (Commented out for testing, uncomment for real production if you want)
        if today.month != 12 or today.day > 25:
            if manual_interaction:
                await manual_interaction.response.send_message("💤 Mission Aborted: Not currently Advent season.", ephemeral=True)
            return

        data = aoc.get_leaderboard_data()
        if not data:
            if manual_interaction:
                await manual_interaction.response.send_message("❌ Error: Could not retrieve intel from HQ (AoC API).", ephemeral=True)
            return

        day_str = str(today.day)
        
        slackers = []      # 0 stars
        in_progress = []   # 1 star

        # Get the target channel
        channel = self.bot.get_channel(config.CHANNEL_ID)
        
        if manual_interaction:
            channel = manual_interaction.channel

        if not channel:
            print(f"❌ Error: Could not find channel {config.CHANNEL_ID}")
            return

        members = data.get('members', {})
        for member_id, details in members.items():
            # Get the raw AoC name
            raw_name = details['name'] or f"Anon #{member_id}"
            
            # Convert to Ping if possible using our new storage util
            display_name = storage.get_discord_mention(raw_name)
            
            day_data = details['completion_day_level'].get(day_str, {})
            star_count = len(day_data) 

            if star_count == 0:
                slackers.append(display_name)
            elif star_count == 1:
                # STRICT MODE: 1 star is "In the Field"
                in_progress.append(display_name)

        # --- SEND REPORT ---
        
        if manual_interaction:
            await manual_interaction.response.send_message("✅ Manual check initiated.", ephemeral=True)

        if not slackers and not in_progress:
            await channel.send(f"🎉 **Day {day_str} Debrief:** Mission Accomplished! The entire squad has secured 2 stars.")
            return

        # Build the message
        msg = f"🌵 **Day {day_str} Mission Report**\n"
        
        if slackers:
            msg += f"⚠ **MIA (0/2 Stars):** {', '.join(slackers)}\n"
        
        if in_progress:
            msg += f"⏳ **In the Field (1/2 Stars):** {', '.join(in_progress)}\n"
            
        msg += f"\nMove out: https://adventofcode.com/{config.YEAR}/day/{today.day}"
        
        await channel.send(msg)

    # --- NEW: LEADERBOARD LOGIC ---
    async def run_leaderboard_post(self, manual_interaction=None):
        data = aoc.get_leaderboard_data()
        if not data:
            if manual_interaction:
                await manual_interaction.response.send_message("❌ Error: Intel retrieval failed.", ephemeral=True)
            return

        # Get members and sort by local_score (highest first)
        members = list(data.get('members', {}).values())
        # Sort logic: Primary = Score (Desc), Secondary = Stars (Desc)
        members.sort(key=lambda x: (x['local_score'], x['stars']), reverse=True)

        channel = self.bot.get_channel(config.CHANNEL_ID)
        if manual_interaction:
            channel = manual_interaction.channel
            await manual_interaction.response.send_message("✅ Leaderboard requested.", ephemeral=True)

        # Build Message
        msg = "🏆 **Tactical Standings (Current Score)**\n"
        msg += "-----------------------------------\n"
        
        medals = ["🥇", "🥈", "🥉"]
        
        for index, member in enumerate(members):
            raw_name = member['name'] or f"Anon #{member['id']}"
            display_name = storage.get_discord_mention(raw_name)
            score = member['local_score']
            stars = member['stars']
            
            # Add medal for top 3, numbers for rest
            rank = medals[index] if index < 3 else f"#{index+1}"
            
            msg += f"{rank} **{display_name}** • {score} pts ({stars} ⭐)\n"

        await channel.send(msg)

    @tasks.loop(time=config.CHECK_TIME)
    async def daily_reminder(self):
        await self.run_mission_check()

# 2. Daily Leaderboard (23:55 UTC)
    # Note: We need to define this time in config.py or here
    # 23:55 UTC = 6:55 PM EST
    leaderboard_time = datetime.time(hour=23, minute=55, tzinfo=datetime.timezone.utc)
    @tasks.loop(time=leaderboard_time)
    async def daily_leaderboard(self):
        await self.run_leaderboard_post()

    @daily_reminder.before_loop
    async def before_daily_reminder(self):
        await self.bot.wait_until_ready()

    @daily_leaderboard.before_loop
    async def before_daily_leaderboard(self):
        await self.bot.wait_until_ready()

    @app_commands.command(name="mission_report", description="Force a manual leaderboard check right now.")
    async def mission_report(self, interaction: discord.Interaction):
        await self.run_mission_check(manual_interaction=interaction)

    @app_commands.command(name="leaderboard", description="Show the current standings.")
    async def leaderboard(self, interaction: discord.Interaction):
        await self.run_leaderboard_post(manual_interaction=interaction)

async def setup(bot):
    await bot.add_cog(Scheduler(bot))