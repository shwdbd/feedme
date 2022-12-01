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
