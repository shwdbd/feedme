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
import pandas as pd


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
                sql_list = []
                for idx_stock, stock_code in enumerate(stock_code_list, 1):
                    rs = bs.query_history_k_data_plus(code=stock_code, fields=BaostockGateWay.FIELDS_DAY, frequency=BaostockGateWay.FRQ_DAY, adjustflag="3")
                    data_list = []
                    if rs.error_code == BaostockGateWay.RES_SUCCESS:
                        # TODO 将返回值变为dataframe的过程，可以抽象
                        while rs.next():
                            data_list.append(rs.get_row_data())
                        res_df = pd.DataFrame(data_list, columns=rs.fields)
                        # print(res_df.shape[0])

                        if res_df is not None and res_df.shape[0] > 0:
                            count_data = 0
                            sql_list.append(
                                "delete from ods_baostock_cnstock_k_d where code='{code}'".format(code=stock_code))
                            for index, row in res_df.iterrows():
                                sql = "insert into ods_baostock_cnstock_k_d "
                                sql += " (trade_date, code, open, high, low, close, preclose, volume, amount, adjustflag, turn, tradestatus, pctChg, isST) "
                                sql += " values "
                                sql += " ('{trade_date}', '{code}', {open}, {high}, {low}, {close}, {preclose}, '{volume}', '{amount}', '{adjustflag}', '{turn}', '{tradestatus}', '{pctChg}', '{isST}') ".format(
                                    trade_date=row['date'], code=row['code'], open=row['open'], high=row['high'], low=row['low'], close=row['close'], preclose=row['preclose'], volume=row['volume'],
                                    amount=row['amount'], adjustflag=row['adjustflag'], turn=row['turn'], tradestatus=row['tradestatus'], pctChg=row['pctChg'], isST=row['isST'])
                                # print(sql)
                                sql_list.append(sql)
                                count_data += 1
                            
                            idx_stock += 1
                            log.info("{0} : {1} {2}".format(idx_stock, stock_code, count_data))
                            
                            if (idx_stock % 50) == 1:
                                print(len(sql_list))
                                db.execute(sql_list)
                                sql_list = []
                            
                        else:
                            log.info("{0} : {1} is empty".format(idx_stock, stock_code))

                # TODO 可以设置一个参数，批量进行提交
                print(len(sql_list))
                db.execute(sql_list)
                # FIXME 使用executemany优化
                
                bs.logout()

            return True
        except Exception as err:
            print(sql)
            log.info("Baostock下载证券清单失败，错误原因 : {err}".format(err=err))
            return False


if __name__ == "__main__":
    # 股票清单
    unit = SecurityListUnit()
    res = unit.download_all(start_date=None)
    print(res)

    # # 股票日K线
    # unit = CnStockDailyK()
    # res = unit.download_all(replace=False)
    # print(res)
