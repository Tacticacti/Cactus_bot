import discord
from discord.ext import commands
import config
import asyncio

# Setup Bot Class
class AoCBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # This function runs automatically when the bot starts
        # We load our "Cogs" (extensions) here
        
        # List of extension files to load (note the dots instead of slashes)
        extensions = [
            'cogs.general',
            'cogs.scheduler'
        ]
        
        for ext in extensions:
            try:
                await self.load_extension(ext)
                print(f"✅ Loaded extension: {ext}")
            except Exception as e:
                print(f"❌ Failed to load extension {ext}: {e}")

        # Sync slash commands with Discord
        try:
            synced = await self.tree.sync()
            print(f"✅ Synced {len(synced)} slash commands")
        except Exception as e:
            print(f"❌ Failed to sync commands: {e}")

    async def on_ready(self):
        print(f'🚀 Logged in as {self.user} (ID: {self.user.id})')
        print('------')

# Run the Bot
async def main():
    bot = AoCBot()
    async with bot:
        await bot.start(config.TOKEN)

if __name__ == '__main__':
    if not config.TOKEN:
        print("Error: DISCORD_TOKEN is missing from config!")
    else:
        asyncio.run(main())