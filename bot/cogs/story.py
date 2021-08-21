import discord
from discord.ext import commands
from . import Server
from typing import Union

class Story(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        await commands.guild_only().predicate(ctx)
        await commands.bot_has_permissions(send_messages=True, read_message_history=True).predicate(ctx)

        try:
            await commands.has_any_role("story", "Story").predicate(ctx)
        except commands.errors.MissingAnyRole:
            try:
                await commands.has_permissions(manage_guild=True).predicate(ctx)
            except commands.errors.MissingPermissions:
                try:
                    await commands.has_permissions(manage_channels=True).predicate(ctx)
                except commands.errors.MissingPermissions:
                    return False

        return True



    @commands.command(name="compile",aliases=["raw"], description= "Raw story compilation. needs message id to work.", hidden = True)
    async def compile_(self,ctx, message_id : discord.Message, send_DM = "false", *, Title=None):
        await ctx.channel.trigger_typing()

        story = ''
        story += message_id.content if not message_id.author.bot else ""

        async for i in ctx.channel.history(limit=100_000,after=message_id):
            if i.author.bot or i.id == ctx.message.id:
                continue
            data = i.content
            story += " " + data.strip()

        if send_DM.lower() in ["true","dm","me",'t']:
            reciver = ctx.author
        else:
            reciver = ctx.channel

        if not Title:
            story = "**STORY**\n" + story
        else:
            story = f"**{Title}**\n{story}"

        # [result[i: i + 2000] for i in range(0, len(result), 2000)]
        for i in [story[i: i + 2000] for i in range(0, len(story), 2000)]:
            await reciver.send(i)


    @commands.group(name="story", description="Combines all messages from stories start to end message.", invoke_without_command=True)
    @commands.cooldown(1, 1, commands.BucketType.member)
    async def story(self, ctx):
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        await ctx.send("Type `yes` if you want me to DM you current story.\n(This does not end stroy just DMs you current story).")
        msg = await self.bot.wait_for('message', check=check, timeout=60)

        if msg.content.lower() != "yes":
            return

        # await self.end(ctx, send_DM = True)
        await ctx.send("I will DM you the story.")
        await ctx.invoke(self.end, send_DM = "true", end_=False)


    @story.command(name= "start", aliases=["sts"], description= "Start a new story. Messages after this command will be in story.")
    @commands.cooldown(1, 10, commands.BucketType.guild)
    async def start(self, ctx):
        msg = await ctx.send("Messages after this message will be in story: (Do not delete this message)")
        channel = ctx.channel.id
        message = msg.id
        story_message = f"{channel}-{message}"

        server = await self.bot.session.get( Server, ctx.guild.id)

        if server.story:
            await ctx.send(f"There is an ongoing story, end it before stating new. see: `{ctx.prefix}help story end`")
            return

        server.story = story_message

    @story.command(name= "end", aliases=["es"])
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def end(self, ctx, send_DM = "false", *, Title = None, end_=True):
        server = await self.bot.session.get( Server, ctx.guild.id )
        if not server.story:
            await ctx.send(f"No ongoing story found! See `{ctx.prefix}help story start`")
            return

        story_message = [int(i) for i in server.story.split("-")]

        if ctx.channel.id != story_message[0]:
            ctx.channel = ctx.guild.get_channel( story_message[0] )

        msg = await ctx.channel.fetch_message(story_message[1])

        await ctx.invoke(self.compile_, message_id = msg, send_DM = send_DM, Title= Title)

        if end_:
            server.story = None

    @story.command(name= "id", aliases= ["msg", "change",'update'], description= "Change Story message's id.\n(In case message was deleted, give a new message id)")
    async def change(self, ctx, message_id : Union[discord.Message, str]):
        if isinstance(message_id, discord.Message):
            message_id = message_id.id

        server = await self.bot.session.get( Server, ctx.guild.id )
        if not server.story:
            return
        server.story = server.story.split("-")[0] + f"-{message_id}"

        await ctx.send("Updated Story Starting point.", delete_after=5)

def setup(client):
    client.add_cog( Story(client))
