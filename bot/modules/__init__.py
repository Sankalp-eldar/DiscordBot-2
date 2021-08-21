from discord.ext.buttons import Paginator
import discord
import asyncio
from functools import partial
from .errors import IntegrityError

class Pag(Paginator):
    async def teardown(self):
        try:
            await self.page.clear_reactions()
        except discord.HTTPException:
            pass

def clean_code(content):
    if content.startswith("```") and content.endswith("```"):
        return "\n".join(content.split("\n")[1:])[:-3]
    else:
        return content

def create_embed(title = None, content = None, color = 65535, footer = None, **kwargs):
    embed = discord.Embed(title=title or "", description= content or "", color= color)
    for k, v in kwargs.items():
        if isinstance(v, dict):
            embed.add_field(name=k, value=v["value"], inline = v["inline"])
        else:
            embed.add_field(name=k, value=v )
    if footer:
        embed.set_footer(text=footer)
    return embed

async def pool_func(func, *args, **kw):
    loop = asyncio.get_running_loop()
    func = partial(func, *args, **kw)
    result = await loop.run_in_executor(None, func)
    return result


class Container:
    def __init__(self):
        self._keys = dict()
    def __len__(self):
        return len( self._keys )
    def __repr__(self):
        return f"Container( Total: {len(self)})"

    def get(self, attar, _id):
        attar_key = self._keys.get(attar)
        if not attar_key:
            raise KeyError("Unknown Key.")

        for i in self.__dict__[attar]:
            if i.__dict__[attar_key] == _id:
                return i

    def add(self, attar, value):
        attar_key = self._keys[attar]
        _id = value.__dict__[attar_key]
        exists = self.get(attar, _id)
        if exists:
            raise IntegrityError("Duplicate key. key attribute must be unique.")

        self.__dict__[attar].append(value)
        return self

    def is_empty(self):
        for attar in self._keys:
            if self.__dict__[attar]:
                return False
        return True

    def get_nonempty(self) -> list:
        nonempty = list()
        for attar in self._keys:
            if self.__dict__[attar]:
                nonempty.append( self.__dict__[attar] )
        return nonempty

    def add_attar(self, attar : str, key : str):
        self.__dict__[attar] = list()
        self._keys[attar] = key
        return self
    def del_attar(self, attar):
        del self.__dict__[attar]
        del self._keys[attar]
        return self
    def attar_key(self, attar, key):
        if attar not in self._keys:
            raise AttributeError("No attribute named %s" % attar)
        self._keys[attar] = key
        return self
    def get_attar(self):
        return self._keys

