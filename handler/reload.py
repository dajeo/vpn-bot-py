import subprocess

from telegram import Update
from telegram.ext import ContextTypes, Application, CommandHandler

import utils


async def reload(update: Update, _: ContextTypes.DEFAULT_TYPE):
    if not utils.is_owner(update.message.chat_id):
        return

    try:
        subprocess.call(["wg-quick", "down", "/etc/wireguard/wg0.conf"])
        subprocess.call(["wg-quick", "up", "/etc/wireguard/wg0.conf"])

        await update.message.reply_text("Сервис перезапущен.")
    except Exception as err:
        print("Error while reloading WireGuard:", err)
        await update.message.reply_text("Ошибка при выполнении команд.")


def init_reload(app: Application):
    app.add_handler(CommandHandler("reload", reload))
