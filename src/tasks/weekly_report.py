from discord.ext import tasks
import datetime
import logging
from src.config import WEEKLY_REPORT_DAY, WEEKLY_REPORT_HOUR


def start_weekly_report(bot):
    """Initialize and start the weekly report task."""

    report_time = datetime.time(hour=WEEKLY_REPORT_HOUR)

    @tasks.loop(time=report_time)
    async def weekly_report():
        """Generate and send weekly reports on scheduled day and time."""
        now = datetime.datetime.now()

        if now.weekday() == WEEKLY_REPORT_DAY:
            try:
                reports_cog = bot.get_cog("Reports")
                if reports_cog:

                    await reports_cog.send_weekly_report()
                else:
                    logging.warning("Reports cog not found. Cannot send weekly report.")
            except Exception as e:
                logging.error(f"Error generating weekly report: {e}", exc_info=True)

    weekly_report.start()

    return weekly_report
