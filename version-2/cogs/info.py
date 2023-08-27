import discord

from discord.ext.commands import Cog, command, group
from discord.ext import commands
from typing import Optional
from discord import Embed
import humanize
from datetime import datetime

class Information(Cog):
    def __init__(self, bot) -> None:
        self.bot = bot 
      

    @command(
        name = 'help',
        description = '"Basic help command".',
        aliases = ['h'],
        usage = 'help (Command)',
        extras = 'help avatar',
        parameters = {
            "Command": commands.command
        }
    )
    async def help(self, ctx):
            return await ctx.approve(
                "view the support server [here](https://discord.gg/naza)"
            )

    @command()
    async def afk(self, ctx, *, reason="AFK"):      
        ts = int(datetime.datetime.now().timestamp())   
        result = await self.bot.db.fetchrow("SELECT * FROM afk WHERE guild_id = $1 AND user_id = $2", ctx.guild.id, ctx.author.id) 
        if result is None:
            await self.bot.db.execute("INSERT INTO afk (guild_id, user_id, reason, afk_timestamp) VALUES ($1, $2, $3, $4)", ctx.guild.id, ctx.author.id, reason, ts)
            await ctx.msg(f"You're now AFK with the status: **{reason}**")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        result = await self.bot.db.fetchrow("SELECT * FROM afk WHERE guild_id = $1 AND user_id = $2", message.guild.id, message.author.id)
        if result:
            await self.bot.db.execute("DELETE FROM afk WHERE guild_id = $1 AND user_id = $2", message.guild.id, message.author.id)
            elapsed_time = datetime.datetime.now() - datetime.datetime.fromtimestamp(result['afk_timestamp'])
            await message.channel.send(f"Welcome back, you were AFK for {humanize.naturaldelta(elapsed_time)}.\nStatus: {result['reason']}")

            
async def setup(bot):
    await bot.add_cog(Information(bot))
