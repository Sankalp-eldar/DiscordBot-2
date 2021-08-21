import discord
from discord.ext import commands



class Moderator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        is_guild = await commands.guild_only().predicate(ctx)
        has_perm = await commands.has_permissions(manage_guild=True).predicate(ctx)
        send_perms = await commands.bot_has_permissions(send_messages=True, embed_links=True).predicate(ctx)
        return is_guild and has_perm and send_perms



def setup(client):
    client.add_cog( Moderator(client))
