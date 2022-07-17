#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   first_strategy.py
@Time    :   2022/07/05 21:33:32
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   第一个示例


'''
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import os
import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])
import pandas as pd
# Import the backtrader platform
import backtrader as bt


# 当前文件路径
data_file_dir = os.path.dirname(os.path.abspath(__file__))


# Create a Stratey
class TestStrategy(bt.Strategy):

    def log(self, txt, dt=None):
        ''' 记录日志 '''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.dataclose[0])


def run():
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    cerebro.addstrategy(TestStrategy)

    # Datas are in a subfolder of the samples. Need to find where the script is
    # because it could have been called from anywhere
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    datapath = os.path.join(modpath, r"dfqc.csv")
    dataframe = pd.read_csv(datapath, index_col=0, parse_dates=True)
    # Create a Data Feed
    data = bt.feeds.PandasData(dataname=dataframe, fromdate=datetime.datetime(2016, 12, 1), todate=datetime.datetime(2016, 12, 31))

    # Add the Data Feed to Cerebro
    cerebro.adddata(data)

    # Set our desired cash start
    cerebro.broker.setcash(100000.0)

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Run over everything
    cerebro.run()

    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())


if __name__ == "__main__":
    # print(os.path.dirname(os.path.abspath(__file__)))

    # modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    # print(os.path.join(modpath, r"dfqc.csv"))

    # print(os.path.exists(data_file_dir + r"\dfqc.csv"))
    run()
