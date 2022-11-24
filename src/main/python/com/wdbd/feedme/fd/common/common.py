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
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import logging.config
import configparser
# import pymongo
import datetime
import os
import sqlite3


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


def conn_sqlite3():
    """ 连接本地数据库 """
    return sqlite3.connect(get_cfg(section="cmbcft", key="db.path"))


def dict_factory(cursor, row):
    """ sqlite3 按dict格式返回 """
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class SQLiteDb:
    """SQlite3数据库访问上下文
    """

    def __init__(self):
        self.db_path = get_cfg(section="sqlite3", key="db.path")
        self.conn = sqlite3.connect(self.db_path)       # TODO 如果连接不上，则报错
        self.conn.row_factory = dict_factory
        self.cur = self.conn.cursor()

    def __str__(self):
        return "sqlite数据库上下文管理器，数据库位置：" + self.db_path

    def __enter__(self):
        # 返回类对象本身
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cur.close()
        self.conn.close()
        # print("连接已关闭")

    def _log_sql(self, sql):
        """ 记录SQL语句 """
        get_logger().debug("SQL:" + str(sql))

    def _log_err_sql(self, sql):
        """ 记录ERR SQL语句 """
        get_logger().error("ERR SQL:" + str(sql))

    # 查询单条数据
    def query_one(self, sql):
        """ 查询单条 """
        try:
            self._log_sql(sql)
            self.cur.execute(sql)
            res = self.cur.fetchone()
            return res
        except Exception as e:
            self._log_err_sql(sql)
            get_logger().error("SQL错误: " + str(e))
            return None

    def query(self, sql):
        """ 查询全部 """
        try:
            self._log_sql(sql)
            self.cur.execute(sql)
            res = self.cur.fetchall()
            return res
        except Exception as e:
            self._log_err_sql(sql)
            get_logger().error("SQL错误: " + str(e))
            return None

    def execute(self, sqls):
        """ 执行单条或少量的SQL语句() """
        if type(sqls) is str:
            sql_list = [sqls]
        else:
            sql_list = sqls

        try:
            for sql_str in sql_list:
                self._log_sql(sql_str)
                self.cur.execute(sql_str)
            self.conn.commit()
            self._log_sql("事务提交")
        except Exception as err:
            self._log_err_sql(sqls)
            get_logger().error("SQL错误 = " + str(err))
            self.conn.rollback()
            self._log_sql("事务已回滚")

    def execute_many(self, sql_str, data):
        """ 执行批量SQL语句 """
        if data is None or len(data) == 0:
            return

        try:
            self._log_sql("批量SQL:" + sql_str)
            self._log_sql("批量数据，总记录数{0} ".format(len(data)))
            self.cur.executemany(sql_str, data)
            self.conn.commit()
            self._log_sql("事务提交")
            return True
        except Exception as err:
            self._log_err_sql(sql_str)
            get_logger().error("SQL错误 = " + str(err))
            self.conn.rollback()
            self._log_sql("事务已回滚")
            return False


# =============================================
# ORM 工具函数

# 连接数据库引擎
def get_engine():
    DB_CONN_STR = "sqlite:///" + get_cfg(section="sqlite3", key="db.path")
    echo = bool(get_cfg(section="sqlite3", key="echo"))
    engine = create_engine(DB_CONN_STR, echo=echo)
    return engine


Base = declarative_base()


def get_session():
    """ 取得数据库会话 """
    Session = sessionmaker(bind=get_engine())
    return Session()


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
    """ 临时，取得当前的路径 """
    print(os.getcwd())
    print("realpath = " + os.path.realpath(__file__))
    return print("\\".join(os.path.abspath(__file__).split("\\")[:-1]))


# =============================================
# 其他工具函数

# DataFrame转成的dict格式，转成数据对象
def record2object(record: dict, obj: object):
    """DataFrame转成的dict格式，转成数据对象

    前提要求：record中的每个字段，都在Object中有同名的属性

    record样子：{'col1':1, 'col2':0.5}

    Args:
        record (dict): 待转换的dict
        record (dict): 转换后的object

    Returns:
        object: 转换后的object
    """
    if not dict:
        return None
    if not isinstance(record, dict):
        return None

    for f_name in record.keys():
        setattr(obj, f_name, record[f_name])

    return obj


# DataFrame转成的dict列表，转成数据对象列表
def records2objlist(pd_df: list, clz):
    """ DataFrame转成的dict列表，转成数据对象列表 """
    obj_list = []
    for d in pd_df.to_dict("records"):
        obj_list.append(record2object(d, clz()))
    return obj_list


# if __name__ == "__main__":
#     # print(get_cfg(section="sqlite3", key="db.path"))
#     e = get_engine()
#     print(e)

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
