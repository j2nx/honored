import discord
from discord.ext import commands
import random
from honored.config import Color
import asyncio

class banners(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild_id = None
        self.channel_id = None

    async def missing_permissions(self, ctx, *perms):
        missing_perms = [perm for perm in perms if not getattr(ctx.channel.permissions_for(ctx.author), perm, False)]
        if missing_perms:
            formatted_perms = ", ".join(missing_perms)
            await ctx.warn(f"You're missing the permissions: `{formatted_perms}`")

    def randnum(self, fname):
        lines = open(fname).read().splitlines()
        return random.choice(lines)

    async def save(self, guild_id, channel_id):
        query = "INSERT INTO banners (guild_id, channel_id) VALUES ($1, $2)"
        await self.bot.db.execute(query, guild_id, channel_id)

    async def delete(self, guild_id, channel_id):
        query = "DELETE FROM banners WHERE guild_id = $1 AND channel_id = $2"
        await self.bot.db.execute(query, guild_id, channel_id)

    async def send_banners(self, ctx):
        while await self.is_send(self.guild_id, self.channel_id): 
            url = self.randnum('banners.txt')

            embed = discord.Embed(title="", color=Color.msg)
            embed.set_image(url=url)

            await ctx.send(embed=embed)
            await asyncio.sleep(10)

    async def is_send(self, guild_id, channel_id):
        query = "SELECT * FROM banners WHERE guild_id = $1 AND channel_id = $2"
        result = await self.bot.db.fetchrow(query, guild_id, channel_id)
        return bool(result)

    @commands.command(aliases=['autobanners', 'autobanner'])
    @commands.has_permissions(manage_channels=True)
    async def banners(self, ctx, channel: discord.TextChannel = None):
      try:
        check = await self.bot.db.fetch('SELECT * from banners WHERE guild_id = $1 AND channel_id = $2', ctx.guild.id, ctx.channel.id)
        if check:
          await ctx.deny("banners are already running")
          return

        if channel is None:
            channel = ctx.channel

        self.guild_id = ctx.guild.id
        self.channel_id = channel.id
        await self.is_send(self.guild_id, self.channel_id)
        await self.save(self.guild_id, self.channel_id)
        await ctx.approve(f'Sending banners in {ctx.channel.mention}')

        await self.send_banners(ctx)
      except Exception as e:
          print(f'failed to send banners {e}')
          return await self.send_banners(ctx)

    @banners.error
    async def banners_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await self.missing_permissions(ctx, 'manage_channels')

    @commands.command(aliases=['bannersstop'])
    @commands.has_permissions(manage_channels=True)
    async def stopbanners(self, ctx):
      try:
        check = await self.bot.db.fetch('SELECT * from banners WHERE guild_id = $1 AND channel_id = $2', ctx.guild.id, ctx.channel.id)
        if not check:
          await ctx.deny("banners are not running")
          return

        await self.delete(self.guild_id, self.channel_id)
        await ctx.reply("**Stopping banners**")
      except Exception as e:
        await ctx.deny('failed to turn off pfps')

    @stopbanners.error
    async def stopbanners_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await self.missing_permissions(ctx, 'manage_channels')

async def setup(bot):
    await bot.add_cog(banners(bot))