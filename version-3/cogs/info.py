import discord

from discord.ext.commands import Cog, command, group
from discord.ext import commands
from typing import Optional
from discord import Embed
import humanize
import datetime
from honored.config import Color

class Information(Cog):
    def __init__(self, bot) -> None:
        self.bot = bot 

    @commands.Cog.listener()
    async def on_message(self, message):
      view = discord.ui.View()
      button = discord.ui.Button(
          label="Invite",
          url="https://discord.com/api/oauth2/authorize?client_id=1123556084607627316&permissions=8&scope=bot"
      )
      view.add_item(button)
      if message.author == self.bot.user:
          return
      if self.bot.user in message.mentions and message.content.strip() == f"<@{self.bot.user.id}>":
          prefix = await self.bot.get_prefix(message)
          await message.channel.send(embed=discord.Embed(description=f"My prefix is `{prefix}`", color=Color.msg), view=view)
          return


  
    @command(
        name = 'help',
        description = '"Basic help command".',
        aliases = ['h'],
        usage = 'help (Command)',
        extras = 'help avatar',
        parameters = {
            "Command": commands.command
        }
    )
    async def help(self, ctx):
        await ctx.send('<https://honored.rip/commands>, server @ [server](https://honored.rip/discord)')


    @command(aliases=['inv'])
    async def invite(self, ctx):
        view = discord.ui.View()
        inv = discord.ui.Button(
        label="Invite",
          url="https://discord.com/api/oauth2/authorize?client_id=1123556084607627316&permissions=8&scope=bot"
    )
    

        sup = discord.ui.Button(
        label="Support",
        url="https://discord.gg/honoredbot"
       )
    
        view.add_item(inv)
        view.add_item(sup)
    
        await ctx.send(view=view)
      
    @command(aliases=['bi'])
    @commands.guild_only()
    async def botinfo(self, ctx):
      total_servers = len(self.bot.guilds)
      total_members = sum([guild.member_count for guild in self.bot.guilds])
      bot_creator1 = self.bot.get_user(1108907120788787243)
      bot_creator2 = self.bot.get_user(780652476427665408)

      view = discord.ui.View()
      button = discord.ui.Button(
          label="invite",
          url="https://discord.com/api/oauth2/authorize?client_id=1123556084607627316&permissions=8&scope=bot"
      )
      view.add_item(button)
    
      embed = discord.Embed(title="Bot Information", color=Color.msg)
      embed.add_field(name="Total Servers", value=total_servers, inline=True)
      embed.add_field(name="Total Members", value=total_members, inline=True)
      embed.add_field(name="Bot Creators", value=f"{bot_creator1.mention}\n{bot_creator2.mention}", inline=False)
      embed.set_footer(text="Thank you for using the bot!")
      await ctx.send(embed=embed, view=view)
    


    @commands.command(name="terms", aliases=['tos'])
    async def tos(self, ctx):
        await ctx.approve("a message has been sent to your dms")
        await ctx.author.send("here is our terms of service https://pastebin.com/qtaDUeRw")

    @commands.command(name="privacy")
    async def privacy(self, ctx):
        await ctx.approve("a message has been sent to your dms")
        await ctx.author.send("here is our privacy policy https://pastebin.com/3nd7NR1z")


    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
      cid = 1147912754066366574 



      channel = self.bot.get_channel(cid)
      if channel:
          await channel.send(f"Bot left guild: **{guild.name}** (**{guild.id}**)  {guild.member_count}")

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
      cid = 1147912754066366574 



      channel = self.bot.get_channel(cid)
      if channel:
          await channel.send(f"Bot joined guild: **{guild.name}** **{guild.id}**  {guild.member_count}")

    @commands.command(aliases=['creds'])
    async def credits(self, ctx):
      embed = discord.Embed(
        title='dev team:',
        description='<@1108907120788787243>\n<@780652476427665408>',
        color=Color.msg)


      
      embed.set_author(
        name='Honored credits',
        icon_url='https://cdn.discordapp.com/avatars/1123556084607627316/98e0aa9bb5d7e2d279a8bedf6941ad5b.png?size=1024'
      )

      await ctx.send(embed=embed)
            
async def setup(bot):
    await bot.add_cog(Information(bot))