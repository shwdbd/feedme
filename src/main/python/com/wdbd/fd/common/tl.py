# -*- encoding: utf-8 -*-
#!/usr/bin/env python
'''
@File    :   tl.py
@Time    :   2023/12/19 11:39:44
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   公共工具集合
'''
import logging.config
import configparser
import datetime
from pathlib import Path
import os


# 为开发、测试配置不同配置文件, 正常为""，单元测试为test
ENVIRONMENT = ""
# ENVIRONMENT = "test"


def is_test_mode() -> bool:
    """判断是否为测试模式
    Returns:
        bool: True or False
    """
    # print(f"ENVIRONMENT = {ENVIRONMENT}")
    return ENVIRONMENT.lower() == 'test'


# =============================================


class Result:
    """ 通用结果返回 """

    def __init__(self, result: bool = True, msg: str = None):
        self.result = result
        self.msg = msg

    def __str__(self) -> str:
        # return "结果：{result} | {msg}".format(result=self.result, msg=self.msg)
        return f"结果：{self.result} | {self.msg}"

    def __eq__(self, other):
        if not isinstance(other, Result):  # 检查类型一致性
            return False

        # 比较对象的各个重要属性是否相等
        return (self.result == other.result and
                self.msg == other.msg)


# =============================================
# 日志
# 使用方式：log.info('xxxx')
# 返回公共日志记录器
def get_logger():
    """返回公共日志记录器

    Args:
        config_file_path (str of path, optional): 日志配置文件路径. Defaults to None，使用默认文件.

    Returns:
        logger: 日志记录器
    """
    if ENVIRONMENT == 'test':
        config_file_path = os.path.join(Path().cwd(), "src/test/config/fd_log.conf")
    else:
        config_file_path = os.path.join(Path().cwd(), "src/main/config/fd_log.conf")

    # 确保配置文件存在
    if not config_file_path.exists():
        raise FileNotFoundError(f"日志文件配置 {config_file_path} 不存在")

    logging.config.fileConfig(config_file_path, disable_existing_loggers=False)
    return logging.getLogger('fd')


# 返回数据处理服务用日志记录器
# def get_server_logger() -> logging.Logger:
#     """返回数据处理服务用日志记录器

#     Args:
#         config_file_path (str of path, optional): 日志配置文件路径. Defaults to None，使用默认文件.

#     Returns:
#         logger: 日志记录器
#     """
#     if ENVIRONMENT == 'test':
#         config_file_path = os.path.join(Path().cwd(), "src/test/config/fd_log.conf")
#     else:
#         config_file_path = os.path.join(Path().cwd(), "src/main/config/fd_log.conf")

#     logging.config.fileConfig(config_file_path, disable_existing_loggers=False, encoding="UTF-8")
#     return logging.getLogger('fd_server')


# # 返回特定Action用日志记录器
# def get_action_logger(action_name: str) -> logging.Logger:
#     """获得Action专用日志器

#     Args:
#         action_name (str): _description_

#     Returns:
#         logging.Logger: _description_
#     """
#     return get_logger()


# # 返回特定Group用日志记录器
# def get_group_logger(group_name: str) -> logging.Logger:
#     """
#     获取指定组名的日志记录器

#     Args:
#         group_name (str): 组名
#     Returns:
#         logging.Logger: 日志记录器对象
#     """
#     if ENVIRONMENT == 'test':
#         config_file_path = r"src\\test\\config\\fd_log.conf"
#     else:
#         config_file_path = r"src\\main\\config\\fd_log.conf"

#     logging.config.fileConfig(config_file_path)
#     log_group = logging.getLogger('fd_group')
#     return log_group


