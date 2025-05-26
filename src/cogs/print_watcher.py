import discord
from discord.ext import commands, tasks
import aiohttp
import logging
from src.utils.file_operations import (
    get_watched_prints,
    update_print_change_date,
    load_watched_prints,
)
from src.config import PRINTS_ENDPOINT, PRINT_CHECK_INTERVAL_HOURS


class PrintWatcher(commands.Cog):
    """Cog for watching Sejm prints for changes."""

    def __init__(self, bot):
        self.bot = bot
        load_watched_prints()
        self.check_watched_prints_task.start()

    @tasks.loop(hours=PRINT_CHECK_INTERVAL_HOURS)
    async def check_watched_prints_task(self):
        """Task to check for changes in watched prints."""
        logging.info("Running check_watched_prints_task...")
        watched_prints = get_watched_prints()

        async with aiohttp.ClientSession() as session:
            for user_id, prints in watched_prints.items():
                for print_nr, last_change_date in list(prints.items()):
                    try:
                        async with session.get(
                            f"{PRINTS_ENDPOINT}/{print_nr}"
                        ) as response:
                            if response.status == 200:
                                data = await response.json()
                                current_change_date = data.get("changeDate", "")

                                # Jeśli data się zmieniła, powiadom użytkownika
                                if (
                                    current_change_date
                                    and current_change_date != last_change_date
                                ):
                                    try:
                                        user = await self.bot.fetch_user(int(user_id))
                                        if user:
                                            message = (
                                                f"**Aktualizacja druku nr {print_nr}**\n"
                                                f"**Poprzednia data zmiany:** {last_change_date}\n"
                                                f"**Nowa data zmiany:** {current_change_date}\n"
                                                f"Użyj `!druk {print_nr}` aby zobaczyć szczegóły."
                                            )
                                            try:
                                                await user.send(message)
                                            except discord.Forbidden:
                                                logging.warning(
                                                    f"Could not send DM to user {user_id} for print {print_nr}. User might have DMs disabled."
                                                )
                                                pass

                                        update_print_change_date(
                                            user_id, print_nr, current_change_date
                                        )
                                    except Exception as e:
                                        logging.error(
                                            f"Error notifying user {user_id} about print {print_nr}: {e}",
                                            exc_info=True,
                                        )
                    except Exception as e:
                        logging.error(
                            f"Error checking print {print_nr}: {e}", exc_info=True
                        )

    def cog_unload(self):
        self.check_watched_prints_task.cancel()
