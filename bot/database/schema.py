from sqlalchemy import Column, String, Table, null, ForeignKey, Integer, Text
from sqlalchemy.orm import declarative_base, relationship #, selectinload
from sqlalchemy.future import create_engine
# from sqlalchemy.dialects.mysql import INTEGER

import json
from typing import List, Optional
import logging

if __name__ != "__main__":
    from ..constants import PREFIX_SPLIT
else:
    PREFIX_SPLIT = ","

logger = logging.getLogger(__name__)

Base = declarative_base()

# ~;;~
class Server(Base):
    __tablename__ = "server"

    id_ = Column(String(20), primary_key=True, autoincrement=False)
    name = Column(String(50))
    prefix = Column(String(100), default=";;" )
    story = Column(String(40), default=null() )
    activity = Column(String(20), default=null() )
    welcome = Column(String(20), default=null() )

    blacklist = relationship("BlackList", back_populates = "guild", lazy=False ) #Column(String, default=null() )
    whitelist = relationship("WhiteList", back_populates = "guild", lazy=False )

    def __repr__( self ):
        return f"Guild(id = {self.id_} prefix = {self.prefix_split})"


    def find(self, col, type_, id):
        for row in col:
            if type_ == "user":
                if row.user == str(id):
                    return row
            elif type_ == "channel":
                if row.channel == str(id):
                    return row

    def find_all(self, col, type_) -> set:
        result = set()
        for row in col:
            if type_ == "user":
                if row.user:
                    result.add(int(row.user))
            elif type_ == "channel":
                if row.channel:
                    result.add(int(row.channel))

    @property
    def prefix_split(self):
        return [i for i in self.prefix.split(PREFIX_SPLIT) ]

    @property
    def id(self):
        return int(self.id_)
    
    @property
    def stroy_id(self):
        return [int(i) for i in self.stroy.split("-")]



class BlackList(Base):
    __tablename__ = 'blacklist'

    # id_ = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    id_ = Column(Integer, primary_key=True, autoincrement=True)
    channel = Column(String(20), default=null())
    user = Column(String(20), default=null())
    guild_id = Column(String(20), ForeignKey("server.id_"), nullable=False )

    guild = relationship("Server", back_populates = "blacklist", lazy=False)

    def __repr__(self):
        return f"Blacklist(Guild = {self.guild_id} User = {self.user} Channel = {self.channel})"

class WhiteList(Base):
    __tablename__ = 'whitelist'

    # id_ = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    id_ = Column(Integer, primary_key=True, autoincrement=True)
    channel = Column(String(20), default=null())
    user = Column(String(20), default=null())
    guild_id = Column(String(20), ForeignKey("server.id_"), nullable=False )

    guild = relationship("Server", back_populates = "whitelist", lazy=False)

    def __repr__(self):
        return f"Whitelist(Guild = {self.guild_id} User = {self.user} Channel = {self.channel})"


class Welcome(Base):
    __tablename__ = 'welcome'

    id_ = Column(String(20), primary_key=True, autoincrement=False)
    channel = Column(String(20), unique=True)
    pfp = Column(Integer)
    coordinates = Column(String(10), default= "0,0" )
    embed_ = Column(Text, default=null())
    state = Column(String(8), default="false")
    round = Column(Integer, default = 0)

    def __repr__(self):
        return f"Welcome(Guild = {self.id_} Channel = {self.channel} pfp = {self.pfp} coordinates = {self.posxy})"

    @property
    def id(self) -> int:
        return int(self.id_)

    @property
    def posxy(self) -> List[int]:
        return [int(i) for i in self.coordinates.split(",")]

    @property
    def embed(self) -> dict:
        try:
            data = json.loads(self.embed_)
        except json.decoder.JSONDecodeError:
            if self.embed_ :
                logger.critical(self.embed_)
            data = None
        return data

    @embed.setter
    def embed(self, data : Optional[dict]) -> None:
        if not data:
            self.embed_ = None
            return
        self.embed_ = json.dumps(data)

    @embed.deleter
    def embed(self, val) -> None:
        self.embed_ = None
    
    def load(self, data):
        return json.loads(data)


if __name__ == "__main__":
    def create(engine, base):
        base.metadata.drop_all(engine)
        base.metadata.create_all(engine)

    engine = create_engine('mysql+mysqlconnector://root:1234@localhost:3306/alchemy', future=True, hide_parameters=True)
    create(engine, Base)

