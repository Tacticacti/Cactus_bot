import discord
from discord.ext import commands
from utils import ai
from discord.ext import tasks

class Chat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._cooldowns = {}
        # Start a cleanup task
        self.cleanup_task.start()
    
    def cog_unload(self):
        self.cleanup_task.cancel()

    @tasks.loop(minutes=30)
    async def cleanup_task(self):
        """Removes old entries from the cooldown dictionary to save RAM"""
        current_time = time.time()
        # Keep only users who chatted in the last 60 seconds
        self._cooldowns = {
            user_id: timestamp 
            for user_id, timestamp in self._cooldowns.items() 
            if current_time - timestamp < 60
        }

    @commands.Cog.listener()
    async def on_message(self, message):
        # 1. Ignore messages sent by the bot itself
        if message.author == self.bot.user:
            return

        # 2. Check if the bot was mentioned (pinged)
        if self.bot.user in message.mentions:
            
            # Show a "Typing..." indicator so the user knows we are thinking
            async with message.channel.typing():
                # Clean the message (remove the @AoCBot part so the AI reads it clearly)
                clean_text = message.content.replace(f'<@{self.bot.user.id}>', '').strip()
                
                # Ask the brain
                response = ai.ask_gemini(clean_text, message.author.display_name)
                
                # Reply to the user
                await message.reply(response)

async def setup(bot):
    await bot.add_cog(Chat(bot))