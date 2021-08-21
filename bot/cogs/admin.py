import discord
from discord.ext import commands
import logging

logger = logging.getLogger(__name__)


# ___ coppied ___ # eval command
import contextlib
import io
import textwrap
from traceback import format_exception
from ..modules import clean_code, Pag
# from discord.ext.buttons import Paginator



class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(name="load", description="Loads a given cog.")
    async def load_cog(self, ctx, name):
        try:
            self.bot.load_extension(f"bot.cogs.{name}")
        except discord.ext.commands.errors.ExtensionAlreadyLoaded:
            self.bot.reload_extension(f"bot.cogs.{name}")
        await ctx.send(f"Loaded {name}")
    @commands.command("unload", description= "Unloads a given cog.")
    async def unload_cog(self, ctx, name):
        self.bot.unload_extension(f"bot.cogs.{name}")
        await ctx.send(f"Unloaded {name}")
    @commands.command("reload", description= "Reloads a given cog.")
    async def reload_cog(self, ctx, name):
        self.bot.reload_extension(f"bot.cogs.{name}")
        await ctx.send(f"Reloaded {name}")



    @commands.command(name="reset", description="Reset chached data.")
    async def reload_data(self, ctx):
        await self.bot.load_data()
        await ctx.send("Data reload complete.")

    @commands.command(name="reconnect_db",aliases=["db"], description="create a new connection to the database.")
    async def reconnect_db(self, ctx):
        await self.bot.session.commit()
        await self.bot.session.close()
        # self.session = self.bot.sessionmaker()
        await self.bot.on_connect()
    
        bot_user = ctx.guild.get_member(self.bot.user.id)
        permissions = ctx.channel.permissions_for(bot_user)
        if permissions.send_messages:
            await ctx.send("Connection reset complete.")
        if permissions.manage_messages:
            await ctx.message.delete()



    async def cog_check(self, ctx):
        if not self.bot.owner_id:
            self.bot.owner_id = 580009035743494156
        if ctx.author.id == int(self.bot.owner_id):
            if ctx.guild:
                if ctx.guild.name != "Einstein":
                    return False
            return True
        return False

    # async def cog_command_error(self, ctx, err):
    #     # ctx.author.send("hi, error")
    #     if isinstance(err, discord.ext.commands.errors.CheckFailure):
    #         logger.warning(f"Check failure. command used by {ctx.author.name}, in Guild: {ctx.guild.name}, Guild id: {ctx.guild.id}")
    #         return
    #     exception = "```py" + "".join(format_exception(err, err, err.__traceback__)) + "```"
    #     await ctx.author.send(exception)



    @commands.command(name='eval',aliases=['py'],hidden=True)
    @commands.guild_only()
    async def _eval(self, ctx, *, code):
        bot_user = ctx.guild.get_member(self.bot.user.id)
        permissions = ctx.channel.permissions_for(bot_user)
        if not permissions.send_messages:
            await ctx.author.send("Can't send message in channel'")
            return
        if not permissions.embed_links:
            await ctx.send("Can't send embeds.")
            return

        code = clean_code(code)
        local_variables = {
            "discord": discord,
            "commands": commands,
            "bot": self.bot,
            "ctx": ctx,
            "channel": ctx.channel,
            "author": ctx.author,
            "guild": ctx.guild,
            "message": ctx.message
        }

        stdout = io.StringIO()

        try:
            with contextlib.redirect_stdout(stdout):
                exec(
                    f"async def func():\n{textwrap.indent(code, '    ')}", local_variables,
                )

                obj = await local_variables["func"]()
                result = f"{stdout.getvalue()}\n-- {obj}\n"
                if result == "\n-- None\n":
                    if permissions.add_reactions:
                        await ctx.message.add_reaction(emoji="✅")
                    return

        except Exception as e:
            result = "".join(format_exception(e, e, e.__traceback__))

        pager = Pag(
            timeout=100,
            entries=[result[i: i + 2000] for i in range(0, len(result), 2000)],
            length=1,
            prefix="```py\n",
            suffix="```"
        )

        await pager.start(ctx)



def setup(client):
    client.add_cog(Admin(client))

