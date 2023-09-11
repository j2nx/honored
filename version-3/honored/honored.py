import discord, random, string
from discord.ext import commands
import os
import asyncio
import asyncpg
import colorama
import requests
import glob
from webserver import keep_alive


from discord.ext.commands import Command
from colorama import (Fore, Style)
from discord import Embed, Guild
from .config import Authorization, Emoji, Color
import sys
from typing import Union


keep_alive()
class GuildProxy:
    def __init__(self, guild_id):
        self.guild_id = guild_id
        self.guild = None
        self.url = None
        self.members = []

    async def fetch_guild(self, bot):

        self.guild = await bot.fetch_guild(self.guild_id)
        self.members = self.guild.members if self.guild else []

    def set_url(self, url):

        self.url = url

    def get_guild_id(self):

        return self.guild_id

    def get_guild(self):

        return self.guild

    def get_url(self):

        return self.url

    def is_ready(self):

        return self.guild is not None and self.url is not None

    def get_member_names(self):

        return [member.name for member in self.members]

    def get_member_count(self):

        return len(self.members)

    def find_member_by_name(self, name):

        for member in self.members:
            if member.name == name:
                return member
        return None

    def get_online_members(self):

        return [member for member in self.members if member.status == "online"]

    def get_member_roles(self, member):
        return member.roles if member in self.members else []

    def get_member_top_role(self, member):

        roles = self.get_member_roles(member)
        return max(roles, key=lambda role: role.position) if roles else None



class CustomContextBase(commands.Context):
    async def custom_method_base(self):

        pass

class HonoredContext(CustomContextBase):
    async def approve(self, message: str) -> None:
        embed = Embed(description=f'{Emoji.approve} {message}', color=Color.approve)
        await self.send(embed=embed)

    async def warn(self, message: str) -> None:
        embed = Embed(description=f'{Emoji.warn} {message}', color=Color.warn)
        await self.send(embed=embed)

    async def deny(self, message: str) -> None:
        embed = Embed(description=f'{Emoji.deny} {message}', color=Color.deny)
        await self.send(embed=embed)

    async def msg(self, message: str) -> None:
        embed = Embed(description=f'{message}', color=Color.msg)
        await self.send(embed=embed)

class Worker(commands.AutoShardedBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def get_context(self, message, *, cls=HonoredContext):
        return await super().get_context(message, cls=cls)
      
class honored(Worker):
    def __init__(self) -> None:
        intents = discord.Intents.all()

        super().__init__(
            command_prefix=Authorization.getprefix,
            strip_after_prefix=True,
            help_command=None,
            chunk_guilds_on_startup=False,
            case_insensitive=True,
            owner_ids=Authorization.owner_ids,
            activity=discord.Activity(
                type=discord.ActivityType.streaming,
                name='-help for support server',
                url='https://twitch.tv/honored'
            ),
            intents=intents,
            allowed_mentions=discord.AllowedMentions(
                everyone=True,
                users=True,
                roles=False,
                replied_user=True,
            )
        )
        self.pool = {
            'host': Authorization.database.host,
            'password': Authorization.database.password,
            'database': Authorization.database.database,
            'user': Authorization.database.user,
            'port': Authorization.database.port
        }
        self.ready = None

    async def on_ready(self) -> None:
        if not self.ready:
            self.ready = True
            self.debugger = True
            self.logger = True
            self.hook = True
        else:
            return
        try:
            self.db = await asyncpg.create_pool(**self.pool)
        except Exception as e:
            print(
                f'Could not proccess database ({e})\n'
                'Have you tried Creating a database? (https://supabase.com/)\n'
                'Most Likely you have invalid creditals.. so please check em.'
            )
            pass

    async def young_bull(self) -> None:
        await self.load_extension('jishaku')
        cog_files = glob.glob('cogs/*.py')
        for cog_file in cog_files:
            try:
                cog_name = os.path.splitext(os.path.basename(cog_file))[0]
                await self.load_extension(f"cogs.{cog_name}")
            except Exception as e:
                print(
                    f"Yo.. Lowkey we just lost another cog boy. {e} ({cog_name})"
                )
    async def on_connect(self) -> None:
        await self.young_bull()
        return print("connected")
        async def create_db(self: commands.AutoShardedBot): 
          await self.db.execute("CREATE TABLE IF NOT EXISTS prefixes (guild_id BIGINT, prefix TEXT)")  
          await self.db.execute("CREATE TABLE IF NOT EXISTS reactionrole (guild_id BIGINT, message_id BIGINT, channel_id BIGINT, role_id BIGINT, emoji_id BIGINT, emoji_text TEXT);")
          await self.db.execute("CREATE TABLE IF NOT EXISTS discrim (Guild BIGINT PRIMARY KEY, Channel BIGINT NOT NULL;")
          await self.db.execute("CREATE TABLE IF NOT EXISTS filtered_keywords (id SERIAL PRIMARY KEY, guild_id BIGINT, keyword TEXT);")
          await self.db.execute("CREATE TABLE IF NOT EXISTS welcome (guild BIGINT, channel BIGINT, message TEXT);")
          await self.db.execute("CREATE TABLE IF NOT EXISTS afk (guild_id BIGINT, user_id BIGINT, reason TEXT, time INTEGER);")
          await self.db.execute("CREATE TABLE lastfm (user_id BIGINT PRIMARY KEY, username TEXT);")
          await self.bot.db.execute("CREATE TABLE IF NOT EXISTS active_guilds (guild_id BIGINT PRIMARY KEY, channel_id BIGINT);")
          await self.bot.db.execute("CREATE TABLE IF NOT EXISTS pfps (guild_id BIGINT, channel_id BIGINT);")
          await self.bot.db.execute("CREATE TABLE IF NOT EXISTS banners (guild_id BIGINT, channel_id BIGINT);")