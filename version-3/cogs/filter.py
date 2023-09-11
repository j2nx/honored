import discord
from discord.ext import commands
from honored.checks import Perms
from discord import Embed
from discord.ext.commands import Cog, command, group, has_permissions, is_owner, Paginator
import discord
from discord.ext import commands
from honored.config import Color
class Filter(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    async def missing_permissions(self, ctx, *perms):
        missing_perms = [perm for perm in perms if not getattr(ctx.channel.permissions_for(ctx.author), perm, False)]
        if missing_perms:
            formatted_perms = ", ".join(missing_perms)
            await ctx.warn(f"You're missing the permissions: `{formatted_perms}`")

  
    async def get_filtered_keywords(self, guild_id):
        query = "SELECT keyword FROM filtered_keywords WHERE guild_id = $1"
        rows = await self.bot.db.fetch(query, guild_id)
        return [row['keyword'] for row in rows]

    async def add_filtered_keyword(self, guild_id, keyword):
        query = "INSERT INTO filtered_keywords (guild_id, keyword) VALUES ($1, $2)"
        await self.bot.db.execute(query, guild_id, keyword)

    async def remove_filtered_keyword(self, guild_id, keyword):
        query = "DELETE FROM filtered_keywords WHERE guild_id = $1 AND keyword = $2"
        await self.bot.db.execute(query, guild_id, keyword)

    @commands.group(invoke_without_command=True)
    @commands.has_permissions(manage_messages=True)
    async def filter(self, ctx):
        """Group command to manage message filtering."""
        await ctx.channel.typing()
        embed = Embed(title='filter', color=Color.msg).set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
        embed.add_field(
            name='Permissions',
            value="manage_messages"
        )
        embed.add_field(
            name='Usage',
            value=(
                f"```bf\nSyntax: -filter add/remove (-filter list)\n"
                f"Example: -filter add/remove yurrion```"
            )
        )
        await ctx.send(embed=embed)

    @filter.command(name="add")
    @has_permissions(manage_messages=True)
    async def add_filter(self, ctx, keyword):
        """Set the keyword to watch for and filter messages."""
        keyword = keyword.lower()
        guild_id = ctx.guild.id
        await ctx.channel.typing()
        await self.add_filtered_keyword(guild_id, keyword)
        await ctx.approve(f"Now filtering '{keyword}'")

    @add_filter.error
    async def add_filter_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await self.missing_permissions(ctx, 'manage_messages')

    @filter.command(name="remove")
    @has_permissions(manage_messages=True)
    async def remove_filter(self, ctx, keyword):
        """Remove the keyword from the message filtering."""
        keyword = keyword.lower()
        guild_id = ctx.guild.id
        await ctx.channel.typing()
        await self.remove_filtered_keyword(guild_id, keyword)
        await ctx.approve(f"Removed '{keyword}' from the filter list.")

    @remove_filter.error
    async def remove_filter_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await self.missing_permissions(ctx, 'manage_messages')

    @filter.command(name="list")
    @has_permissions(manage_messages=True)
    async def list_filters(self, ctx):
        """Show the list of filtered keywords using pagination."""
        guild_id = ctx.guild.id
        filtered_keywords = await self.get_filtered_keywords(guild_id)
        await ctx.channel.typing()
        if not filtered_keywords:
            await ctx.warn("The filter list is empty.")
            return

        paginator = commands.Paginator(prefix="```-", suffix="```")
        for keyword in filtered_keywords:
            paginator.add_line(keyword)

        for page in paginator.pages:
            await ctx.send(page)

    @list_filters.error
    async def prune_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await self.missing_permissions(ctx, 'manage_messages')

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        guild_id = message.guild.id
        filtered_keywords = await self.get_filtered_keywords(guild_id)

        if any(keyword in message.content.lower() for keyword in filtered_keywords):
            try:
                await message.delete()
            except discord.Forbidden:
                await message.channel.send("I don't have permission to delete messages!")
async def setup(bot):
  await bot.add_cog(Filter(bot))