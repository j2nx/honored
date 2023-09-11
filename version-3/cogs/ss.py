import discord
from discord.ext import commands 
import requests
from honored.config import Color, Emoji
from cogs.cogs import PartialRole
from bs4 import BeautifulSoup

class ss(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log = 1147912754066366574

    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        log = discord.Embed(description=f"command {ctx.prefix}{ctx.command} was used in guild {ctx.guild.name}: {ctx.guild.id} by {ctx.author.mention}", color=Color.msg)
        await self.bot.get_channel(self.log).send(embed=log)

  
    async def missing_permissions(self, ctx, *perms):
        missing_perms = [perm for perm in perms if not getattr(ctx.channel.permissions_for(ctx.author), perm, False)]
        if missing_perms:
            formatted_perms = ", ".join(missing_perms)
            await ctx.warn(f"You're missing the permissions: `{formatted_perms}`")
  
    @commands.group(name='role', invoke_without_command=True)
    @commands.has_permissions(manage_roles=True)
    async def role(self, ctx, member: discord.Member = None, *, role: PartialRole = None):
        try:
            if member is None or role is None:
                embed = discord.Embed(title='role', color=Color.msg).set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
                embed.add_field(
                    name='Permissions',
                    value="manage_roles"
                )
                embed.add_field(
                    name='Usage',
                    value=(
                        f"```bf\nSyntax: -role (member) (role)\n"
                        f"Example: -role @yurrion honored```"
                    )
                )
                await ctx.send(embed=embed)
                return
            
            if role in member.roles:
                await member.remove_roles(role)
                await ctx.approve(f"{role.mention} has been removed from {member.mention}.")
            else:
                await member.add_roles(role)
                await ctx.approve(f"{member.mention} has been given {role.mention}")
            
            if role is None:
                await ctx.deny(f"No role named '{role}' found.")
        
        except discord.Forbidden:
            await ctx.deny("I don't have 'manage_roles' permissions")

      
    @role.error
    async def role_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await self.missing_permissions(ctx, 'manage_roles')
        if isinstance(error, commands.BadArgument):
            await ctx.deny(error)

  
    @role.command(name='create')
    @commands.has_permissions(manage_roles=True)
    async def createrole(self, ctx, *, role_name: str=None):
          try:
            role = await ctx.guild.create_role(name=role_name)
            await ctx.approve(f"Role `{role.name}` has been created.")
          except discord.Forbidden:
            await ctx.deny("I don't have permission to create roles.")
    @createrole.error
    async def createrole_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await self.missing_permissions(ctx, 'manage_roles')
  
    @role.command(name='edit')
    @commands.has_permissions(manage_roles=True)
    async def roleedit(self, ctx, role: discord.Role, *, new_name: str):
        try:
            await role.edit(name=new_name)
            await ctx.approve(f"Role `{role.name}` has been edited to `{new_name}`.")
        except discord.Forbidden:
            await ctx.deny("I don't have permission to edit roles.")

    @roleedit.error
    async def roleedit_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await self.missing_permissions(ctx, 'manage_roles')
  
    @role.command(name='delete')
    @commands.has_permissions(manage_roles=True)
    async def rdelete(self, ctx, role: discord.Role):
        try:
            await role.delete()
            await ctx.approve(f"Role `{role.name}` has been deleted.")
        except discord.Forbidden:
            await ctx.deny("I don't have permission to delete roles.")

    @rdelete.error
    async def rdelete_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await self.missing_permissions(ctx, 'manage_roles')


    @commands.group(invoke_without_command=True)
    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    async def unlock(self, ctx, channel: discord.TextChannel = None):
        channel = channel or ctx.channel

        
      
        if channel.overwrites_for(ctx.guild.default_role).send_messages is True:
            await ctx.msg(f" {Emoji.unlock} {channel.mention} is already unlocked.")
            return

        
        overwrites = channel.overwrites_for(ctx.guild.default_role)
        overwrites.send_messages = True
        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrites)

        await ctx.msg(f" {Emoji.unlock} {channel.mention} has been unlocked.")

    @unlock.error
    async def unlock_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await self.missing_permissions(ctx, 'manage_channels')
  
    @unlock.command()
    @commands.has_permissions(manage_channels=True)

    async def all(self, ctx):
      guild = ctx.guild
      for channel in guild.text_channels:
          await channel.set_permissions(ctx.guild.default_role, send_messages=True)
      await ctx.msg(f"{Emoji.lock} All text channels have been unlocked.")

    @all.error
    async def all_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await self.missing_permissions(ctx, 'manage_channels')

    @commands.command(name="tiktok", aliases=['tt'])
    async def get_tiktok_info(self, ctx, username):
        # Create a TikTok URL based on the provided username
        url = f"https://tiktok.com/@{username}"
        
        # Send a request to the TikTok URL
        response = requests.get(url)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            

            follower_count = soup.find('span', {'class': 'follower-count'})
            following_count = soup.find('span', {'class': 'following-count'})
            like_count = soup.find('span', {'class': 'like-count'})

            print(f"Follower Count: {follower_count}")
            print(f"Following Count: {following_count}")
            print(f"Like Count: {like_count}")
async def setup(bot):
  await bot.add_cog(ss(bot))