from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters

from helpers.main import show_statistic


buttons = {
    'servers': '🖥 Мої сервери',
    'remove_server': '🗑 Видалити мої сервери', 
    'join_attack': '🚀 Приєднатись до атаки', 
    'statistic': '📊 Статистика',
    'help': '📖 Довідка' 
}

keyboard = [[KeyboardButton(buttons[id])] for id in buttons]

def statistic(update: Update, context: CallbackContext):
    message = update.message.reply_text('⏳ Зачекай, я збираю статистику...')

    msg = show_statistic()
    message.edit_text(msg, parse_mode='MarkdownV2')

def other(update: Update, context: CallbackContext):
    update.message.reply_text('Нічого не роблю 🫣')

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        'Цей демо-бот показує статистику ДДоС атак на відданих в управління серверах.\n' +
        'Спробуй кнопку "📊 Статистика" 😉', 
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

def message_handler(update: Update, context: CallbackContext) -> None:
    button_clicked = update.message.text
    if button_clicked == buttons['statistic']:
        statistic(update, context)
    elif button_clicked == buttons['help']:
        help_command(update, context)
    else:
        other(update, context)

def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Працює тільки кнопка "📊 Статистика", інші відпочивають 🫠')

def main() -> None:
    """Run the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater("REPLACE_ME")

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, message_handler))
    updater.dispatcher.add_handler(CommandHandler('help', help_command))

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
    main()