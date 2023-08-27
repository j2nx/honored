import discord
from discord.ext import commands
from webserver import keep_alive
import os
import datetime 
import sqlite3
import humanize
os.environ['JISHAKU_NO_UNDERSCORE'] = 'True'
os.environ['JISHAKU_RETAIN'] = 'True'

token = os.environ['DISCORD_TOKEN']

def create_table():
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            money INTEGER DEFAULT 0
        )
    """)
    connection.commit()
    connection.close()

create_table()

def create_table():
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
        )
    """)
    connection.commit()
    connection.close()

intents = discord.Intents.all()

custom_prefixes = {}

default_prefixes = '-'

async def determine_prefix(bot, message):
    guild = message.guild
    if guild:
        return custom_prefixes.get(guild.id, default_prefixes)
    else:
        return default_prefixes
      
bot = commands.Bot(command_prefix = determine_prefix,
                   intents=intents,
                   owner_ids=([
                     780652476427665408, 1108907120788787243,
                     999010191804739615, 1114332327619866815,
                     1065348443339489322
                   ]))
bot.remove_command("help")
authorized_user_ids = [
  780652476427665408, 1108907120788787243, 999010191804739615,
  1065348443339489322
]

keep_alive()


@bot.event
async def on_ready():
  print(f'Bot connected as {bot.user}. {bot.user.id}')
  await bot.load_extension("jishaku")
  await bot.load_extension("cogs.cogs")
  await bot.load_extension("cogs.cogs2")
@bot.command(aliases=['prefix'])
@commands.guild_only()
@commands.has_permissions(manage_guild = True)
async def setprefix(self, ctx, *, prefixes=""):
    custom_prefixes(ctx.guild.id) == prefixes.split() or default_prefixes
    await ctx.send("👍")

prefix = default_prefixes or custom_prefixes

@bot.listen('on_message')
async def on_message(message):
    mention = f'<@{bot.user.id}>'
    if message.content.startswith(f'{mention}'):
        await message.channel.send(f"luh tonkie, my prefix is `{prefix}`")

@bot.command(aliases=['hey', 'hi'])
async def hello(ctx):
  """Greets the user with a fun message."""
  await ctx.reply("wsg luh tonkie ponkie")



@bot.command()
@commands.guild_only()
async def ping(ctx):
        """Checks the bot's latency."""
        latency = bot.latency
        await ctx.send(f"bot latency: {round(latency * 1000)}ms")
  

@bot.command()
async def status(ctx, *, activity):
  """Sets the streaming status for the bot (bot owner only)."""
  allowed_ids = [
    1108907120788787243, 780652476427665408, 999010191804739615,
    1065348443339489322, 847709507965812736
  ]
  if ctx.author.id in allowed_ids:
    await bot.change_presence(activity=discord.Streaming(
    name=activity, url="https://www.twitch.tv/discord"))

  embed = discord.Embed(title=f"Streaming status has been set to: {activity}")
                        
  await ctx.send(embed=embed)


@bot.command()
@commands.guild_only()
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member):
  """Mutes a member by assigning the 'Muted' role (moderator only)."""
                        
  mute_role = discord.utils.get(ctx.guild.roles, name="Muted")

  if not mute_role:
    mute_role = await ctx.guild.create_role(name="Muted")

    for channel in ctx.guild.channels:
      await channel.set_permissions(mute_role, send_messages=False)

  await member.add_roles(mute_role)
  await ctx.send(f"{member.mention} has been muted.")


@bot.command()
@commands.guild_only()
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, member: discord.Member):
  """Unmutes a member by removing the 'Muted' role (moderator only)."""
  mute_role = discord.utils.get(ctx.guild.roles, name="Muted")

  if mute_role in member.roles:
    await member.remove_roles(mute_role)
    await ctx.send(f"{member.mention} has been unmuted.")
  else:
    await ctx.send("User is not muted.")


@bot.command(aliases=['bi', 'info', 'information'])
@commands.guild_only()
async def botinfo(ctx):
    """Displays information about the bot."""
    total_servers = len(bot.guilds)
    total_members = sum([guild.member_count for guild in bot.guilds])
    bot_creator1 = bot.get_user(1108907120788787243)
    bot_creator2 = bot.get_user(780652476427665408)
    invite_link = "https://discord.com/oauth2/authorize?client_id=1115694529505398846&scope=bot+applications.commands&permissions=93248"
    uptime = datetime.datetime.utcnow() - bot.start_time
    uptime_formatted = humanize.precisedelta(uptime, format='%0.0f')
    
    embed = discord.Embed(title="Bot Information")
    embed.add_field(name="Total Servers", value=total_servers, inline=True)
    embed.add_field(name="Total Members", value=total_members, inline=True)
    embed.add_field(name="Bot Creators", value=f"{bot_creator1.mention}\n{bot_creator2.mention}", inline=False)
    embed.add_field(name="Uptime", value=uptime_formatted, inline=False)
    embed.add_field(name="Bot Invite Link", value=f"[Invite Link]({invite_link})", inline=False)
    embed.set_footer(text="Thank you for using the bot!")
    
    await ctx.send(embed=embed)



