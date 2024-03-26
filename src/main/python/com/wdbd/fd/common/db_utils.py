#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   db_utils.py
@Time    :   2024/03/26 16:10:57
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   数据库工具类
'''
from sqlalchemy import text
from com.wdbd.fd.model.db import get_engine
from sqlalchemy.orm import sessionmaker
import com.wdbd.fd.common.tl as tl
from sqlalchemy.exc import SQLAlchemyError as SQLAlchemyError


class DbUtils:
    """ 数据库工具库 """

    # 统计某表中符合条件的记录数量
    @staticmethod
    def count(table_name: str, sql_where_str: str = None) -> int:
        """ 统计某表中符合条件的记录数量

        返回-1说明发生错误

        Args:
            table_name (str): 数据库表名
            sql_where_str (str, optional): Where SQL语句(原生SQL). Defaults to None.

        Returns:
            long: 符合条件的记录数量
        """
        try:
            engine = get_engine()
            Session = sessionmaker(bind=engine)
            session = Session()

            if sql_where_str:
                sql_query = text(f"SELECT count(*) as count_all FROM {table_name} where {sql_where_str}")
            else:
                sql_query = text(f"SELECT count(*) as count_all FROM {table_name}")
            tl.get_logger().debug(f"SQL = {sql_query}")
            result = session.execute(sql_query)

            return result.first()[0]
        except SQLAlchemyError as sqle:
            msg = "SQL异常" + str(sqle)
            tl.get_logger().error(msg)
            return -1
        finally:
            session.close()

    # 清空某个数据库表
    @staticmethod
    def clear_table_data(table_name: str, sql_where_str: str = None):
        """ 清空某个数据库表

        Args:
            table_name (str): 数据库表名
            sql_where_str (str, optional): Where SQL语句(原生SQL). Defaults to None.

        """
        try:
            if sql_where_str:
                sql_query = text(f"DELETE FROM {table_name} where {sql_where_str}")
            else:
                sql_query = text(f"TRUNCATE TABLE {table_name} ")
            tl.get_logger().debug(f"SQL = {sql_query}")

            engine = get_engine()
            with engine.begin() as connection:
                connection.execute(sql_query)
            tl.get_logger().debug(f"表{table_name}已清空, 清空条件: {sql_where_str}")

        except SQLAlchemyError as sqle:
            msg = "SQL异常" + str(sqle)
            tl.get_logger().error(msg)


if __name__ == "__main__":
    # print(DbUtils.count(table_name="ods_akshare_stock_sse_summary"))
    # print(DbUtils.count(table_name="ods_akshare_stock_sse_summary", sql_where_str="trade_date='20240325'"))
    # DbUtils.clear_table_data(table_name="comm_server")
    pass
