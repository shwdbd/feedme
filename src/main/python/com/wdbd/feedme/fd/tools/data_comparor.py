#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   data_comparor.py
@Time    :   2022/07/27 10:10:51
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   数据比较器
'''
from com.wdbd.feedme.fd.common.common import SQLiteDb as SQLiteDb
from com.wdbd.feedme.fd.ds_baostock.bs_stock import datasouce_stat as bs_datasouce_stat
from com.wdbd.feedme.fd.ds_efinance.ef_stock import datasouce_stat as ef_datasouce_stat


def datasouce_stat():
    """数据源统计信息刷新
    """
    bs_datasouce_stat()
    ef_datasouce_stat()


def compare_bs_ef_stock_list():
    """比较 baostock、efinance的A股票清单

    Returns:
        bool, [msg]: 是否一致，差异清单(文字)
    """
    res = True
    message = []

    with SQLiteDb() as db:
        # 先比较数量
        count_bs = db.query_one("select count(*) as count_all from ods_baostock_stock_basic where type_id = 1")["count_all"]
        count_ef = db.query_one("select count(*) as count_all from ods_efinance_cnstock_list")["count_all"]
        if count_bs != count_ef:
            message.append("股票数量不一致,Baostock数量{0},efinance数量{1}".format(count_bs, count_ef))
            # 找出并集中的差异：
            msg = "efinance中有而不在baostock中有的股票,它们是: "
            sql = " select stock_id, stock_name from ods_efinance_cnstock_list "
            sql += " where stock_id not in ( "
            sql += " select substr(code, 4, 6) from ods_baostock_stock_basic where type_id = 1 "
            sql += " ) order by stock_id "
            rs = db.query(sql)
            for record in rs:
                msg += "{name}[{code}], ".format(name=record["stock_name"], code=record["stock_id"])
            message.append(msg)

            msg = "baostock中有而不在efinance中有的股票, 它们是: "
            sql = " select code, code_name from ods_baostock_stock_basic "
            sql += " where substr(code, 4, 6) not in (select stock_id from ods_efinance_cnstock_list) "
            sql += " and type_id = 1 "
            rs = db.query(sql)
            for record in rs:
                msg += "{name}[{code}], ".format(name=record["code_name"], code=record["code"])
            message.append(msg)

        # 比较股票价格差异
        sql = "select distinct trade_date from ods_efinance_cnstock_k_d order by trade_date desc limit 3"   # FIXME 去除limit
        rs = db.query(sql)
        for record in rs:
            print("比对{0}价格".format(record["trade_date"]))
            # print(record["trade_date"])
            sql = "select * from ods_efinance_cnstock_k_d where trade_date='{d}' order by stock_id".format(d=record["trade_date"])
            rs_ef_stock = db.query(sql)
            for row_ef_stock in rs_ef_stock:
                sql = "select * from ods_baostock_cnstock_k_d where trade_date='{d}' and substr(code, 4, 6)='{sid}'".format(d=record["trade_date"], sid=row_ef_stock["stock_id"])
                # print(sql)
                stock_bs = db.query_one(sql)
                # print(rs_bs_stock)
                # 比较
                if stock_bs is None:
                    print("股票{name}[{id}]，日期{d} baostock无数据".format(name=row_ef_stock["stock_name"], id=row_ef_stock["stock_id"], d=record["trade_date"]))
                elif ((stock_bs["open"] != row_ef_stock["open"]) or (stock_bs["high"] != row_ef_stock["high"])):
                    print("股票{name}[{id}]，日期{d}数据不一致".format(name=row_ef_stock["stock_name"], id=row_ef_stock["stock_id"], d=record["trade_date"]))
                    # TODO print都要改成message.append("xxx")

    # TODO 待实现

    # TODO 用s1比较s2
    # TODO 用s2比较s1

    if len(message) > 0:
        res = False
    return res, message


if __name__ == "__main__":
    # # 比较
    # res, msg = compare_bs_ef_stock_list()
    # print(res)
    # print(msg[0])

    # 数据统计
    datasouce_stat()
