import discord
from discord.ext import commands

class PresenceFilterCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_keywords = {}  # Dictionary to store user-specific keywords

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Logged in as {self.bot.user.name}')

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
    user_id = after.id

    if user_id in self.user_keywords:
        keyword = self.user_keywords[user_id].lower()

        # Print activity names and keywords for debugging
        print(f"Activity Names: {[activity.name.lower() for activity in after.activities]}")
        print(f"Keyword: {keyword}")

        if any(keyword in activity.name.lower() for activity in after.activities):
            # Kick the user and send them a DM
            await after.send("You were kicked from the server for using a filtered keyword in your status.")
            await after.kick(reason="Filtered keyword in status")

    @commands.command(name="presencefilter", aliases=['pf'])
    async def presencefilter(self, ctx, keyword):
        # Store the user's keyword in the dictionary
        self.user_keywords[ctx.author.id] = keyword
        await ctx.send(f"{keyword} is now being filtered in statuses")

async def setup(bot):
    await bot.add_cog(PresenceFilterCog(bot))