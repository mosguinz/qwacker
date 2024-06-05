import logging
import os

import discord
from discord.ext.commands import Bot

GUILD_ID = os.getenv("GUILD_ID")
BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

log = logging.getLogger(__name__)
GUILD = discord.Object(id=GUILD_ID)
PREFIX = "/"

intents = discord.Intents.default()
intents.message_content = True


class Qwacker(Bot):
    def __init__(self, **kwargs):
        super().__init__(
            command_prefix=PREFIX,
            case_insensitive=True,
            intents=intents
        )

    async def setup_hook(self) -> None:
        await self.load_extension("bot.extensions.archive_channels")

        self.tree.copy_global_to(guild=GUILD)
        await self.tree.sync(guild=GUILD)


bot = Qwacker()


@bot.event
async def on_ready():
    log.info(f"Ready. Logged in as {bot.user} (ID: {bot.user.id}).")


bot.run(BOT_TOKEN)