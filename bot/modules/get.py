import discord
from discord.ext import commands
from ..database import Server, Welcome #, BlackList, WhiteList
from ..constants import PREFIX_SPLIT
from .errors import UnknownListType
from typing import Union


async def get_prefix(bot, message) -> list:
    """
    Recives bot and message from "command_prefix" of bot
    queries prefix of message guild if any else returns ""
    for DM channels, enabling use without prefix.

    Note: might be a bad idea as it uses mysql for each message
    """

    guild = message.guild

    # DM channels
    if not guild:
        return [""]

    server = await bot.session.get(Server, guild.id)
    prefix = server.prefix.split(PREFIX_SPLIT)

    # stmt = select(Server.prefix).where(Server.id_ == guild.id)
    # prefix = (await bot.session.execute( stmt )).scalar_one().split(",")

    prefix.sort(reverse=True, key = lambda e: len(e))
    return commands.when_mentioned_or(*prefix)(bot, message)


async def get_lists(bot, guild : Union[str, int, discord.Guild, discord.Object], table : str) -> discord.Object:
    if isinstance(guild, (discord.Guild, discord.Object) ):
        guild = str(guild.id)
    elif isinstance(guild, int):
        guild = str(guild)

    server = await bot.session.get( Server, guild )

    if table == "blacklist":
        table = server.blacklist
    elif table == "whitelist":
        table = server.whitelist
    else:
        raise UnknownListType("Unknown Type", "Only 'blacklist' or 'whitelist'")

    channel = set()
    user = set()
    for row in table:
        if row.channel:
            channel.add(row.channel)
        elif row.user:
            user.add(row.user)
        # channel = {ch.channel for ch in table if ch.channel}
        # user = {user.user for user in table if user.user}

    obj = discord.Object(int(server.id_))
    obj.channel = channel
    obj.user = user
    #{"id": guild.id_ ,"channel": channel, "user": user}
    return obj

async def get_whitelist(bot, guild):
    return await get_lists(bot, guild, "whitelist")
async def get_blacklist(bot, guild):
    return await get_lists(bot, guild, "blacklist")

async def get_welcome(bot, guild):
    if isinstance(guild, (discord.Guild, discord.Object) ):
        guild = str(guild.id)
    elif isinstance(guild, int):
        guild = str(guild)

    welcome = await bot.session.get( Welcome, guild )
    if welcome:
        return welcome.channel


