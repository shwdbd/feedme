#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   dbtool.py
@Time    :   2022/04/14 22:19:08
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   数据库工具
'''
import sqlite3
from dbutils.pooled_db import PooledDB
from app.extensions.tools.log_tools import logger
from app import app
import os

DB_POOL = None


class SQLHelper:
    """ 数据库工具类 """

    def __init__(self, log=None):
        if log:
            self.log = log
        else:
            self.log = logger
        # db_path = r'C:\sqlite\Dbs\data.db'
        db_path = app.config["SQLITE_DB_PATH"]
        self.dbpool = PooledDB(creator=sqlite3, database=db_path,
                               # 连接池中最小空闲连接数
                               mincached=app.config["DBPOOL_MINCACHED"],
                               # 连接池中最大空闲连接数
                               maxcached=app.config["DBPOOL_MAXCACHED"],
                               # 允许的最大连接数
                               maxconnections=app.config["DBPOOL_MAXCONNECTIONS"],
                               # 设置为true，则阻塞并等待直到连接数量减少，false默认情况下将报告错误。
                               blocking=app.config["DBPOOL_BLOCKING"],
                               # 默认=1表示每当从池中获取时，使用ping()检查连接
                               ping=app.config["DBPOOL_PING"]
                               )

    def __open(self):
        """ 取得数据库连接和游标 """
        conn = self.dbpool.connection()
        cursor = conn.cursor()
        self.log.debug("create conn")
        return conn, cursor

    def __close(self, conn, cursor):
        """ 关闭数据库连接和游标 """
        self.log.debug("close conn")
        cursor.close()
        conn.close()

    # 取得一个数据库连接
    @staticmethod
    def _get_conn():
        # conn = self.dbpool.connection()
        conn = sqlite3.connect(app.config["SQLITE_DB_PATH"])
        return conn

    # 执行SQL语句
    def execute(self, sql) -> bool:
        """ 执行SQL """
        try:
            conn, cur = self.__open()
            if type(sql) is list:
                # 多语句
                for sql_str in sql:
                    cur.execute(sql_str)
                    self.log.debug("【sql】" + sql_str)
            else:
                # 单条语句
                sql_str = sql
                cur.execute(sql_str)
                self.log.debug("【sql】" + sql_str)
            conn.commit()
            self.log.debug("【sql commit】")
            return True
        except Exception as err:
            self.log.error("【error sql】" + sql_str)
            self.log.error("【sql exception】" + str(err))
            conn.rollback()
            self.log.debug("【roll back】")
            return False
        finally:
            self.__close(conn, cur)

    # 执行SQL文件
    def execute_sqlfile(self, file_path: str) -> bool:
        """执行.sql文件

        Args:
            file_path (str): .sql文件的绝对路径

        Returns:
            bool: 执行结果
        """
        ENCODING = "utf-8"
        SPILT = ";"
        if not os.path.exists(file_path):
            return False
        with open(file_path, encoding=ENCODING) as sql_f:
            sql_str = sql_f.read()
            sqls = sql_str.split(SPILT)
            return self.execute(sqls)

    # 查询并返回全部
    def query_all(self, sql: str, dtype: str = "tuple") -> list:
        """ 查询并返回全部记录 """
        if not sql:
            return None
        try:
            conn, cur = self.__open()
            cur.execute(sql)
            records = cur.fetchall()  # (1, 'a')
            if records:
                if dtype == 'dict':
                    d_records = []
                    for r in records:
                        d_records.append(
                            dict(zip([c[0] for c in cur.description], r)))
                        # [{'id': '00', 'name': '分行公共', 'dept_type': 2}, {...}]
                    return d_records
                else:
                    # ('00', '分行公共', 2)
                    return records
            else:
                # 返回空记录
                return []
        except Exception as err:
            self.log.error("【error sql】" + sql)
            self.log.error("【sql exception】" + str(err))
            return None
        finally:
            self.__close(conn, cur)

    # 查询返回一条
    def query_one(self, sql: str, dtype: str = "tuple"):
        """ 查询并返回一条记录 """
        if not sql:
            return None
        try:
            conn, cur = self.__open()
            cur.execute(sql)
            record = cur.fetchone()  # (1, 'a')
            if record:
                if dtype == 'dict':
                    d_record = dict(
                        zip([c[0] for c in cur.description], record))
                    # {'id': '00', 'name': '分行公共', 'dept_type': 2}
                    return d_record
                else:
                    # ('00', '分行公共', 2)
                    return record
            else:
                # 返回空记录
                if dtype == 'dict':
                    return {}
                else:
                    return ()
        except Exception as err:
            self.log.error("【error sql】" + sql)
            self.log.error("【sql exception】" + str(err))
            return None
        finally:
            self.__close(conn, cur)

    # 判断表是否存在
    def table_exist(self, table_name: str) -> bool:
        """判断表是否存在

        Args:
            table_name (str): 表名

        Returns:
            bool: 是否存在
        """
        sql = "select count(*) as count from sqlite_master where name='{name}'".format(
            name=table_name)
        res = self.query_one(sql, dtype="dict")
        if res is None or res is {} or res["count"] == 0:
            return False
        else:
            return True


class DbContext:
    """ 数据库直接访问上下文 """

    def __enter__(self):
        return SQLHelper()

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_value:
            print(exc_value)


# if __name__ == "__main__":
#     # # 直接调用模式：
#     # db = SQLHelper()
#     # sql = "insert into admin_dept values ('xxx', 'nnnnn', 'xxx')"
#     # res = db.execute(sql)
#     # print(res)

#     # # 使用上下文
#     # with DbContext() as dbctx:
#     #     sql_list = []
#     #     sql_list.append("create table test_t (id VARCHAR (20), name VARCHAR (20))")
#     #     sql = "insert into test_t values ('22222', 'nnnnn')"
#     #     sql_list.append(sql)
#     #     sql_list.append("insert into test_t values ('3333', 'nnnnn')")
#     #     dbctx.execute(sql_list)

#     # # 执行.sql文件
#     # with DbContext() as db:
#     #     res = db.execute_sqlfile(r"src/test/python/tools/init.sql")
#     #     print(res)

#     # # 判断表是否存在
#     # with DbContext() as db:
#     #     res = db.table_exist("admin_user")
#     #     print(res)
#     #     res = db.table_exist("xxx")
#     #     print(res)

#     # # 查询一条
#     # with DbContext() as db:
#     #     res = db.query_one(r"select * from admin_dept where id = 2", dtype='dict')
#     #     print(type(res))
#     #     print(res)

#     # 查询全部
#     with DbContext() as db:
#         res = db.query_all(r"select * from admin_dept ", dtype='dict')
#         print(type(res))
#         print(res)
