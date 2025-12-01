import discord
from discord import app_commands
from discord.ext import commands
import datetime
import config
from utils import aoc, storage

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="test", description="Check if the bot is alive")
    async def test(self, interaction: discord.Interaction):
        await interaction.response.send_message("🌵 System Online. TacticalCacti Bot ready for orders.")

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
        await interaction.response.send_message("🔍 Verifying credentials with HQ...", ephemeral=True)
        
        data = aoc.get_leaderboard_data()
        
        if data:
            member_count = len(data.get('members', {}))
            await interaction.followup.send(f"✅ **Connection Established.** Linked to leaderboard with {member_count} operatives.")
        else:
            await interaction.followup.send("❌ **Connection Failed.** Check credentials in config.")

    # --- UPDATED LINK COMMAND ---
    @app_commands.command(name="link", description="Link your Advent of Code name to your Discord account for pings.")
    @app_commands.describe(aoc_name="Your exact username on the Advent of Code leaderboard")
    async def link(self, interaction: discord.Interaction, aoc_name: str):
        # 1. Check if user is ALREADY linked
        existing_name = storage.get_aoc_name_by_id(interaction.user.id)
        if existing_name:
            await interaction.response.send_message(
                f"🚫 **Access Denied:** You are already registered as `{existing_name}`.\n"
                "One operative cannot man two stations. Contact an admin if this is an error.",
                ephemeral=True
            )
            return

        # 2. Defer (loading state)
        await interaction.response.defer(ephemeral=True)

        # 3. Verify Existence on Leaderboard
        data = aoc.get_leaderboard_data()
        if not data:
            await interaction.followup.send("❌ **Network Error:** Could not fetch leaderboard. Try again later.")
            return

        valid_members = {}
        members = data.get('members', {})
        
        for member_id, details in members.items():
            name = details.get('name')
            if name:
                valid_members[name.lower()] = name
            else:
                anon_key = f"anon #{member_id}"
                valid_members[anon_key] = f"Anon #{member_id}"

        # 4. Check Match
        input_lower = aoc_name.lower()
        if input_lower not in valid_members:
            await interaction.followup.send(
                f"🚫 **User Not Found:** The username `{aoc_name}` does not exist on the leaderboard.",
                ephemeral=True
            )
            return

        correct_name = valid_members[input_lower]

        # 5. Check if THIS AoC Name is already claimed by someone else
        # (Prevents two people from claiming the same leaderboard spot)
        existing_owner_ping = storage.get_discord_mention(correct_name)
        if existing_owner_ping != correct_name: # If it returned a ping, it's taken
             await interaction.followup.send(
                f"🚫 **Identity Conflict:** The user `{correct_name}` is already claimed by {existing_owner_ping}.",
                ephemeral=True
            )
             return

        # 6. Save
        success = storage.save_user(correct_name, interaction.user.id)
        
        if success:
            await interaction.followup.send(
                f"✅ **Identity Verified.** Linked `{correct_name}` to {interaction.user.mention}.",
                ephemeral=True
            )
        else:
            await interaction.followup.send("❌ **Database Error:** Could not save link.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(General(bot))