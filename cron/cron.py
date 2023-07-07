import threading
import time

import schedule


def job():
    print("job work")


def worker():
    schedule.every().day.at("14:00").do(job)

    while True:
        schedule.run_pending()
        time.sleep(1)


def start():
    thread = threading.Thread(target=worker)
    thread.daemon = True
    thread.start()
