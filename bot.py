import discord
from discord.ext import commands
import config
import asyncio

# Define the Bot Class
class AoCBot(commands.Bot):
    def __init__(self):
        # We need message_content intent so the bot can read chats to reply to pings
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # This function runs automatically when the bot starts
        # We load our "Cogs" (extensions) here
        
        # List of extension files to load
        # Ensure you have the folders: cogs/ and utils/
        extensions = [
            'cogs.general',   # Slash commands like /next
            'cogs.scheduler', # Daily 8am reminder
            'cogs.chat'       # Gemini AI replies
        ]
        
        for ext in extensions:
            try:
                await self.load_extension(ext)
                print(f"✅ Loaded extension: {ext}")
            except Exception as e:
                print(f"❌ Failed to load extension {ext}: {e}")

        # Sync slash commands with Discord so they show up in the menu
        try:
            synced = await self.tree.sync()
            print(f"✅ Synced {len(synced)} slash commands")
        except Exception as e:
            print(f"❌ Failed to sync commands: {e}")

    async def on_ready(self):
        print(f'🚀 Logged in as {self.user} (ID: {self.user.id})')
        print('------')

# Main Execution
async def main():
    bot = AoCBot()
    async with bot:
        await bot.start(config.TOKEN)

if __name__ == '__main__':
    if not config.TOKEN:
        print("Error: DISCORD_TOKEN is missing from config!")
    else:
        asyncio.run(main())