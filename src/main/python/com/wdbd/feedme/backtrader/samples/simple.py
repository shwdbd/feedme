#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   simple.py
@Time    :   2022/11/28 14:04:18
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   最简单的，加载每日K线，然后输出close价格的策略
'''
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import backtrader as bt
import tushare as ts
import pandas as pd
import datetime
from backtrader.feeds import PandasData
import os
import sys
import sqlite3


# 使用GenericCSVData读取csv文件
def get_csv_datafeed():
    # 使用GenericCSVData读取csv文件
    # Datas are in a subfolder of the samples. Need to find where the script is
    # because it could have been called from anywhere
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    datapath = os.path.join(modpath, r"dfqc.csv")
    data = bt.feeds.GenericCSVData(dataname=datapath,
                                   fromdate=datetime.datetime(2016, 12, 1),
                                   todate=datetime.datetime(2016, 12, 4),
                                   dtformat=('%Y-%m-%d'),
                                   datetime=0,
                                   openinterest=None,      # 指明无此列
                                   )
    return data


# csv文件，加一列PE
class GenericCSV_PE(bt.feeds.GenericCSVData):
    """ 增加一列PE的Datafeed """

    # Add a 'pe' line to the inherited ones from the base class
    lines = ('pe',)

    # openinterest in GenericCSVData has index 7 ... add 1
    # add the parameter to the parameters inherited from the base class
    params = (('pe', 6),)   # 第7列


# 使用GenericCSVData读取csv文件
def get_csv_pe():
    # 使用GenericCSVData读取csv文件
    # Datas are in a subfolder of the samples. Need to find where the script is
    # because it could have been called from anywhere
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    datapath = os.path.join(modpath, r"dfqc.csv")
    data = GenericCSV_PE(dataname=datapath,
                         fromdate=datetime.datetime(2016, 12, 1),
                         todate=datetime.datetime(2016, 12, 4),
                         dtformat=('%Y-%m-%d'),
                         datetime=0,
                         openinterest=None,      # 指明无此列
                         )
    return data


# 使用PandasData对象读取csv文件
def get_csv_pd_datafeed():
    # 使用PandasData对象读取csv文件
    # Datas are in a subfolder of the samples. Need to find where the script is
    # because it could have been called from anywhere
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    datapath = os.path.join(modpath, r"dfqc.csv")
    dataframe = pd.read_csv(datapath, index_col=0, parse_dates=True)
    # Create a Data Feed
    data = bt.feeds.PandasData(name="mystock",
                               dataname=dataframe,
                               fromdate=datetime.datetime(2016, 12, 1),
                               todate=datetime.datetime(2016, 12, 10),
                               open=1-1,
                               close=2-1,
                               high=3-1,
                               low=4-1,
                               )
    return data


def get_tushare_data(start="20200101", end="20200131"):
    # 从tushare在线读取数据

    stock_id = "000001.SZ"
    start = "20190101"
    end = "20190110"
    dt_start = datetime.datetime.strptime(start, "%Y%m%d")
    dt_end = datetime.datetime.strptime(end, "%Y%m%d")
    TOKEN = '341d66d4586929fa56f3f987e6c0d5bd23fb2a88f5a48b83904d134b'
    ts.set_token(TOKEN)
    pro = ts.pro_api()

    try:
        # 加载数据
        df = pro.daily(ts_code=stock_id, start_date=start, end_date=end)
        # 将日期列，设置成index
        df.index = pd.to_datetime(df.trade_date, format='%Y%m%d')
        print(df.head())
        data = PandasData(
            name="股票数据",
            dataname=df, fromdate=dt_start, todate=dt_end,
            # datatime=0,
            # open=3-1,
            # high=4-1
            close='close'
        )
        return data
    except Exception as err:
        print("下载{0}完毕失败！")
        print("失败原因 = " + str(err))


def get_db(start="20200101", end="20200131"):
    # 从本地sqlite3数据库读取数据

    stock_id = "000001.SZ"
    start = "20190101"
    end = "20190105"
    dt_start = datetime.datetime.strptime(start, "%Y%m%d")
    dt_end = datetime.datetime.strptime(end, "%Y%m%d")
    
    # 连接数据库
    conn = sqlite3.connect('C:\\fd_data\\db\\fd.db')
    df = pd.read_sql("select * from ods_tushare_daily where ts_code='600016.SH' and trade_date <='20190105' and trade_date>='20190101'", con=conn)
    # 将日期列，设置成index
    df.index = pd.to_datetime(df.trade_date, format='%Y%m%d')
    print(df.head())

    data = PandasData(
        name="股票数据",
        dataname=df, fromdate=dt_start, todate=dt_end,
        # datatime=1,
        # dtformat=('%Y%m%d'),
        open="p_open",
        high="p_high",
        close="p_close",
        low="p_low",
        volume=None,
        openinterest=None,
    )
    return data


def run():
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    cerebro.addstrategy(TestStrategy)

    # 获取数据集合
    # data = get_csv_pd_datafeed()      # 使用pandas读取csv文件
    # data = get_csv_datafeed()         # 直接读取csv文件
    # data = get_csv_pe()               # 直接读取csv文件，加一列自定义列
    # data = get_tushare_data()         # 使用pandas读取tushare在线api
    data = get_db()                     # 使用pandas读取本地数据库
    cerebro.adddata(data)

    # Set our desired cash start
    cerebro.broker.setcash(100000.0)

    # Print out the starting conditions
    print('初始账户资金: %.2f' % cerebro.broker.getvalue())

    # Run over everything
    cerebro.run()

    # Print out the final result
    print('最终账户资金: %.2f' % cerebro.broker.getvalue())


# 最简单的策略，打印每日的收盘价
class TestStrategy(bt.Strategy):

    def log(self, txt, dt=None):
        ''' 记录日志 '''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # dataclose是指向每日收盘价的变量
        self.dataclose = self.datas[0].close
        # self.pe = self.datas[0].pe

    def next(self):
        # 打印每期的收盘价
        self.log('Close, %.2f' % self.dataclose[0])
        # self.log('PE, %.2f' % self.pe[0])


if __name__ == '__main__':
    run()
    # get_db()
