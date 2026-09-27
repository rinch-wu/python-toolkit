# 安装库：pip install psutil
import psutil


def kill_process(process_name="chromedriver.exe"):
    """
    :param process_name: 进程名称
    """

    # 查找所有的Chrome驱动进程
    process_list = [process for process in psutil.process_iter() if process.name() == process_name]
    if len(process_list) > 0:
        # 如果有多个Chrome驱动程序正在运行，则杀死所有的Chrome驱动程序
        for process in process_list:
            process.kill()
        print("存在Chrome驱动程序，并且已杀死所有Chrome驱动程序")
    else:
        print("没有Chrome驱动程序正在运行")
