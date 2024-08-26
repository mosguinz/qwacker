import csv
import logging
import random
import traceback
from dataclasses import dataclass, field
from datetime import datetime

import discord
import emoji
from discord import app_commands, Embed
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


@dataclass
class DiscussionLeader:
    first: str
    last: str
    email: str
    sections: list[int] = field(default_factory=list)
    username: str = None
    emojis: list[str] = field(default_factory=list)
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

    @property
    def preferred_name(self):
        """Returns the preferred name, if one exists. Otherwise, returns the first name."""
        return self.preferred or self.first

    @property
    def full_name(self):
        """Returns "First Last" or "First "Preferred" Last"."""
        if self.preferred:
            return f"{self.first} “{self.preferred}” {self.last}"
        return f"{self.first} {self.last}"

    @property
    def sections_string(self):
        """Returns "Section 1" or "Sections 1 and 2" or "Sections 1, 2, and 3"."""
        if len(self.sections) == 1:
            return f"Section {self.sections[0]}"
        elif len(self.sections) == 2:
            return f"Sections {self.sections[0]} and {self.sections[1]}"
        else:
            return f"Sections {', '.join(str(s) for s in self.sections[:-1])}, and {self.sections[-1]}"

    @property
    def ask_channel_name(self) -> str:
        """Returns "❓ask-name"."""
        return f"❓ask-{self.preferred_name}"

    @property
    def role_name(self) -> str:
        """Returns "Team Name"."""
        return f"Team {self.preferred_name}"


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
            name=dl.full_name,
            value=f"{dl.role_emoji} <@&{dl.role.id if dl.role else dl.role_name}>\n" f"-# {dl.sections_string}",
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
    """
    Create the "❓ask-name" channel for a given DL.

    The created channel contains the DL's section(s) and email. The permission is set
    such that users with the DL's role can access the channel. For access to work properly,
    the parent category must not have other overrides for other publicly-assignable roles.
    """
    channel = await category.create_text_channel(name=dl.ask_channel_name)
    await channel.edit(
        topic=f"<@&{dl.role.id}> **{dl.sections_string}** \n\n"
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

    @group.command(name="setup", description="Set up roles and ask-channels for Discussion Leaders.")
    @app_commands.describe(category="The category to place the channels in.")
    @app_commands.describe(role_channel="The channel to send the role reaction embed.")
    @app_commands.describe(csv_file="The CSV file to read.")
    async def dl_setup(
        self,
        interaction: discord.Interaction,
        category: discord.CategoryChannel,
        role_channel: discord.TextChannel,
        csv_file: discord.Attachment = None,
    ) -> None:
        if not csv_file:
            await interaction.response.send_message("TODO: Show help + CSV format")
            return

        await interaction.response.defer(thinking=True)
        dls: list[DiscussionLeader]

        try:
            b = await csv_file.read()
            dls = parse_csv(b.decode("utf-8"))
        except ValueError as e:
            await interaction.followup.send(f"Bad CSV format: ```{''.join(traceback.format_exception(e))}```")
            return

        await interaction.followup.send("CSV file successfully parsed. Creating roles...")

        # Sort by preferred name for channel creation.
        dls = assign_role_emoji(dls)
        dls.sort(key=lambda d: d.preferred_name)
        for dl in dls:
            # Create role and channel for DL.
            dl.role = await interaction.guild.create_role(name=dl.role_name, color=discord.Color.orange())
            channel = await create_ask_channel(dl, category)
            await interaction.followup.send(f"Created role <@&{dl.role.id}> and {channel.jump_url} for {dl.full_name}.")

        # Sort by last name for role selection.
        dls.sort(key=lambda d: d.last)
        role_message = await role_channel.send(embed=create_role_embed(dls))

        # Add the reactions to the message.
        # This is the ONLY way to guarantee order of reaction that is consistent with the embed
        # because Carl-bot's `!rr addmany` does not respect the order of the reactions provided.
        for dl in dls:
            await role_message.add_reaction(dl.role_emoji)

        await interaction.followup.send(
            content="\n".join(
                [
                    "# Set up reaction roles",
                    f"A message have been sent for role selection: {role_message.jump_url}. "
                    "Carl-bot handles role assignments, not this bot.",
                    "To add reactions for role selection, copy and send the following command:",
                    f"```/reactionrole addmany channel:{role_channel.id} message_id:{role_message.id} emoji_role_pair:",
                    *(f"{d.role_emoji} {d.role.id}" for d in dls),
                    "```",
                ]
            )
        )


async def setup(bot: commands.Bot):
    log.info("Loading DLSetup extension")
    await bot.add_cog(DLSetup(bot))
