import csv
import logging
import pprint
import random
import traceback
from dataclasses import dataclass
from datetime import datetime
from typing import Self

import discord
import emoji
from discord import app_commands, Embed, TextChannel
from discord.ext import commands

log = logging.getLogger()

# fmt: off
DL_TABS_URL = "https://dl.ducta.net"
# Hopefully non-offensive food emojis...
FALLBACK_EMOJIS = [
    "🍇", "🍈", "🍉", "🍊", "🍋", "🍋‍🟩", "🍌", "🍍", "🥭", "🍎", "🍏",
    "🍐", "🍒", "🍓", "🫐", "🥝", "🍅", "🫒", "🥥", "🥑", "🍮", "🍯",
    "🥔", "🥕", "🌽", "🌶️", "🫑", "🥒", "🥬", "🥦", "🧄", "🧅", "🥜",
    "🫘", "🌰", "🫚", "🫛", "🍄‍🟫", "🍞", "🥐", "🥖", "🫓", "🥨", "🥯",
    "🥞", "🧇", "🧀", "🍖", "🍗", "🥩", "🥓", "🍔", "🍟", "🍕", "🌭",
    "🥪", "🌮", "🌯", "🫔", "🥙", "🧆", "🥚", "🍳", "🥘", "🍲", "🫕",
    "🥣", "🥗", "🍿", "🧈", "🧂", "🥫", "🍝", "🍱", "🍘", "🍙", "🍚",
    "🍛", "🍜", "🍠", "🍢", "🍣", "🍤", "🍥", "🥮", "🍡", "🥟", "🥠",
    "🥡", "🍦", "🍧", "🍨", "🍩", "🍪", "🎂", "🍰", "🧁", "🥧", "🍫",
    "🍬", "🍭",
]
# fmt: on


class DiscussionLeader:
    first: str
    last: str
    email: str
    sections: list[int] = []
    username: str = None
    emojis: list[str] = []
    preferred: str = None
    timestamp: datetime = None

    # assigned after role creation
    role: discord.Role = None
    role_emoji: str = None

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

        if preferred := d.get("Preferred"):
            self.preferred = preferred if preferred.lower() != self.first.lower() else None

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

    def get_preferred_name(self):
        """Returns the preferred name, if one exists. Otherwise, returns the first name."""
        return self.preferred or self.first

    def get_full_name(self):
        """Returns "First Last" or "First "Preferred" Last"."""
        if self.preferred:
            return f"{self.first} “{self.preferred}” {self.last}"
        return f"{self.first} {self.last}"

    def get_sections_string(self):
        """Returns "Section 1" or "Sections 1 and 2" or "Sections 1, 2, and 3"."""
        if len(self.sections) == 1:
            return f"Section {self.sections[0]}"
        elif len(self.sections) == 2:
            return f"Sections {self.sections[0]} and {self.sections[1]}"
        else:
            return f"Sections {', '.join(str(s) for s in self.sections[:-1])}, and {self.sections[-1]}"

    def get_ask_channel_name(self) -> str:
        """Returns "❓ask-name"."""
        return f"❓ask-{self.get_preferred_name()}"

    def get_role_name(self) -> str:
        """Returns "Team Name"."""
        return f"Team {self.get_preferred_name()}"


def parse_csv(raw_csv: str) -> list[DiscussionLeader]:
    reader = csv.DictReader(raw_csv.splitlines())
    dls = []

    if missing := {"First", "Last", "Email", "Sections", "Username"} - set(reader.fieldnames):
        raise ValueError(f"Missing required fields: {', '.join(missing)}. Got: {reader.fieldnames}")

    for i, row in enumerate(reader, start=1):
        try:
            dl = DiscussionLeader(row)
            dls.append(dl)
        except Exception as e:
            raise ValueError(f"Parsing failed at row {i}: {row}") from e

    return dls


def create_role_embed(dls: list[DiscussionLeader]) -> Embed:
    """Create embed for role selections."""
    embed = Embed()
    embed.set_author(name="For CSC 215 Duclings")
    embed.description = (
        "Click on the reactions below to access the channel for your Discussion Section. "
        "You will also be notified for any notifications your Discussion Leader sends."
    )
    sorted_dls = sorted(dls, key=lambda d: d.last)
    for dl in sorted_dls:
        embed.add_field(
            name=dl.get_full_name(),
            value=f"{dl.role_emoji} <@&{dl.role.id if dl.role else dl.get_role_name()}>\n"
            f"-# {dl.get_sections_string()}",
            inline=True,
        )
    return embed


def assign_role_emoji(dls: list[DiscussionLeader]) -> list[DiscussionLeader]:
    """Assign role emojis based on their provided preference."""
    dls.sort(key=lambda d: d.timestamp or datetime.today(), reverse=True)
    chosen_emojis = []
    for dl in dls:
        for e in dl.emojis:
            if e not in chosen_emojis:
                dl.role_emoji = e
                chosen_emojis.append(e)
                break
        # Possible infinite loop if there are more than 100 DLs and all of them pick a food emoji...
        while dl.role_emoji is None:
            dl.role_emoji = random.choice(FALLBACK_EMOJIS)

    return dls


async def create_ask_channel(dl: DiscussionLeader, category: discord.CategoryChannel) -> discord.TextChannel:
    channel = await category.create_text_channel(name=dl.get_ask_channel_name())
    await channel.edit(
        topic=f"<@&{dl.role.id}> **{dl.get_sections_string()}** \n\n"
        f"For sensitive issues, please email {dl.email}. "
        f"For session times and agenda, visit {DL_TABS_URL}."
    )
    await channel.set_permissions(target=dl.role, read_messages=True)
    return channel


class DLSetup(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    group = app_commands.Group(name="dl", description="Manage discussion leader (DL) roles and channels.")

    @group.command(name="add", description="Add a DL role and channel.")
    async def dl_add(
        self,
        interaction: discord.Interaction,
    ):
        pass

    @group.command(name="setup", description="Set up roles and ask-channels for Discussion Leaders")
    @app_commands.describe(csv_file="The CSV file to read.")
    async def dl_setup(
        self, interaction: discord.Interaction, category: discord.CategoryChannel, csv_file: discord.Attachment = None
    ) -> None:
        if not csv_file:
            await interaction.response.send_message("TODO: Show help + CSV format")
            return

        b = await csv_file.read()
        try:
            dls = parse_csv(b.decode("utf-8"))

            chosen_emojis = []
            # first sort DLs by timestamp submitted for emoji preference
            dls.sort(key=lambda dl: dl.timestamp, reverse=True)

            for dl in dls:
                role = await interaction.guild.create_role(name=dl.get_role_name())
                channel = await create_ask_channel(dl, category, role)

        except ValueError as e:
            await interaction.response.send_message(f"```{''.join(traceback.format_exception(e))}```")
            return

        await interaction.response.send_message(embed=Embed(description=f"```{pprint.pformat(dls)}```"))


async def setup(bot: commands.Bot):
    log.info("Loading DLSetup extension")
    await bot.add_cog(DLSetup(bot))
