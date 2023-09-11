import os, discord
from discord.ext.commands import Paginator, Cog, command, group, has_permissions, is_owner
from discord.ext import commands, tasks

class owner(Cog):
    def __init__(self, bot):
        self.bot = bot
      

  
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



    @command(name='setstream')
    @is_owner()
    async def set_stream(self, ctx, *, stream_title):
        
        await self.bot.change_presence(activity=discord.Streaming(name=stream_title, url="https://www.twitch.tv/discord"))
        await ctx.send(f"Stream title set to: {stream_title}")


    @command(name='leave')
    @is_owner()
    async def leaveserver(self, ctx, server_id: int = None):
        if server_id:
            guild = self.bot.get_guild(server_id)
            if guild:
              await guild.leave()
              await ctx.msg("leaving server...")
            else:
                await ctx.msg("Couldn't find a server with that ID.")
        else:
            await ctx.msg("Leaving the server...")
            await ctx.guild.leave()




async def setup(bot) -> None:
    await bot.add_cog(owner(bot))      