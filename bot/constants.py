REQUIRED = [
    "discord",
    "buttons",
    "sqlalchemy",
    "mysql-connector-python",
    "aiomysql"
]

PREFIX_SPLIT = ","


ENGINE = 'mysql+aiomysql://Reaper:1234@localhost:3306/alchemy'

ENGINE_lite = 'sqlite+aiosqlite:///alchemy.db'

# non saync engine
ENGINE_ = 'mysql+mysqlconnector://Reaper:1234@localhost:3306/alchemy'

# logging format
FORMAT = '%(asctime)s:%(levelname)s:%(name)s: %(message)s'

import logging
# logging modules
same = logging.INFO
LOGGING = {
    "discord" : {
        "file" : "discord.log",
        "level" : same
        },
    "sqlalchemy"  : {
        "file" : "sqlalchemy.log",
        "level" : same
        },
    "bot"  : {
        "file" : "bot.log",
        "level" : same
        }
}
