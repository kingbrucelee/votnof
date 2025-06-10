import discord
from discord.ext import commands
import aiohttp
import urllib.parse
import logging
from src.config import PRINTS_ENDPOINT, PROCESSES_ENDPOINT


class PrintsInfo(commands.Cog):
    """Commands for getting information about Sejm prints."""

    def __init__(self, bot):
        self.bot = bot

    async def _fetch_process_data(
        self, session: aiohttp.ClientSession, process_nr: str
    ):
        """Fetch process data for a given process number."""
        try:
            async with session.get(
                f"{PROCESSES_ENDPOINT}/{process_nr}"
            ) as process_response:
                if process_response.status == 200:
                    return await process_response.json()
                elif process_response.status == 404:
                    logging.info(f"Process {process_nr} not found (HTTP 404).")
                    return None
                else:
                    logging.warning(
                        f"Error fetching process {process_nr}: HTTP {process_response.status}"
                    )
                    return None
        except aiohttp.ClientError as e:
            logging.warning(f"Network error fetching process {process_nr}: {e}")
            return None
        except Exception as e:
            logging.error(
                f"Unexpected error fetching process {process_nr}: {e}", exc_info=True
            )
            return None

    @commands.command(name="druk")
    async def print_info(self, ctx, nr: str):
        """Displays information about a Sejm print with the given number."""
        try:
            # Check if the print number is valid
            if not nr.isdigit():
                await ctx.send("Proszę podać poprawny numer druku (tylko cyfry).")
                return
            nr = nr.strip()  # Remove leading/trailing whitespace
            if not nr:
                await ctx.send("Proszę podać numer druku.")
                return
            # Fetch print data
            logging.info(f"Fetching print data for nr: {nr}")
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{PRINTS_ENDPOINT}/{nr}") as response:
                    if response.status != 200:
                        if response.status == 404:
                            await ctx.send(f"Nie znaleziono druku o numerze {nr}")
                        else:
                            await ctx.send(
                                f"Błąd przy pobieraniu danych: HTTP {response.status}"
                            )
                        return

                    data = await response.json()

            # Prepare data
            title = data.get("title", "Brak tytułu")
            delivery_date = data.get("deliveryDate", "Brak daty")
            change_date = data.get("changeDate", "Brak daty")

            # Prepare attachments information
            attachments_info = ""
            if "attachments" in data and data["attachments"]:
                for i, attachment in enumerate(data["attachments"]):
                    attachment_link = (
                        f"{PRINTS_ENDPOINT}/{nr}/{urllib.parse.quote(attachment)}"
                    )
                    attachments_info += (
                        f"**Załącznik {i+1}:** [{attachment}]({attachment_link})\n"
                    )
            else:
                attachments_info = "Brak załączników"

            # Prepare process information
            process_info = "**Proces:** Brak informacji\n"
            process_data = None

            async with aiohttp.ClientSession() as session:
                process_data = await self._fetch_process_data(session, nr)

                # If process not found, check if processPrint exists
                if not process_data or (
                    not process_data.get("passed") and not process_data.get("stages")
                ):
                    if "processPrint" in data and data["processPrint"]:
                        fallback_process_nr = data["processPrint"][0]
                        logging.info(
                            f"Attempting fallback process fetch for print {nr} using {fallback_process_nr}"
                        )
                        process_data = await self._fetch_process_data(
                            session, fallback_process_nr
                        )

            if process_data:
                stages = process_data.get("stages", [])
                if process_data.get("passed", False):
                    info = f"Uchwalono {process_data.get('closureDate', 'Brak daty')}"
                elif stages:
                    info = stages[-1].get("stageName", "Brak informacji o etapie")
                else:
                    info = "Brak informacji o etapie"
                process_info = f"**Etap procesu:** {info}\n"

            # Prepare message
            message = (
                f"**Nr druku:** {nr}\n"
                f"**Tytuł:** {title}\n"
                f"**Data dostarczenia:** {delivery_date}\n"
                f"**Data zmiany:** {change_date}\n"
                f"{process_info}"
                f"{attachments_info}"
            )

            await ctx.send(message)
        except Exception as e:
            logging.error(f"Error in !druk command for print {nr}: {e}", exc_info=True)
            await ctx.send(f"Wystąpił błąd: {str(e)}")

    @commands.command(name="pomoc")
    async def help_command(self, ctx):
        """Displays a list of available commands."""
        commands_list = (
            "**Dostępne komendy:**\n"
            "**!druk [numer]** - Wyświetla informacje o druku o podanym numerze\n"
            "**!obserwuj [numer]** - Dodaje druk do obserwowanych\n"
            "**!anuluj [numer]** - Usuwa druk z obserwowanych\n"
            "**!moje_druki** - Wyświetla listę obserwowanych druków\n"
            "**!raport [dni=7]** - Generuje raport o drukach z ostatnich X dni\n"
            "**!ustaw_kanał** - Ustawia bieżący kanał jako kanał do raportów tygodniowych (wymaga uprawnień admina)\n"
            "**!pomoc** - Wyświetla tę wiadomość\n"
        )
        await ctx.send(commands_list)
