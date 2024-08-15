import csv
import logging
import pprint
import traceback
from dataclasses import dataclass
from datetime import datetime
from typing import Self

import discord
import emoji
from discord import app_commands, Embed
from discord.ext import commands

log = logging.getLogger()


class DL:
    first: str
    last: str
    email: str
    sections: list[int] = []
    username: str = None
    emojis: list[str] = []
    preferred: str = None
    timestamp: datetime = None

    def __init__(self, d: dict):
        for field in "First", "Last", "Email", "Sections":
            if not d[field]:
                raise ValueError(f"Missing value for {field}")
        self.first = d.get("First")
        self.last = d.get("Last")
        self.email = d.get("Email")

        try:
            self.sections = list(int(s) for s in d.get("Sections").split(","))
        except ValueError:
            raise ValueError(
                f"Bad value for Sections field, expecting comma-separated integers, got: {d.get('Sections')}"
            )

        self.preferred = d.get("Preferred") or None

        # try to escape some :emojis:
        self.emojis = list(e["emoji"] for e in emoji.emoji_list(emoji.emojize(d.get("Emojis", ""), language="alias")))

        if raw_ts := d.get("Timestamp"):
            try:
                self.timestamp = datetime.fromisoformat(raw_ts)
            except ValueError:
                raise ValueError(f"Bad timestamp format. Must be ISO 8601. Got: {raw_ts}")

    def __repr__(self) -> str:
        return (
            f"DL(first={self.first!r}, last={self.last!r}, preferred={self.preferred!r}, "
            f"email={self.email!r}, sections={self.sections!r}, username={self.username!r}, "
            f"emojis={self.emojis!r}), timestamp={self.timestamp!r}"
        )


def parse_csv(raw_csv: str) -> list[DL]:
    reader = csv.DictReader(raw_csv.splitlines())
    dls = []

    if missing := {"First", "Last", "Email", "Sections", "Username"} - set(reader.fieldnames):
        raise ValueError(f"Missing required fields: {', '.join(missing)}. Got: {reader.fieldnames}")

    for i, row in enumerate(reader, start=1):
        try:
            dl = DL(row)
            dls.append(dl)
        except Exception as e:
            raise ValueError(f"Parsing failed at row {i}: {row}") from e

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

        await interaction.response.send_message(embed=Embed(description=f"```{pprint.pformat(dls)}```"))


async def setup(bot: commands.Bot):
    log.info("Loading DLSetup extension")
    await bot.add_cog(DLSetup(bot))
