import discord
from discord.ext import commands
from random import choice
import asyncio
from datetime import datetime, timedelta


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    async def cog_check(self, ctx):
        is_guild = await commands.guild_only().predicate(ctx)
        has_perm = await commands.has_permissions(manage_messages=True).predicate(ctx)
        send_perms = await commands.bot_has_permissions(send_messages=True, embed_links=True).predicate(ctx)
        return is_guild and has_perm and send_perms

    @commands.command(name="give", description = "Start a giveaway. \nTime units are (s, m , h, d, w) with there usual meaning,\nuse only one time unit.")
    async def give(self, ctx, price, duration = "10m", winners :int = 1, host :discord.Member = None, mention_role : discord.Role = None):
        # cha = guild.get_channel(809804502085271592)
        host = host if isinstance(host, discord.Member) else ctx.author
        try:
            sleep = convert_to_seconds(duration)
        except:
            duration = "10m"
            sleep = convert_to_seconds(duration)

        duration = (datetime.now() + timedelta(hours= 5.5, seconds=sleep)).strftime("%d %b, %Y at %I:%M:%S %p")

        emb = discord.Embed(title=f"Giveaway: {price}", description="react with 🎉 to enter")
        emb.add_field(name="Hosted by:",value = host.mention )
        emb.set_footer(text=f"{winners} Winners | Ends at: {duration}")
        msg = await ctx.send(embed=emb)
        await msg.add_reaction ("🎉")

        role = mention_role.mention if isinstance(mention_role, discord.Role) else "<@&835473104326230036>"
        await ctx.send(role)

        await asyncio.sleep( sleep )

        prize = f"Congratulations you won **{price}**:\n"

        num = winners

        msg = await ctx.fetch_message(msg.id)
        winners = []
        reactions = msg.reactions

        for reaction in reactions:
            if reaction.emoji == "🎉":
                users = [i for i in await reaction.users().flatten() if not i.bot]
                for i in range(num):
                    if not users:
                        continue
                    ch = choice( users )
                    winners.append(ch)
                    users.remove(ch)
        winner = "\n".join([winner.mention for winner in winners])

        if not winner:
            await ctx.send("Not enough reactions.")
            return

        await msg.reply(prize+winner)

        emb = msg.embeds[0]
        emb.add_field(name="winners:",value=winner,inline=False)
        await msg.edit(embed=emb)

    @commands.command(name="reroll", description = "reroll a giveaway, decides a single winner from reactions.")
    async def reroll(self, ctx, message : discord.Message):
        reactions = message.reactions
        for reaction in reactions:
            if reaction.emoji == "🎉":
                users = [i for i in await reaction.users().flatten() if not i.bot]
                if not users:
                    winner = ""
                    break
                winner = choice( users )

        if not winner:
            await ctx.send("Not enough reactions.")
            return

        await message.reply( f"New winner is: {winner.mention}")


    @commands.command()
    async def echo(self,ctx, channel : discord.TextChannel,*,txt=None):
        if not txt:
            return

        perm = channel.permissions_for(ctx.author)
        bot_perm = channel.permissions_for(ctx.guild.me)
        if (not perm.send_messages) or (not bot_perm.send_messages):
            return await ctx.message.add_reaction(emoji="❌")
        await channel.send(txt)
        await ctx.message.add_reaction(emoji="✅")

    @commands.command(aliases=["clean","2"], description="Delete specified number of messages")
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def purge(self,ctx,limit=2):
        await ctx.message.delete()
        await ctx.channel.purge(limit=limit)
        data = await ctx.send("Deleted {} messages.".format(limit))
        await data.delete(delay=1)

    @commands.command(name="ClearDm",aliases=["cdm"], description="Clear bot messages in DM")
    @commands.dm_only()
    async def clear_dm(self,ctx,limit=20):
        async for i in ctx.channel.history(limit=limit):
            if i.author.id == 835754878651334697:
                await i.delete()

    @commands.Cog.listener(name="on_member_update")
    async def tracking(self,before, after):
        guild = after.guild.id
        if after.bot or guild != 602074836839301130:
            return
        channel = 730317175147200563
        if not channel:
            return
        if after.status != discord.Status.online:
            return

        bec = discord.utils.find(lambda x: isinstance(x, (discord.Activity,
            discord.Game,discord.Streaming)) ,before.activities)
        act = discord.utils.find(lambda x: isinstance(x, (discord.Activity,
            discord.Game,discord.Streaming)), after.activities)
    # if before.activity != after.activity:
        if None in {bec, act}:
            if isinstance(act,discord.Streaming):
                channel = after.guild.get_channel(channel)
                await channel.send(f"**{after.display_name}** is streaming **{act.game}** on **{act.platform}**\nWatch them here:{act.url}")
            elif isinstance(act,(discord.Game,discord.Activity)):
                channel = after.guild.get_channel(channel)
                await channel.send(f"**{after.display_name}** has started playing **{act.name}**")

            elif isinstance(bec,discord.Streaming):
                channel = after.guild.get_channel(channel)
                await channel.send(f"**{after.display_name}** has stopped streaming **{bec.game}**")
            elif isinstance(bec,(discord.Game,discord.Activity)):
                channel = after.guild.get_channel(channel)
                await channel.send(f"**{after.display_name}** has stopped playing **{bec.name}**")

    @commands.command(name="verify", hidden=True)
    async def verify(self, ctx):
        channel = ctx.channel
        if channel.id != 837915404675710986:
            return #await ctx.send("Why. why try to misuse this little bot.")
        user = ctx.author

        mem_role = ctx.guild.get_role(729299970590769195)
        await user.add_roles(mem_role, reason="Verified!")



seconds_per_unit = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}

def convert_to_seconds(s):
    s = s.lower()
    return float((s[:-1])) * seconds_per_unit[s[-1]]

def setup(client):
    client.add_cog( Utility(client))

