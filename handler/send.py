from telegram import Update
from telegram.ext import Application, ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters

import handler
import utils
from db import User

CLIENT_ID, CONF_FILE = range(2)


async def send(update: Update, _: ContextTypes.DEFAULT_TYPE) -> int:
    if not utils.is_owner(update.message.chat_id):
        return ConversationHandler.END

    await update.message.reply_text("Введите ID клиента:")
    return CLIENT_ID


async def client_id_conv(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = update.message.text

    query = User.select().where(User.chat_id == chat_id)

    if not query.exists():
        await update.message.reply_text("Клиент не найдет в базе данных.")
        return ConversationHandler.END

    user: User = query.get()

    context.user_data["chat_id"] = chat_id

    if user.new_client:
        await update.message.reply_text("Отправьте конфигурационный файл:")
        return CONF_FILE

    await context.bot.send_message(chat_id, "Конфигурация активирована. Мяу :3")
    await update.message.reply_text("Сообщение отправлено.")
    return ConversationHandler.END


async def conf_file_conv(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = context.user_data["chat_id"]

    await context.bot.send_document(
        chat_id,
        update.message.document,
        "Ваш конфигурационный файл готов. Для получения инструкции используйте /instruction"
    )

    await update.message.reply_text("Сообщение отправлено.")
    return ConversationHandler.END


def init_send(app: Application):
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("send", send)],
        states={
            CLIENT_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, client_id_conv)],
            CONF_FILE: [MessageHandler(filters.ATTACHMENT, conf_file_conv)],
        },
        fallbacks=[CommandHandler("cancel", handler.cancel_conv)]
    )

    app.add_handler(conv_handler)
