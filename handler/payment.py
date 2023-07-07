import uuid
from datetime import datetime

from telegram import Update, LabeledPrice
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, CommandHandler, Application, PreCheckoutQueryHandler, MessageHandler, filters

import conf
import db
from utils import translate_date

SECRET = str(uuid.uuid4())


async def start_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = db.User.select().where(db.User.chat_id == update.message.chat_id)

    if not query.exists():
        await update.message.reply_text("Перед оплатой зарегистрируйтесь /start")
        return

    user: db.User = query.get()

    if user.paid_at:
        expired_at = translate_date(user.paid_at)
        await update.message.reply_text(f"Вы уже оплатили VPN. Следующая оплата {expired_at}")
        return

    chat_id = update.message.chat_id
    title = "Оплата сервиса"
    description = "Оплата VPN сервиса на два месяца в Польше."
    payload = SECRET
    currency = "RUB"
    price = 100
    prices = [LabeledPrice("Польша", price * 100)]

    await context.bot.send_invoice(
        chat_id,
        title,
        description,
        payload,
        conf.get()["payments"]["token"],
        currency,
        prices
    )


async def pre_checkout_callback(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.pre_checkout_query

    if query.invoice_payload != SECRET:
        await query.answer(ok=False, error_message="Ошибка проверки подлинности платежа.")
    else:
        await query.answer(ok=True)


async def successful_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = db.User.select().where(db.User.chat_id == update.message.chat_id)

    if not query.exists():
        await update.message.reply_text("Перед оплатой зарегистрируйтесь /start")
        return

    now = datetime.now()

    user: db.User = query.get()

    is_old_client = user.old_client
    client_name = user.name

    if not user.old_client:
        user.first_paid = now

    if user.transaction_number > 1:
        user.old_client = True

    user.paid_at = now
    user.transaction_number += 1
    user.save()

    await context.bot.send_message(
        conf.get()["bot"]["owner"],
        f"Заказ оплачен, клиент \({client_name}\) ожидает конфигурацию\. `{update.message.chat_id}`",
        parse_mode=ParseMode.MARKDOWN_V2
    )

    if is_old_client:
        await update.message.reply_text(
            "Подписка оплачена! Проверьте подключение к VPN, если оно отсутствует, "
            "в течении суток все будет восстановлено."
        )
    else:
        await update.message.reply_text(
            "Наши поздравления с покупкой VPN! В течении суток вам будет отправлена инструкция."
        )


def init_payment(app: Application):
    app.add_handler(CommandHandler("pay", start_payment))
    app.add_handler(PreCheckoutQueryHandler(pre_checkout_callback))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback))
