#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   __init__.py
@Time    :   2023/07/20 11:18:58
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   Akshare 数据服务
'''
from com.wdbd.feedme.fd.ds_akshare.ak_cal import AkTradeCal
from com.wdbd.feedme.fd.ds_akshare.ak_stock import AkCNStockList


def download_ak_cal():
    """下载Ak全量交易日历数据
    """
    srv = AkTradeCal()
    return srv.download()


def download_ak_stock_list():
    """下载更新Ak股票清单
    """
    srv = AkCNStockList()
    return srv.download()
