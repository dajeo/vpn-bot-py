from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, Application, CommandHandler, CallbackQueryHandler


def get_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton("Android", callback_data="android"),
            InlineKeyboardButton("iOS", callback_data="ios")
        ],
        [
            InlineKeyboardButton("Windows", callback_data="win"),
            InlineKeyboardButton("macOS", callback_data="mac")
        ],
        [
            InlineKeyboardButton("Отмена", callback_data="cancel")
        ]
    ]

    return InlineKeyboardMarkup(keyboard)


async def instruction(update: Update, _: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Выберете вашу платформу:", reply_markup=get_keyboard())


async def instruction_callback(update: Update, _: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data

    await query.answer()

    if data == "back":
        await query.edit_message_text("Выберете вашу платформу:", reply_markup=get_keyboard())
        return
    elif data == "cancel":
        await query.delete_message()
        return

    i = "1. Установите WireGuard\n\n" \
        "{link}\n\n" \
        "2. Скачайте файл имя.conf\n\n" \
        "{body}" \
        "Проверить работоспособность можно на сайте https://vpn.dajeo.by/check/\n\n" \
        "<i>Предупреждение: не делитесь вашим профилем, он может обрабатывать только одно подключение!</i>"

    if data == "android" or data == "ios":
        i = i.format(
            link="https://play.google.com/store/apps/details?id=com.wireguard.android" if data == "android" else
            "https://apps.apple.com/ru/app/wireguard/id1441195209",
            body="3. Откройте WireGuard и нажмите на кнопку плюс (+)\n\n"
            "4. Выберете пункт Импорт из файла или архива, выберете скачанный файл и укажите название\n\n"
            "5. Теперь вверху экрана вы можете активировать только что созданный профиль\n\n"
        )
    else:
        i = i.format(
            link="https://download.wireguard.com/windows-client/wireguard-installer.exe" if data == "win" else
            "https://apps.apple.com/us/app/wireguard/id1451685025",
            body="3. Откройте WireGuard и нажмите на кнопку Импорт туннелей из файла...\n\n"
            "4. Выберете скачанный файл и нажмите Подключить\n\n"
        )

    keyboard = [[
        InlineKeyboardButton("Назад", callback_data="back"), InlineKeyboardButton("Отмена", callback_data="cancel")
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        i, reply_markup=reply_markup, parse_mode=ParseMode.HTML, disable_web_page_preview=True
    )


def init_instruction(app: Application):
    app.add_handler(CommandHandler("instruction", instruction))
    app.add_handler(CallbackQueryHandler(instruction_callback))
