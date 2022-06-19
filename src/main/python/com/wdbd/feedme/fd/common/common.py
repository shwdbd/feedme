#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   common.py
@Time    :   2021/08/13 13:03:38
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   公共服务类

gtp v0.1.6 从旧版本迁移来的内容有：
1. 配置文件读取
2. mongodb数据库访问
3. 文本日志
4. 日期时间的处理
'''

import logging.config
import configparser
# import pymongo
import datetime
import os

# TODO 为生产、测试配置不同配置文件
TEST_MODE = False


# =============================================
# 配置文件
def get_cfg(section, key):
    """ 读取数据下载服务配置文件内容 """
    if TEST_MODE:
        file_path = "src/test/config/fd.cfg"
    else:
        file_path = "src/main/config/fd.cfg"

    try:
        cf = configparser.ConfigParser()
        cf.read(file_path, encoding="UTF-8")

        return cf.get(section=section, option=key)
    except Exception as err:
        print("读取fd.cfg配置文件出现问题，err={0}".format(err))
        print("配置文件路径：{0}".format(file_path))
        return None


def get_server_cfg(key):
    """ 读取数据下载服务配置文件内容 """
    return get_cfg(section="fdserver", key=key)


def get_mongo_cfg(key):
    """ 读取mongo数据库配置文件内容 """
    return get_cfg(section="mongo", key=key)


# # =============================================
# # 数据库连接
# def get_mgconn():
#     """ 连接数据库，连接不上抛出异常 """
#     try:
#         user = get_mongo_cfg("user")
#         password = get_mongo_cfg("password")
#         db_host = get_mongo_cfg("db_host")
#         db_port = get_mongo_cfg("db_port")
#         db_name = get_mongo_cfg("db_name")
#         url = "mongodb://{user}:{pwd}@{host}:{port}/?authSource={dbname}&ssl=false".format(
#             user=user, pwd=password, host=db_host, port=db_port, dbname=db_name)
#         # 建立连接
#         client = pymongo.MongoClient(url)
#         return client
#     except Exception as err:
#         get_logger().error("连接mongo数据库出现问题。err = {0}".format(err))


# def get_mgdb(dbname=get_mongo_cfg("db_name")):
#     """ 返回数据库对象 """
#     return get_mgconn().get_database(dbname)


# =============================================
# 日志
# 使用方式：log.info('xxxx')
def get_logger():
    """返回日志记录器

    Args:
        config_file_path (str of path, optional): 日志配置文件路径. Defaults to None，使用默认文件.

    Returns:
        logger: 日志记录器
    """
    if TEST_MODE:
        config_file_path = r"src/test/config/log.cfg"
    else:
        config_file_path = r"src/main/config/log.cfg"

    logging.config.fileConfig(config_file_path)
    return logging.getLogger('gtp')


# =============================================
# 日期时间工具
DATE_FORMAT = "%Y%m%d"
TIME_FORMAT = "%Y%m%d %H%M%S"


def today():
    """取得当前系统日期的字符串"""
    return datetime.datetime.now().strftime(DATE_FORMAT)


def now():
    """取得当前系统时间的字符串"""
    return datetime.datetime.now().strftime(TIME_FORMAT)


def get_p():
    print(os.getcwd())
    print("realpath = " + os.path.realpath(__file__))
    return print("\\".join(os.path.abspath(__file__).split("\\")[:-1]))

# if __name__ == "__main__":
#     # get_logger().info("xxxx")
#     # print(get_server_cfg(""))
#     # print(get_server_cfg("dataunit.path"))
#     # print(get_mgconn())
#     # print(get_mgconn().list_database_names())
#     # print(get_mongo_cfg("user"))
#     # 日期时间
#     # print(today())

#     # # mongodb事务性试验
#     # cx = get_mgconn()
#     # db = get_mgdb()
#     # session = cx.start_session()
#     # session.start_transaction()
#     # try:
#     #     data = {"a":1, "b":"B"}
#     #     db["my_table"].insert_one(data)
#     #     db["my_table_error"].insert_one(data)
#     #     print("done")
#     # except Exception as err:
#     #     print(str(err))
#     #     session.abort_transaction()
#     #     print("abort")
#     # else:
#     #     session.commit_transaction()
#     #     print("commit")
#     # finally:
#     #     session.end_session()


# if __name__ == "__main__":
#     print(os.path.join(os.path.dirname(__file__), ".."))
#     print(os.getcwd())
#     print(os.path.abspath(__file__))
#     print("\\".join(os.path.abspath(__file__).split("\\")[:-7]))
