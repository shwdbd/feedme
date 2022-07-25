#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   ef_stock.py
@Time    :   2022/07/24 22:25:12
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   efinance 股票数据下载
'''
import efinance as ef
from com.wdbd.feedme.fd.common.data_gateway import EFinanceGateWay
import datetime
from com.wdbd.feedme.fd.common.common import SQLiteDb as SQLiteDb
import com.wdbd.feedme.fd.common.common as tl
from progress.bar import Bar


class SecurityListUnit:
    """ 证券清单下载 """

    def download_all(self, start_date=None):
        """ 全量下载 """
        log = tl.get_logger()
        t1 = datetime.datetime.now()
        log.info("【eFinance】开始下载 证券清单")

        try:
            gw = EFinanceGateWay()
            df = gw.call(callback=ef.stock.get_realtime_quotes)[["股票代码", '股票名称', '市场类型']]
            log.info("【eFinance】获得 证券清单 接口数据{0}条".format(df.shape[0]))
            bar = Bar('证券清单', max=(df.shape[0] / 100)+2)
            # print(df)

            sql_list = []
            with SQLiteDb() as db:
                sql_list.append("delete from ods_efinance_cnstock_list")
                for index, row in df.iterrows():
                    # print(row['code_name'])
                    sql = "insert into ods_efinance_cnstock_list "
                    sql += " (stock_name, stock_id, market) "
                    sql += " values "
                    sql += " ('{stock_name}', '{stock_id}', '{market}') ".format(
                        stock_name=row['股票名称'], stock_id=row['股票代码'], market=row['市场类型'])
                    sql_list.append(sql)
                    if (index) % 100 == 0:
                        bar.next()
                db.execute(sql_list)
                bar.next()

                sql = "select count(*) as count_all from ods_efinance_cnstock_list "
                count = db.query_one(sql)
                t2 = datetime.datetime.now()
                print("\n")     # 跳过，更好的显示
                log.info("【eFinance】导入 证券清单 {c} 条数据，耗时{t}".format(
                    c=count["count_all"], t=(t2-t1)))
            return True
        except Exception as err:
            log.info("eFinance下载证券清单失败，错误原因 : {err}".format(err=err))
            return False


class CnStockDailyK:
    """ A股日K线 """

    def download_all(self, start_date=None):
        """ 下载存量 """
        log = tl.get_logger()
        log.info("【eFinance】开始下载 A股日K线 数据")
        sql = ""

        try:
            gw = EFinanceGateWay()
            with SQLiteDb() as db:
                # 取得全部的股票代码清单
                sql = "select stock_id from ods_efinance_cnstock_list"
                rs = db.query(sql)

                # 取得全部股票数量
                count_stock = db.query_one("select count(*) as count_all from ods_efinance_cnstock_list")['count_all']

                idx_stock = 0
                for record in rs:
                    sql_list = []
                    code = record["stock_id"]
                    count_data = 0
                    df = gw.call(callback=ef.stock.get_quote_history, stock_codes=code)
                    # 数据清洗
                    df.fillna(0, inplace=True)

                    sql_list.append(
                        "delete from ods_efinance_cnstock_k_d where stock_id='{code}'".format(code=code))
                    for index, row in df.iterrows():
                        sql = "insert into ods_efinance_cnstock_k_d "
                        sql += " (stock_name, stock_id, trade_date, open, high, low, close, volume, amount, amp, pctChg, amtChg, turn) "
                        sql += " values "
                        sql += " ('{stock_name}','{stock_id}','{trade_date}', {open}, {high}, {low}, {close}, '{volume}', '{amount}', '{amp}', '{pctChg}', '{amtChg}', '{turn}') ".format(
                            stock_name=row['股票名称'], stock_id=row['股票代码'], trade_date=row['日期'], open=row['开盘'], high=row['最高'], low=row['最低'], close=row['收盘'], volume=row['成交量'],
                            amount=row['成交额'], amp=row['振幅'], turn=row['换手率'], pctChg=row['涨跌幅'], amtChg=row['涨跌额'])
                        # print(sql)
                        sql_list.append(sql)
                        count_data += 1
                    db.execute(sql_list)
                    idx_stock += 1
                    log.info("{0}/{1} : {2} {3}".format(idx_stock, count_stock, code, count_data))
            return True
        except Exception as err:
            print(sql)
            log.info("eFinance下载证券清单失败，错误原因 : {err}".format(err=err))
            return False


if __name__ == "__main__":
    # # 股票清单
    # unit = SecurityListUnit()
    # res = unit.download_all()
    # print(res)

    # 股票日k线
    unit = CnStockDailyK()
    res = unit.download_all()
    print(res)
