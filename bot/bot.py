import discord , os
from discord.ext import commands, tasks
import logging
import asyncio
from traceback import format_exception
import datetime

logger = logging.getLogger(__name__)

from .database import Server, Welcome, select
from .database.engine import Session
from .modules.get import get_prefix, get_blacklist, get_whitelist, get_welcome


# ["admin"]

class One_word_story(commands.Bot):
    def __init__(self, *args, **kwargs):
        self._cogs = [i[:-3] for i in os.listdir("./bot/cogs") if i.endswith(".py") and not i.startswith("_")]
        self.sessionmaker = Session
        if not self._cogs:
            logger.warning("NO COGS found")
        super().__init__(command_prefix=get_prefix, case_insensitive=True, *args, **kwargs)
        self.update_connection.start()
        self.connection_made = False

    def setup(self):
        logger.info("Running setup...")

        for cog in self._cogs:
            self.load_extension(f"bot.cogs.{cog}")
            logger.info(f" Loaded {cog} cog.")

        logger.info("Setup complete.")

    def run(self,token ,*args, **kwargs):
        # TOKEN = os.getenv("TOKEN")
        self.setup()
        logger.info("Running bot...")
        super().run(token, *args, **kwargs)


    async def on_ready(self):
        activity = discord.Activity(type=discord.ActivityType.watching, name ="YOU, and Reading.")
        await self.change_presence(activity = activity)

        print(f"HI, Connected as: {self.user}")
        logger.info("Client Ready.")


    async def on_command_error(self, ctx, err):
        if isinstance(err, commands.errors.CommandNotFound):
            return
        if isinstance(err, commands.errors.MissingPermissions):
            # msg = await ctx.send(str(err))
            # await msg.delete(delay=4)
            return
        if isinstance(err, commands.errors.MissingRequiredArgument):
            await ctx.send("Incorrect syntax for command.")
            # await msg.delete(delay=4)
            return
        if isinstance(err, commands.errors.NoPrivateMessage):
            await ctx.send("Cannot use this command in DM.")
            return
        if isinstance(err, commands.errors.BotMissingPermissions):
            if err.missing_perms.send_messages:
                await ctx.send(f"Bot is Missing permissions. {err.missing_perms}")
            print(err)
            return
        if isinstance(err, commands.errors.CommandOnCooldown):
            await ctx.send(str(err))
            return
        if isinstance(err, commands.errors.PrivateMessageOnly):
            await ctx.send(str(err))
            return
        if isinstance(err, commands.errors.BadArgument):
            await ctx.send(str(err))
            return

        # self.session.rollback()
        logger.error(err)
        result = "".join(format_exception(err, err, err.__traceback__))
        channel = self.get_channel(839110474284793866)

        now = datetime.datetime.now() + datetime.timedelta(hours=5.5)
        now = now.strftime("%d %b, %Y at %I:%M:%S %p")
        await channel.send(f"{now}\n```py\n{result}```")
        # raise err

    async def close(self):
        try:
            await self.session.commit()
        except:
            await self.session.rollback()
        await self.session.close()
        try:
            self.update_connection.cancel()
        except asyncio.CancelledError:
            pass
        await super().close()


    async def on_connect(self):
        if not self.connection_made:
            logger.info("Bot client Connected.")

        self.session = self.sessionmaker()

        await self.wait_until_ready()
        # self.setup()

        guild_ids = [str(guild.id) for guild in self.guilds]
        statement = select( Server ).where(Server.id_.in_(guild_ids) )
        result = await self.session.execute( statement )

        registered_guilds = {int(guild[0].id_) for guild in result.unique().all()}

        stmt = select( Welcome ).where(Welcome.id_.in_(guild_ids) )
        (await self.session.execute( stmt )).unique().all()
        # result structure:
        # [
        # ( Guild(id = 760130003555581964 prefix = [;;]), 
        # )
        # ]
        for server in self.guilds:
            if server.id not in registered_guilds:
                new_guild = Server(id_ = server.id , name = server.name)
                self.session.add(new_guild)
        await self.session.commit()
        await self.load_data()
        self.connection_made = True


    async def on_guild_join(self, guild):
        new_guild = Server(id_ = guild.id , name=guild.name)
        self.session.add( new_guild )
        await self.load_data()



    async def on_message(self, message):
        if not self.is_ready():
            return
        if not message.guild:
            await self.process_commands(message)
            return
        blacklist = self.blacklist[message.guild.id]
        whitelist = self.whitelist[message.guild.id]
        channel = str(message.channel.id)
        user = str(message.author.id)

        perms = message.channel.permissions_for(message.author)

        if perms.administrator:
            pass
        elif user in whitelist.user:
            pass
        elif whitelist.channel:
            if channel in whitelist.channel:
                pass
        elif user in blacklist.user:
            return
        elif channel in blacklist.channel:
            return

        await self.process_commands(message)

    async def load_data(self):
        try:
            del self.blacklist
            del self.whitelist
            del self.welcome
        except AttributeError:
            pass
        self.blacklist = dict()
        self.whitelist = dict()
        self.welcome = dict()

        for guild in self.guilds:
            blacklist = await get_blacklist(self, guild.id)
            self.blacklist[guild.id] = blacklist

            whitelist = await get_whitelist(self, guild.id)
            self.whitelist[guild.id] = whitelist

            welcome = await get_welcome(self, guild.id)
            if welcome:
                self.welcome[guild.id] = int(welcome)

    @tasks.loop(minutes=20)
    async def update_connection(self):
        if not self.connection_made:
            return
        try:
            await self.session.commit()
        except:
            await self.session.rollback()
        await self.session.close()

        await self.on_connect()

    @update_connection.before_loop
    async def wait(self):
        await self.wait_until_ready()

