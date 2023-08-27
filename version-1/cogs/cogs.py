import discord, aiohttp, os
import asyncio, time

from discord.ext import commands, tasks



class utility(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        super().__init__()
    
    @commands.command(
        name = 'purge',
        description = 'Deletes a certain amount of messages',
        aliases = ['c', 'clear'],
        usage = 'Syntax: purge[clear, prune] <trigger / optional> <amount>\nExample: purge[clear, prune] hi 100'
    )
    @commands.has_permissions(manage_messages=True)
    async def prune(self, ctx, amount: int=None):
        if amount is None: 
            amount = 100
            await ctx.send(ctx, f'{ctx.author.mention}, Limit not specified, Clearing **100** messages.')
            await asyncio.sleep(2)
            await ctx.channel.purge(limit=100)
        try:
            await ctx.channel.purge(limit=amount + 1)
            await ctx.send(ctx, f'{ctx.author.mention}, Cleared **{amount}** Messages from {ctx.channel.mention}.')
        except Exception as e:
            return await ctx.send(
                embed = discord.Embed(
                    description = f'> {ctx.author.mention}, cleared **{amount}** messages from {ctx.channel.mention}',
                    
                )
            )
          
async def setup(bot):
    await bot.add_cog(utility(bot))
