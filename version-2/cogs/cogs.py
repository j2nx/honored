import discord, aiohttp
import asyncio, time
from discord.ext.commands import Cog, command, group, has_permissions, guild_only, MemberConverter, BadArgument, MissingPermissions
from discord.ext import commands, tasks
from jishaku.types import ContextA
from jishaku.math import mean_stddev
import typing
from typing import Optional
import datetime
from datetime import timezone
from honored.checks import Perms
from discord import Embed, Forbidden
import humanize
from honored.config import Emoji

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

    @commands.Cog.listener()
    async def on_message(self, message):
      if message.author == self.bot.user:
          return

      if self.bot.user in message.mentions and message.content.strip() == f"<@{self.bot.user.id}>":

          prefix = await self.bot.get_prefix(message)
          await message.channel.send(f"My prefix is `{prefix}`")
          return

    async def is_user_blacklisted(self, user_id):
        query = "SELECT user_id FROM blacklisted_users WHERE user_id = $1"
        result = await self.bot.db.fetchrow(query, user_id)
        return result is not None
          
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


    @command(
        name='role',
        description='Adds or removes a role from a person',
        usage='role (member) (role)',
    )
    @has_permissions(manage_roles=True)
    @guild_only()
    async def role(self, ctx, member: discord.Member = None, *, role: PartialRole):
        if member is None or not role:
            embed = discord.Embed(title='role').set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
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
        return

    @role.error
    async def role_error(self, ctx, error):
        if isinstance(error, MissingPermissions):
            await self.missing_permissions(ctx, 'manage_roles')
        if isinstance(error, commands.BadArgument):
            await ctx.deny(error)

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
    async def ban(self, ctx, member: MemberConverter = None, *, reason="No reason provided."):
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
            await ctx.send(f"{member} has been banned | {reason}")
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
            embed = discord.Embed(title='unban').set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
            embed.add_field(
                name='Permissions',
                value="ban_members"
            )
            embed.add_field(
                name='Usage',
                value=(
                    f"```bf\nSyntax: -unban (member)\n"
                    f"Example: -unban yurrion```"
                )
            )
            await ctx.send(embed=embed)
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
      
    @command()
    @has_permissions(manage_messages=True)
    @guild_only()
    async def mute(self, ctx, member: discord.Member = None, *, reason=None):
      if member is None:
        embed = Embed(title='mute').set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
        embed.add_field(
            name='Permissions',
            value="manage_messages"
        )
        embed.add_field(
            name='Usage',
            value=(
                f"```bf\nSyntax: -mute (member)\n"
                f"Example: -mute @yurrion```"
            )
        )
        await ctx.send(embed=embed)
        return
        if member == ctx.author:
            await ctx.deny("You cannot mute yourself.")
            return

        if member == self.bot.user:
            await ctx.deny("I cannot mute myself.")
            return

        if ctx.author.top_role <= member.top_role:
            await ctx.deny("You cannot mute a member with the same or higher role than yourself.")
            return

        muted_role = discord.utils.get(ctx.guild.roles, name="HonoredMuted")
        if not muted_role:
           await ctx.warn('you do not have muted roles set. Please setup muted roles by doing **setupmute**')
        try:
            await member.add_roles(muted_role, reason=reason)
            await ctx.approve(f"{member.mention} has been muted. Reason: {reason}")
        except discord.Forbidden:
            await ctx.deny("I don't have permission to manage roles.")
        except discord.HTTPException:
            await ctx.warn("An error occurred while trying to mute the member.") 

    @mute.error
    async def mute_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await self.missing_permissions(ctx, 'manage_messages')
  
    @command()
    @has_permissions(manage_roles=True)
    @guild_only()
    async def setupmute(self, ctx):
        muted_role = discord.utils.get(ctx.guild.roles, name="HonoredMuted")
        if muted_role:
            await ctx.deny("The 'Muted' role already exists.")
            return

        try:
            
            muted_role = await ctx.guild.create_role(name="HonoredMuted")

            
            for channel in ctx.guild.text_channels:
                await channel.set_permissions(muted_role, send_messages=False)

            await ctx.approve("The 'HonoredMuted' role has been created and set up successfully.")
        except discord.Forbidden:
            await ctx.deny("I don't have permission to manage roles.")
        except discord.HTTPException:
            await ctx.warn("An error occurred while trying to set up the 'Muted' role.")

    @setupmute.error
    async def setupmute_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await self.missing_permissions(ctx, 'manage_roles')
          
    @command(
        name='embed',
        description='Creates a discord embed',
        usage='-embed [text] [$v (optional)]',
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

        embed = discord.Embed(description=description)
        if image_url:
            embed.set_image(url=image_url)

        await ctx.send(embed=embed)


    @embed.error
    async def embed_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await self.missing_permissions(ctx, 'manage_guild')


    @command(
      name="rtt", 
      aliases=["ping"])
    @guild_only()
    async def jsk_rtt(self, ctx: ContextA):
        """
        Calculates Round-Trip Time to the API.
        """

        message = None


        api_readings: typing.List[float] = []

        websocket_readings: typing.List[float] = []


        for _ in range(6):
            
            text = "Calculating round-trip time...\n\n"
            text += "\n".join(f"Reading {index + 1}: {reading * 1000:.2f}ms" for index, reading in enumerate(api_readings))

            if api_readings:
                average, stddev = mean_stddev(api_readings)

                text += f"\n\nAverage: {average * 1000:.2f} \N{PLUS-MINUS SIGN} {stddev * 1000:.2f}ms"
            else:
                text += "\n\nNo readings yet."

            if websocket_readings:
                average = sum(websocket_readings) / len(websocket_readings)

                text += f"\nWebsocket latency: {average * 1000:.2f}ms"
            else:
                text += f"\nWebsocket latency: {self.bot.latency * 1000:.2f}ms"

            
            if message:
                before = time.perf_counter()
                await message.edit(content=text)
                after = time.perf_counter()

                api_readings.append(after - before)
            else:
                before = time.perf_counter()
                message = await ctx.send(content=text)
                after = time.perf_counter()

                api_readings.append(after - before)

            
            if self.bot.latency > 0.0:
                websocket_readings.append(self.bot.latency)

    @command(
      name='members',
      description='shows the amount of members the bot has')
    @guild_only()
    async def members(self, ctx):
        total_members = sum(guild.member_count for guild in self.bot.guilds)
        await ctx.approve(f"Total number of members in bot guilds: {total_members}")
      
    @command(
      name="guilds", 
      description="shows the amount of guilds the bot has")
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

        
        embed = discord.Embed(title="Server Info:")
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

        embed = discord.Embed(title=f"{separator}{guild.name}{separator} statistics")
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
            embed = Embed(title=f"{member.name}'s avatar", url=avatar_url)
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
            embed = Embed(title=f"{member.name}'s server avatar", url=avatar_url)
            embed.set_image(url=avatar_url)
            await ctx.send(embed=embed)
        else:
            await ctx.warn("This member doesn't have a server avatar set.")

    @command(aliases=['sicon'])
    @guild_only()
    async def servericon(self, ctx):
        icon_url = ctx.guild.icon
        if icon_url:
            embed = Embed(title=f"{ctx.guild.name}'s server icon", url=icon_url)
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
        
          embed = Embed(title=f"{user.name}'s banner", url=banner_url)
          embed.set_image(url=banner_url)
          await ctx.send(embed=embed)

    @command(aliases=['bi'])
    @guild_only()
    async def botinfo(self, ctx):
        total_servers = len(self.bot.guilds)
        total_members = sum([guild.member_count for guild in self.bot.guilds])
        bot_creator1 = self.bot.get_user(1108907120788787243)
        bot_creator2 = self.bot.get_user(780652476427665408)
        invite_link = "https://discord.com/api/oauth2/authorize?client_id=1123556084607627316&permissions=8&scope=bot"
    
        embed = Embed(title="Bot Information")
        embed.add_field(name="Total Servers", value=total_servers, inline=True)
        embed.add_field(name="Total Members", value=total_members, inline=True)
        embed.add_field(name="Bot Creators", value=f"{bot_creator1.mention}\n{bot_creator2.mention}", inline=False)
        embed.add_field(name="Bot Invite Link", value=f"[Invite Link]({invite_link})", inline=False)
        embed.set_footer(text="Thank you for using the bot!")
    
        await ctx.send(embed=embed)




    
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

    @command()
    @has_permissions(manage_messages=True)
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
            await self.missing_permissions(ctx, 'manage_messages')
          
    @command()
    @has_permissions(manage_messages=True)
    @guild_only()
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
            await self.missing_permissions(ctx, 'manage_messages')
  
    @command(description="changes the guild prefix", usage="[prefix]", help="config", brief="manage guild")
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
      await ctx.send("👍", delete_after=1)

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

        embed = discord.Embed(title=f"Roles in {guild.name} (Page {current_page + 1}/{total_pages})", description=roles_str)
        return embed
      
    @command(aliases=["setnick", "nick"])
    @has_permissions(manage_nicknames=True)
    async def nickname(self, ctx, member: discord.Member, *, nick: str=None):
      if nick == None or nick.lower() == "none": return await ctx.approve(f"cleared **{member.name}'s** nickname")
      await member.edit(nick=nick)
      return await ctx.approve(f"Changed **{member.name}'s** nickname to **{nick}**") 
          
    @nickname.error
    async def nicknane_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await self.missing_permissions(ctx, 'manage_nicknames')


    @command(name="nuke")
    @has_permissions(administrator=True)
    async def nuke(self, ctx):
        confirmation_message = await ctx.send("Are you sure you want to clone this channel? (y/n)")
        
        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel and message.content.lower() in ["y", "n"]
        
        try:
            response_message = await self.bot.wait_for("message", check=check, timeout=30)
        except asyncio.TimeoutError:
            await confirmation_message.delete()
            return await ctx.send("Nuke command timed out.")
        
        await confirmation_message.delete()
        
        if response_message.content.lower() == "y":
            channel = ctx.channel
            new_channel = await channel.clone(reason="channel cloned from nuke")
            await channel.edit(position=ctx.channel.position)
            await ctx.channel.delete()
            

            await new_channel.send("first")
        else:
            await ctx.send("Nuke command cancelled.")
async def setup(bot):
    await bot.add_cog(normal(bot))
