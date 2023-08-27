import discord
from discord.ext import commands, tasks

class BanError(commands.CommandError):
    def __init__(self, message):
        self.message = message
      
class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
      name = 'ban',
      description = 'bans a member',
      aliases = ['b'],
    )
    @commands.has_permissions(ban_members=True)
    @commands.guild_only()
    async def ban(self, ctx, member: discord.Member, *, reason = None):
        if member == ctx.author:
            raise BanError('You cannot ban yourself.')
        elif member == self.bot.user:
            raise BanError('I cannot ban myself.')

        await member.ban(reason=reason)
        await ctx.send(embed = discord.Embed(description = f"> {member.mention} has been banned for {reason}"))

    @ban.error
    async def ban_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send('You do not have permission to ban members.')
        elif isinstance(error, commands.BadArgument):
            await ctx.send('Invalid member.')
        elif isinstance(error, BanError):
            await ctx.send(error.message)
          
class mod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
            
       
    @commands.command(
      name='unban', 
      description='Unbans a member', 
      aliases=['ub'],)
    @commands.has_permissions(ban_members=True)
    @commands.guild_only()
    async def unban(self, ctx, *, member):
          banned_users = await ctx.guild.bans()
          member_name, member_discriminator = member.split('#')

          for ban_entry in banned_users:
            user = ban_entry.user
            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                await ctx.send(embed=discord.Embed(description=f'> {member} has been unbanned.'))
            return

            # If the member was not found in the ban list
            await ctx.send(embed=discord.Embed(description='> Member not found in the ban list.'))

async def setup(bot):
    await bot.add_cog(Moderation(bot))
    await bot.add_cog(mod(bot))
