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


# 为开发、测试配置不同配置文件, 正常为""，单元测试为test
ENVIRONMENT = ""
# ENVIRONMENT = "test"


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
    print(config_file_path)
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

    logging.config.fileConfig(config_file_path, disable_existing_loggers=False)
    return logging.getLogger('fd_server')


# 返回特定Action用日志记录器
def get_action_logger(action_name: str) -> logging.Logger:
    if ENVIRONMENT == 'test':
        config_file_path = r"src\\test\\config\\fd_log.conf"
    else:
        config_file_path = r"src\\main\\config\\fd_log.conf"

    logging.config.fileConfig(config_file_path)
    log_action = logging.getLogger('fd_action')
    # handlers = [h for h in log_action.handlers]         # 取得全部的Handler
    theHandler = log_action.handlers[0]
    # print(theHandler)
    formatter = logging.Formatter('[%(asctime)s][%(levelname)-5s] 【{0}】 %(message)s '.format(action_name), datefmt="%Y-%m-%d %H:%M:%S")
    theHandler.setFormatter(formatter)
    return log_action


# if __name__ == "__main__":
#     log = get_logger()
#     log.info("xxxx")

#     log_s = get_server_logger()
#     log_s.info("xxxx")

#     log_a = get_action_logger("tushare")
#     log_a.info("ts test")
