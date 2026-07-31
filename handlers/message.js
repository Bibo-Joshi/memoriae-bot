import { api } from 'sdk';

import {
  BOT_MENTION,
  infoKeyboard,
  infoText,
  reminderKeyboard,
  reportError,
} from 'lib/bot';

const HELP_COMMAND = /^\/(?:start|help)(?:@\S+)?(?:\s|$)/i;
const POSTPONED_REMINDER = new RegExp(`^${BOT_MENTION.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\s+(\\d+)\\s*$`);

function getText(message) {
  return typeof message.text === 'string' ? message.text.trim() : '';
}

async function sendInfo(message) {
  await api.sendMessage({
    chat_id: message.chat.id,
    text: infoText(),
    parse_mode: 'HTML',
    reply_markup: infoKeyboard(),
    reply_to_message_id: message.message_id,
  });
}

async function sendReminder(message) {
  await api.sendMessage({
    chat_id: message.chat.id,
    text: 'You need that again?',
    reply_markup: reminderKeyboard(message.message_id),
    reply_to_message_id: message.message_id,
  });
}

async function sendPostponedReminder(message, reminderId) {
  const forwarded = await api.forwardMessage({
    chat_id: message.chat.id,
    from_chat_id: message.chat.id,
    message_id: reminderId,
    disable_notification: true,
  });

  await api.sendMessage({
    chat_id: message.chat.id,
    text: 'You need that again?',
    reply_markup: reminderKeyboard(reminderId),
    disable_notification: true,
    reply_to_message_id: forwarded.message_id,
  });
}

export default async function (message, ctx) {
  try {
    const text = getText(message);

    if (HELP_COMMAND.test(text)) {
      await sendInfo(message);
      return;
    }

    const postponedReminder = text.match(POSTPONED_REMINDER);
    if (postponedReminder) {
      await sendPostponedReminder(message, Number(postponedReminder[1]));
      return;
    }

    if (text.startsWith(BOT_MENTION)) {
      throw new Error('Missing postponed reminder message id.');
    }

    await sendReminder(message);
  } catch (error) {
    await reportError(error, ctx.update);
    throw error;
  }
}
