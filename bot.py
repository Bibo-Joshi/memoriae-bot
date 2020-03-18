#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Methods for the bot functionality."""
import sys
import traceback
from typing import Optional
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (CallbackContext, Dispatcher, MessageHandler, PrefixHandler,
                          CommandHandler, CallbackQueryHandler, Filters)
from telegram.utils.helpers import mention_html
from emoji import emojize

HOMEPAGE: str = 'https://hirschheissich.gitlab.io/memoriae-bot/'
""":obj:`str`: Homepage of this bot."""
ADMIN: int = -1
""":obj:`int`: Chat ID of the admin. Needs to be overridden in main.py"""
CALLBACK_NO: str = 'dont_postpone'
""":obj:`str`: Callback data for not postponing reminders."""


def info(update: Update, context: CallbackContext) -> None:
    """
    Returns some info about the bot.

    Args:
        update: The Telegram update.
        context: The callback context as provided by the dispatcher.
    """
    text = emojize(
        ('I\'m the <b>Memoriae Bot</b> and I\'m a thin wrapper for Telegrams timed messages. My '
         'profession is postponing reminders. Just send me a timed message and follow along.'
         '\n\nTo learn more about me, please visit my homepage '
         ':slightly_smiling_face:.'),
        use_aliases=True)

    keyboard = InlineKeyboardMarkup.from_button(
        InlineKeyboardButton(emojize('Memoriae Bot :robot_face:', use_aliases=True), url=HOMEPAGE))

    update.message.reply_text(text, reply_markup=keyboard)


def error(update: Update, context: CallbackContext):
    """
    Informs the originator of the update that an error occured and forwards the traceback to the
    admin.

    Args:
        update: The Telegram update.
        context: The callback context as provided by the dispatcher.
    """
    # Inform sender of update, that something went wrong
    if update.effective_message:
        text = emojize('Something went wrong :worried:. I informed the admin :nerd_face:.',
                       use_aliases=True)
        update.effective_message.reply_text(text)

    # Get traceback
    trace = ''.join(traceback.format_tb(sys.exc_info()[2]))

    # Gather information from the update
    payload = ''
    if update.effective_user:
        payload += ' with the user {}'.format(
            mention_html(update.effective_user.id, update.effective_user.first_name))
    if update.effective_chat:
        payload += f' within the chat <i>{update.effective_chat.title}</i>'
        if update.effective_chat.username:
            payload += f' (@{update.effective_chat.username})'
    if update.poll:
        payload += f' with the poll id {update.poll.id}.'
    text = f'Hey.\nThe error <code>{context.error}</code> happened{payload}. The full ' \
           f'traceback:\n\n<code>{trace}</code>'

    # Send to admin
    context.bot.send_message(ADMIN, text)

    # we raise the error again, so the logger module catches it.
    raise


def keyboard(update: Optional[Update] = None,
             message_id: Optional[str] = None) -> InlineKeyboardButton:
    """
    Builds the keyboard to append to postpone messages. Exactly one of the optionals mey be passed.

    Args:
        update: Optional. A Telegram update. If passed, the contained message will be the
            postponed reminder.
        message_id: Optional. A messages ID. If passed, the corresponding measseg will be the
            postponed reminder.
    """
    if update is not None and message_id is not None:
        raise ValueError('Only one optional argument may be passed.')

    if update is not None:
        id_ = str(update.effective_message.message_id)
    if message_id is not None:
        id_ = message_id

    return InlineKeyboardMarkup.from_row([
        InlineKeyboardButton(text=emojize('No :heavy_check_mark:', use_aliases=True),
                             callback_data=CALLBACK_NO),
        InlineKeyboardButton(text=emojize('Yes :clock7:', use_aliases=True),
                             switch_inline_query_current_chat=id_),
    ])


def answer_reminder(update: Update, context: CallbackContext):
    """
    Answers a reminder and asks, whether to postpone it.

    Args:
        update: The Telegram update.
        context: The callback context as provided by the dispatcher.
    """
    update.message.reply_text('You need that again?', reply_markup=keyboard(update=update))


def answer_postponed_reminder(update: Update, context: CallbackContext):
    """
    Deletes the auxiliary reminder and posts the original one. Also asks, whether to postpone it
    again.

    Args:
        update: The Telegram update.
        context: The callback context as provided by the dispatcher.
    """
    update.message.delete()

    message_id = context.args[0]
    reminder = context.bot.forward_message(chat_id=update.effective_chat.id,
                                           from_chat_id=update.effective_chat.id,
                                           message_id=message_id,
                                           disable_notification=True)

    reminder.reply_text('You need that again?',
                        reply_markup=keyboard(message_id=message_id),
                        disable_notification=True)


def delete_message(update: Update, context: CallbackContext):
    """
    Deletes the message of the incoming callback query.

    Args:
        update: The Telegram update.
        context: The callback context as provided by the dispatcher.
    """
    update.callback_query.message.delete()


def register_dispatcher(disptacher: Dispatcher) -> None:
    """
    Adds handlers and sets up jobs. Convenience method to avoid doing that all in the main script.

    Args:
        disptacher: The :class:`telegram.ext.Dispatcher`.
    """
    dp = disptacher

    # error handler
    dp.add_error_handler(error)

    # basic command handlers
    dp.add_handler(CommandHandler(['start', 'help'], info))

    # Handle postponed reminders
    dp.add_handler(
        PrefixHandler(prefix='@',
                      command=dp.bot.get_me().username,
                      callback=answer_postponed_reminder))

    # Handle first time reminders
    dp.add_handler(MessageHandler(Filters.all, answer_reminder))

    # Delete postponing inqueries, when not needed
    dp.add_handler(
        CallbackQueryHandler(callback=delete_message, pattern='^{}$'.format(CALLBACK_NO)))
