#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   fd_api.py
@Time    :   2022/11/29 22:18:15
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   数据查询API接口
'''
import com.wdbd.feedme.fd.ds_tushare.fd_api_impl as tushare_impl
import com.wdbd.feedme.fd.ds_akshare.fd_api_impl as akshare_impl
import com.wdbd.feedme.fd.common.common as tl


# 当前最新的数据日期
def get_last_date() -> str:
    """取得当前最新的数据日期

    Returns:
        str: 日期,yyyyMMdd
    """
    return tushare_impl.get_last_date()


# 取得最早的数据日期
def get_eldly_date() -> str:
    """取得当前最早的数据日期

    Returns:
        str: 日期,yyyyMMdd
    """
    return tushare_impl.get_eldly_date()


# 判断是否交易日
def is_trade_date(date: str, exchange="SSE") -> bool:
    """是否交易日

    Args:
        date (str): 日期,yyyyMMdd
        exchange (str, optional): 交易所. Defaults to "SSE".

    Returns:
        bool: 是否交易日
    """
    return tushare_impl.is_trade_date(date, exchange)


# 判断某日是否已有数据
def has_data(date: str, item: str = "daily", ds: str = "tushare") -> bool:
    """检查某日是否已有数据

    Args:
        date (str): 日期
        item (str, optional): 数据项目. Defaults to "daily".
        ds (str, optional): 数据源. Defaults to "tushare".

    Returns:
        bool: _description_
    """
    if ds.lower() == 'tushare':
        return tushare_impl.has_data(date, item, ds)
    else:
        return False


# 查看交易日历信息
def get_cal_info() -> dict:
    """ 查看交易日历信息

    返回一个dict，其内容有：
    start_date = yyyyMMdd
    end_date = yyyyMMdd
    exchange = ['SSE', ...]

    Returns:
        dict: 交易日历信息字典
    """
    return tushare_impl.get_cal_info()


# 返回全部股票id
def get_stockid(return_type: str = "tushare", exchange: str = None, stock_status: str = None) -> list:
    """ 取得股票id列表

    Args:
        exchange (str, optional): 指定交易所（SSE|SZE|BJE）. Defaults to None，默认是全部交易所.
        stock_status (str, optional): 股票上市状态，L上市 D退市 P暂停上市. Defaults to None，默认仅返.
        return_type (str, optional): 返回样式. Defaults to "tushare"，默认按tushare样式返回，即600016.SH.

    Returns:
        list<str>: 股票代码列表
    """
    return akshare_impl.get_stockid(return_type, exchange, stock_status)


# 返回日期范围
def get_dates(start: str = None, is_trade_date_only: bool = True, end: str = tl.today(), source: str = "akshare") -> list:
    """返回日期范围

    Args:
        start (str, optional): 开始日期，默认为最早日期
        is_trade_date_only (bool, optional): 是否仅返回交易日？ Defaults to True.
        end (str, optional): 截止日期. Defaults to 今日.
        source (str, optional): 数据源. Defaults to "akshare".

    Returns:
        list: _description_
    """
    if source.lower() == 'akshare':
        return akshare_impl.get_dates(start=start, is_trade_date_only=is_trade_date_only, end=end, source=source)
    return []
