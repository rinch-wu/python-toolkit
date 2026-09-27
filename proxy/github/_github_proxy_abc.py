import requests
from typing import NamedTuple, Callable
import json
import datetime
import pytz


class OldCommitException(Exception):
    pass
    # def __init__(self, owner, repo, filepath, url, message):
    #     self.owner = owner
    #     self.repo = repo
    #     self.filepath = filepath
    #     self.url = url
    #     super(message)

def split(string: str, split_char: str = ',./:'):
    split_char0 = split_char[0]
    for i in split_char[1:]:
        string = string.replace(i, split_char0)
    return string.split(split_char0)

class GithubProxy:
    owner_repo: str
    filepath_list: list[str]
    default_func_data_prefix: Callable[[str], str] = lambda filepath: split(filepath)[1] + '://'
    default_func_process_data: Callable[[str], list[str]] = lambda data: data.split('\n')

    filepath_list_index = -1
    data = []
    data_index = 0
    # update_time = None # 最近更新时间

    def __init__(self, owner_repo, filepath_list, func_data_prefix = default_func_data_prefix, func_process_data = default_func_process_data):
        self.owner_repo = owner_repo
        self.filepath_list = filepath_list
        self.func_data_prefix = func_data_prefix
        self.func_process_data = func_process_data

    def __iter__(self):
        return self

    def __next__(self):
        while True:
            if self.data_index >= len(self.data):
                self.filepath_list_index += 1
                if self.filepath_list_index >= len(self.filepath_list):
                    raise StopIteration
                else:
                    self.data_index = 0
                    try:
                        self.data = self.get_data(
                            self.filepath_list[self.filepath_list_index])
                    except OldCommitException as e:
                        print(e.args)
                        continue
            else:
                result = self.data[self.data_index]
                self.data_index += 1
                return result

        assert(False, 'cant reach there')

    def verify_update_datetime(self, filepath) -> None:
        # https://api.github.com/repos/proxifly/free-proxy-list/commits?page=1&per_page=1&path=/proxies/all/data.json
        url = f'https://api.github.com/repos{self.owner_repo}/commits?per_page=1&path={filepath}'
        data_str = get_response(url)
        data_json = json.loads(data_str)
        datetime_str = data_json[0]['commit']['committer']['date']
        datetime_commit = datetime.datetime.strptime(
            datetime_str, '%Y-%m-%dT%H:%M:%S%z')
        datetime_now = datetime.datetime.now().astimezone(pytz.UTC)
        timedelta = datetime.timedelta(minutes=20)
        print(datetime_commit + timedelta)
        print(datetime_now)
        if datetime_commit + timedelta < datetime_now:
            raise OldCommitException(
                'file is too old', f'{self.owner}', f'{self.repo}', f'{self.filepath}', f'{url}')

    def get_data(self, filepath) -> list[str]:
        self.verify_update_datetime(filepath)

        # https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/all/data.json
        url = f'https://raw.githubusercontent.com{self.owner_repo}/main{filepath}'
        data = get_response(url)
        data_prefix = self.func_data_prefix(filepath)
        data_processed = self.func_process_data(data)
        data_processed = [ data_prefix + i for i in data_processed]
        return data_processed


def get_response(url) -> str:
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        raise Exception('response status error', f'{url=}', f'{response=}')
