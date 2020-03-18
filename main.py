#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The script that runs the bot."""
import logging
from configparser import ConfigParser
from telegram import ParseMode
from telegram.ext import Updater, Defaults

import bot

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    filename='mb.log')

logger = logging.getLogger(__name__)


def main():
    """Start the bot."""
    # Read configuration values from bot.ini
    config = ConfigParser()
    config.read('bot.ini')
    token = config['memoriae-bot']['token']
    admin = config['memoriae-bot']['admins_chat_id']
    bot.ADMIN = admin

    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    defaults = Defaults(parse_mode=ParseMode.HTML, quote=True)
    updater = Updater(token, use_context=True, defaults=defaults)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher
    bot.register_dispatcher(dp)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
