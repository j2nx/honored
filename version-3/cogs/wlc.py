import discord
from discord.ext import commands
from honored.config import Color

class welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def missing_permissions(self, ctx, *perms):
        missing_perms = [perm for perm in perms if not getattr(ctx.channel.permissions_for(ctx.author), perm, False)]
        if missing_perms:
            formatted_perms = ", ".join(missing_perms)
            await ctx.warn(f"You're missing the permissions: `{formatted_perms}`")
    @commands.Cog.listener()
    async def on_member_join(self, member):
      try:
        data = await self.bot.db.fetchrow('SELECT * FROM welcome WHERE guild = $1', member.guild.id)
        if data:
            v = data['message']
            channel = self.bot.get_channel(int(data['channel']))

            v = v.replace('{user.mention}', member.mention)
            v = v.replace('{user.id}', str(member.id))
            v = v.replace('{guild.count}', str(member.guild.member_count))

         

            title = None
            description = None
            image_url = None


            if '{title}' in v:
                title_start = v.index('{title}') + 7
                title_end = v.index('{/title}', title_start)
                title = v[title_start:title_end].strip()


            if '{description}' in v:
                description_start = v.index('{description}') + 13
                description_end = v.index('{/description}', description_start)
                description = v[description_start:description_end].strip()


            if '{image}' in v:
                image_start = v.index('{image}') + 8
                image_end = v.index('{/image}', image_start)
                image_url = v[image_start:image_end].strip()

            if title or description or image_url:
                e = discord.Embed(color=Color.msg)

                if title:
                    e.title = title

                if description:
                    e.description = description

                if image_url:
                    e.set_image(url=image_url)

                await channel.send(embed=e)
            else:

                await channel.send(v)
      except Exception as e:
          print(e)

    @commands.group(
        name='welcome',
        description='Welcomes new users to your Guild.',
        aliases=['welc', 'wlc'],
        usage='Syntax: welcome[wlc, welc] <subcommand> (message)\nExample: welcome[wlc, welc] add #message hello',
        extras='',
        invoke_without_command=True
    )
    @commands.has_permissions(manage_guild=True)
    async def welcome(self, ctx):
            embed = discord.Embed(title='welcome', color=Color.msg).set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
            embed.add_field(
              name='description',
              value="add/remove a welcome message in your guild"
            )
            embed.add_field(
              name='Permissions',
              value="manage_guild"
            )
            embed.add_field(
              name='**aliases**',
              value="welc, wlc"
            )
            await ctx.send(embed=embed)
            return


    @welcome.error
    async def welcome_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await self.missing_permissions(ctx, 'manage_guild')


    @welcome.command(
        name = 'add',
        description = 'Adds a channel to your welcome configuration',
        aliases = ['create'],
        usage = 'Syntax: welcome[wlc, welc] <create> (message)\nExample: welcome[wlc, welc] add #message hello'
    )
    @commands.has_permissions(manage_guild=True)
    async def create(self, ctx, channel: discord.TextChannel, *, message: str):
          try:
            check = await self.bot.db.fetch('SELECT * from welcome WHERE guild = $1', ctx.guild.id)
            if check:
                await self.bot.db.execute('UPDATE welcome SET channel = $1, message = $2 WHERE guild = $3', channel.id, message, ctx.guild.id)
                return await ctx.approve(f'Updated the **Welcome Message** for {channel.mention}.')
            else:
                await self.bot.db.execute('INSERT INTO welcome (guild, channel, message) VALUES ($1, $2, $3)', ctx.guild.id, channel.id, message)
                await ctx.approve(f'Created a **Welcome Message** & bined it to {channel.mention}')
        
          except Exception as e:
            print(e)

    @create.error
    async def create_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await self.missing_permissions(ctx, 'manage_guild')

    @welcome.command(
        name='remove',
        description='Removes the welcome configuration for this guild.',
        usage='Syntax: remove',
    )
    @commands.has_permissions(manage_guild=True)
    async def removewelcome(self, ctx, channel: discord.TextChannel):
        try:
            await self.bot.db.execute('DELETE FROM welcome WHERE guild = $1', ctx.guild.id)
            await ctx.approve(f"Welcome message has been removed from {channel.mention}")
        except Exception as e:
            print(e)
            await ctx.warn("An error occurred while removing the welcome configuration.")

    @removewelcome.error
    async def removewelcome_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await self.missing_permissions(ctx, 'manage_guild')
  
    @welcome.command(
        name='test',
        description='Tests the welcome message for the current guild.',
        usage='Syntax: welcome_test',
    )
    @commands.has_permissions(manage_guild=True)
    async def welcometest(self, ctx):
        try:
            
            new_member = ctx.author
            await self.on_member_join(new_member)
            await ctx.approve("Welcome message has been tested successfully")
        except Exception as e:
            print(e)
            await ctx.warn("An error occurred while testing the welcome message.")

    @welcometest.error
    async def welcometest_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await self.missing_permissions(ctx, 'manage_guild')

async def setup(bot):
    await bot.add_cog(welcome(bot))