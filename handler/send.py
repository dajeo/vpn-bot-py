from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters

import conf
import handler
from db import User

CLIENT_ID, CONF_FILE = range(2)


async def send_to_client(update: Update, _: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.chat_id != int(conf.get()["bot"]["owner"]):
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

    await context.bot.send_message(
        chat_id,
        "1. Установите WireGuard\n\n"
        "Android: https://play.google.com/store/apps/details?id=com.wireguard.android\n"
        "iOS: https://apps.apple.com/ru/app/wireguard/id1441195209\n\n"
        "2. Скачайте файл имя.conf\n\n"
        "3. Откройте WireGuard и нажмите на кнопку плюс (+)\n\n"
        "4. Выберете пункт Импорт из файла или архива, выберете скачанный файл и укажите название\n\n"
        "5. Теперь вверху экрана вы можете активировать только что созданный профиль\n\n"
        "Проверить работоспособность можно на сайте https://vpn.dajeo.by/check/\n\n"
        "Для других платформ инструкцию вы можете найти на сайте https://vpn.dajeo.by/instruction\n\n"
        "<i>Предупреждение: не делитесь вашим профилем, он может обрабатывать только одно подключение!</i>",
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True
    )
    await context.bot.send_document(
        chat_id,
        update.message.document,
        "Ваш конфигурационный файл готов."
    )

    await update.message.reply_text("Сообщение отправлено.")
    return ConversationHandler.END


def init_send(app: Application):
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("send", send_to_client)],
        states={
            CLIENT_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, client_id_conv)],
            CONF_FILE: [MessageHandler(filters.ATTACHMENT, conf_file_conv)],
        },
        fallbacks=[CommandHandler("cancel", handler.cancel_conv)]
    )

    app.add_handler(conv_handler)
