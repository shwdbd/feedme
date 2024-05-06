#!/usr/bin/env python
# -*- encoding: utf-8 -*-
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


# 为开发、测试配置不同配置文件, 正常为""，单元测试为test
ENVIRONMENT = ""
# ENVIRONMENT = "test"


class Result:
    """ 通用结果返回 """

    def __init__(self, result: bool = True, msg: str = None):
        self.result = result
        self.msg = msg

    def __str__(self) -> str:
        return "结果：{result} | {msg}".format(result=self.result, msg=self.msg)

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
        config_file_path = r"src\\test\\config\\fd_log.conf"
    else:
        config_file_path = r"src\\main\\config\\fd_log.conf"
    logging.config.fileConfig(config_file_path, disable_existing_loggers=False)
    return logging.getLogger('fd')


# 返回数据处理服务用日志记录器
def get_server_logger() -> logging.Logger:
    """返回数据处理服务用日志记录器

    Args:
        config_file_path (str of path, optional): 日志配置文件路径. Defaults to None，使用默认文件.

    Returns:
        logger: 日志记录器
    """
    if ENVIRONMENT == 'test':
        config_file_path = r"src\\test\\config\\fd_log.conf"
    else:
        config_file_path = r"src\\main\\config\\fd_log.conf"

    logging.config.fileConfig(config_file_path, disable_existing_loggers=False, encoding="UTF-8")
    return logging.getLogger('fd_server')


# 返回特定Action用日志记录器
def get_action_logger(action_name: str) -> logging.Logger:
    """获得Action专用日志器

    Args:
        action_name (str): _description_

    Returns:
        logging.Logger: _description_
    """
    # FIXME 待优化，删除此功能
    return get_logger()


# 返回特定Group用日志记录器
def get_group_logger(group_name: str) -> logging.Logger:
    if ENVIRONMENT == 'test':
        config_file_path = r"src\\test\\config\\fd_log.conf"
    else:
        config_file_path = r"src\\main\\config\\fd_log.conf"

    logging.config.fileConfig(config_file_path)
    log_group = logging.getLogger('fd_group')
    # # handlers = [h for h in log_group.handlers]         # 取得全部的Handler
    # # print(handlers[0].format())
    # theHandler = log_group.handlers[0]
    # # print(theHandler)
    # formatter = logging.Formatter('[%(asctime)s][%(levelname)-5s] 【组：{name}】 %(message)s '.format(name=group_name), datefmt="%Y-%m-%d %H:%M:%S")
    # theHandler.setFormatter(formatter)
    return log_group


# =============================================
# 配置文件
def get_cfg(section, key):
    """ 读取数据下载服务配置文件内容 """
    if ENVIRONMENT == 'test':
        # 测试环境
        file_path = "src/test/config/fd.cfg"
    else:
        # 开发环境
        file_path = "src/main/config/fd.cfg"

    try:
        config_parser = configparser.ConfigParser()
        config_parser.read(file_path, encoding="UTF-8")

        return config_parser.get(section=section, option=key)
    except Exception as err:
        print(f"读取{file_path}配置文件出现问题, err={err}")
        return None


# 读取配置文件目录
def get_config_dir():
    if ENVIRONMENT == 'test':
        # 测试环境
        return "src/test/config/"
    else:
        # 开发环境
        return "src/main/config/"


# =============================================
# 日期时间工具
DATE_FORMAT = "%Y%m%d"
TIME_FORMAT = "%Y%m%d %H%M%S"
DATE_VIEW_FORMAT = "%Y-%m-%d"
TIME_VIEW_FORMAT = "%Y-%m-%d %H:%M:%S"


def today():
    """取得当前系统日期的字符串"""
    # print(datetime.datetime.now())
    return datetime.datetime.now().strftime(DATE_FORMAT)


def now():
    """取得当前系统时间的字符串"""
    return datetime.datetime.now().strftime(TIME_FORMAT)


def d2dbstr(view_str: str) -> str:
    """ 日期视图格式yyyy-MM-dd转数据库格式yyyyMMdd """
    if not view_str:
        return ""
    try:
        dt = datetime.datetime.strptime(view_str, DATE_VIEW_FORMAT)
        return datetime.datetime.strftime(dt, DATE_FORMAT)
    except ValueError:
        # 如果输入的字符串不符合 DATE_VIEW_FORMAT 格式，返回原值
        return view_str
    except Exception as e:
        print(f"日期格式转换错误， {view_str},  {e}")
        return view_str


def d2viewstr(db_str: str) -> str:
    """ 日期数据库格式yyyyMMdd转视图格式yyyy-MM-dd """
    if not db_str:
        return ""
    try:
        dt = datetime.datetime.strptime(db_str, DATE_FORMAT)
        return datetime.datetime.strftime(dt, DATE_VIEW_FORMAT)
    except ValueError:
        # 如果输入的字符串不符合 格式，返回空字符串或抛出异常，具体取决于业务需求
        return ""
