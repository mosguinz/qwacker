import discord
from discord import app_commands
from discord.ext import commands


class ArchiveCategory(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="archive", description="Archive text channels in the given category ID"
    )
    @app_commands.describe(
        category_id="The ID of the category containing the channels to archive",
        destination_id="The ID of the category to move the channels into",
        suffix="Suffix to add to the channel name",
    )
    @app_commands.describe()
    async def archive(
        self,
        interaction: discord.Interaction,
        category_id: int,
        destination_id: int,
        suffix: str = None,
    ):
        await interaction.response.send_message("test")


async def setup(bot: commands.Bot):
    await bot.add_cog(ArchiveCategory(bot))
