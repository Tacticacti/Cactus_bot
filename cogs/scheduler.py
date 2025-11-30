import discord
from discord.ext import commands, tasks
import datetime
import config
from utils import aoc

class Scheduler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.daily_reminder.start() # Start the loop immediately when loaded

    def cog_unload(self):
        self.daily_reminder.cancel() # Stop loop if this file is unloaded

    @tasks.loop(time=config.CHECK_TIME)
    async def daily_reminder(self):
        # Timezone logic
        est = datetime.timezone(datetime.timedelta(hours=-5))
        today = datetime.datetime.now(est)

        # Only run during Advent (Dec 1 - Dec 25)
        if today.month != 12 or today.day > 25:
            return

        data = aoc.get_leaderboard_data()
        if not data:
            return

        day_str = str(today.day)
        slacking_members = []

        members = data.get('members', {})
        for member_id, details in members.items():
            name = details['name'] or f"Anon #{member_id}"
            completion_data = details['completion_day_level']
            
            # If they haven't done part 2 for today
            if day_str not in completion_data or '2' not in completion_data[day_str]:
                slacking_members.append(name)

        channel = self.bot.get_channel(config.CHANNEL_ID)
        
        if not channel:
            print(f"❌ Error: Could not find channel {config.CHANNEL_ID}")
            return

        if not slacking_members:
            await channel.send(f"🎉 **Day {day_str} Update:** Everyone has finished! Great job team!")
        else:
            slacker_names = ", ".join(slacking_members)
            await channel.send(
                f"🔔 **Day {day_str} Reminder!**\n"
                f"The puzzle is waiting! These elves still need to earn their stars:\n"
                f"👉 **{slacker_names}**\n"
                f"Go get 'em: https://adventofcode.com/{config.YEAR}/day/{today.day}"
            )

    @daily_reminder.before_loop
    async def before_daily_reminder(self):
        # Wait until the bot is fully ready before starting the timer logic
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(Scheduler(bot))