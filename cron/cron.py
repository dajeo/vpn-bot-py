import random
import threading
import time
from datetime import datetime

import schedule
from telegram.constants import ParseMode

import conf
import utils
from db import User


def job():
    users: list[User] = User.select().where(User.paid_at is not None)

    for user in users:
        now = datetime.now()
        expired_at = utils.add_months(user.paid_at, 2)
        u = user
        if now >= utils.remove_days(expired_at, 3) and not user.expired and not user.waiting_payment:
            u.waiting_payment = True
            u.save()

            utils.send_message(
                user.chat_id, "Через три дня заканчивается подписка. Оплатите чтобы продолжать пользоваться VPN."
            )
        elif now >= expired_at and not user.expired:
            u.waiting_payment = True
            u.expired = True
            u.save()

            utils.send_message(
                user.chat_id, "Ваша подписка закончилась, до полного отключения конфигурации у вас есть еще три дня."
            )
        elif now >= utils.add_days(expired_at, 3) and not user.shutdown_notice:
            u.shutdown_notice = True
            u.save()

            utils.send_message(
                conf.get()["bot"]["owner"],
                f"Клиент <code>{user.chat_id}</code> ({user.name}) не оплатил подписку.",
                ParseMode.HTML
            )

            kidney = random.choices([True, False], weights=[2, 8])

            msg = "Сервис отключен до оплаты подписки."

            if kidney == [True]:
                msg += " <s>Иначе мы вырежем вам почку.</s>"

            utils.send_message(user.chat_id, msg, ParseMode.HTML)


def worker():
    schedule.every().day.at("14:00").do(job)
    # schedule.every(10).seconds.do(job)

    while True:
        schedule.run_pending()
        time.sleep(1)


def start():
    thread = threading.Thread(target=worker)
    thread.daemon = True
    thread.start()
