import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import logging

from src.cogs.prints_info import PrintsInfo
from src.cogs.prints_watch import PrintsWatch
from src.cogs.reports import Reports
from src.cogs.print_watcher import PrintWatcher

from src.tasks.weekly_report import start_weekly_report

load_dotenv()

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


async def setup(bot):
    """
    Sets up and adds the bot's cogs.

    Args:
        bot (commands.Bot): The bot instance.
    """
    await bot.add_cog(PrintsInfo(bot))
    await bot.add_cog(PrintsWatch(bot))
    await bot.add_cog(Reports(bot))
    await bot.add_cog(PrintWatcher(bot))


def main():
    """
    The main function to set up and run the Discord bot.
    """
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix="!", intents=intents)

    @bot.event
    async def on_ready():
        """
        Handles the bot's ready event.
        Logs bot information and starts the weekly report task.
        """
        logging.info(f"Logged in as {bot.user} (ID: {bot.user.id})")
        logging.info("------")

        start_weekly_report(bot)

        # Load cogs
        await setup(bot)

    @bot.event
    async def on_command_error(ctx, error):
        """
        Handles errors that occur during command invocation.

        Args:
            ctx (commands.Context): The context of the command.
            error (commands.CommandError): The error that occurred.
        """
        if isinstance(error, commands.CommandNotFound):
            await ctx.send(
                "Nie znaleziono takiej komendy. Użyj `!pomoc` aby zobaczyć listę dostępnych komend."
            )
        elif isinstance(error, commands.BadArgument):
            await ctx.send(
                f"Błąd argumentu: {error}. Sprawdź poprawność wprowadzonych danych."
            )
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                f"Brakuje wymaganego argumentu: {error.param.name}. Sprawdź `!pomoc` dla tej komendy."
            )
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("Nie masz wystarczających uprawnień do użycia tej komendy.")
        else:
            logging.error(f"An error occurred: {error}", exc_info=True)
            await ctx.send("Wystąpił błąd. Spróbuj ponownie później.")

    # Handle "druk nr X" message format
    @bot.event
    async def on_message(message):
        """
        Handles incoming messages.
        Processes commands and a specific message format ("druk nr X").

        Args:
            message (discord.Message): The incoming message.
        """
        # Ignore messages from bots
        if message.author.bot:
            return

        if message.content.startswith("druk nr"):
            nr_druku = message.content.strip("druk nr").strip()
            ctx = await bot.get_context(message)
            command = bot.get_command("druk")
            if command:
                await ctx.invoke(command, nr=nr_druku)

        await bot.process_commands(message)

    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise ValueError(
            "No Discord token found. Set the DISCORD_TOKEN environment variable."
        )
    bot.run(token)


if __name__ == "__main__":
    main()
