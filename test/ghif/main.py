import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

import src.ghif
import cProfile
import asyncio

token = ""
with open("token.txt", "r") as handle:
    token = handle.read().strip()

src.ghif.config(token)

cProfile.run(
    'asyncio.run(src.ghif.load("https://github.com/Rapptz/discord.py/", "master", "discord"))',
    "stats",
)

exit(0)
mapping: list[dict[str, str | int]] = asyncio.run(
    src.ghif.load("https://github.com/Rapptz/discord.py/", "master", "discord")
)

import json

with open("output.json", "w") as handle:
    json.dump(mapping, handle, indent=4)
