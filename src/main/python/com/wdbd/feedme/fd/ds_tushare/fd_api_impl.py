#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   fd_api_impl.py
@Time    :   2022/11/29 22:19:56
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   数据接口的Tushare实现
'''
from com.wdbd.feedme.fd.common.common import get_session
from com.wdbd.feedme.fd.orm.ods_tables import OdsDsStat, OdsTushareTradeCal, OdsTushareDaily
# import pandas as pd
import sqlalchemy


def get_last_date() -> str:
    """取得当前最新的数据日期

    Returns:
        str: 日期,yyyyMMdd
    """
    session = get_session()
    res = session.query(OdsDsStat.end_bar).filter_by(ds_id='tushare.daily').one_or_none()
    session.close()
    if not res:
        return None
    else:
        return res[0]


# 取得最早的数据日期
def get_eldly_date() -> str:
    """取得当前最早的数据日期

    Returns:
        str: 日期,yyyyMMdd
    """
    session = get_session()
    res = session.query(OdsTushareTradeCal.start_bar).filter_by(ds_id='tushare.daily').one_or_none()
    session.close()
    if not res:
        return None
    else:
        return res[0]


# 是否交易日
def is_trade_date(date: str, exchange="SSE") -> bool:
    """是否交易日

    Args:
        date (str): 日期,yyyyMMdd
        exchange (str, optional): 交易所. Defaults to "SSE".

    Returns:
        bool: 是否交易日
    """
    session = get_session()
    res = session.query(OdsTushareTradeCal.is_open).filter_by(exchange=exchange, cal_date=date).one_or_none()
    session.close()
    if not res:
        return False
    elif res[0] == '1':
        return True
    else:
        return False


def has_data(date: str, item: str = "daily", ds: str = "tushare") -> bool:
    """检查某日是否已有数据

    Args:
        date (str): 日期
        item (str, optional): 数据项目. Defaults to "daily".
        ds (str, optional): 数据源. Defaults to "tushare".

    Returns:
        bool: _description_
    """
    if item.lower() == 'daily':
        # 股票日线数据
        session = get_session()
        res = session.query(sqlalchemy.func.count(OdsTushareDaily.ts_code)).filter(OdsTushareDaily.trade_date == date).one_or_none()
        session.close()
        if res[0] > 0:
            return True
        else:
            return False
    else:
        return False


# if __name__ == "__main__":
#     print(has_data("20181121"))
