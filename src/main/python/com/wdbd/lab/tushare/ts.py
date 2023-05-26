#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   ts.py
@Time    :   2023/03/14 21:53:35
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   tushare试验
'''
import tushare as ts
from com.wdbd.feedme.fd.common.data_gateway import TushareGateWay


# 股票清单
def get_stock_list():
    gw = TushareGateWay()
    # df = gw.call(gw.api.stock_basic, )
    df = gw.call(gw.api.stock_basic)
    return df["list_date"].min()


# 股票日线
def get_daily_k():
    # # 是否包括退市股票 日线？
    # # 4  000024.SZ  000024    招商地产(退)  None     None     主板  19930607
    # gw = TushareGateWay()
    # df = gw.call(gw.api.daily, trade_date='20230316', ts_code='000024.SZ')
    # return df.head()

    # # 是否包括 停牌 股票 日线？
    # # 0  603578.SH   20230316           None            S
    # gw = TushareGateWay()
    # df = gw.call(gw.api.daily, trade_date='20230316', ts_code='603578.SH')
    # # df = gw.call(gw.api.suspend_d, trade_date='20230316')
    # return df.head()

    # 最早的数据
    gw = TushareGateWay()
    df = gw.call(gw.api.daily, ts_code='000001.SZ')
    return df["trade_date"].min()


# 最早的日历日期
def find_eldest_cal_date():
    """最早的日历日期
    """
    gw = TushareGateWay()
    df = gw.call(gw.api.trade_cal)
    return df["trade_date"].min()


# 每日指标
def daily_basic():
    gw = TushareGateWay()
    df = gw.call(gw.api.daily_basic, exchange='SSE')
    return df["cal_date"].min()


if __name__ == "__main__":
    print(get_daily_k())
