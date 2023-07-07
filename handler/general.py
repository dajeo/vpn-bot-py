from telegram import Update
from telegram.ext import ConversationHandler, ContextTypes


async def cancel_conv(update: Update, _: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Команда отменена.")
    return ConversationHandler.END
