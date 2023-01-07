#!/usr/bin/env python3
"""Methods for the bot functionality."""
import html
import json
import logging
import traceback
from typing import List, Optional, cast

from telegram import Chat, InlineKeyboardButton, InlineKeyboardMarkup, Message, Update
from telegram.error import BadRequest, Forbidden
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    PrefixHandler,
    filters,
)

HOMEPAGE: str = "https://Bibo-Joshi.github.io/memoriae-bot/"
""":obj:`str`: Homepage of this bot."""
ADMIN: int = -1
""":obj:`int`: Chat ID of the admin. Needs to be overridden in main.py"""
CALLBACK_NO: str = "dont_postpone"
""":obj:`str`: Callback data for not postponing reminders."""


async def info(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Returns some info about the bot.

    Args:
        update: The Telegram update.
        _: The callback context as provided by the application.
    """
    text = (
        "I'm the <b>Memoriae Bot</b> and I'm a thin wrapper for Telegrams timed messages. My "
        "profession is postponing reminders. Just send me a timed message and follow along."
        "\n\nTo learn more about me, please visit my homepage 🙂."
    )

    reply_markup = InlineKeyboardMarkup.from_button(
        InlineKeyboardButton("Memoriae Bot 🤖", url=HOMEPAGE)
    )

    await cast(Message, update.message).reply_text(text, reply_markup=reply_markup)


async def error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Informs the originator of the update that an error occurred and forwards the traceback to
    the admin.

    Args:
        update: The Telegram update.
        context: The callback context as provided by the application.
    """
    admin_id = ADMIN
    logger = logging.getLogger(__name__)

    # Log the error before we do anything else, so we can see it even if something breaks.
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

    if (
        isinstance(context.error, Forbidden)
        or (isinstance(context.error, BadRequest) and "Query is too old" in str(context.error))
        or context.error is None
    ):
        return

    # Inform sender of update, that something went wrong
    if isinstance(update, Update) and update.effective_message:
        text = "Something went wrong 😟. I informed the admin 🤓."
        await update.effective_message.reply_text(text)

    # Get traceback
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)

    # Build the message with some markup and additional information about what happened.
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message_1 = (
        f"An exception was raised while handling an update\n\n"
        f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}</pre>"
    )
    message_2 = f"<pre>{html.escape(tb_string)}</pre>"

    # Finally, send the messages
    # We send update and traceback in two parts to reduce the chance of hitting max length
    sent_message = await context.bot.send_message(chat_id=admin_id, text=message_1)
    try:
        await sent_message.reply_html(message_2)
    except BadRequest as exc:
        if "too long" not in str(exc):
            raise exc
        message = (
            f"Hey.\nThe error <code>{html.escape(str(context.error))}</code> happened."
            f" The traceback is too long to send, but it was written to the log."
        )
        await context.bot.send_message(chat_id=admin_id, text=message)


def keyboard(
    update: Optional[Update] = None, message_id: Optional[str] = None
) -> InlineKeyboardMarkup:
    """
    Builds the keyboard to append to postpone messages. Exactly one of the optionals mey be passed.

    Args:
        update: Optional. A Telegram update. If passed, the contained message will be the
            postponed reminder.
        message_id: Optional. A messages ID. If passed, the corresponding measseg will be the
            postponed reminder.
    """
    if update is not None and message_id is not None:
        raise ValueError("Only one optional argument may be passed.")

    id_: Optional[str] = None
    if update is not None and update.effective_message is not None:
        id_ = str(update.effective_message.message_id)
    if message_id is not None:
        id_ = message_id

    return InlineKeyboardMarkup.from_row(
        [
            InlineKeyboardButton(text="No ✔️", callback_data=CALLBACK_NO),
            InlineKeyboardButton(
                text="Yes 🕖",
                switch_inline_query_current_chat=id_,
            ),
        ]
    )


async def answer_reminder(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Answers a reminder and asks whether to postpone it.

    Args:
        update: The Telegram update.
        _: The callback context as provided by the application.
    """
    await cast(Message, update.message).reply_text(
        "You need that again?", reply_markup=keyboard(update=update)
    )


async def answer_postponed_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Deletes the auxiliary reminder and posts the original one. Also asks whether to postpone it
    again.

    Args:
        update: The Telegram update.
        context: The callback context as provided by the application.
    """
    await cast(Message, update.message).delete()

    message_id = cast(List[str], context.args)[0]
    chat = cast(Chat, update.effective_chat)
    reminder = await context.bot.forward_message(
        chat_id=chat.id,
        from_chat_id=chat.id,
        message_id=int(message_id),
        disable_notification=True,
    )

    await reminder.reply_text(
        "You need that again?",
        reply_markup=keyboard(message_id=message_id),
        disable_notification=True,
    )


async def delete_message(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Deletes the message of the incoming callback query.

    Args:
        update: The Telegram update.
        _: The callback context as provided by the application.
    """
    await update.callback_query.message.delete()  # type: ignore[union-attr]


async def register_application(application: Application) -> None:
    """
    Adds handlers and sets up jobs. Convenience method to avoid doing that all in the main script.

    Args:
        application: The :class:`telegram.ext.Dispatcher`.
    """
    app = application

    # error handler
    app.add_error_handler(error)

    # basic command handlers
    app.add_handler(CommandHandler(["start", "help"], info))

    # Handle postponed reminders
    app.add_handler(
        PrefixHandler(prefix="@", command=app.bot.username, callback=answer_postponed_reminder)
    )

    # Handle first time reminders
    app.add_handler(MessageHandler(filters.ALL, answer_reminder))

    # Delete postponing queries, when not needed
    app.add_handler(CallbackQueryHandler(callback=delete_message, pattern=f"^{CALLBACK_NO}$"))
