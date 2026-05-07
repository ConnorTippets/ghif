import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

import src.ghif

token = ""
with open("token.txt", "r") as handle:
    token = handle.read().strip()

src.ghif.config(token)
src.ghif.load("https://github.com/Rapptz/discord.py/", "master", "discord")
