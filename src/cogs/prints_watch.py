import discord
from discord.ext import commands
import aiohttp
from src.utils.file_operations import (
    add_watched_print,
    remove_watched_print,
    get_user_watched_prints,
)
from src.config import PRINTS_ENDPOINT


class PrintsWatch(commands.Cog):
    """Commands for watching Sejm prints for changes."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="obserwuj")
    async def watch_print(self, ctx, nr: str):
        """Adds a print to the watched list."""
        user_id = str(ctx.author.id)
        # Check if the print number is valid
        if not nr.isdigit():
            await ctx.send("Proszę podać poprawny numer druku (tylko cyfry).")
            return
        nr = nr.strip()
        if not nr:
            await ctx.send("Proszę podać numer druku.")
            return
        try:
            # Check if the print exists
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

            # Add to watched
            change_date = data.get("changeDate", "")
            added = add_watched_print(user_id, nr, change_date)

            await ctx.send(
                f"Druk nr {nr} został dodany do obserwowanych. Otrzymasz powiadomienie o zmianach."
            )
        except Exception as e:
            await ctx.send(f"Wystąpił błąd: {str(e)}")

    @commands.command(name="anuluj")
    async def unwatch_print(self, ctx, nr: str):
        """Removes a print from the watched list."""
        user_id = str(ctx.author.id)

        removed = remove_watched_print(user_id, nr)
        if removed:
            await ctx.send(f"Druk nr {nr} został usunięty z obserwowanych.")
        else:
            await ctx.send(f"Nie obserwujesz druku nr {nr}.")

    @commands.command(name="moje_druki")
    async def list_watched_prints(self, ctx):
        """Displays the list of watched prints."""
        user_id = str(ctx.author.id)

        watched = get_user_watched_prints(user_id)
        if watched:
            message = "**Twoje obserwowane druki:**\n"
            for nr in watched:
                message += f"- Druk nr {nr}\n"
            await ctx.send(message)
        else:
            await ctx.send("Nie obserwujesz żadnych druków.")