@bot.command(aliases=['si'])
@commands.guild_only()
async def serverinfo(ctx):
    name = str(ctx.guild.name)
    description = str(ctx.guild.description)

    owner = str(ctx.guild.owner)
    id = str(ctx.guild.id)
    memberCount = str(ctx.guild.member_count)

    icon = str(ctx.guild.icon)

    embed = discord.Embed(
        title=name + " Server Information",
        description=description,
    )
    embed.set_thumbnail(url=icon)
    embed.add_field(name="Owner", value=owner, inline=True)
    embed.add_field(name="Server ID", value=id, inline=True)
   
    embed.add_field(name="Member Count", value=memberCount, inline=True)

    await ctx.send(embed=embed)
  
@bot.command()
@commands.guild_only()
async def join(ctx):
  """Joins the voice channel that the user is connected to."""
  if ctx.author.voice is None or ctx.author.voice.channel is None:
    await ctx.send("You are not connected to a voice channel.")
    return

  channel = ctx.author.voice.channel
  voice_client = ctx.voice_client

  if voice_client is not None:
    await voice_client.move_to(channel)
  else:
    voice_client = await channel.connect(reconnect=True, timeout=15)

  await ctx.send(f"Joined voice channel: {channel}")

@bot.command()
@commands.guild_only()
async def leave(ctx):
  """Leaves the current voice channel."""
  voice_client = ctx.voice_client

  if voice_client is None:
    await ctx.send("I'm not connected to a voice channel.")
    return

  await voice_client.disconnect()
  await ctx.send("Left the voice channel.")

@bot.command(aliases=['whois', 'wi', 'userinfo', 'user'])
@commands.guild_only()
async def ui(ctx, member: discord.Member = None):
  """Displays information about a user."""
  member = member or ctx.author

  embed = discord.Embed(title="User Information", color=member.color)
  embed.set_thumbnail(url=member.avatar.url)
  embed.add_field(name="Name", value=member.name)
  embed.add_field(name="Discriminator", value=member.discriminator)
  embed.add_field(name="ID", value=member.id)
  embed.add_field(name="Created At",
                  value=member.created_at.strftime("%b %d, %Y %H:%M:%S UTC"))

  if member.top_role != member.guild.default_role:
    embed.add_field(name="Top Role", value=member.top_role.mention)
  embed.set_footer(text=f"Requested by {ctx.author.name}",
                   icon_url=ctx.author.avatar.url)

  await ctx.send(embed=embed)


sniped_messages = {}


@bot.event
async def on_message_delete(message):
  sniped_messages[message.channel.id] = message


@bot.command(aliases=['s'])
@commands.guild_only()
async def snipe(ctx):
  """Retrieves the most recently deleted message in the current channel."""
  channel = ctx.channel
  if channel.id not in sniped_messages:
    await ctx.send("There are no recently deleted messages to snipe.")
    return

  message = sniped_messages[channel.id]

  embed = discord.Embed(title=message.content)
  embed.set_author(name=message.author.display_name,
                   icon_url=message.author.avatar.url)
  embed.set_footer(
    text=f"Deleted at {message.created_at.strftime('%b %d, %Y %H:%M:%S UTC')}")

  await ctx.send(embed=embed)

@bot.command()
@commands.guild_only()
async def help(ctx):
    invite_link = "https://discord.com/invite/honored"
    
    embed = discord.Embed(
        description=f"To view all commands, join the bot server [here]({invite_link})"
    )
    await ctx.send(embed=embed)



@bot.command(aliases=['avatar', 'pfp'])
@commands.guild_only()
async def av(ctx, member: discord.Member = None):
  """Displays the avatar of a user."""
  member = member or ctx.author
  embed = discord.Embed(title=f"Avatar - {member.name}")
                        
  embed.set_image(url=member.avatar)
  await ctx.send(embed=embed)


