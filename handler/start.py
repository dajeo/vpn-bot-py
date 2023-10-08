from telegram import Update
from telegram.ext import Application, ContextTypes, CommandHandler, ConversationHandler, filters, MessageHandler

import db
import handler
from utils import translate_date

CLIENT_NAME = 0


async def start(update: Update, _: ContextTypes.DEFAULT_TYPE) -> int:
    query = db.User.select().where(db.User.chat_id == update.message.chat_id)
    if not query.exists():
        await update.message.reply_text(
            "Добро пожаловать! Чтобы начать пользоваться VPN сервисом, вам нужно зарегистрироваться, "
            "пожалуйста, введите Ваше имя и фамилию (для отмены введите /cancel):"
        )
        return CLIENT_NAME

    user: db.User = query.get()
    if not user.paid_at:
        await update.message.reply_text("Подписка не оплачена. Для оплаты используйте команду /pay")
    else:
        expired_at = translate_date(user.paid_at)
        await update.message.reply_text(f"Подписка оплачена до {expired_at}")

    return ConversationHandler.END


async def client_name_conv(update: Update, _: ContextTypes.DEFAULT_TYPE) -> int:
    name = update.message.text

    try:
        db.User.create(chat_id=update.message.chat_id, name=name)
        await update.message.reply_text("Вы успешно зарегистрированы. Для оплаты используйте /pay")
    except Exception as err:
        print("Error while creating user:", err)
        await update.message.reply_text("Произошла ошибка при регистрации. Повторите позже или обратитесь к @dajeo")

    return ConversationHandler.END


def init_start(app: Application):
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CLIENT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, client_name_conv)],
        },
        fallbacks=[CommandHandler("cancel", handler.cancel_conv)]
    )

    app.add_handler(conv_handler)
