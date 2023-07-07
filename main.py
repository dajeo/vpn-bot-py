import logging

import conf
import cron
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes
)
import db
import handler

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)


def main():
    conf.init("config.ini")
    db.init()

    config = conf.get()

    cron.start()

    app = Application.builder().token(config["bot"]["token"]).build()

    handler.init_start(app)
    handler.init_payment(app)
    handler.init_send(app)

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