@bot.command()
@commands.guild_only()
async def banner(ctx, user:discord.Member):
    if user == None:
        user = ctx.author
    req = await bot.http.request(discord.http.Route("GET", "/users/{uid}", uid=user.id))
    banner_id = req["banner"]
    if banner_id:
        banner_url = f"https://cdn.discordapp.com/banners/{user.id}/{banner_id}?size=1024"
        
        embed = discord.Embed(title=f"banner - {user.name}")
        embed.set_image(url=banner_url)
        await ctx.send(embed=embed)


@bot.command(aliases=['setbotpfp', 'setavatar'])
async def setbotav(ctx):
  allowed_ids = [1108907120788787243, 780652476427665408, 999010191804739615, 995597365845184552]

  if ctx.author.id in allowed_ids:
    if len(ctx.message.attachments) == 0:
      await ctx.send("Please upload an image file.")
    return

  attachment = ctx.message.attachments[0]

  if not attachment.filename.lower().endswith(
    ('.png', '.jpg', '.jpeg', '.gif')):
    await ctx.send("Please upload a valid image file (PNG, JPG, JPEG, GIF).")
    return

  try:

    await attachment.save(attachment.filename)

    with open(attachment.filename, 'rb') as file:
      avatar_bytes = file.read()

    await bot.user.edit(avatar=avatar_bytes)

    os.remove(attachment.filename)

    await ctx.send("oki.")
  except Exception as e:
    await ctx.send(f"An error occurred while setting the bot avatar: {e}")


@bot.command()
async def dm(ctx, member: discord.Member, *, message):
  """Sends a direct message to a user (bot owner only)."""
  allowed_ids = [780652476427665408, 1108907120788787243, 999010191804739615]

  if ctx.author.id in allowed_ids:
    try:
      await member.send(message)
      await ctx.send(f"Sent a DM to {member.mention}")
    except discord.Forbidden:
      embed = discord.Embed(title="Unable to send a DM.",
      description="Make sure the user allows DMs from this server or the bot is not blocked.")
    await ctx.send(embed=embed)


@bot.command(aliases=['gban', 'globalb'])
async def globalban(ctx, user: discord.User):
  allowed_ids = [780652476427665408, 1108907120788787243, 999010191804739615]
  if ctx.author.id in allowed_ids:
    embed = discord.Embed

  for guild in bot.guilds:
    await guild.ban(user)
    title = f"{user.mention} got beamed!",
    color = discord.Color.green()

    await ctx.send(embed=embed)


@bot.command()
async def uptime(ctx):
  """Displays the bot's uptime."""
  uptime = datetime.datetime.utcnow() - bot.start_time
  days = uptime.days
  hours, remainder = divmod(uptime.seconds, 3600)
  minutes, seconds = divmod(remainder, 60)

  await ctx.send(
    f"I have been online for {days} days, {hours} hours, {minutes} minutes, and {seconds} seconds."
  )


bot.start_time = datetime.datetime.utcnow()


@bot.command()
@commands.guild_only()
async def translate(ctx, *, text):
  """Translates text to the specified language."""
  translation = translator.translate(text)
  translated_text = translation.text
  source_lang = translation.src
  dest_lang = translation.dest
  await ctx.send(
    f"Original Text: {text}\nTranslation ({source_lang} to {dest_lang}): {translated_text}"
  )


@bot.command()
@commands.guild_only()
async def define(ctx, *, word):
  """Provides the definition of a word."""
  definition = dictionary.meaning(word)
  if definition:
    first_definition = definition[list(definition.keys())[0]]
    await ctx.send(f"Word: {word}\nDefinition: {first_definition}")
  else:
    await ctx.send("No definition found for the word.")


@bot.command()
@commands.guild_only()
async def commands(ctx):
  """Displays the list of available commands."""
  command_list = bot.commands
  num_commands = len(command_list)

  embed = discord.Embed(title="Bot Commands",
    description=f"there are a total of ({num_commands} commands)")
  await ctx.send(embed=embed)


@bot.command(aliases=['roleall'])
async def massrole(ctx, role_name):
  role = discord.utils.get(ctx.guild.roles, name=role_name)
  if role is None:
    embed = discord.Embed(
      title='Role Not Found',
      description=f'The role "{role_name}" does not exist.')
    await ctx.send(embed=embed)
    return

  count = 0
  for member in ctx.guild.members:
    if not member.bot:
      await member.add_roles(role)
      count += 1

  embed = discord.Embed(
    title='Role Assignment',
    description=f'Assigned the role "{role_name}" to {count} members.')
  await ctx.send(embed=embed)


