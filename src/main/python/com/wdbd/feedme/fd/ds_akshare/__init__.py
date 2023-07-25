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
from com.wdbd.feedme.fd.ds_akshare.ak_news import AkCCTVNews
from com.wdbd.feedme.fd.ds_akshare.ak_stock import AkCNStockList, AkStockDaily_EM


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


def download_ak_stock_daily_EM_all():
    """按日下载股票日线（东财）
    """
    srv = AkStockDaily_EM()
    # return srv.download_all(stockid_test='600016.SH')
    return srv.download_all()


def download_ak_stock_daily_EM_bydate(date: str, date2: str = None):
    """按日下载股票日线（东财）
    """
    srv = AkStockDaily_EM()
    return srv.download_by_date(date=date, date2=date2)


def download_ak_cctvnews():
    """下载全量新闻联播文字稿
    """
    srv = AkCCTVNews()
    return srv.download_all()


def download_ak_cctvnews_bydate(date):
    """下载全量新闻联播文字稿（按日）
    """
    srv = AkCCTVNews()
    return srv.download_bydate(date, is_log_stat=True)
