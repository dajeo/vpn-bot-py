import logging
import uuid
import configparser
from telegram import Update, LabeledPrice
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    PreCheckoutQueryHandler,
    MessageHandler,
    ConversationHandler,
    filters
)
from telegram.constants import ParseMode

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)
config = configparser.ConfigParser()
config.read("config.ini")

SECRET = str(uuid.uuid4())
CLIENT_ID, CONF_FILE = range(2)


async def start_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    title = "Оплата сервиса"
    description = "Оплата сервиса на два месяца в Польше. При оформлении заказа укажите вашу реальную имя и фамилию!"
    payload = SECRET
    currency = "RUB"
    price = 100
    prices = [LabeledPrice("Польша", price * 100)]

    await context.bot.send_invoice(
        chat_id,
        title,
        description,
        payload,
        config["payments"]["token"],
        currency,
        prices,
        need_name=True
    )


async def pre_checkout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.pre_checkout_query

    if query.invoice_payload != SECRET:
        await query.answer(ok=False, error_message="Ошибка проверки подлинности платежа")
    else:
        await query.answer(ok=True)


async def successful_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    client_name = update.message.successful_payment.order_info.name
    await context.bot.send_message(
        config["bot"]["owner"],
        f"Заказ оплачен, клиент \({client_name}\) ожидает конфигурацию\. `{update.message.chat_id}`",
        parse_mode=ParseMode.MARKDOWN_V2
    )
    await update.message.reply_text("Спасибо за покупку. В течение суток вам будет отправлена конфигурация VPN.")


async def send_to_client(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.chat_id != int(config["bot"]["owner"]):
        return ConversationHandler.END

    await update.message.reply_text("Введите ID клиента.")
    return CLIENT_ID


async def client_id_conv(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["chat_id"] = update.message.text
    await update.message.reply_text("Отправьте конфигурационный файл.")
    return CONF_FILE


async def conf_file_conv(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await context.bot.send_document(
        context.user_data["chat_id"],
        update.message.document,
        "Ваш конфигурационный файл готов."
    )
    await update.message.reply_text("Сообщение отправлено.")
    return ConversationHandler.END


async def cancel_conv(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Команда отменена.")
    return ConversationHandler.END


def main():
    app = Application.builder().token(config["bot"]["token"]).build()

    app.add_handler(CommandHandler("pay", start_payment))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("send", send_to_client)],
        states={
            CLIENT_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, client_id_conv)],
            CONF_FILE: [MessageHandler(filters.ATTACHMENT, conf_file_conv)]
        },
        fallbacks=[CommandHandler("cancel", cancel_conv)]
    )

    app.add_handler(conv_handler)

    app.add_handler(PreCheckoutQueryHandler(pre_checkout_callback))

    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback))

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
