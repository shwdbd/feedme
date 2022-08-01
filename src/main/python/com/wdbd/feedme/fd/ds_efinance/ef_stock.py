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


class SecurityListUnit:
    """ 证券清单下载 """

    def download_all(self, start_date=None):
        """ 全量下载 """
        log = tl.get_logger()
        t1 = datetime.datetime.now()
        log.info("【eFinance】开始下载 证券清单")

        try:
            gw = EFinanceGateWay()
            df = gw.call(callback=ef.stock.get_realtime_quotes)[['股票名称', "股票代码", '市场类型']]
            log.info("【eFinance】获得 证券清单 接口数据{0}条".format(df.shape[0]))

            with SQLiteDb() as db:
                sql = "delete from ods_efinance_cnstock_list"
                db.execute(sql)

                sql = "insert into ods_efinance_cnstock_list "
                sql += " (stock_name, stock_id, market) "
                sql += " values "
                sql += " (?, ?, ?) "
                db.execute_many(sql, df.to_records(index=False))

                sql = "select count(*) as count_all from ods_efinance_cnstock_list "
                count = db.query_one(sql)
                t2 = datetime.datetime.now()
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
                sql = "select stock_id from ods_efinance_cnstock_list limit 2"
                rs = db.query(sql)

                # 取得全部股票数量
                count_stock = db.query_one("select count(*) as count_all from ods_efinance_cnstock_list")['count_all']

                for idx_stock, record in enumerate(rs, 1):
                    code = record["stock_id"]
                    df = gw.call(callback=ef.stock.get_quote_history, stock_codes=code)
                    # 数据清洗
                    df.fillna(0, inplace=True)

                    # data clear
                    df = df[["股票名称", "股票代码", "日期", "开盘", "最高", "最低", "收盘", "成交量", "成交额", "振幅", "涨跌幅", "涨跌额", "换手率"]]
                    # delete
                    db.execute("delete from ods_efinance_cnstock_k_d where stock_id='{code}'".format(code=code))
                    # insert data
                    sql = "insert into ods_efinance_cnstock_k_d "
                    sql += " (stock_name, stock_id, trade_date, open, high, low, close, volume, amount, amp, pctChg, amtChg, turn) "
                    sql += " values "
                    sql += " (?,?,?,?,?,?,?,?,?,?,?,?,?) "
                    res = db.execute_many(sql, df.to_records(index=False))

                    if res:
                        log.info("{0}/{1} : {2} {3}".format(idx_stock, count_stock, code, df.shape[0]))
                    else:
                        log.info("{0}/{1} : {2} 下载失败".format(idx_stock, count_stock, code))

            log.info("全部股票日K线下载完成")
            return True
        except Exception as err:
            log.error("eFinance下载证券清单失败，错误原因 : {err}".format(err=err))
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
