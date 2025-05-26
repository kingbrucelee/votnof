import discord
from discord.ext import commands
import aiohttp
import datetime
import logging
import urllib.parse
import discord.utils
from src.config import PRINTS_ENDPOINT, DISCORD_MAX_MESSAGE_LENGTH


class Reports(commands.Cog):
    """Komendy dla generowania raportów"""

    def __init__(self, bot):
        self.bot = bot

        self.report_channels = set()

    @commands.command(name="raport")
    async def generate_report(self, ctx, days: int = 7):
        """Generuje raport o drukach z ostatnich X dni (domyślnie 7)."""
        await ctx.send(f"Generuję raport z ostatnich {days} dni...")

        try:
            report_parts = await self._generate_report(days)

            if report_parts:
                for i, part in enumerate(report_parts):
                    await ctx.send(f"{part}\n*Część {i+1}/{len(report_parts)}*")
            else:
                await ctx.send(f"Brak druków sejmowych z ostatnich {days} dni.")
        except Exception as e:
            logging.error(f"Wystąpił błąd przy generowaniu raportu: {e}", exc_info=True)
            await ctx.send("Wystąpił błąd przy generowaniu raportu ")

    @commands.command(name="ustaw_kanał")
    @commands.has_permissions(administrator=True)
    async def set_channel(self, ctx):
        """Ustawia bieżący kanał jako kanał do raportów tygodniowych."""
        self.report_channels.add(ctx.channel.id)
        await ctx.send(
            f"Kanał {ctx.channel.mention} został ustawiony jako kanał do raportów tygodniowych. "
            f"Raporty będą wysyłane w każdy poniedziałek"
        )

    @set_channel.error
    async def set_channel_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Nie masz uprawnień administratora do użycia tej komendy.")

    async def _generate_report(self, days):
        """Generate report for the last X days."""
        logging.info(f"Generating report for the last {days} days")
        if not isinstance(days, int) or days <= 0:
            raise ValueError("Liczba dni musi być dodatnią liczbą całkowitą.")
        logging.info(f"Fetching prints from {PRINTS_ENDPOINT} for the last {days} days")
        # Pobierz wszystkie druki z API
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    f"{PRINTS_ENDPOINT}?sort_by=-deliveryDate"
                ) as all_prints_response:
                    all_prints_response.raise_for_status()
                    all_prints = await all_prints_response.json()
            except aiohttp.ClientError as e:
                logging.error(f"Błąd przy pobieraniu listy druków: {e}", exc_info=True)
                raise Exception(f"Błąd przy pobieraniu listy druków: {e}")

            cutoff_date = (
                datetime.datetime.now() - datetime.timedelta(days=days)
            ).strftime("%Y-%m-%d")

            recent_prints = []
            for print_item in all_prints:
                delivery_date = print_item.get("deliveryDate", "")
                if delivery_date < cutoff_date:
                    break

                recent_prints.append(
                    {
                        "number": print_item.get("number"),
                        "title": print_item.get("title", "Brak tytułu"),
                        "deliveryDate": delivery_date,
                        "attachments": print_item.get("attachments", []),
                        "processPrint": print_item.get("processPrint", []),
                    }
                )

            recent_prints.sort(key=lambda x: x["deliveryDate"], reverse=True)

        if recent_prints:
            report = f"**Raport druków sejmowych z ostatnich {days} dni:**\n\n"
            logging.info(f"Found {len(recent_prints)} prints in the last {days} days")
            prints_by_date = {}
            for print_item in recent_prints:
                date = print_item["deliveryDate"]
                if date not in prints_by_date:
                    prints_by_date[date] = []
                prints_by_date[date].append(print_item)

            report_lines = []
            for date in sorted(prints_by_date.keys(), reverse=True):
                report_lines.append(f"**{date}**")
                for print_item in prints_by_date[date]:
                    print_nr = print_item.get("number")
                    title = print_item.get("title", "Brak tytułu")
                    attachments = print_item.get("attachments", [])
                    process_print_numbers = print_item.get("processPrint", [])

                    escaped_title = discord.utils.escape_markdown(title)
                    report_line_content = f"Druk nr {print_nr}: {escaped_title[:300]}{'...' if len(escaped_title) > 300 else ''}"
                    # If there are attachments, create a link to the first one
                    if attachments:
                        first_attachment = attachments[0]
                        attachment_link = f"{PRINTS_ENDPOINT}/{print_nr}/{urllib.parse.quote(first_attachment)}"
                        report_line_content = (
                            f"[{report_line_content}]({attachment_link})"
                        )

                    process_info_suffix = ""
                    if process_print_numbers and str(process_print_numbers[0]) != str(
                        print_nr
                    ):
                        process_info_suffix = f" (-> {process_print_numbers[0]})"

                    report_lines.append(f"- {report_line_content}{process_info_suffix}")
                report_lines.append("")
            report_parts = []
            current_part = f"**Raport druków sejmowych z ostatnich {days} dni:**\n\n"
            for line in report_lines:
                if len(current_part) + len(line) + 1 > DISCORD_MAX_MESSAGE_LENGTH:
                    report_parts.append(current_part)
                    current_part = line + "\n"
                else:
                    current_part += line + "\n"
            if current_part:
                report_parts.append(current_part)

            return report_parts
        else:
            return []

    async def send_weekly_report(self):
        """Send weekly report to all registered channels."""
        try:
            report_parts = await self._generate_report(7)

            if not report_parts:
                return

            for channel_id in self.report_channels:
                try:
                    channel = self.bot.get_channel(channel_id)
                    if channel:
                        for i, part in enumerate(report_parts):
                            await channel.send(
                                f"{part}\n*Część {i+1}/{len(report_parts)}*"
                            )
                except Exception as e:
                    logging.error(
                        f"Błąd przy wysyłaniu raportu do kanału {channel_id}: {e}",
                        exc_info=True,
                    )

            for guild in self.bot.guilds:
                for channel in guild.text_channels:
                    if (
                        "druki" in channel.name.lower()
                        and "sejm" in channel.name.lower()
                    ):
                        if channel.id not in self.report_channels:
                            for i, part in enumerate(report_parts):
                                try:
                                    await channel.send(
                                        f"{part}\n*Część {i+1}/{len(report_parts)}*"
                                    )
                                except Exception as e:
                                    logging.error(
                                        f"Błąd przy wysyłaniu raportu do kanału {channel.id} (nazwa: {channel.name}): {e}",
                                        exc_info=True,
                                    )
        except Exception as e:
            logging.error(
                f"Wystąpił błąd przy generowaniu tygodniowego raportu: {e}",
                exc_info=True,
            )
