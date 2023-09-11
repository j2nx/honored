import discord
from discord.ext import commands
import datetime
from datetime import timezone
import humanize
from honored.config import Color
class Antinuke(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.anti_bot_enabled = False
        self.ban_cache = {}
      
    @commands.Cog.listener()
    async def on_member_join(self, member):
        if self.anti_bot_enabled and member.bot:
            await member.ban(reason="AntiNuke: Bot added to server without whitelist")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def antibot(self, ctx):
        self.anti_bot_enabled = not self.anti_bot_enabled
        status = "on" if self.anti_bot_enabled else "off"
        await ctx.msg(f"Antibot feature has been turned {status}.")
        if status.lower() not in ["on", "off"]:
          await ctx.msg("please use either on or off")

    @commands.command()
    async def afk(self, ctx, *, reason="AFK"):      
        ts = int(datetime.datetime.now().timestamp())   
        result = await self.bot.db.fetchrow("SELECT * FROM afk WHERE guild_id = $1 AND user_id = $2", ctx.guild.id, ctx.author.id) 
        if result is None:
          await self.bot.db.execute("INSERT INTO afk (guild_id, user_id, reason, time) VALUES ($1, $2, $3, $4)", ctx.guild.id, ctx.author.id, reason, ts)
          await ctx.msg(f"You're now AFK with the status: **{reason}**")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

            mentioned_users = message.mentions
            for user in mentioned_users:
                result = await self.bot.db.fetchrow("SELECT * FROM afk WHERE guild_id = $1 AND LOWER(user_id) = LOWER($2)", message.guild.id, user.id)
                if result:
                    elapsed_time = datetime.datetime.now() - datetime.datetime.fromtimestamp(result['time'])
                    afk_message = f"{user.display_name} is AFK for {humanize.naturaldelta(elapsed_time)}. Status: {result['reason']}"
                    await message.channel.send(afk_message)
    
            result = await self.bot.db.fetchrow("SELECT * FROM afk WHERE guild_id = $1 AND user_id = $2", message.guild.id, message.author.id)
            if result:
                await self.bot.db.execute("DELETE FROM afk WHERE guild_id = $1 AND user_id = $2", message.guild.id, message.author.id)
                elapsed_time = datetime.datetime.now() - datetime.datetime.fromtimestamp(result['time'])
                await message.channel.send(embed = discord.Embed(description=f"Welcome back, you were AFK for {humanize.naturaldelta(elapsed_time)}.\nStatus: {result['reason']}", color=Color.msg))


async def setup(bot):
    await bot.add_cog(Antinuke(bot))
