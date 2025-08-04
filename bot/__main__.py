import logging
import os

import discord
from discord.ext.commands import Bot

from bot.constants import Bot as BotConfig
from bot.constants import Guild


discord.utils.setup_logging()
log = logging.getLogger()

intents = discord.Intents.default()
intents.message_content = True

GUILD = discord.Object(id=Guild.id)


class Qwacker(Bot):
    def __init__(self, **kwargs):
        super().__init__(
            command_prefix=BotConfig.prefix, case_insensitive=True, intents=intents
        )

    async def setup_hook(self) -> None:
        await self.load_extension("bot.extensions.archive_channels")
        await self.load_extension("bot.extensions.rules")
        await self.load_extension("bot.extensions.dl_setup")

        self.tree.copy_global_to(guild=GUILD)
        await self.tree.sync(guild=GUILD)


bot: Bot = Qwacker()


@bot.event
async def on_ready():
    guild = await bot.fetch_guild(Guild.id)
    log.info(f"Ready. Logged in as {bot.user} (ID: {bot.user.id}).")
    log.info(f"Current guild: {guild.name} (ID: {guild.id}).")


bot.run(BotConfig.token)
