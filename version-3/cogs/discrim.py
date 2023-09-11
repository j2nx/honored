import discord
from discord.ext import commands
from honored.config import Color

class Discrim(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.name != after.name:
            for guild in self.bot.guilds:
                check = await self.bot.db.fetchrow('SELECT channel FROM username_tracking WHERE guild = $1', guild.id)
                if check:
                    channel = self.bot.get_channel(check['channel'])
                    await channel.send(
                        f"**{before}** is now available"
                    )
    
    @commands.group(
        name='usernames',
        aliases=[
            'name',
        ],
        description='Sets a username change tracking channel or removes one.'
    )
    async def username(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(title='Username Tracker', color=Color.msg)
            embed.add_field(name='setchannel', value='Sets the username change tracking channel for this guild.', inline=False)
            await ctx.send(embed=embed)

    @username.command(
        name='add',
        description='Sets the username change tracking channel for this guild.',
        usage='username setchannel #channel',
    )
    @commands.has_permissions(manage_channels=True)
    async def add(self, ctx, channel: discord.TextChannel | discord.Thread):
        guild_id = ctx.guild.id
        await self.bot.db.execute('INSERT INTO discrim (guild, channel) VALUES ($1, $2) ON CONFLICT (guild) DO UPDATE SET channel = $2', guild_id, channel.id)
        await ctx.approve(f"Tracking usernames in {channel.mention}.")

async def setup(bot):
    await bot.add_cog(Discrim(bot))