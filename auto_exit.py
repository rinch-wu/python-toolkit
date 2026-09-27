import datetime
import logging
import os
import signal
import threading
import time


class AutoExit:

    timer_list: list[threading.Timer] = []
    lock = threading.Lock()

    @classmethod
    def auto_exit_with_time(cls):

        start_time = datetime.datetime.now()
        end_time = start_time.replace(hour=23, minute=50, second=0, microsecond=0)

        timedelta_1 = end_time - start_time
        timedelta_2 = datetime.timedelta(hours=2)
        timedelta = max(timedelta_1, timedelta_2)

        seconds = timedelta.total_seconds()

        cls.auto_exit(seconds)

    @classmethod
    def auto_exit(cls, seconds: float = 60 * 60):
        thread = threading.Timer(seconds, lambda: os.kill(os.getpid(), signal.SIGINT))
        thread.setDaemon(True)
        thread.start()

        with cls.lock:
            cls.timer_list.append(thread)

    @classmethod
    def remove_all(cls):
        with cls.lock:
            for x in cls.timer_list:
                x.cancel()

            print(f"{len(cls.timer_list)=}")
            cls.timer_list = []
