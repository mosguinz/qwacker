import discord
from discord import app_commands
from discord.ext import commands


class ArchiveCategory(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="archive", description="Archive text channels in the given category ID")
    @app_commands.describe(
        to_archive="Text channel or category to archive",
        destination="Category to move the channels into",
        suffix="Suffix to add to the channel name e.g., “-fa23”",
    )
    async def archive(
        self,
        interaction: discord.Interaction,
        to_archive: discord.TextChannel | discord.CategoryChannel,
        destination: discord.CategoryChannel,
        suffix: str = None,
    ):
        channels = to_archive.text_channels if isinstance(to_archive, discord.CategoryChannel) else [to_archive]

        for channel in channels:
            if suffix:
                await channel.edit(name=channel.name + suffix, reason="Archiving channel")
            await channel.move(end=True, category=destination, sync_permissions=True, reason="Archiving channel")

        await interaction.response.send_message(f"Finished archiving {len(channels)} channel(s).")


async def setup(bot: commands.Bot):
    await bot.add_cog(ArchiveCategory(bot))
