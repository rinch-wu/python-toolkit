import base64
import datetime
import json
import random
import string
from typing import Iterable
from urllib.parse import parse_qs, urlparse

from tqdm import tqdm

charset_lowercase_digits = string.ascii_lowercase + string.digits


def generate_str(length_min: int, length_max: int = None, charset: str = charset_lowercase_digits):
    length_max = length_max or length_min

    name_length = random.randint(length_min, length_max)
    name = "".join(random.choices(charset, k=name_length))
    return name


def unicode_2_plain(str):
    return str.encode().decode("unicode escape")


def get_pbar(data: Iterable) -> tqdm:
    pbar = tqdm(
        data,
        dynamic_ncols=True,
        postfix="#",
        smoothing=60 * 60,
        bar_format=" {percentage:3.0f}% = {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}{postfix}] |{bar:10}| {desc}\n",
    )
    return pbar


def get_url_param(url, param_key):
    parsed_url = urlparse(url)
    params = parse_qs(parsed_url.query)
    param_value = params[param_key][0]
    return param_value


def get_week(format: str = "%Y%m%d"):
    date_now_utc = datetime.datetime.utcnow().date()
    days_since_monday = date_now_utc.weekday()
    day_sun_utc = date_now_utc - datetime.timedelta(days=days_since_monday + 1)
    day_sat_utc = day_sun_utc + datetime.timedelta(days=6)

    date_list = (day_sun_utc, day_sat_utc, date_now_utc)
    date_list_str = [i.strftime(format) for i in date_list]
    return (date_list, date_list_str)


def str2base64(original_string):
    bytestring = original_string.encode("utf-8")
    base64_bytestring = base64.b64encode(bytestring)
    base64_string = base64_bytestring.decode("utf-8")
    return base64_string


def base642str(base64_string):
    base64_bytestring = base64_string.encode("utf-8")
    bytestring = base64.b64decode(base64_bytestring)
    original_string = bytestring.decode("utf-8")
    return original_string


def json_stringify(data: dict):
    return json.dumps(data, separators=(",", ":"))


@staticmethod
def merge_dict(dict_target: dict[str, str], dict_now: dict[str, str], prefix: str) -> None:
    dict_tmp = {k + prefix: v for k, v in dict_now.items()}
    assert (dict_target and dict_tmp) == {}, (dict_now, dict_target)
    dict_target |= dict_tmp
