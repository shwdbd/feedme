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
from progress.bar import Bar


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
            bar = Bar('证券清单', max=(df.shape[0] / 100)+2)

            sql_list = []
            with SQLiteDb() as db:
                sql_list.append("delete from ods_baostock_stock_basic")
                for index, row in df.iterrows():
                    # print(row['code_name'])
                    sql = "insert into ods_baostock_stock_basic "
                    sql += " (code, code_name, ipoDate, outDate, type_id, status_id) "
                    sql += " values "
                    sql += " ('{code}', '{code_name}', '{ipoDate}', '{outDate}', '{type_id}', '{status_id}') ".format(
                        code=row['code'], code_name=row['code_name'], ipoDate=row['ipoDate'], outDate=row['outDate'], type_id=row['type'], status_id=row['status'])
                    sql_list.append(sql)
                    if (index) % 100 == 0:
                        bar.next()
                db.execute(sql_list)
                bar.next()

                sql = "select count(*) as count_all from ods_baostock_stock_basic "
                count = db.query_one(sql)
                t2 = datetime.datetime.now()
                print("\n")     # 跳过，更好的显示
                log.info("【Baostock】导入 证券清单 {c} 条数据，耗时{t}".format(
                    c=count["count_all"], t=(t2-t1)))
            return True
        except Exception as err:
            log.info("Baostock下载证券清单失败，错误原因 : {err}".format(err=err))
            return False


class CnStockDailyK:
    """ A股日K线 """

    def download_all(self, start_date=None):
        """ 下载存量 """
        log = tl.get_logger()
        log.info("【Baostock】开始下载 A股日K线 数据")
        sql = ""

        try:
            gw = BaostockGateWay()
            with SQLiteDb() as db:
                # 取得全部的股票代码清单
                sql = "select code from ods_baostock_stock_basic where type_id=1"
                rs = db.query(sql)

                idx_stock = 0
                for record in rs:
                    # print(row["code"])
                    sql_list = []
                    code = record["code"]
                    count_data = 0
                    df = gw.call(callback=bs.query_history_k_data_plus, code=code,
                                 fields=BaostockGateWay.FIELDS_DAY, frequency=BaostockGateWay.FRQ_DAY, adjustflag="3")
                    # 数据清洗
                    df.fillna(0, inplace=True)

                    sql_list.append(
                        "delete from ods_baostock_cnstock_k_d where code='{code}'".format(code=code))
                    for index, row in df.iterrows():
                        sql = "insert into ods_baostock_cnstock_k_d "
                        sql += " (trade_date, code, open, high, low, close, preclose, volume, amount, adjustflag, turn, tradestatus, pctChg, isST) "
                        sql += " values "
                        sql += " ('{trade_date}', '{code}', {open}, {high}, {low}, {close}, {preclose}, '{volume}', '{amount}', '{adjustflag}', '{turn}', '{tradestatus}', '{pctChg}', '{isST}') ".format(
                            trade_date=row['date'], code=row['code'], open=row['open'], high=row['high'], low=row['low'], close=row['close'], preclose=row['preclose'], volume=row['volume'],
                            amount=row['amount'], adjustflag=row['adjustflag'], turn=row['turn'], tradestatus=row['tradestatus'], pctChg=row['pctChg'], isST=row['isST'])
                        # print(sql)
                        sql_list.append(sql)
                        count_data += 1
                    db.execute(sql_list)
                    idx_stock += 1
                    log.info("{0} : {1} {2}".format(idx_stock, code, count_data))
            return True
        except Exception as err:
            print(sql)
            log.info("Baostock下载证券清单失败，错误原因 : {err}".format(err=err))
            return False


if __name__ == "__main__":
    # # 股票清单
    # unit = SecurityListUnit()
    # res = unit.download_all(start_date="20220101")
    # print(res)

    # 股票日K线
    unit = CnStockDailyK()
    res = unit.download_all()
    print(res)
