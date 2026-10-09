import { api } from 'sdk';

export const BOT_TITLE = 'Memoriae Bot';
export const BOT_USERNAME = 'YOUR_BOT_NAME';
export const BOT_MENTION = `@${BOT_USERNAME}`;
export const ADMIN_ID = 123456789;
export const HOMEPAGE_URL = 'https://Bibo-Joshi.github.io/memoriae-bot/';
export const CALLBACK_NO = 'dont_postpone';

export function escapeHtml(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}

export function infoText() {
  return (
    `I'm the <b>${escapeHtml(BOT_TITLE)}</b> and I'm a thin wrapper for Telegrams timed messages. ` +
    'My profession is postponing reminders. Just send me a timed message and follow along.' +
    '\n\nTo learn more about me, please visit my homepage 🙂.'
  );
}

export function infoKeyboard() {
  return {
    inline_keyboard: [[{ text: `${BOT_TITLE} 🤖`, url: HOMEPAGE_URL }]],
  };
}

export function reminderKeyboard(messageId) {
  return {
    inline_keyboard: [[
      { text: 'No ✔️', callback_data: CALLBACK_NO },
      { text: 'Yes 🕖', switch_inline_query_current_chat: String(messageId) },
    ]],
  };
}

function formatUpdate(update) {
  try {
    return JSON.stringify(update, null, 2);
  } catch (error) {
    return String(update);
  }
}

function isTooLongError(error) {
  const message = String(error && (error.description || error.message || error));
  return /too long/i.test(message);
}

export async function reportError(error, update) {
  console.error('Exception while handling an update:', error);

  const updateText = formatUpdate(update);
  const details = [
    'An exception was raised while handling an update',
    '',
    `<pre>update = ${escapeHtml(updateText)}</pre>`,
    `<pre>${escapeHtml(error && error.stack ? error.stack : String(error))}</pre>`,
  ].join('\n');

  try {
    await api.sendMessage({
      chat_id: ADMIN_ID,
      text: details,
      parse_mode: 'HTML',
    });
  } catch (adminError) {
    if (!isTooLongError(adminError)) {
      throw adminError;
    }

    await api.sendMessage({
      chat_id: ADMIN_ID,
      text: `An error happened: ${String(error)}`,
    });
  }
}
