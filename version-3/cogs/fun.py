import discord
from discord.ext import commands
from discord.ext.commands import Cog, command
import random
from discord import Embed

class fun(Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @command(aliases=['pack'])
    async def roast(self, ctx, member: discord.Member=None):
        if member is None:
            embed = discord.Embed(title='roast').set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
            embed.add_field(
                name='Usage',
                value=(
                    f"```bf\nSyntax: -roast (member)\n"
                    f"Example: -roast @yurrion```"
                )
            )
            await ctx.send(embed=embed)
            return

        excluded_ids = [780652476427665408, 1131576620134707251]
        if member.id in excluded_ids:
            response = "I could never roast such a beautiful human. They're perfect!"
        else:
            response = f"{member.mention}, {roasts[random.randint(0, len(roasts)-1)]}"

        await ctx.msg(response)


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
async def setup(bot):
    await bot.add_cog(fun(bot))