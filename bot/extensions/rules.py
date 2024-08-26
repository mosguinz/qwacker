import logging

import discord
from discord import app_commands, Embed
from discord.ext import commands

log = logging.getLogger()

rules_embed = Embed(title="Rules")
rules_embed.description = (
    "Welcome! This is a student-run Discord server for Professor Ta’s classes. To keep things "
    "running smoothly, we kindly ask that you follow a few simple rules."
)
rules_embed.add_field(
    name="😀 Don’t be an asshole", value="No harassment of any kind. Be nice to one another.", inline=False
)
rules_embed.add_field(
    name="🤓 Do not violate the course guidelines and/or policies",
    value="Don’t do anything that will get you kicked out of the class here, like cheating or sharing your solutions "
    "on this server.",
    inline=False,
)
rules_embed.add_field(
    name="😴 Respect people’s boundaries",
    value="This server was created to help students connect with their graders and mentors, who are here voluntarily "
    "to support your success in the course. Please feel free to reach out for help but also be considerate of "
    "their time.",
    inline=False,
)

disclaimer_embed = Embed(title="Disclaimer")
disclaimer_embed.description = "\n\n".join(
    (
        "This Discord server is independently managed by current and former students of Professor Ta "
        "and is not affiliated, authorized, endorsed by, or in any way officially associated with the University or "
        "the Department of Computer Science.",
        "**Your participation is entirely optional**, and the content shared here is for informational purposes only. "
        "Any announcements or communications from tutors, graders, discussion leaders, or any members acting on "
        "official capacity on Discord are provided for your convenience and do not replace official channels such as "
        "email and Canvas discussion forums.",
        "The Department of Computer Science, Professor Ta, and members of his team are not affiliated with this "
        "server and are not responsible for moderating its content. Any advice or information shared here should be "
        "cross-referenced with official resources. The maintainers of this server are not responsible for any "
        "inaccuracies or issues that may arise from the use of this server.",
        "We’ve kept this space running for our fellow Duclings since Spring 2021 and hope to pass it on to future "
        "cohorts — please help us maintain it by adhering to the rules and using common sense.",
    )
)

pick_roles_embed = Embed(title="Ready?")
pick_roles_embed.description = (
    "Click on the reaction below to indicate your agreement with the rules and gain access "
    "to the server. After that, proceed to <#815094070900031530> to obtain your roles!"
)


class Rules(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    group = app_commands.Group(name="rules", description="Manage server rules")

    @group.command(name="post", description="Post the server rules")
    @app_commands.describe(destination="The channel to post to. If not provided, the current channel will be used.")
    async def post(self, interaction: discord.Interaction, destination: discord.TextChannel = None):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You do not have permission to invoke this command.")
            return

        welcome = "# Welcome to CSC Duclings!"
        embeds = [rules_embed, disclaimer_embed, pick_roles_embed]
        if destination:
            message = await destination.send(content=welcome, embeds=embeds)
            await interaction.response.send_message(content=message.jump_url)
            await message.add_reaction("👍")
            await interaction.followup.send("Make sure that carl-bot is set up to assign role for the reaction.")
        else:
            await interaction.response.send_message(content=welcome, embeds=embeds)

    @group.command(name="update", description="Update the server rules")
    async def rules_update(self, interaction: discord.Interaction, channel: discord.TextChannel, message_id: str):
        await interaction.response.defer(thinking=True)

        try:
            message = await channel.fetch_message(int(message_id))
        except (ValueError, discord.NotFound) as e:
            await interaction.followup.send(f"Could not find message with ID {message_id} in {channel.jump_url}.")
            return

        if message.author.id != self.bot.user.id:
            await interaction.followup.send("The bot is not the author of this message.")
            return

        welcome = "# Welcome to CSC Duclings!"
        embeds = [rules_embed, disclaimer_embed, pick_roles_embed]
        await message.edit(content=welcome, embeds=embeds)
        await message.add_reaction("👍")
        await interaction.followup.send(
            f"Edited {message.jump_url}. Make sure that carl-bot is set up to assign role for the reaction."
        )


async def setup(bot: commands.Bot):
    log.info("Loading Rules extension")
    await bot.add_cog(Rules(bot))