def get_cfg(section: str, key: str, config_file_path: str = None):
    """
    读取数据下载服务配置文件内容
    
    Args:
        section (str): 配置文件的section名
        key (str): 配置文件中section下的key名
        config_file_path (str, optional): 配置文件路径，默认为None，表示使用默认路径
    
    Returns:
        Any: 配置文件中section下key对应的值，如果读取失败则返回None
    """
    project_path = Path()

    if config_file_path:
        # 使用外部指定的配置文件路径
        file_path = config_file_path
    elif ENVIRONMENT == 'test':
        # 测试环境使用测试路径
        file_path = os.path.join(project_path.cwd(), "src/test/config/fd.cfg")
    else:
        # 开发环境、生产环境使用默认路径
        file_path = os.path.join(project_path.cwd(), "src/main/config/fd.cfg")

    try:
        config_parser = configparser.ConfigParser()
        config_parser.read(file_path, encoding="UTF-8")
        return config_parser.get(section=section, option=key)
    except FileNotFoundError as err:
        # 配置文件未发现
        print(f"配置文件{file_path}未能读取, err={err}")
        return None
    except configparser.Error as err:
        # 只捕获configparser可能抛出的异常，例如NoSectionError, NoOptionError等
        print(f"读取{file_path}配置文件出现问题, err={err}")
        return None

# 读取配置文件目录
def get_config_dir():
    """
    获取配置文件目录路径。
    
    Args:
        无参数。

    Returns:
        str: 配置文件目录路径，根据环境变量 `ENVIRONMENT` 的值返回不同的路径。
        如果 `ENVIRONMENT` 为 'test'，则返回测试环境的配置文件目录路径；
        否则返回开发和生产环境的配置文件目录路径。
    """
    if ENVIRONMENT == 'test':
        # 测试环境
        return os.path.join(Path().cwd(), "src/test/config/")
        # return "src/test/config/"
    else:
        # 开发和生产环境
        # return "src/main/config/"
        return os.path.join(Path().cwd(), "src/main/config/")


# =============================================
# 日期时间工具（常量）
DATE_FORMAT = "%Y%m%d"
TIME_FORMAT = "%Y%m%d %H%M%S"
DATE_VIEW_FORMAT = "%Y-%m-%d"
TIME_VIEW_FORMAT = "%Y-%m-%d %H:%M:%S"


def today():
    """取得当前系统日期的字符串， yyyyMMdd 格式"""
    # print(datetime.datetime.now())
    return datetime.datetime.now().strftime(DATE_FORMAT)


def now():
    """取得当前系统时间的字符串, 格式为 yyyyMMdd HHmmss """
    return datetime.datetime.now().strftime(TIME_FORMAT)


def d2dbstr(view_str: str) -> str:
    """
    将日期视图格式（yyyy-MM-dd）转换为数据库格式（yyyyMMdd）。
    
    Args:
        view_str (str): 日期视图格式字符串，格式为yyyy-MM-dd。
    
    Returns:
        str: 转换后的数据库格式字符串，格式为yyyyMMdd。
    
    """
    if not view_str:
        return ""
    try:
        dt = datetime.datetime.strptime(view_str, DATE_VIEW_FORMAT)
        return datetime.datetime.strftime(dt, DATE_FORMAT)
    except ValueError:
        # 如果输入的字符串不符合 DATE_VIEW_FORMAT 格式，返回原值
        print(f"日期格式转换错误，输入的字符串为：{view_str}")
        return view_str


def d2viewstr(db_str: str) -> str:
    """
    将日期数据库格式（yyyyMMdd）转换为视图格式（yyyy-MM-dd）。
    
    Args:
        db_str (str): 待转换的日期数据库格式字符串，格式为yyyyMMdd。
    
    Returns:
        str: 转换后的日期视图格式字符串，格式为yyyy-MM-dd。如果输入为空字符串，则返回空字符串。
    
    Raises:
        该函数不会主动抛出异常，但如果输入的字符串不符合yyyyMMdd格式，会返回空字符串。
    """
    if not db_str:
        return ""
    try:
        dt = datetime.datetime.strptime(db_str, DATE_FORMAT)
        return datetime.datetime.strftime(dt, DATE_VIEW_FORMAT)
    except ValueError:
        # 如果输入的字符串不符合 格式，返回空字符串或抛出异常，具体取决于业务需求
        return ""
