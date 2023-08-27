import discord
import asyncio
from discord.ext.commands import Cog, command, group, has_permissions

class Discrim(Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.discrim_enabled = True
        
    @Cog.listener()
    async def on_member_update(self, before, after):
        if self.discrim_enabled and before.discriminator != after.discriminator:
            for guild in self.bot.guilds:
                check = await self.bot.db.fetchrow('SELECT channel FROM discrim WHERE Guild = $1', guild.id)
                if check:
                    channel = self.bot.get_channel(check['channel'])
                    await channel.send(
                        f"**{after.name}#{after.discriminator}** is now available"
                    )
    
    @group(
        name='discrim',
        aliases=[
            'tracker', 
            'tags',
        ],
      )
    async def discrim(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(title='Discrim')
            embed.add_field(name='add', value='Adds a discrim channel.', inline=False)
            embed.add_field(name='stop', value='Stops tracking discrim.', inline=False)
            await ctx.send(embed=embed)

    @discrim.command()
    @has_permissions(manage_channels=True)
    async def add(
        self, ctx, *,
        channel: discord.TextChannel | discord.Thread = None
    ):
        if not channel: 
            return await ctx.warn(
                f"{ctx.author.mention}: "
                "You haven't provided a channel."
            )
        try:
            check = await self.bot.db.fetch('SELECT * FROM discrim WHERE Guild = $1', ctx.guild.id)
            if not check:
                await self.bot.db.execute(
                    'INSERT INTO discrim (guild, channel) VALUES ($1, $2);', 
                    ctx.guild.id, channel.id
                )
            if check:
                await self.bot.db.execute(
                    'UPDATE discrim SET channel = $1 WHERE guild = $2',
                    channel.id, ctx.guild.id
                )
            await ctx.approve(
                f"{ctx.author.mention}: {f'Updated **{channel.name}** for' if check else 'Now logging'} "
                f"usernames in {channel.mention}."
            )
        except Exception as e:
            await ctx.warn(
                f"{ctx.author.mention}: Could not do this operation: "
                f"{e}"
            )

    @discrim.command()
    @has_permissions(manage_channels=True)
    async def stop(self, ctx):
        self.discrim_enabled = False
        await ctx.approve("username tracking has stopped.")



async def setup(bot):
    await bot.add_cog(Discrim(bot))
