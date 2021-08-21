from bot import One_word_story
import os
from bot.constants import LOGGING
from bot.modules.logs import set_logging
from discord import Intents

TOKEN = os.getenv("TOKEN")
print(TOKEN)

intents = Intents.all()

def main():
    for module, v in LOGGING.items():
        set_logging( module, v.get('file'), v.get('level') )

    bot = One_word_story(intents=intents)
    bot.run(TOKEN, reconnect=True)

if __name__ == '__main__':
    main()

