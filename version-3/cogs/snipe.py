import discord
from discord.ext import commands
import re
import datetime
from honored.config import Emoji, Color

class Snipe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.deleted_messages = {}

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.content:
            channel_id = message.channel.id
            if channel_id not in self.deleted_messages:
                self.deleted_messages[channel_id] = []

            content = message.content
            if self.contains_invite_link(content):
                content = f" {Emoji.warn} This message contains an invite link."

            self.deleted_messages[channel_id].append((content, message.author.name, message.created_at))

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.content != after.content:
            await self.on_message_delete(before)

    def contains_invite_link(self, content):
        invite_pattern = r"(discord\.gg/|discord\.com\/invite/|discordapp\.com\/invite\/)[a-zA-Z0-9]+"
        return bool(re.search(invite_pattern, content))

    @commands.command(aliases=['s'])
    async def snipe(self, ctx, index: int = 1):
        channel_id = ctx.channel.id
        if channel_id in self.deleted_messages:
            deleted_list = self.deleted_messages[channel_id]
            total_deleted = len(deleted_list)
            if 1 <= index <= total_deleted:
                content, author, created_at = deleted_list[-index]

                embed = discord.Embed(description=content, color=Color.msg)
                embed.set_author(name=author)

                central_tz = datetime.timezone(datetime.timedelta(hours=-5))
                created_at_central = created_at.astimezone(central_tz)
                time_difference = datetime.datetime.now(central_tz) - created_at_central

                embed.set_footer(text=f"{index}/{total_deleted}  |  {created_at_central.strftime('%I:%M %p')}")

                await ctx.send(embed=embed)
            else:
                await ctx.deny("Invalid message.")
        else:
            await ctx.warn("No recently deleted messages to snipe.")


async def setup(bot):
    await bot.add_cog(Snipe(bot))