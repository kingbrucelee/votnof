import discord
from discord.ext import commands
import aiohttp
import datetime
import logging
import urllib.parse
import discord.utils
import textwrap
from src.config import PRINTS_ENDPOINT, DISCORD_MAX_MESSAGE_LENGTH


class Reports(commands.Cog):
    """Commands for generating reports."""

    def __init__(self, bot):
        self.bot = bot

        self.report_channels = set()

    @commands.command(name="raport")
    async def generate_report(self, ctx, days: int = 7):
        """Generates a report of prints from the last X days (default is 7)."""
        await ctx.send(f"Generuję raport z ostatnich {days} dni...")

        try:
            report_messages = await self._generate_report(days)

            if report_messages:
                for message in report_messages:
                    await ctx.send(message)
            else:
                await ctx.send(f"Brak druków sejmowych z ostatnich {days} dni.")
        except Exception as e:
            logging.error(f"Error generating report: {e}", exc_info=True)
            await ctx.send("Wystąpił błąd przy generowaniu raportu ")

    @commands.command(name="ustaw_kanał")
    @commands.has_permissions(administrator=True)
    async def set_channel(self, ctx):
        """Sets the current channel as the channel for weekly reports."""
        self.report_channels.add(ctx.channel.id)
        await ctx.send(
            f"Kanał {ctx.channel.mention} został ustawiony jako kanał do raportów tygodniowych. "
            f"Raporty będą wysyłane w każdy poniedziałek"
        )

    @set_channel.error
    async def set_channel_error(self, ctx, error):
        """
        Handles errors for the set_channel command.

        Args:
            ctx (commands.Context): The context of the command.
            error (commands.CommandError): The error that occurred.
        """
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Nie masz uprawnień administratora do użycia tej komendy.")

    async def _generate_report(self, days):
        """Generate report for the last X days."""
        logging.info(f"Generating report for the last {days} days")
        if not isinstance(days, int) or days <= 0:
            raise ValueError("Liczba dni musi być dodatnią liczbą całkowitą.")
        logging.info(f"Fetching prints from {PRINTS_ENDPOINT} for the last {days} days")
        # Fetch all prints from the API
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    f"{PRINTS_ENDPOINT}?sort_by=-deliveryDate"
                ) as all_prints_response:
                    all_prints_response.raise_for_status()
                    all_prints = await all_prints_response.json()
            except aiohttp.ClientError as e:
                logging.error(f"Error fetching prints list: {e}", exc_info=True)
                raise Exception(f"Error fetching prints list: {e}")

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
                    shortened_title = textwrap.shorten(
                        escaped_title, width=300, placeholder="..."
                    )
                    report_line_content = f"Druk nr {print_nr}: {shortened_title}"
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
            current_message_lines = []
            initial_header = f"**Raport druków sejmowych z ostatnich {days} dni:**\n\n"
            current_message_lines.append(initial_header)

            for line in report_lines:
                temp_content_length = (
                    sum(len(l) for l in current_message_lines) + len(line) + 1
                )

                if temp_content_length > DISCORD_MAX_MESSAGE_LENGTH:
                    report_parts.append("".join(current_message_lines))
                    current_message_lines = [line + "\n"]
                else:
                    current_message_lines.append(line + "\n")

            if current_message_lines:
                report_parts.append("".join(current_message_lines))

            final_report_messages = []
            total_parts = len(report_parts)
            for i, part_content in enumerate(report_parts):
                suffix = f"\n*Część {i+1}/{total_parts}*"
                final_message = part_content + suffix
                final_report_messages.append(final_message)

            return final_report_messages
        else:
            return []

    async def send_weekly_report(self):
        """
        Send weekly report to all registered channels.
        """
        try:
            report_messages = await self._generate_report(7)

            if not report_messages:
                return

            for channel_id in self.report_channels:
                try:
                    channel = self.bot.get_channel(channel_id)
                    if channel:
                        for message in report_messages:
                            await channel.send(message)
                except Exception as e:
                    logging.error(
                        f"Error sending report to channel {channel_id}: {e}",
                        exc_info=True,
                    )

            for guild in self.bot.guilds:
                for channel in guild.text_channels:
                    if (
                        "druki" in channel.name.lower()
                        and "sejm" in channel.name.lower()
                    ):
                        if channel.id not in self.report_channels:
                            for message in report_messages:
                                try:
                                    await channel.send(message)
                                except Exception as e:
                                    logging.error(
                                        f"Error sending report to channel {channel.id} (name: {channel.name}): {e}",
                                        exc_info=True,
                                    )
        except Exception as e:
            logging.error(
                f"Error generating weekly report: {e}",
                exc_info=True,
            )
