import discord
from discord.ext import commands
from . import Server, Welcome, pool_func, create_embed

import logging

logger = logging.getLogger(__name__)

image_path = "images/"

class Welcome_settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    async def cog_check(self, ctx):
        await commands.guild_only().predicate(ctx)
        try:
            await commands.has_permissions(manage_guild=True).predicate(ctx)
        except commands.errors.MissingPermissions:
            return False

        await commands.bot_has_permissions(send_messages=True, embed_links=True, read_message_history=True).predicate(ctx)
        return True

    @commands.Cog.listener(name="on_member_join")
    async def listening(self, member):
        guild = member.guild
        if guild.id not in self.bot.welcome:
            return

        channel = self.bot.welcome[guild.id]
        channel = guild.get_channel( int(channel) )

        ctx = discord.Object
        ctx.guild = guild
        ctx.author = member
        ctx.channel = channel

        await self.test(ctx)

    @commands.group(name= "welcome", aliases=["wc"], description="Set a welcome message for new members.", invoke_without_command=True)
    async def welcome(self, ctx):
        welcome = await self.bot.session.get( Welcome, ctx.guild.id )
        if welcome:
            await ctx.send(f"Sending welcome message in <#{welcome.channel}>")
        else:
            await ctx.send(f"To set Welcome message. see **`{ctx.prefix}help welcome create`**")


    @welcome.command(name= "toggle", aliases=["state"], description="Stop/resume sending welcome messages.")
    async def toggle(self, ctx, state : str):
        welcome = await self.bot.session.get( Welcome, ctx.guild.id )
        if not welcome:
            return
        if not welcome.embed:
            return

        if state.lower() in ['false', 'disable', 'f', 'off']:
            welcome.state = 'false'
        elif state.lower() in ['true', 'enable', 't', 'on']:
            welcome.state = 'true'
        else:
            return

        await ctx.send(f"Changed state to **{state}**")

    @welcome.command(name= "create", aliases=['cr'], description= "Start intractive session to create a new welcome message.")
    async def create(self, ctx):
        # await ctx.send()
        user = ctx.author
        def check(m):
            return m.author.id == user.id and m.channel.id == ctx.channel.id
        async def bye():
            await ctx.send("Stopped. Bye!")
        async def say(text, msg=False, **kwargs):
            await ctx.send(text, **kwargs)
            reply = await self.bot.wait_for('message', check=check, timeout= 60)
            return reply.content.lower() if not msg else reply

        reply = await say("Do you want to create a new welcome message?\n**[y/anything]:**")
        if reply != 'y':
            return await bye()

        thumb = "text 1\n **'Thumbnail'** appears where server icon is displayed."
        img = "text 2\n **'image'** appears where your profile picture is displayed."


        welcome_embed = discord.Embed()

        """ Example """
        reply = await say("Do you want a example of embed?\n**type `~` to stop, [y/anything]:**")
        if reply == '~':
            return await bye()
        elif reply == 'y':
            embed = create_embed("Title", "Description", footer="footer", field_1=thumb, field_2=img)
            embed.set_thumbnail(url=ctx.guild.icon_url).\
                set_image(url=user.avatar_url)
            await ctx.send(embed = embed)


        """ Thumbnail """
        reply = await say("Do you want thumbnail to be **server icon?**\n**type `~` to stop,  [y/anything(no thumbnail)]**")
        if reply == "~":
            return await bye()
        elif reply == "y":
            welcome_embed.set_thumbnail(url = None)


        reply = await say("Color of embed: **(hex value)**")
        try:
            if reply == "~":
                return await bye()
            if reply.startswith("#"):
                reply = reply.strip("#")
            reply = int(reply, 16)
        except ValueError:
            ctx.send("Invalid color hex, anyway.")



        """ TITLE and Description """
        reply = await say("What should be **Title and Description?** seprate them like Title | description\n**type `~` to stop.**")
        if reply == "~":
            return await bye()
        reply = reply.split("|")
        if len(reply) == 2:
            welcome_embed.title = reply[0]
            welcome_embed.description = reply[1]
        else:
            welcome_embed.title = reply[0]

        reply = await say("**Number of fields** you want: (idk max lets keep it **below 6.**)")
        if reply == "~":
            return await bye()
        if reply.isdigit():
            reply = int(reply)
            if 0 < reply < 6:
                for _ in range(reply):
                    reply = await say("Send: Title of field | Text of field")
                    reply = reply.split("|")
                    welcome_embed.add_field(name = reply[0], value = reply[1:])



        """ Image """
        reply = await say("**Send a image** to be used as `image` of Embed.\
            \ntype **`user`** if you want it to be **member's profile picture**", msg=True)
        if reply.content.lower() == "~":
            return await bye()
        elif reply.content.lower() == "user":
            welcome_embed.set_image(url= None)
        else:
            try:
                img = reply.attachments[0]
                img = BytesIO(await img.read())
                img = Image.open(img)
                await pool_func(img.save, f"{image_path}welcome_{ctx.guild.id}.png")
                welcome_embed.set_image(url="attachment://welcome.png")
            except:
                await bye()
                raise

        """ pfp location etc """
        reply = await say("I am Tired. just send **possition,size,round** like this (no quotes) 'x,y size round'")
        reply = reply.split()

        dict_embed = welcome_embed.to_dict()
        print(dict_embed)

        channel : discord.TextChannel = await say("Send **channel.**")

        if not isinstance(channel, discord.TextChannel):
            if "<#" in channel:
                channel = channel.replace("<#", "").replace(">", "")
        else:
            channel = channel.id

        if not dict_embed:
            return await bye()

        welcome = await self.bot.session.get( Welcome, ctx.guild.id)
        if not welcome:
            welcome = Welcome(id_ = ctx.guild.id)
            self.bot.session.add( welcome )
        welcome.channel = channel
        welcome.coordinates = reply[0]
        welcome.pfp = reply[1]
        welcome.round = reply[2]
        welcome.state = "true"
        welcome.embed = dict_embed

        server = await self.bot.session.get( Server, ctx.guild.id )
        server.welcome = channel
        self.bot.welcome[ctx.guild.id] = channel

        await ctx.send("Done!")


    @welcome.command(name= "edit", description="Make Changes in message.")
    async def change(self, ctx):
        welcome = await self.bot.session.get( Welcome, ctx.guild.id )
        if not welcome:
            return
        if not welcome.embed:
            await ctx.send( "Create a Welcome message before editing!" )

        await ctx.send(welcome.embed)
        def check(m):
            return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id

        msg = await self.bot.wait_for('message', check=check, timeout= 100)
        welcome.embed = welcome.load(msg.content)


    @welcome.command(name= "channel", aliases=["ch"])
    async def change_channel(self, ctx, channel : discord.TextChannel):
        welcome = await self.bot.session.get( Welcome, ctx.guild.id )
        if not welcome:
            return
        self.bot.welcome[ctx.guild.id] = channel.id
        welcome.channel = str(channel.id)


    @welcome.command(name= "test", description="Test the welcome message.")
    async def test(self, ctx):
        welcome = await self.bot.session.get( Welcome, ctx.guild.id )
        if not welcome:
            return
        if not welcome.embed:
            try:
                await ctx.send( "Create a Welcome message before testing!" )
            except:
                pass

        channel = ctx.channel

        bot_user = ctx.guild.get_member(self.bot.user.id)
        perms = channel.permissions_for(bot_user)
        if not (perms.send_messages and perms.embed_links and perms.attach_files):
            return

        path = f"{image_path}welcome_{ctx.guild.id}.png"
        try:
            image_ = await place_image(path, ctx.author, welcome.posxy, welcome.pfp, welcome.round)
            image = discord.File(image_, filename= f"welcome.png")
        except Exception as e:
            image = None
            logger.warning(str(e))

        dict_embed = welcome.embed
        try:
            a = dict_embed["thumbnail"]['url'].lower()
            if a == "none":
                dict_embed["thumbnail"]['url'] = str(ctx.guild.icon_url)
        except KeyError:
            pass
        try:
            a = dict_embed["image"]["url"]
            if a != "attachment://welcome.png":
                dict_embed["image"]["url"] = str(ctx.author.avatar_url)
        except KeyError:
            pass

        embed = discord.Embed.from_dict(dict_embed)
        embed.set_footer(text=f"{ctx.author.joined_at.strftime('%d %b, %Y at %I:%M:%S %p')}")
        await channel.send(file = image, embed = embed)
        os.remove(image_)



import os
from PIL import Image, ImageDraw
from io import BytesIO

def add_corners(im, rad) -> Image.Image:
    circle = Image.new('L', (rad * 2, rad * 2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, rad * 2, rad * 2), fill=255)
    alpha = Image.new('L', im.size, 255)
    w, h = im.size
    alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
    alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
    alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
    alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad))
    im.putalpha(alpha)
    return im

async def place_image(image, user,location=(0,0),size=None,_round=0) -> BytesIO:
    # result = BytesIO()
    pfp = user.avatar_url_as(format='png')
    pfp = BytesIO(await pfp.read())

    with Image.open(pfp) as pfp:
        if isinstance(size,(tuple,list,set)):
            pfp = pfp.resize(size)

        with Image.open(image) as im:
            im.paste(pfp, location )
            path = image_path + f"{user.guild.id}_{user.id}.png"

            im = add_corners(im, _round)
            await pool_func(im.save, path, format="PNG" )

    return path




def setup(client):
    client.add_cog( Welcome_settings(client))
