#!/usr/bin/env python3
"""The script that runs the bot."""
import logging
from configparser import ConfigParser

from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, Defaults

import bot

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    filename="mb.log",
)

logger = logging.getLogger(__name__)


def main() -> None:
    """Start the bot."""
    # Read configuration values from bot.ini
    config = ConfigParser()
    config.read("bot.ini")
    token = config["memoriae-bot"]["token"]
    admin = config["memoriae-bot"]["admins_chat_id"]
    bot.ADMIN = int(admin)

    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    defaults = Defaults(parse_mode=ParseMode.HTML, quote=True)
    application = (
        ApplicationBuilder()
        .token(token)
        .defaults(defaults)
        .post_init(bot.register_application)
        .build()
    )
    application.run_polling()


if __name__ == "__main__":
    main()
