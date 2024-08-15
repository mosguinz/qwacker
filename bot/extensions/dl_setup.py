import csv
import logging
import pprint
import traceback
from dataclasses import dataclass
from typing import Self

import discord
import emoji
from discord import app_commands
from discord.ext import commands

log = logging.getLogger()


@dataclass
class DL:
    first: str
    last: str
    email: str
    sections: list[int]
    username: str
    emojis: list[str]
    preferred: str = None

    @classmethod
    def from_dict_csv(cls: Self, d: dict) -> Self:
        for field in "First", "Last", "Email", "Sections":
            if not d[field]:
                raise ValueError(f"Missing value for {field}")
        cls.first = d.get("First")
        cls.last = d.get("Last")
        cls.email = d.get("Email")

        try:
            cls.sections = list(int(s) for s in ",".split(d.get("Sections")))
        except ValueError:
            raise ValueError(
                f"Bad value for Sections field, expecting comma-separated integers, got: {d.get('Sections')}"
            )

        cls.preferred = d.get("Preferred") or None

        for character in d.get("Emojis", "").replace(" ", ""):
            if emoji.is_emoji(character):
                cls.emojis.append(character)
            else:
                raise ValueError(f"'{character}' is not a valid emoji character")

        return cls


def parse_csv(raw_csv: str) -> list[DL]:
    reader = csv.DictReader(raw_csv.splitlines())
    dls = []

    if missing := {"First", "Last", "Email", "Sections", "Username"} - set(reader.fieldnames):
        raise ValueError(f"Missing required fields: {', '.join(missing)}. Got: {reader.fieldnames}")

    for i, row in enumerate(reader, start=1):
        try:
            dl = DL.from_dict_csv(row)
        except ValueError as e:
            raise ValueError(f"Parsing failed at row {i}") from e
    return dls


class DLSetup(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    group = app_commands.Group(name="dl", description="Manage discussion leader (DL) roles and channels.")

    @group.command(name="add", description="Add a DL role and channel.")
    async def dl_add(
        self,
        interaction: discord.Interaction,
        first: str,
        last: str,
        preferred: str,
        email: str,
        sections: str,
        user: discord.User,
        emojis: str,
    ):
        pass

    @group.command(name="setup", description="Set up roles and ask-channels for Discussion Leaders")
    @app_commands.describe(csv_file="The CSV file to read.")
    async def dl_setup(self, interaction: discord.Interaction, csv_file: discord.Attachment = None) -> None:
        if not csv_file:
            await interaction.response.send_message("TODO: Show help + CSV format")
            return
        b = await csv_file.read()
        try:
            dls = parse_csv(b.decode("utf-8"))
        except ValueError as e:
            await interaction.response.send_message(f"```{''.join(traceback.format_exception(e))}```")
            return

        await interaction.response.send_message(dls)


async def setup(bot: commands.Bot):
    log.info("Loading DLSetup extension")
    await bot.add_cog(DLSetup(bot))
