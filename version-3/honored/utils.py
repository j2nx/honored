import discord
from discord.ext import commands
from typing import Union
class GoodRole(commands.Converter):
  async def convert(self, ctx: commands.Context, argument): 
    try: role = await commands.RoleConverter().convert(ctx, argument)
    except commands.BadArgument: role = discord.utils.get(ctx.guild.roles, name=argument) 
    if role is None: 
      role = ctx.find_role(argument)
      if role is None: raise commands.BadArgument(f"No role called **{argument}** found") 
    if role.position >= ctx.guild.me.top_role.position: raise commands.BadArgument("This role cannot be managed by the bot") 
    if ctx.author.id == ctx.guild.owner_id: return role 
    if role.position >= ctx.author.top_role.position: raise commands.BadArgument(f"You cannot manage this role")
    return role

class NoStaff(commands.Converter): 
  async def convert(self, ctx: commands.Context, argument): 
    try: member = await commands.MemberConverter().convert(ctx, argument)
    except commands.BadArgument: member = discord.utils.get(ctx.guild.members, name=argument)
    if member is None: raise commands.BadArgument(f"No member called **{argument}** found")  
    if member.id == ctx.guild.me.id: raise commands.BadArgument("leave me alone <:mmangry:1081633006923546684>") 
    if member.top_role.position >= ctx.guild.me.top_role.position: raise commands.BadArgument(f"The bot cannot execute the command on **{member}**") 
    if ctx.author.id == ctx.guild.owner_id: return member
    if member.top_role.position >= ctx.author.top_role.position or member.id == ctx.guild.owner_id: raise commands.BadArgument(f"You cannot use this command on **{member}**") 
    return member

class Whitelist: 
  async def whitelist_things(ctx: commands.Context, module: str, target: Union[discord.Member, discord.User, discord.TextChannel]): 
    check = await ctx.bot.db.fetchrow("SELECT * FROM whitelist WHERE guild_id = $1 AND module = $2 AND object_id = $3 AND mode = $4", ctx.guild.id, module, target.id, "user" if isinstance(target, discord.Member) or isinstance(target, discord.User) else "channel")
    if check: return await ctx.send_warning( f"{f'**{target}**' if isinstance(target, discord.Member) else target.mention} is **already** whitelisted for **{module}**")
    await ctx.bot.db.execute("INSERT INTO whitelist VALUES ($1,$2,$3,$4)", ctx.guild.id, module, target.id, "user" if isinstance(target, discord.Member) or isinstance(target, discord.User) else "channel")
    return await ctx.send_success(f"{f'**{target}**' if isinstance(target, discord.Member) else target.mention} is now whitelisted for **{module}**")

  async def unwhitelist_things(ctx: commands.Context, module: str, target: Union[discord.Member, discord.TextChannel]): 
    check = await ctx.bot.db.fetchrow("SELECT * FROM whitelist WHERE guild_id = $1 AND module = $2 AND object_id = $3 AND mode = $4", ctx.guild.id, module, target.id, "user" if isinstance(target, discord.Member) or isinstance(target, discord.User) else "channel")
    if not check: return await ctx.send_warning( f"{f'**{target}**' if isinstance(target, discord.Member) else target.mention} is **not** whitelisted from **{module}**")
    await ctx.bot.db.execute("DELETE FROM whitelist WHERE guild_id = $1 AND module = $2 AND object_id = $3 AND mode = $4", ctx.guild.id, module, target.id, "user" if isinstance(target, discord.Member) or isinstance(target, discord.User) else "channel")
    return await ctx.send_success(f"{f'**{target}**' if isinstance(target, discord.Member) else target.mention} is now unwhitelisted from **{module}**")

  async def whitelisted_things(ctx: commands.Context, module: str, target: str): 
   i=0
   k=1
   l=0
   mes = ""
   number = []
   messages = []  
   results = await ctx.bot.db.fetch("SELECT * FROM whitelist WHERE guild_id = $1 AND module = $2 AND mode = $3", ctx.guild.id, module, target)
   if len(results) == 0: return await ctx.send_warning( f"No whitelisted **{target}s** found for **{module}**")  
   for result in results:
    id = result['object_id'] 
    if target == "channel": mes = f"{mes}`{k}` {f'{ctx.guild.get_channel(id).mention} ({id})' if ctx.guild.get_channel(result['object_id']) is not None else result['object_id']}\n"
    else: mes = f"{mes} `{k}` {await ctx.bot.fetch_user(id)} ({id})\n"
    k+=1
    l+=1
    if l == 10:
     messages.append(mes)
     number.append(discord.Embed(color=ctx.bot.color, title=f"whitelisted {target}s ({len(results)})", description=messages[i]))
     i+=1
     mes = ""
     l=0
    
   messages.append(mes)  
   number.append(discord.Embed(color=ctx.bot.color, title=f"whitelisted {target}s ({len(results)})", description=messages[i]))
   await ctx.paginator(number)