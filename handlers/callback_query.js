import { api } from 'sdk';

import { CALLBACK_NO, reportError } from 'lib/bot';

export default async function (query, ctx) {
  try {
    if (query.data !== CALLBACK_NO) {
      return;
    }

    if (query.message) {
      await api.deleteMessage({
        chat_id: query.message.chat.id,
        message_id: query.message.message_id,
      });
    }

    await api.answerCallbackQuery({
      callback_query_id: query.id,
    });
  } catch (error) {
    await reportError(error, ctx.update);
    throw error;
  }
}
