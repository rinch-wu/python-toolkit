import asyncio
import atexit
import datetime
import inspect
import logging
import threading
import time
import traceback
from functools import partial
from typing import Callable

import tqdm

# from .state_store import StateStore


class StateStore:
    def __init__(self, total: int, count_done: int = 0, count_error: int = 0):
        self.total = total
        self.count_done = count_done
        self.count_error = count_error

        self.lock = threading.Lock()

    def done(self):
        with self.lock:
            self.count_done += 1

    def error(self):
        with self.lock:
            self.count_error += 1

    def print(self):
        count_all = self.count_error + self.count_done

        total = self.total
        len_total = len(str(total))

        count_all_str = str(count_all).rjust(len_total)
        count_done_str = str(self.count_done).rjust(len_total)
        count_error_str = str(self.count_error).rjust(len_total)

        logging.info(f"")
        logging.info(f"{total} : total")
        logging.info(f"{count_all_str} : count_all")
        logging.info(f"{count_done_str} : count_done")
        logging.info(f"{count_error_str} : count_error")
        logging.info(f"{(count_all==total)=}")

    def __str__(self):
        return f"{self.total} : {self.count_done} >> {self.count_error} ?"


def map_(map_your, func, iterables: list):
    if not isinstance(iterables, list):
        iterables = list(iterables)

    total = len(iterables)
    len_total = len(str(total))
    state_store = StateStore(total)

    atexit.register(state_store.print)

    @threadname_(len_total=len_total)
    @tqdm_update(total=total, state_store=state_store)
    @except_(state_store=state_store)
    # @time_(total=total)
    def process_wrap(
        # func,
        index: int,
        *,
        data_list: list,
    ):
        data = data_list[index]
        return func(data)

    func_partial = partial(process_wrap, data_list=iterables)
    res = map_your(func_partial, range(total))
    res_value = get_value(res)
    if len(res_value) < 10:
        [print(x) for x in res_value]
    state_store.print()

    return res_value


def get_value(res: list) -> list:

    async def wait_async(tasks):
        results = []
        for task in tasks:
            if inspect.isawaitable(task):
                result = await task
                results.append(result)
            else:
                results.append(task)
        return results

    if len(res) > 0 and inspect.isawaitable(res[0]):
        awaitable = asyncio.gather(*res, return_exceptions=False)
        loop = asyncio.get_event_loop()
        res_value = loop.run_until_complete(awaitable)
    else:
        return res
    # res_value = asyncio.run()
    return res_value


def tqdm_update(func: callable = None, total: int = None, state_store: StateStore = None):
    if func is None:
        return partial(tqdm_update, total=total, state_store=state_store)

    tqdm_ = tqdm.tqdm(
        total=total,
        smoothing=0.05,
    )
    lock = tqdm_.get_lock()
    # lock = threading.Lock()

    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        with lock:
            tqdm_.set_description(str(state_store))
            tqdm_.update()
        return result

    return wrapper


def time_(func: callable = None, total: int = None):
    if func is None:
        return partial(time_, total=total)

    process_start = time.time()

    def wrapper(*args, **kwargs):
        # thread_start = time.time()

        result = func(*args, **kwargs)

        thread_end = time.time()

        index = args[-1]

        process_delta = thread_end - process_start
        bar = tqdm.tqdm.format_meter(index, total, process_delta)
        logging.info(f"bar={bar}")

        return result

    return wrapper


def threadname_(func: callable = None, len_total: int = None):
    if func is None:
        return partial(threadname_, len_total=len_total)

    def wrapper(*args, **kwargs):
        index = args[-1]

        threading.current_thread().name = str(index).rjust(len_total)

        result = func(*args, **kwargs)
        return result

    return wrapper


# def except_(func: callable = None, total: int = None):
def except_(func: callable = None, state_store: StateStore = None):
    if func is None:
        return partial(except_, state_store=state_store)
    print_exc_count_max = 5

    def wrapper(*args, **kwargs):
        # logging.info(f"do {func.__name__}")
        logging.info(f"todo")

        result = None
        try:
            result = func(*args, **kwargs)
        except Exception as e:

            logging.info(f"error")
            info = traceback.format_exc()

            if state_store.count_error < print_exc_count_max:
                print(info)

            logging.error(info)
            state_store.error()

            # raise e
        else:
            # logging.info(f"done {func.__name__}")

            logging.info(f"done")
            state_store.done()
            return result

    return wrapper


# def except_(func: callable = None, total: int = None):
def except_pure(func: callable = None):
    def wrapper(*args, **kwargs):
        # logging.info(f"do {func.__name__}")
        logging.info(f"todo")

        result = None
        try:
            result = func(*args, **kwargs)
        except Exception as e:

            logging.info(f"error")
            info = traceback.format_exc()

            logging.error(info)

            raise e
        else:
            # logging.info(f"done {func.__name__}")

            logging.info(f"done")
            return result

    return wrapper


def call_when(func_list: list[Callable[[], bool]]):  # Callable[[], bool] | list[Callable[[], bool]]
    if isinstance(func_list, Callable):
        func_list = [func_list]

    assert isinstance(func_list, list)
    assert all([isinstance(i, Callable) for i in func_list])

    def decorator_func(func):
        def wrapper(*args, **kwargs):
            if all([i() for i in func_list]):
                # 条件达成，执行函数
                result = func(*args, **kwargs)
                return result

        return wrapper

    return decorator_func


def lock_(func: callable):
    lock = threading.Lock()

    def wrapper(*args, **kwargs):
        with lock:
            return func(*args, **kwargs)

    return wrapper
