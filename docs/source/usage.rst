Non-functionality
-----------------

The bot commands ``/start`` and ``/help`` will display a short summary of the bots capabilities.

Setting a Reminder
------------------

Reminders are set by sending the bot a timed message. Long-press/right-click the send button for that.

Postponing a Reminder
---------------------

When a reminder is due, i.e. a the corresponding timed message is sent, the bot will ask you, whether
you would like to postpone the reminder.
If not, you can just click ``No``. If you do want to postpone, click ``Yes`` and the bot will enter a
specially formatted message for you. Send it as timed message and when it's due the bot will send you
the original reminder again.

Statistics
----------

This bot uses the `ptbstats <https://Bibo-Joshi.github.io/ptbstats/>`_ plugin to make some usage statistics
available. The commands ``/first`` and ``/reps`` will provide statistics on all reminders sent for the first time and
all repetitions, respectively. Note, that those commands will only work for the admin of the bot.
