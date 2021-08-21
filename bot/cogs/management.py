import discord
from discord.ext import commands
import logging
from typing import Union
from . import Server, create_embed, PREFIX_SPLIT, get_blacklist, get_whitelist, get_prefix, BlackList, WhiteList

logger = logging.getLogger(__name__)

# prefix = self.bot.user.mention + PREFIX_SPLIT
# server = await self.bot.session.get( Server, ctx.guild.id )
# prefix = prefix + server.prefix
# prefix = prefix.split(PREFIX_SPLIT)

blacklist_help_defination = "Bot will not respond in Blacklisted channel or to Blacklisted Users,\
User with manage server permission can add or remove users/channel from blacklist."

whitelist_help_defination = "Bot will respond to everyone in whitelisted channels (i.e even if they are blacklisted)\
and bot will respond to whitelisted users even in blacklisted channels. \nPS: whitelist > blacklist"


class Management(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        is_guild = await commands.guild_only().predicate(ctx)
        has_perm = await commands.has_permissions(manage_channels=True).predicate(ctx)
        send_perms = await commands.bot_has_permissions(send_messages=True, embed_links=True).predicate(ctx)
        return is_guild and has_perm and send_perms


    @commands.group(name="prefix", invoke_without_command=True, description="Add or remove prefix for bot.")
    async def prefix(self, ctx):
        """
        If called without subcommand, shows all prefix for bot.
        """
        prefix = await get_prefix(self.bot, ctx.message)
        del prefix[1]   # the <@!id> mention.
        desc = "\n".join( [f"{i+1}. {v}" for i, v in enumerate(prefix)] )

        embed = create_embed("Prefixes", desc)
        await ctx.send(embed=embed)


    @prefix.command(name="add", aliases=["+"])
    async def add_prefix(self, ctx, prefix :str):
        server = await self.bot.session.get( Server, ctx.guild.id )
        prefixes = server.prefix.split(PREFIX_SPLIT)

        if prefix not in prefixes:
            server.prefix = f"{server.prefix}{PREFIX_SPLIT}{prefix}"

        await ctx.send(f"Added prefix {prefix}")

    @prefix.command(name="remove", aliases=["-"])
    async def remove_prefix(self, ctx, prefix :str ):
        server = await self.bot.session.get( Server, ctx.guild.id )
        try:
            new_prefixes = server.prefix.split(PREFIX_SPLIT)
            new_prefixes.remove(prefix)
        except ValueError:
            await ctx.send(f"{prefix} is not a prefix for this bot.")
            return
        server.prefix = PREFIX_SPLIT.join(new_prefixes)

        await ctx.send(f"Removed prefix {prefix}")


    @commands.group(name="blacklist", aliases=["bl"],invoke_without_command=True, description="Blacklist a user or channel.", help=blacklist_help_defination)
    async def guild_blacklist(self, ctx):
        blacklist = await get_blacklist(self.bot, ctx.guild )
        user = [f"<@!{i}>" for i in blacklist.user]
        channel = [f"<#{i}>" for i in blacklist.channel]
        user = "\n".join(user) or "No blacklisted user"
        channel = "\n".join(channel) or "No blacklisted channel"
        embed = create_embed("Blacklisted",  Channel = channel, Users = user, footer=ctx.message.created_at)

        await ctx.send(embed = embed)

    @guild_blacklist.command(name="add", aliases= ["+"], description="Add to blacklist")
    async def add_blacklist(self, ctx, user_or_channel : Union[discord.TextChannel, discord.Member]):
        # server = await self.bot.session.get( Server, ctx.guild.id)
        if isinstance(user_or_channel, discord.Member):
            blacklisted = BlackList(user= user_or_channel.id, guild_id =ctx.guild.id)#, guild= server )
            self.bot.blacklist[ctx.guild.id].user.update(str(user_or_channel.id))
        elif isinstance(user_or_channel, discord.TextChannel):
            blacklisted = BlackList(channel = user_or_channel.id, guild_id = ctx.guild.id)#, guild= server)

            # blacklist[ctx.guild.id] is a discord.Object given by ..modules.get.get_blacklist
            # ^ this is created by load_data func in ..bot
            self.bot.blacklist[ctx.guild.id].channel.update(str(user_or_channel.id))
        else:
            raise Exception("Unexpected Work by management blacklist")

        self.bot.session.add( blacklisted )

        await ctx.send(f"**{user_or_channel.name}** Added to blacklist.")

    @guild_blacklist.command(name="remove", aliases=["-"], description="Remove from blacklist")
    async def remove_blacklist(self, ctx, user_or_channel : Union[discord.TextChannel, discord.Member]):
        server = await self.bot.session.get( Server, ctx.guild.id)
        if isinstance(user_or_channel, discord.Member):
            print(server)
            black = [i for i in server.blacklist if i.user == str(user_or_channel.id)]
        elif isinstance(user_or_channel, discord.TextChannel):
            black = [i for i in server.blacklist if i.channel == str(user_or_channel.id)]
        else:
            raise Exception("Unexpected Work by management blacklist")

        if black:
            await self.bot.session.delete( black[0] )

        await ctx.send(f"**{user_or_channel.name}** Removed from blacklist.")


    @commands.group(name="whitelist", aliases=["wl"],invoke_without_command=True, description="Whitelist a user or channel.", help=whitelist_help_defination)
    async def guild_whitelist(self, ctx):
        whitelist = await get_whitelist(self.bot, ctx.guild )
        user = [f"<@!{i}>" for i in whitelist.user]
        channel = [f"<#{i}>" for i in whitelist.channel]
        user = "\n".join(user) or "No whitelisted user"
        channel = "\n".join(channel) or "No whitelisted channel"
        embed = create_embed("Whitelisted",  Channel = channel, Users = user, footer=ctx.message.created_at)

        await ctx.send(embed = embed)

    @guild_whitelist.command(name="add", aliases= ["+"], description="Add to whitelist")
    async def add_whitelist(self, ctx, user_or_channel : Union[discord.TextChannel, discord.Member]):
        if isinstance(user_or_channel, discord.Member):
            whitelisted = WhiteList(user= user_or_channel.id, guild_id =ctx.guild.id)#, guild= server )
            self.bot.blacklist[ctx.guild.id].user.update(str(user_or_channel.id))
        elif isinstance(user_or_channel, discord.TextChannel):
            whitelisted = WhiteList(channel = user_or_channel.id, guild_id = ctx.guild.id)#, guild= server)

            # blacklist[ctx.guild.id] is a discord.Object given by ..modules.get.get_blacklist
            # ^ this is created by load_data func in ..bot
            self.bot.blacklist[ctx.guild.id].channel.update(str(user_or_channel.id))
        else:
            raise Exception("Unexpected Work by management whitelist")

        self.bot.session.add( whitelisted )

        await ctx.send(f"**{user_or_channel.name}** Added to whitelist.")

    @guild_whitelist.command(name="remove", aliases=["-"], description="Remove from whitelist")
    async def remove_whitelist(self, ctx, user_or_channel : Union[discord.TextChannel, discord.Member]):
        server = await self.bot.session.get( Server, ctx.guild.id)
        if isinstance(user_or_channel, discord.Member):
            white = [i for i in server.blacklist if i.user == str(user_or_channel.id)]
        elif isinstance(user_or_channel, discord.TextChannel):
            white = [i for i in server.blacklist if i.channel == str(user_or_channel.id)]
        else:
            raise Exception("Unexpected Work by management whitelist")

        if white:
            await self.bot.session.delete( white[0] )

        await ctx.send(f"**{user_or_channel.name}** Removed from whitelist.")






def setup(client):
    client.add_cog(Management(client))
