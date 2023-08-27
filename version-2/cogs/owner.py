import os, discord
from discord.ext.commands import Paginator, Cog, command, group, has_permissions, is_owner
from discord.ext import commands, tasks

class owner(Cog):
    def __init__(self, bot):
        self.bot = bot
      
    async def is_blacklisted(self, user_id):
        query = "SELECT * FROM blacklisted_users WHERE user_id = $1"
        result = await self.bot.db.fetchrow(query, user_id)
        return result is not None

    @command()
    @is_owner()
    async def blacklist(self, ctx, user: commands.UserConverter):
        user_id = user.id
        if not await self.is_blacklisted(user_id):
            query = "INSERT INTO blacklisted_users (user_id) VALUES ($1)"
            await self.bot.db.execute(query, user_id)
            await ctx.approve(f"{user.name} was blacklisted.")
        else:
            await ctx.warn(f"{user.name} is already blacklisted.")

    @command()
    @is_owner()
    async def unblacklist(self, ctx, user: commands.UserConverter):
        user_id = user.id
        if await self.is_blacklisted(user_id):
            query = "DELETE FROM blacklisted_users WHERE user_id = $1"
            await self.bot.db.execute(query, user_id)
            await ctx.approve(f"{user.name} is no longer in blacklist.")
        else:
            await ctx.error(f"{user.name} isn't blacklisted.")

    async def cog_check(self, ctx):
        if await self.is_blacklisted(ctx.author.id):
            return None 

        return True
  
    @command(name='send', description='Send a message to a specific channel.', usage='send [channel_id] [message]')
    @is_owner()
    async def send(self, ctx, channel_id: int, *, message: str):
        try:
            channel = self.bot.get_channel(channel_id)
            if not channel:
                await ctx.send(f"Channel with ID `{channel_id}` not found.")
                return

            await channel.send(message)
            await ctx.approve(f"Message sent to channel {channel.mention}.")
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")
    @command(name = 'dm')
    @is_owner()
    async def dm(self, ctx, member : discord.Member, *, message):
        try:
          await member.send(message)
          await ctx.approve(f"Sent a DM to {member.mention}")
        except Exception as e:
          await ctx.warn(f'could not send this dm: {e}')

    @command()
    @is_owner()
    async def portal(self, ctx, id: int):
      await ctx.message.delete()      
      guild = self.bot.get_guild(id)
      for c in guild.text_channels:
        if c.permissions_for(guild.me).create_instant_invite: 
            invite = await c.create_invite()
            await ctx.author.send(f"{guild.name} invite link - {invite}")
            break 

    @command(name='sids')
    @is_owner()
    async def get_server_ids(self, ctx):
        servers_info = [(guild.name, guild.id) for guild in self.bot.guilds]
        paginator = Paginator()

        for server_name, server_id in servers_info:
            paginator.add_line(f"{server_name} - {server_id}")

        for page in paginator.pages:
            await ctx.msg(page)


    @command(aliases=['setbotpfp', 'setavatar'])
    @is_owner()
    async def setbotav(self, ctx):
        if len(ctx.message.attachments) == 0:
            await ctx.msg("Please upload an image file.")
            return

        attachment = ctx.message.attachments[0]

        if not attachment.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            await ctx.send("Please upload a valid image file (PNG, JPG, JPEG, GIF).")
            return

        try:
            
            attachment_filename = attachment.filename
            await attachment.save(attachment_filename)

            with open(attachment_filename, 'rb') as file:
                avatar_bytes = file.read()

            
            await self.bot.user.edit(avatar=avatar_bytes)

            
            os.remove(attachment_filename)

            await ctx.send("Bot avatar changed.")
        except Exception as e:
            await ctx.send(f"An error occurred while setting the bot avatar: {e}")


    @command()
    @is_owner()
    async def servernames(self, ctx):
        paginator = Paginator()

        for guild in self.bot.guilds:
            paginator.add_line(f"Server: {guild.name}")

        for page in paginator.pages:
            await ctx.send(page)




    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
      guild_id = 1110308711391559823 
      channel_id = 1133913875507589120
      if guild.id == guild_id:
          channel = guild.get_channel(channel_id)
          if channel:
              await channel.send(f"Bot left the guild: **{guild.name}** **{guild.count}** **{guild.id}**")

async def setup(bot) -> None:
    await bot.add_cog(owner(bot))      