@bot.command(aliases=['creds'])
async def credits(ctx):
  embed = discord.Embed(
    title='Developer Team:',
    description='<@1108907120788787243> \n<@780652476427665408>',
    )

  embed.add_field(name='Owners:',
                  value='<@999010191804739615 \n<@1065348443339489322>',
                  inline=False)



  embed.set_author(
    name='Honored credits',
    icon_url=
    'https://cdn.discordapp.com/attachments/1115841028788854825/1116426817046323291/f950e8e820b08df28212071f73356c20.png'
  )

  await ctx.send(embed=embed)


@bot.command()
async def invite(ctx):
  permissions = discord.Permissions()
  permissions.update(read_messages=True,
                     send_messages=True,
                     manage_messages=True,
                     embed_links=True,
                     read_message_history=True,
                     add_reactions=True)

  oauth_url = discord.utils.oauth_url(bot.user.id, permissions=permissions)

  embed = discord.Embed(
    title='Bot Invite Link',
    description=f'Click [here]({oauth_url}) to invite the bot to your server.',
    )

  await ctx.author.send(embed=embed)


@bot.command()
async def sticker(ctx, name: str, url: str):
  try:
    sticker = await ctx.guild.create_sticker(name=name, image=url)
    embed = discord.Embed(title='Sticker Created',
                          description=f'Sticker ID: {sticker.id}'
)
    await ctx.send(embed=embed)
  except discord.Forbidden:
    embed = discord.Embed(
      title='Permission Denied',
      description="I don't have permission to create stickers.",
      color=discord.Color.red())
    await ctx.send(embed=embed)
  except discord.HTTPException:
    embed = discord.Embed(
      title='Sticker Creation Failed',
      description='Failed to create sticker. Please check the provided URL.'
)
    await ctx.send(embed=embed)


@bot.command()
async def emoji(ctx, name: str, url: str):
  try:
    emoji = await ctx.guild.create_custom_emoji(name=name, image=url)
    embed = discord.Embed(title='Emoji Created',
                          description=f'Emoji ID: {emoji.id}',
                          color=discord.Color.green())
    await ctx.send(embed=embed)
  except discord.Forbidden:
    embed = discord.Embed(
      title='Permission Denied',
      description="I don't have permission to create emojis.",
      color=discord.Color.red())
    await ctx.send(embed=embed)
  except discord.HTTPException:
    embed = discord.Embed(
      title='Emoji Creation Failed',
      description='Failed to create emoji. Please check the provided URL.',
      color=discord.Color.red())
    await ctx.send(embed=embed)


@bot.command()
async def roast(ctx, member: discord.Member):
    excluded_ids = [780652476427665408, 1108907120788787243]
    if member.id in excluded_ids:
        response = "I could never roast such a beautiful human. They're perfect!"
    else:
        response = f"{member.mention}, {roasts[random.randint(0, len(roasts)-1)]}"
    await ctx.send(response)


roasts = [
  "You're so dumb, you stare at a glass of orange juice for 12 hours because it said 'concentrate'.",
  "If you were any more inbred, you'd be a sandwich.",
  "I'm not saying I hate you, but I would unplug your life support to charge my phone.",
  "I'd call you a donkey, but that would be an insult to donkeys.",
  "I'm not a proctologist, but I know an asshole when I see one.",
  "You must have been born on a highway because that's where most accidents happen.",
  "You're like a cloud. When you disappear, it's a beautiful day.",
  "I was going to give you a nasty look, but I see you already have one.",
  "Your face could scare the chrome off a bumper.",
  "I bet your brain feels as good as new, considering you've never used it.",
  "If laughter is the best medicine, your face must be curing the world.",
  "You have enough fat to make another human.",
  "I'm surprised your mirror hasn't cracked from your ugly reflection.",
  "You're the reason God created the middle finger.",
  "It's a shame you can't Photoshop your personality.",
  "I wouldn't trust you to mow my lawn, let alone make an intelligent decision.",
  "You're a prime example of why some animals eat their young.",
  "You're so bad at directions, even Siri would get lost following you.",
  "Are you a magician? Because every time you enter a room, all the laughter disappears.",
  "You have a face for radio... and a voice for silent movies.",
  "If laughter is the best medicine, your face must be curing the world.",
  "Is your mirror okay? It must be traumatized by what it reflects every day."
  "If being ugly was a crime, you'd be serving a life sentence.",
  "They say everyone has a doppelgänger, but in your case, no one wants to admit it.",
  "I've seen better-looking sandwiches at a gas station.",
  "Your fashion sense is so unique, even blindfolded people would know it's you.",
  "If there was a contest for being average, you'd come in fourth place.",
  "Were you born on April Fools' Day? Because you're a walking punchline.",
  "Your sense of humor is so dry, even a desert would be jealous.",
  "I'm jealous of people who haven't met you yet.",
  "I don't need a billboard; i just need your forehead, that's enough.",
  "You're proof that God has a sense of humor.",
  "You're so dumb, you stare at a glass of orange juice for 12 hours because it said 'concentrate'.",
  "If you were any more inbred, you'd be a sandwich.",
  "I'm not saying I hate you, but I would unplug your life support to charge my phone.",
  "I'd call you a donkey, but that would be an insult to donkeys.",
  "I'm not a proctologist, but I know an asshole when I see one.",
  "You must have been born on a highway because that's where most accidents happen.",
  "You're like a cloud. When you disappear, it's a beautiful day.",
  "I was going to give you a nasty look, but I see you already have one.",
  "Your face could scare the chrome off a bumper.",
  "You gonna stay on my dick until you die! You serve no purpose in life. Your purpose in life is being on my stream sucking on my dick daily! Your purpose is being in that chat blowing that dick daily! Your life is nothing! You serve zero purpose! You should kill yourself now! And give somebody else a piece of that oxygen and ozone layer, that's covered up so we can breathe inside this blue trapped bubble. Because what are you here for? To worship me? Kill yourself. I mean that, with a hundred percent. With a thousand percent."
]

