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
rules_embed.add_field(name="😀 Be nice", value="No harassment of any kind. Don’t be an asshole.", inline=False)
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
        "This server is independently managed by current and former students of Professor Ta "
        "and is not officially affiliated with or endorsed by the University or the "
        "Department of Computer Science.",
        "**Your participation is entirely optional**, and the content shared here is for informational purposes only. "
        "Any announcements or communications from tutors, graders, discussion leaders, or any members acting on "
        "official capacity on Discord are provided for your convenience and do not replace official channels such as "
        "email and Canvas discussion forums.",
        "The Department of Computer Science, Professor Ta, and members of his team are not affiliated with this "
        "server and are not responsible for moderating its content. Any advice or information shared here should be "
        "cross-referenced with official resources. The administrators of this server are not responsible for any "
        "inaccuracies or issues that may arise from the use of this server.",
        "We’ve kept this space running for our fellow Duclings since Spring 2021 and hope to pass it on to future "
        "cohorts — please help us maintain it by adhering to the rules and using common sense.",
    )
)

pick_roles_embed = Embed(title="Ready?")
pick_roles_embed.description = "Head over to <#815094070900031530> and select your roles to gain access to the server!"


class Rules(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="rules", description="Post the server rules")
    @app_commands.describe(destination="The channel to post to. If not provided, the current channel will be used.")
    async def rules(self, interaction: discord.Interaction, destination: discord.TextChannel = None):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You do not have permission to invoke this command.")
            return

        welcome = "# Welcome to CSC Duclings!"
        embeds = [rules_embed, disclaimer_embed, pick_roles_embed]
        if destination:
            message = await destination.send(content=welcome, embeds=embeds)
            await interaction.response.send_message(content=message.jump_url)
        else:
            await interaction.response.send_message(content=welcome, embeds=embeds)


async def setup(bot: commands.Bot):
    log.info("Loading Rules extension")
    await bot.add_cog(Rules(bot))
