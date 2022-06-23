#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   io_tools.py
@Time    :   2022/04/15 19:32:31
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   数据导入导出工具
'''
import os
import pandas as pd
from app.extensions.tools.dbtool import DbContext, SQLHelper
from app.extensions.tools.log_tools import logger


# CSV配置项目
CSV_ENCODING = "utf-8"
CSV_SEP = ","


def csv2db(csv_file: str, table_name: str, *args, **kwargs) -> int:
    """ 将csv文件导入数据库表 """
    # FIXME csv文件与表字段无法一一对应，是个缺憾

    # 检查文件是否存在
    if not os.path.exists(csv_file):
        logger.error("导入文件不存在，导入失败！" + csv_file)
        return -1
    # 监测表是否存在
    with DbContext() as db:
        if not db.table_exist(table_name):
            logger.error("导入目标表({0})不存在，导入失败！".format(table_name))
            return -1
        try:
            conn = SQLHelper._get_conn()
            # 读取文件
            df = pd.read_csv(filepath_or_buffer=csv_file, sep=CSV_SEP,
                             header=0, thousands=',', encoding=CSV_ENCODING, *args, **kwargs)
            # print(df)
            if df.shape[0] > 0:
                db.execute("delete from {t_name}".format(
                    t_name=table_name))    # 清空原有数据
                df.to_sql(name=table_name, con=conn,
                          if_exists='append', index=False)
                logger.debug("CSV {file_line_count}行 ==> db.{table_name}".format(
                    file_line_count=df.shape[0], table_name=table_name))
            return df.shape[0]
        except Exception as err:
            print('导入发生异常，' + str(err))
            return -1
        finally:
            conn.close()


def excel2db(excel_file: str, table_name: str, sheet_name: str = None, *args, **kwargs) -> int:
    """ 将excel文件导入数据库表 """
    # TODO 待实现
    # 检查文件是否存在
    if not os.path.exists(excel_file):
        logger.error("导入文件不存在，导入失败！" + excel_file)
        return -1
    # 检查文件，
    # 监测表是否存在
    with DbContext() as db:
        if not db.table_exist(table_name):
            logger.error("导入目标表({0})不存在，导入失败！".format(table_name))
            return -1
        try:
            conn = SQLHelper._get_conn()
            # 读取文件
            df = pd.read_excel(filepath=excel_file, sheet_name=sheet_name,
                               thousands=',', *args, **kwargs)
            # print(df)
            if df.shape[0] > 0:
                db.execute("delete from {t_name}".format(
                    t_name=table_name))    # 清空原有数据
                df.to_sql(name=table_name, con=conn,
                          if_exists='append', index=False)
                logger.debug("CSV {file_line_count}行 ==> db.{table_name}".format(
                    file_line_count=df.shape[0], table_name=table_name))
            return df.shape[0]
        except Exception as err:
            print('导入发生异常，' + str(err))
            return -1
        finally:
            conn.close()


if __name__ == "__main__":
    f = r"src\test\python\tools\csv_files\test_t1.csv"

    res = csv2db(f, table_name="test_t1")
    print(res)

    # print(os.path.dirname(__file__))
    # print(os.path.exists(__file__))
