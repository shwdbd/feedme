#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   bs_stock.py
@Time    :   2022/07/17 17:51:24
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   Baostock数据下载
'''
from com.wdbd.feedme.fd.common.data_gateway import BaostockGateWay
import baostock as bs
from com.wdbd.feedme.fd.common.common import SQLiteDb as SQLiteDb
import com.wdbd.feedme.fd.common.common as tl
import datetime
# import pandas as pd


class SecurityListUnit:
    """ 证券清单下载 """

    def download_all(self, start_date=None):
        """ 下载全量证券清单 """
        log = tl.get_logger()
        t1 = datetime.datetime.now()
        log.info("【Baostock】开始下载 证券清单")

        try:
            gw = BaostockGateWay()
            df = gw.call(callback=bs.query_stock_basic)
            log.info("【Baostock】获得 证券清单 接口数据{0}条".format(df.shape[0]))
            # 数据清洗
            df = df[["code", "code_name", "ipoDate", "outDate", "type", "status"]]

            with SQLiteDb() as db:
                sql = "delete from ods_baostock_stock_basic"
                db.execute(sql)

                sql = "insert into ods_baostock_stock_basic "
                sql += " (code, code_name, ipoDate, outDate, type_id, status_id) "
                sql += " values "
                sql += " (?, ?, ?, ?, ?, ?) "
                db.execute_many(sql, df.to_records(index=False))

                # 查询
                sql = "select count(*) as count_all from ods_baostock_stock_basic "
                count = db.query_one(sql)
                t2 = datetime.datetime.now()
                log.info("【Baostock】导入 证券清单 {c} 条数据，耗时{t}".format(
                    c=count["count_all"], t=(t2-t1)))
            return True
        except Exception as err:
            log.info("Baostock下载证券清单失败，错误原因 : {err}".format(err=err))
            return False


class CnStockDailyK:
    """ A股日K线 """

    def download_all(self, start_date=None, replace=False):
        """ 下载存量 """
        log = tl.get_logger()
        log.info("【Baostock】开始下载 A股日K线 数据")
        sql = ""
        gw = BaostockGateWay()

        try:
            with SQLiteDb() as db:
                # 取得全部的股票代码清单
                if replace:
                    sql = "select code from ods_baostock_stock_basic where type_id=1"
                else:
                    sql = "select code from ods_baostock_stock_basic where type_id=1 and code not in (select distinct code from ods_baostock_cnstock_k_d)"
                rs = db.query(sql)
                log.info("需要下载股票{0}支".format(len(rs)))

                stock_code_list = []
                for record in rs:
                    stock_code_list.append(record["code"])
                # print(stock_code_list)

                bs.login()
                for idx_stock, stock_code in enumerate(stock_code_list, 1):
                    rs = bs.query_history_k_data_plus(code=stock_code, fields=BaostockGateWay.FIELDS_DAY, frequency=BaostockGateWay.FRQ_DAY, adjustflag="3")

                    if rs.error_code == BaostockGateWay.RES_SUCCESS:
                        res_df = gw.rs_2_dataframe(rs)

                        if res_df is not None and res_df.shape[0] > 0:
                            # data clear
                            df = res_df[["date", "code", "open", "high", "low", "close", "preclose", "volume", "amount", "adjustflag", "turn", "tradestatus", "pctChg", "isST"]]
                            # delete
                            db.execute("delete from ods_baostock_cnstock_k_d where code='{code}'".format(code=stock_code))
                            # insert data
                            sql = "insert into ods_baostock_cnstock_k_d "
                            sql += " (trade_date, code, open, high, low, close, preclose, volume, amount, adjustflag, turn, tradestatus, pctChg, isST) "
                            sql += " values "
                            sql += " (?,?,?,?,?,?,?,?,?,?,?,?,?,?) "
                            db.execute_many(sql, df.to_records(index=False))

                            log.info("{0} : {1} {2}".format(idx_stock, stock_code, res_df.shape[0]))
                        else:
                            log.info("{0} : {1} is empty".format(idx_stock, stock_code))
                bs.logout()

                # 回显插入的股票数量
                count_stock = db.query_one("select count(distinct code) as count_all from ods_baostock_cnstock_k_d")["count_all"]
                log.info("共下载{0}支股票日K线数据".format(count_stock))

            return True
        except Exception as err:
            log.error("Baostock下载证券清单失败, 错误原因 : {err}".format(err=err))
            return False


def datasouce_stat():
    """ 统计数据刷新 """
    with SQLiteDb() as db:
        # 取得全部的股票代码清单
        id = "baostock.stock.daily_k"
        sql = "select min(distinct trade_date) as start_date, max(distinct trade_date) as end_date from ods_baostock_cnstock_k_d"
        rs = db.query_one(sql)
        start_date = rs["start_date"]
        end_date = rs["end_date"]

        if start_date is None:
            tl.get_logger().info("baostock股票K线表无数据")
            return
        else:
            sql = "delete from dwd_dtsrc_stat where data_source='{id}'".format(id=id)
            db.execute(sql)
            sql = "insert into dwd_dtsrc_stat (data_source, start_dt, end_dt, error_msg) values (?,?,?,?)"
            db.execute_many(sql, [(id, start_date, end_date, '')])
            tl.get_logger().info("baostock股票K线统计完成")
            return


if __name__ == "__main__":
    # # 股票清单
    # unit = SecurityListUnit()
    # res = unit.download_all(start_date=None)
    # print(res)

    # 股票日K线
    unit = CnStockDailyK()
    res = unit.download_all(replace=False)
    print(res)