@bot.command()
async def encrypt(ctx, shift: int, *, message: str):
    encrypted_message = ""
    for char in message:
        if char.isalpha():
            shifted_char = chr((ord(char.upper()) - 65 + shift) % 26 + 65)
            encrypted_message += shifted_char if char.isupper() else shifted_char.lower()
        else:
            encrypted_message += char
    
    embed = discord.Embed(title="Encryption")
    embed.add_field(name="Original Message", value=message, inline=False)
    embed.add_field(name="Shift Value", value=str(shift), inline=False)
    embed.add_field(name="Encrypted Message", value=encrypted_message, inline=False)
    
    await ctx.send(embed=embed)

@bot.command()
async def decrypt(ctx, shift: int, *, encrypted_message: str):
    decrypted_message = ""
    for char in encrypted_message:
        if char.isalpha():
            shifted_char = chr((ord(char.upper()) - 65 - shift) % 26 + 65)
            decrypted_message += shifted_char if char.isupper() else shifted_char.lower()
        else:
            decrypted_message += char
    
    embed = discord.Embed(title="Decryption")
    embed.add_field(name="Encrypted Message", value=encrypted_message, inline=False)
    embed.add_field(name="Shift Value", value=str(shift), inline=False)
    embed.add_field(name="Decrypted Message", value=decrypted_message, inline=False)
    
    await ctx.send(embed=embed)




@bot.command(aliases=['ruin', 'outcharm', 'harlem'])
async def nine(ctx):
    tribute_message = "In loving memory of Nine,\n" \
                      "A friend who left, but forever shines.\n" \
                      "Your presence brought joy, laughter, and cheer,\n" \
                      "Leaving us with memories that we hold dear.\n" \
                      "Though you're gone, your friendship remains,\n" \
                      "In our hearts, forever it sustains. You were so kind and sharing to everyone you encountered, all of us will miss you and await your return. xoxo honored development team."

    await ctx.send(tribute_message)

allowed_users = [1108907120788787243, 780652476427665408, 999010191804739615]


@bot.command()
async def send(ctx, channel_id: int, *, message: str):
    if ctx.author.id not in allowed_users:
        await ctx.send("This command can only be used by specific users.")
        return

    channel = bot.get_channel(channel_id)

    if channel is None:
        await ctx.send("Invalid channel ID.")
        return

    await channel.send(message)
    await ctx.send("Message sent successfully.")

@bot.command()
async def servers(ctx):
    allowed_ids = [780652476427665408, 1108907120788787243]  
    if ctx.author.id in allowed_ids:
      for guild in bot.guilds:
        await ctx.send(f"Server: {guild.name}")

@bot.command()
async def roles(ctx):
    roles = ctx.guild.roles

    role_names = [role.name for role in roles]
    role_mentions = [role.mention for role in roles]

    role_names_str = '\n'.join(role_names)

    embed = discord.Embed(title='Server Roles', color=discord.Color.blue())
    embed.add_field(name='Role Names', value=role_names_str, inline=True)

    for i in range(0, len(role_mentions), 10):
        mentions_chunk = role_mentions[i:i + 10]
        mentions_chunk_str = ' '.join(mentions_chunk)
        embed.add_field(name='Role Mentions', value=mentions_chunk_str, inline=True)

    await ctx.send(embed=embed)

bot.run(token)
