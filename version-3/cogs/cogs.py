import discord, aiohttp
import asyncio
from discord.ext.commands import Cog, command, group, has_permissions, guild_only, MemberConverter, BadArgument, MissingPermissions
from discord.ext import commands, tasks
from jishaku.types import ContextA
from jishaku.math import mean_stddev
import typing
from typing import Union, Optional
import datetime
from datetime import timezone
from honored.checks import Perms
from discord import Embed, Forbidden
import humanize
from honored.config import Emoji, Color
import humanfriendly


class PartialRole(commands.RoleConverter):
    async def convert(self, ctx, argument):
        guild = ctx.guild
        if guild:
            lower_argument = argument.lower()
            for role in guild.roles:
                if lower_argument in role.name.lower():
                    return role
        raise BadArgument(f"Role '{argument}' not found.")

class normal(Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.auto_responses = {}

    async def missing_permissions(self, ctx, *perms):
        missing_perms = [perm for perm in perms if not getattr(ctx.channel.permissions_for(ctx.author), perm, False)]
        if missing_perms:
            formatted_perms = ", ".join(missing_perms)
            await ctx.warn(f"You're missing the permissions: `{formatted_perms}`")

  
    @command(
        name = 'purge',
        description = 'Deletes a certain amount of messages',
        aliases = ['c', 'clear'],
        usage = 'Syntax: purge[clear, prune] <trigger / optional> <amount>\nExample: purge[clear, prune] hi 100',
    )
    @has_permissions(manage_messages=True)
    @guild_only()
    async def prune(self, ctx, amount: int=None):
        if amount is None:
            embed = Embed(title='clear').set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
            embed.add_field(
                name='**aliases**',
                value="c, purge, prune"
            )
            embed.add_field(
                name='Permissions',
                value="manage_messages"
            )
            embed.add_field(
                name='Usage',
                value=(
                    f"```bf\nSyntax: -clear (amount)\n"
                    f"Example: -clear 100```"
                )
            )
            await ctx.send(embed=embed)
            return
        try:
            await ctx.channel.purge(limit=amount + 1)
            response_messagee = await ctx.approve(f'{ctx.author.mention}, Cleared **{amount}** Messages from {ctx.channel.mention}.')
        except Exception as e:
          await ctx.warn('there was an error clearing messages.')
        await asyncio.sleep(3)  
        await response_messagee.delete()
          
    @prune.error
    async def prune_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await self.missing_permissions(ctx, 'manage_messages')

    @command()
    @has_permissions(kick_members=True)
    @guild_only()
    async def kick(self, ctx, member: discord.Member = None, *, reason="No reason provided."):
      if member is None:
          embed = Embed(title='kick').set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
          embed.add_field(
              name='Permissions',
              value="kick_members"
          )
          embed.add_field(
              name='Usage',
              value=(
                  f"```bf\nSyntax: -kick (member)\n"
                  f"Example: -kick @yurrion```"
              )
          )
          await ctx.send(embed=embed)
          return

      if member == ctx.author:
          await ctx.deny("You cannot kick yourself.")
          return

      if member == self.bot.user:
          await ctx.deny("I cannot kick myself.")
          return

      if ctx.author.top_role <= member.top_role:
          await ctx.deny("You cannot kick a member with the same or higher role than you.")
          return

      try:
          await self.send_kick_dm(ctx.guild, member, reason, ctx.author)
      except discord.Forbidden:
          await ctx.deny("I don't have permission to send DMs to the user.")

      try:
          await member.kick(reason=reason + f"| moderater {ctx.author}")
          await ctx.approve(f"{member.mention} has been kicked from the server | {reason}")
      except discord.Forbidden:
          await ctx.deny("I don't have permission to kick members.")
      except discord.HTTPException:
          await ctx.warn("An error occurred while trying to kick the member.")

    async def send_kick_dm(self, guild, member, reason, moderator):
      try:
          embed = Embed(title="Kicked")
          embed.set_thumbnail(url=guild.icon)
          embed.add_field(name="You have been kicked from", value=f"{guild.name}", inline=False)
          embed.add_field(name="Moderator", value=f"{moderator.name}", inline=False)
          embed.add_field(name="Reason", value=f"{reason}" if reason else "None", inline=False)
          await member.send(embed=embed)
      except discord.Forbidden:
          pass

    @kick.error
    async def kick_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await self.missing_permissions(ctx, 'kick_members')

    @command(name='ban', description='Bans a member', aliases=['b'])
    @guild_only()
    @has_permissions(ban_members=True)
    async def ban(self, ctx, member: typing.Union[discord.Member, discord.User]=None, *, reason="No reason provided."):
      
        if member is None:
            embed = Embed(title='ban').set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
            embed.add_field(
                name='Permissions',
                value="ban_members"
            )
            embed.add_field(
                name='Usage',
                value=(
                    f"```bf\nSyntax: -ban (member)\n"
                    f"Example: -ban @yurrion```"
                )
            )
            await ctx.send(embed=embed)
            return

        if member == ctx.author:
            await ctx.send("You cannot ban yourself.")
            return

        if ctx.author.top_role <= member.top_role:
            await ctx.send("You cannot ban a member with the same or higher role than you.")
            return

        if member == self.bot.user:
            await ctx.send("I cannot be banned.")
            return

        try:
            await ctx.guild.ban(user=member, reason=reason + f" | Banned by {ctx.author}")
            await ctx.approve(f"{member} has been banned | {reason}")
            await self.send_dm(ctx.guild, member, reason, ctx.author)
        except Forbidden:
            await ctx.send(f"Failed to send a DM to {member}.")
        except BadArgument:
            await ctx.send("Invalid member provided. Please mention a user, use their username, or provide their user ID.")

    async def send_dm(self, guild, member, reason, moderator):
        try:
            embed = Embed(title="Banned")
            embed.set_thumbnail(url=guild.icon_url)
            embed.add_field(name="You have been banned in", value=f"{guild.name}", inline=False)
            embed.add_field(name="Moderator", value=f"{moderator.name}", inline=False)
            embed.add_field(name="Reason", value=f"{reason}" if reason else "None", inline=False)
            embed.set_footer(text="If you wish to dispute this punishment, please contact a moderator.")
            await member.send(embed=embed)
        except Forbidden:
            pass

    @ban.error
    async def ban_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await self.missing_permissions(ctx, 'ban_members')



    @command()
    @has_permissions(ban_members=True)
    @guild_only()
    async def unban(self, ctx: commands.Context, member: discord.User=None, *, reason: str="No reason provided"):
        if member is None:
            return

        try:
            await ctx.guild.unban(user=member, reason=reason + f" | unbanned by {ctx.author}")
            await ctx.approve(f"**{member}** has been unbanned.")
        except discord.NotFound:
            await ctx.warn(f"Couldn't find ban for **{member}**.")


    @unban.error
    async def unban_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await self.missing_permissions(ctx, 'ban_members')
          
    @command(
        name='embed',
        description='Creates a discord embed',
        usage='-embed (text) [$v imageurl]',
    )
    @has_permissions(manage_guild=True)
    @guild_only()
    async def embed(self, ctx, *, args=None):

        if args is None:
            embed = discord.Embed(title='Embed')
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
            embed.add_field(name='Permissions', value="manage_guild")
            embed.add_field(name='Usage', value="```bf\nSyntax: -embed (message) $v (imageurl)\nExample: -embed yooo $v (imageurl)```")
            await ctx.send(embed=embed)
            return

        description = args
        image_url = None

        if '$v' in args:
            description, image_url = args.split('$v', 1)
            description = description.strip()
            image_url = image_url.strip()

        embed = discord.Embed(description=description, color=Color.warn)
        if image_url:
            embed.set_image(url=image_url)

        await ctx.send(embed=embed)


    @embed.error
    async def embed_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await self.missing_permissions(ctx, 'manage_guild')


    @commands.command()
    async def ping(self, ctx):
        latency = round(self.bot.latency * 1000)
        await ctx.msg(f'took {latency}ms to ping local hot moms in your area')

    @command(
      name='members',
      description='shows the amount of members the bot has')
    @guild_only()
    async def members(self, ctx):
        total_members = sum(guild.member_count for guild in self.bot.guilds)
        await ctx.approve(f"Total number of members in bot guilds: {total_members}")
      
    @command(
      name="guilds", 
      description="shows the amount of guilds the bot has",
      aliases=['servers'])
    @guild_only()
    async def guilds_count(self, ctx):
        guilds_count = len(self.bot.guilds)
        await ctx.approve(f"I am in {guilds_count} guilds!")

    @command(
      name="serverinfo",
      description="shows the information for your server",
      aliases=["si"]
    )
    @guild_only()
    async def serverinfo(self, ctx):
        guild = ctx.guild

        

        server_id = guild.id
        server_owner = guild.owner
        server_created_at = int(ctx.guild.created_at.timestamp())
        
        member_count = guild.member_count
        online_members = len([member for member in guild.members])

        
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        category_channels = len(guild.categories)

        
        verification_level = str(guild.verification_level)

        
        server_icon_url = str(guild.icon) if guild.icon else None

        
        embed = discord.Embed(title="Server Info:", color=Color.warn)
        embed.set_thumbnail(url=server_icon_url)
        embed.add_field(name="Server ID", value=server_id, inline=False)
        embed.add_field(name="Owner", value=server_owner, inline=False)
        embed.add_field(name ="server created:", value=f"<t:{server_created_at}:R>", inline=False)
        embed.add_field(name="Members", value=f"Total: {member_count}", inline=False)
        embed.add_field(name="Channels", value=f"Text: {text_channels}\nVoice: {voice_channels}\nCategories: {category_channels}", inline=False)
        embed.add_field(name="Verification Level", value=verification_level, inline=False)

        await ctx.send(embed=embed)
    
    @command(aliases=["mc"])
    @guild_only()
    async def membercount(self, ctx, *, vanity_url: str = None):
        if vanity_url:
            try:
                invite = await self.bot.fetch_invite(vanity_url)
                guild = invite.guild
            except discord.NotFound:
                await ctx.warn("Vanity URL not found. Please check the provided URL.")
                return
            except discord.Forbidden:
                await ctx.deny("I don't have permission to fetch the server information.")
                return
            except discord.HTTPException:
                await ctx.send("An error occurred while trying to fetch the server information.")
                return
        else:
            guild = ctx.guild

        member_count = guild.member_count
        humans = sum(member.bot is False for member in guild.members)
        bots = sum(member.bot for member in guild.members)

        separator = "\u200b"

        embed = discord.Embed(title=f"{separator}{guild.name}{separator} statistics", color=Color.warn)
        embed.add_field(name="Total Members", value=str(member_count))
        embed.add_field(name="Humans", value=str(humans))
        embed.add_field(name="Bots", value=str(bots))
        embed.set_thumbnail(url=guild.icon)

        await ctx.send(embed=embed)
    
  
    @commands.command(
        name='avatar',
        aliases=["av", "pfp"]
    )
    @commands.guild_only()
    async def avatar(self, ctx, *, member: Optional[discord.User | discord.Member] = None):
        member = member or ctx.author
        avatar_url = member.avatar
        if avatar_url:
            embed = Embed(title=f"{member.name}'s avatar", url=avatar_url, color=Color.warn)
            embed.set_image(url=avatar_url)
            await ctx.send(embed=embed)
        else:
            await ctx.warn("This member doesn't have an avatar set.")

    @command(aliases=['sav', 'serveravatar'])
    @guild_only()
    async def memberavatar(self, ctx, *, member: discord.Member = None):
        member = member or ctx.author
        avatar_url = member.guild_avatar
        if avatar_url:
            embed = Embed(title=f"{member.name}'s server avatar", url=avatar_url, color=Color.warn)
            embed.set_image(url=avatar_url)
            await ctx.send(embed=embed)
        else:
            await ctx.warn("This member doesn't have a server avatar set.")

    @command(aliases=['sicon'])
    @guild_only()
    async def servericon(self, ctx):
        icon_url = ctx.guild.icon
        if icon_url:
            embed = Embed(title=f"{ctx.guild.name}'s server icon", url=icon_url, color=Color.msg)
            embed.set_image(url=icon_url)
            await ctx.send(embed=embed)
        else:
            await ctx.warn("This server has no icon set.")

          
    @command(
        name='banner',
        description='Shows a member banner',
        usage='banner (Member)',
    )

    @guild_only()
    async def banner(self, ctx, user: discord.Member = None):
      if user == None:
          user = ctx.author
      req = await self.bot.http.request(discord.http.Route("GET", "/users/{uid}", uid=user.id))
      banner_id = req["banner"]
      if banner_id:
          banner_url = f"https://cdn.discordapp.com/banners/{user.id}/{banner_id}?size=1024"
          
          embed = Embed(title=f"{user.name}'s banner", url=banner_url, color=Color.msg)
          embed.set_image(url=banner_url)
          await ctx.send(embed=embed)
      else:
          await ctx.warn("This member doesn't have an avatar set.")




    
    @command(aliases=['seticon'])
    @has_permissions(manage_guild=True)
    @guild_only()
    async def setservericon(self, ctx, image: str = None):
        if image is None and not ctx.message.attachments:
            embed = discord.Embed(title='seticon').set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
            embed.add_field(
                name='Permissions',
                value="manage_guild"
            )
            embed.add_field(
                name='Usage',
                value=(
                    f"```bf\nSyntax: -seticon (image/url)\n"
                    f"Example: -seticon (image/url)```"
                )
            )
            await ctx.send(embed=embed)
            return

        if image is not None and not image.startswith(("http://", "https://")):
            await ctx.send("Invalid image URL format.")
            return

        if image is None:
            image_url = ctx.message.attachments[0].url
        else:
            image_url = image

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(image_url) as response:
                    if response.status != 200:
                        await ctx.send("Failed to fetch the image from the provided URL.")
                        return

                    image_data = await response.read()
                    await ctx.guild.edit(icon=image_data)
                    await ctx.send("Server icon has been updated successfully.")
            except Exception as e:
                await ctx.send(f"An error occurred: {e}")

    @setservericon.error
    async def setservericon_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await self.missing_permissions(ctx, 'manage_guild')

              
    @command(aliases=['setbanner'])
    @has_permissions(manage_guild=True)
    @guild_only()
    async def setguildbanner(self, ctx, image: str = None):
        if image is None and not ctx.message.attachments:
            embed = discord.Embed(title='setbanner').set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
            embed.add_field(
                name='Permissions',
                value="manage_guild"
            )
            embed.add_field(
                name='Usage',
                value=(
                    f"```bf\nSyntax: -setbanner (imageurl)\n"
                    f"Example: -setbanner (imageurl)```"
                )
            )
            await ctx.send(embed=embed)
            return

        if image is not None and not image.startswith(("http://", "https://")):
            await ctx.warn("Invalid image URL format.")
            return

        if image is None:
            image_url = ctx.message.attachments[0].url
        else:
            image_url = image

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(image_url) as response:
                    if response.status != 200:
                        await ctx.warn("Failed to fetch the image from the provided URL.")
                        return

                    image_data = await response.read()
                    await ctx.guild.edit(banner=image_data)
                    await ctx.approve("Guild banner has been updated successfully.")
            except Exception as e:
                await ctx.send(f"An error occurred: {e}")

    @setguildbanner.error
    async def setguildbanner_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await self.missing_permissions(ctx, 'manage_guild')

    @group(invoke_without_command=True)
    @has_permissions(manage_channels=True)
    @guild_only()
    async def lock(self, ctx, channel: discord.TextChannel = None):
        channel = channel or ctx.channel

        
      
        if channel.overwrites_for(ctx.guild.default_role).send_messages is False:
            await ctx.msg(f" {Emoji.lock} {channel.mention} is already locked.")
            return

        
        overwrites = channel.overwrites_for(ctx.guild.default_role)
        overwrites.send_messages = False
        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrites)

        await ctx.msg(f"{Emoji.lock} {channel.mention} has been locked.")

    @lock.error
    async def lock_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await self.missing_permissions(ctx, 'manage_channels')

    @lock.command()
    @has_permissions(manage_channels=True)
    async def all(self, ctx):
      guild = ctx.guild
      for channel in guild.text_channels:
          await channel.set_permissions(ctx.guild.default_role, send_messages=False)
      await ctx.msg(f"{Emoji.lock} All text channels have been locked.")

    @all.error
    async def all_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await self.missing_permissions(ctx, 'manage_channels')
  
    @command()
    @Perms.get_perms("manage_guild")
    async def prefix(self, ctx, prefix: str):      
       if len(prefix) > 3: return await ctx.deny(" The prefix is too long")
       check = await self.bot.db.fetchrow("SELECT * FROM prefixes WHERE guild_id = {}".format(ctx.guild.id)) 
       if check is not None: await self.bot.db.execute("UPDATE prefixes SET prefix = $1 WHERE guild_id = $2", prefix, ctx.guild.id)
       else: await self.bot.db.execute("INSERT INTO prefixes VALUES ($1, $2)", ctx.guild.id, prefix)
       return await ctx.approve(f"guild prefix changed to `{prefix}`".capitalize())

    @prefix.error
    async def prefix_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await self.missing_permissions(ctx, 'manage_guild')

    @command(aliases=["bc", "botclear"])
    @has_permissions(manage_messages=True)
    async def botpurge(self, ctx, amount: int = None):
      if amount is None: 
        embed = Embed(title='botpurge').set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
        embed.add_field(
            name='**aliases**',
            value="bc, botclear"
        )
        embed.add_field(
            name='Permissions',
            value="manage_messages"
        )
        embed.add_field(
            name='Usage',
            value=(
                f"```bf\nSyntax: -bc (amount)\n"
                f"Example: -bc 100```"
            )
        )
        await ctx.send(embed=embed)
        return
        
      mes = [] 
      async for message in ctx.channel.history(): 
        if len(mes) == amount: break 
        if message.author.bot: mes.append(message)

      mes.append(ctx.message)       
      await ctx.channel.delete_messages(mes)   
      await ctx.send("👍", delete_after=2)

    @botpurge.error
    async def botpurge_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await self.missing_permissions(ctx, 'manage_messages')
  
    @command(aliases=['whois', 'wi', 'userinfo', 'user'])
    @guild_only()
    async def ui(self, ctx, member: discord.Member = None):
      member = member or ctx.author

      embed = discord.Embed(title="User Information", color=member.color)
      embed.set_thumbnail(url=member.avatar.url)
      embed.add_field(name="Name", value=member.name)
      embed.add_field(name="ID", value=member.id)
      embed.add_field(name="Created At",
                      value=member.created_at.strftime("%b %d, %Y %H:%M:%S UTC"))

      if member.top_role != member.guild.default_role:
        embed.add_field(name="Top Role", value=member.top_role.mention)
      embed.set_footer(text=f"Requested by {ctx.author.name}",
                       icon_url=ctx.author.avatar.url)
      await ctx.send(embed=embed)




    @command(name='roles', description='Shows all the roles in the guild')
    @guild_only()
    async def roles(self, ctx):
        guild = ctx.guild
        role_list = [role.name for role in sorted(guild.roles, key=lambda r: -r.position) if not role.is_default()]


        items_per_page = 10
        pages = [role_list[i:i+items_per_page] for i in range(0, len(role_list), items_per_page)]

        current_page = 0
        total_pages = len(pages)

        embed = self.create_embed(current_page, total_pages, pages[current_page], guild)
        message = await ctx.send(embed=embed)

        if total_pages > 1:
            await message.add_reaction('⬅️')
            await message.add_reaction('➡️')


        while True:
            try:
                reaction, user = await self.bot.wait_for(
                    'reaction_add',
                    timeout=60,
                    check=lambda reaction, user: user == ctx.author and reaction.message == message and str(reaction.emoji) in ['⬅️', '➡️']
                )
            except TimeoutError:
                break

            if str(reaction.emoji) == '⬅️':
                current_page = (current_page - 1) % total_pages
            elif str(reaction.emoji) == '➡️':
                current_page = (current_page + 1) % total_pages

            await message.edit(embed=self.create_embed(current_page, total_pages, pages[current_page], guild))
            await message.remove_reaction(reaction, user)

    def create_embed(self, current_page, total_pages, role_list, guild):
        roles_str = '\n'.join(role_list)

        embed = discord.Embed(title=f"Roles in {guild.name} (Page {current_page + 1}/{total_pages})", description=roles_str, color=Color.msg)
        return embed

    @commands.command(aliases=["setnick", "nick"])
    @commands.has_permissions(manage_nicknames=True)
    async def nickname(self, ctx, member: discord.Member, *, nick: str = None):
      if nick is None or nick.lower() in ["none", ""]:
          await member.edit(nick=None)
          return await ctx.approve(f"Cleared **{member.name}'s** nickname")
    
      await member.edit(nick=nick)
      return await ctx.approve(f"Changed **{member.name}'s** nickname to **{nick}**") 
          
    @nickname.error
    async def nicknane_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await self.missing_permissions(ctx, 'manage_nicknames')


    @commands.command(name="nuke")
    @has_permissions(administrator=True)
    async def nuke(self, ctx):
      confirmation_message = await ctx.send(embed=discord.Embed(description="Are you sure you want to clone this channel? (y/n)", color=Color.msg))
    
      if confirmation_message:
          def check(message):
              return message.author == ctx.author and message.channel == ctx.channel and message.content.lower() in ["y", "n"]
        
          try:
              response_message = await self.bot.wait_for("message", check=check, timeout=30)
          except asyncio.TimeoutError:
              await confirmation_message.delete()
              return await ctx.msg("Nuke command timed out.")
        
          await confirmation_message.delete()
        
          if response_message.content.lower() == "y":
              channel = ctx.channel
              new_c = await channel.clone(reason="channel cloned from nuke")
              await ctx.channel.edit(position=ctx.channel.position)
              await ctx.channel.delete()
              await new_c.send("first")
          else:
              await ctx.msg("Nuke command cancelled.")
    @nuke.error
    async def nuke_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await self.missing_permissions(ctx, 'administrator')


    @group()
    @has_permissions(manage_channels=True)
    async def channel(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(title='channel', color=Color.msg)
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
            embed.add_field(
                name='Permissions',
                value="manage_messages"
            )
            embed.add_field(
                name='Usage',
                value=(
                    f"```bf\nSyntax: -channel (create/delete) (name)\n"
                    f"Example: -channel create honored```"
                )
            )
            await ctx.send(embed=embed)

    @channel.error
    async def channel_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await self.missing_permissions(ctx, 'manage_channels')
  
    @channel.command(name="create")
    @has_permissions(manage_channels=True)
    async def create(self, ctx, channel_name: str):
        guild = ctx.guild
        category = ctx.channel.category

        new_channel = await guild.create_text_channel(channel_name, category=category)
        await ctx.msg(f"New channel '{new_channel.name}' has been created")

    @create.error
    async def create_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await self.missing_permissions(ctx, 'manage_channels')
          
    @channel.command(name="delete")
    @has_permissions(manage_channels=True)
    async def delete(self, ctx, channel: discord.TextChannel):
        await channel.delete()
        await ctx.msg(f"Channel '{channel.name}' has been deleted")

    @delete.error
    async def delete_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await self.missing_permissions(ctx, 'manage_channels')
  
    @channel.command(name="edit")
    @has_permissions(manage_channels=True)
    async def edit(self, ctx, channel: discord.TextChannel, *, new_name: str):
        await channel.edit(name=new_name)
        await ctx.msg(f"Channel '{channel.name}' has been renamed to '{new_name}'")

    @delete.error
    async def edit_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await self.missing_permissions(ctx, 'manage_channels')

    @command()
    @has_permissions(moderate_members=True)
    async def timeout(self, ctx, member: discord.Member, time: str = "60s", *, reason="No reason provided"):
      if member is None:
        await ctx.warn("specify the member you want to timeout")
        return
      if not member.is_timed_out():
        tim = humanfriendly.parse_timespan(time)
        until = discord.utils.utcnow() + datetime.timedelta(seconds=tim)
    
        await member.timeout(until, reason=reason + " | {}".format(ctx.author))
        await ctx.send(f"**{member}** has been timed out for {humanfriendly.format_timespan(tim)} | {reason}")
      else:
          await ctx.send(f"**{member}** is already timed out.")

    @timeout.error
    async def timeout_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await self.missing_permissions(ctx, 'moderate_members')

    @commands.command()
    @has_permissions(moderate_members=True)
    async def mute(self, ctx, *, member: discord.Member=None): 
      await ctx.invoke(self.bot.get_command("timeout"), member=member) 
    @mute.error
    async def mute_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await self.missing_permissions(ctx, 'moderate_members')
    @command()
    @has_permissions(moderate_members=True)
    async def untimeout(self, ctx, member: discord.Member):
      if member is None:
        await ctx.warn("specify the member you want to untimeout")
        return
      if member.is_timed_out():
        await member.untimeout()
        await ctx.send(f"**{member}** has been untimed out.")
      else:
          await ctx.send("This member is not timed out.")
    @untimeout.error
    async def untimeout_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await self.missing_permissions(ctx, 'moderate_members')

    @commands.command()
    @has_permissions(moderate_members=True)
    async def unmute(self, ctx, member: discord.Member, *, reason: str = "No reason provided"): 
      await ctx.invoke(self.bot.get_command("untimeout"), member=member) 
      
    @command(name='hide')
    @has_permissions(manage_channels=True)
    async def hidechannel(self, ctx):
        channel = ctx.channel
        await channel.set_permissions(ctx.guild.default_role, view_channel=False)
        await ctx.msg(f"{channel.mention} is now hidden.")


    @command(name='unhide')
    @has_permissions(manage_channels=True)
    async def unhidechannel(self, ctx):
        channel = ctx.channel
        await channel.set_permissions(ctx.guild.default_role, view_channel=True)
        await ctx.msg(f"{channel.mention} is now unhidden.")

    @command(aliases=['vu'])
    @guild_only()
    async def vanityuses(self, ctx):
          try:
            vanity_info = await ctx.guild.vanity_invite()
            if vanity_info:
                vanity_url = vanity_info.code
                total_uses = vanity_info.uses
                await ctx.approve(f"The vanity /{vanity_url} has been used {total_uses} times.")
            else:
                await ctx.deny("This server does not have a vanity URL set.")
          except discord.Forbidden:
            await ctx.deny('I do not have permissions to view this vanity url')


    @commands.command(name="autoresponder", aliases=["ar"])
    async def add_autoresponder(self, ctx, *, args):

      guild_id = ctx.guild.id
    

      if guild_id not in self.auto_responses:
          self.auto_responses[guild_id] = {}


      args = args.split(',')

      if len(args) != 2:
          await ctx.send(".")
          return

      keyword = args[0].strip().lower()
      response = args[1].strip()


      self.auto_responses[guild_id][keyword] = response
      await ctx.send(f"Autoresponder added for '{keyword}': {response}")

    @commands.Cog.listener()
    async def on_message(self, message):
      if message.author == self.bot.user:
          return

      content = message.content.lower()
      guild_id = message.guild.id
    

      if guild_id in self.auto_responses:

          for keyword, response in self.auto_responses[guild_id].items():
              if keyword in content:
                  await message.channel.send(response)

async def setup(bot):
    await bot.add_cog(normal(bot))