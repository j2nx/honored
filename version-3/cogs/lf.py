import discord
from discord.ext import commands
import aiohttp
from honored.config import Color
from h.lfh import Handler

class lastfm(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.lfh = Handler("3663d3441c31f8ff3239a18fe49d9ca5")
        self.globalwhoknows_cache = {}

        self.session = aiohttp.ClientSession()

    def cog_unload(self):

        self.bot.loop.create_task(self.session.close())

    async def get_lastfm_username(self, user_id):
        query = "SELECT username FROM lastfm WHERE user_id = $1"
        return await self.bot.db.fetchval(query, user_id)

    async def set_lastfm_username(self, user_id, username):
      query = "INSERT INTO lastfm (user_id, username) VALUES ($1, $2) ON CONFLICT (user_id) DO UPDATE SET username = $2"
      await self.bot.db.execute(query, user_id, username)

    async def remove_lastfm_username(self, user_id, username):
      query = "DELETE FROM lastfm WHERE user_id = $1 AND username = $2"
      await self.bot.db.execute(query, user_id, username)


    @commands.group(aliases=['lastfm'])
    async def lf(self, ctx):
        if ctx.invoked_subcommand is None:
          await ctx.reply(embed=discord.Embed(description = 'view lastfm commands [here](https://honored.rip/commands)', color=Color.msg))
  
    @lf.command()
    async def set(self, ctx, username=None):
      current_username = await self.get_lastfm_username(ctx.author.id)
    
      if username is None:
        await ctx.msg('Please specify the username you want to link to your account')
        return
    
      try:
          await self.set_lastfm_username(ctx.author.id, username)
          await ctx.approve(f"Last.fm username set to {username}")
      except Exception as e:
          if current_username:  
              await ctx.deny(f"You already have a username set: `{current_username}`. If you want to unlink, do `lf unlink`.")
          else:
              await ctx.deny('There was an error setting Last.fm username.')

    @lf.command()
    async def unlink(self, ctx):
      user_id = ctx.author.id
    

      username = await self.get_lastfm_username(user_id)
    
      if username:
          await self.remove_lastfm_username(user_id, username)
          await ctx.approve(f"Last.fm username {username} has successfully been delinked")
      else:
          await ctx.deny("No Last.fm username was found, use lf set.")
      
    @lf.command(aliases=['np', 'fm'], help="lastfm", description="check what song is playing right now", usage="<user>")
    async def nowplaying(self, ctx, *, member: discord.User = None):
        if member is None:
            member = ctx.author

        try:
            await ctx.typing()
            check = await self.bot.db.fetchrow("SELECT * FROM lastfm WHERE user_id = {}".format(member.id))

            if check:
                user = check['username']

                if user != "error":
                    a = await self.lfh.get_tracks_recent(user, 1)
                    artist = a['recenttracks']['track'][0]['artist']['#text'].replace(" ", "+")
                    album = a['recenttracks']['track'][0]['album']['#text'] or "N/A"

                    embed = discord.Embed(colour=Color.msg)
                    embed.add_field(name="**Track:**", value=f"[{a['recenttracks']['track'][0]['name']}]({a['recenttracks']['track'][0]['url']})", inline=False)
                    embed.add_field(name="**Artist:**", value=f"[{a['recenttracks']['track'][0]['artist']['#text']}](https://last.fm/music/{artist})", inline=False)
                    embed.set_author(name=user, icon_url=member.display_avatar, url=f"https://last.fm/user/{user}")
                    embed.set_thumbnail(url=(a['recenttracks']['track'][0])['image'][3]['#text'])
                    embed.set_footer(text=f"Track Playcount: {await self.lfh.get_track_playcount(user, a['recenttracks']['track'][0])} ・Album: {album}", icon_url=(a['recenttracks']['track'][0])['image'][3]['#text'])

                    message = await ctx.reply(embed=embed)
                else:
                    user = check['username']

                    try:
                        replacement_data = await self.lastfm_replacement(user)
                        message = await ctx.send(replacement_data)
                    except:
                        message = await ctx.send(await self.lastfm_replacement(user))
            elif check is None:
                return await ctx.deny(f"**{member}** doesn't have **Last.fm** linked. Use {ctx.prefix}lf set (username) to link your **account**.")
        except Exception as e:
            return await ctx.deny(f"Unable to get **{member.name}'s** recent track {e}".capitalize())

    @lf.command(aliases=['toptracks', 'tt'])
    async def lf_toptracks(self, ctx):
        user_id = ctx.author.id
        lastfm_username = await self.get_lastfm_username(user_id)
        
        if lastfm_username is None:
            await ctx.deny("No Last.fm username set, use lf set.")
            return
        
        api_key = self.api_key
        url = f"http://ws.audioscrobbler.com/2.0/?method=user.gettoptracks&user={lastfm_username}&api_key={api_key}&format=json&limit=10"

        try:
            response = await self.session.get(url)
            data = await response.json()
            top_tracks = data.get("toptracks", {}).get("track", [])

            if not top_tracks:
                await ctx.deny("No top tracks found for this user.")
                return
            
            embed = discord.Embed(title=f"Top 10 Tracks for {lastfm_username}", color=Color.msg)
            for idx, track in enumerate(top_tracks, start=1):
                artist_name = track["artist"]["name"]
                track_name = track["name"]
                play_count = track.get("playcount", "Unknown")
                embed.add_field(name=f"{idx}. {artist_name} - {track_name}", value=f"{play_count} plays", inline=False)
                
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")

  
    async def fetch_artist_info(self, artist_name):
        url = f'http://ws.audioscrobbler.com/2.0/?method=artist.getinfo&artist={artist_name}&api_key={self.api_key}&format=json'
        async with self.session.get(url) as response:
            data = await response.json()
        return data


    @lf.command(name="whoknows", aliases=['wk'], help="lastfm", description="see who knows a certain artist in the server", usage="[artist]")
    async def lf_whoknows(self, ctx, *, artist: str = None):
      await ctx.typing()


      check = await self.bot.db.fetchrow("SELECT username FROM lastfm WHERE user_id = {}".format(ctx.author.id))
    
      if check is None:
          await ctx.deny("No Last.fm username set, use lf set.")
          return

      lastfm_username = check['username']
    
      if not artist:
          resp = await self.lfh.get_tracks_recent(lastfm_username, 1)
          artist = resp["recenttracks"]["track"][0]["artist"]["#text"]

      tuples = []
      rows = []
      ids = [str(m.id) for m in ctx.guild.members]
    

      results = await self.bot.db.fetch(f"SELECT * FROM lastfm WHERE user_id IN ({','.join(ids)})")
    
      if len(results) == 0:
          return await ctx.send('No one has Last.fm set, Use lf set (name)')

      for result in results:
          user_id = int(result[0])
          fmuser2 = result[1]
          us = ctx.guild.get_member(user_id)
          z = await self.lfh.get_artist_playcount(fmuser2, artist)
          tuples.append((str(us), int(z), f"https://last.fm/user/{fmuser2}", us.id))

      num = 0
      for x in sorted(tuples, key=lambda n: n[1], reverse=True)[:10]:
          if x[1] != 0:
              num += 1
              rows.append(f"{'<:Crown:1145767454161776730>' if num == 1 else f'`{num}`'} [**{x[0]}**]({x[2]}) has **{x[1]}** plays")

      if len(rows) == 0:
          return await ctx.reply(f"Nobody (not even you) has listened to {artist}")

      embeds = []
      embed = discord.Embed(color=Color.msg, description="\n".join(rows))
      embed.set_author(name=f"Who knows {artist} in {ctx.guild.name}", icon_url=ctx.guild.icon)
      embed.set_thumbnail(url=ctx.guild.icon)
      embeds.append(embed)
    
      return await ctx.reply(embeds=embeds)


    @lf.command(name="globalwhoknows", aliases=["gwk"], help="lastfm", description="see who knows a certain artist across all servers the bot is in", usage="[artist]")
    async def lf_globalwhoknows(self, ctx: commands.Context, *, artist: str = None):
        await ctx.typing()

        check = await self.bot.db.fetchrow("SELECT username FROM lastfm WHERE user_id = {}".format(ctx.author.id))
        if check is None:
            return await ctx.deny("No Last.fm username set, use lf set.")

        fmuser = check['username']

        if not artist:
            resp = await self.lfh.get_tracks_recent(fmuser, 1)
            artist = resp["recenttracks"]["track"][0]["artist"]["#text"]

        tuples = []

        if not self.globalwhoknows_cache.get(artist):
            ids = [str(m.id) for m in self.bot.users]
            results = await self.bot.db.fetch(f"SELECT * FROM lastfm WHERE user_id IN ({','.join(ids)})")
            if len(results) == 0:
                return await ctx.deny("No one has a **last.fm** account linked")

            for result in results:
                user_id = int(result[0])
                fmuser2 = result[1]
                us = self.bot.get_user(user_id)
                if not us:
                    continue
                z = await self.lfh.get_artist_playcount(fmuser2, artist)
                tuples.append(tuple([str(us), int(z), f"https://last.fm/user/{fmuser2}", us.id]))

            self.globalwhoknows_cache[artist] = sorted(tuples, key=lambda n: n[1])[::-1][:10]

        gwk_list = self.globalwhoknows_cache[artist]

        num = 0
        rows = []
        for x in gwk_list:
            if x[1] != 0:
                num += 1
                rows.append(f"{'<:Crown:1145767454161776730>' if num == 1 else f'`{num}`'} [**{x[0]}**]({x[2]}) has **{x[1]}** plays")

        if len(rows) == 0:
            return await ctx.reply(f"Nobody (not even you) has listened to {artist}")

        embeds = []
        embed = discord.Embed(color=Color.msg, description="\n".join(rows))
        embed.set_author(name=f"Who knows {artist}")
        embed.set_thumbnail(url=ctx.guild.icon)
        embeds.append(embed)

        return await ctx.reply(embed=embeds[0])

    @commands.command(aliases = ['wk'], help="lastfm", description="see who knows a certain artist in the server", usage="[artist]") 
    async def whoknows(self, ctx: commands.Context, *, artist: str=None):
      await ctx.invoke(self.bot.get_command("lf whoknows"), artist=artist)

    @commands.command(aliases = ['gwk'], help="lastfm", description="see who knows a certain artist in the server", usage="[artist]")
    async def globalwhoknows(self, ctx: commands.Context, *, artist: str=None):
      await ctx.invoke(self.bot.get_command("lf globalwhoknows"), artist=artist)

      
    @commands.command()
    async def fm(self, ctx, *, member: discord.Member=None): 
      await ctx.invoke(self.bot.get_command("lf fm"), member=member) 
async def setup(bot):
    await bot.add_cog(lastfm(bot))