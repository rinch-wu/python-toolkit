import glob
import importlib
import os


def get_instance(path_abs, name_, cls):
    module_name = os.path.basename(path_abs)[:-3]
    module = importlib.import_module("." + module_name, package=name_)
    instance_all_list = [getattr(module, x) for x in dir(module)]
    instance_list = [x for x in instance_all_list if isinstance(x, cls)]
    assert len(instance_list) == 1, (path_abs, module_name, instance_list, dir(module))
    instance = instance_list[0]
    return module_name, instance


def get_instance_dict(file_, name_, cls):
    # 获取同级别的文件列表
    dir_ = os.path.dirname(file_)
    file_list = glob.glob("*.py", root_dir=dir_)

    # 排除当前文件
    path_abs_list = [file for file in file_list if file != "__init__.py"]
    res = dict([get_instance(path_abs, name_, cls) for path_abs in path_abs_list])
    return res


# ====================================================

# from table3 import Chain as cls
# from util.import_util import get_instance_dict

# instance_dict = get_instance_dict(__file__, __name__, cls)
# print(instance_dict)
# globals().update(instance_dict)
