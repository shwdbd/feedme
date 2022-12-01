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
from com.wdbd.feedme.fd.common.common import get_session, get_logger
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


# 检查某日是否已有数据
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


def get_cal_info() -> dict:
    """ 查看交易日历信息

    返回一个dict，其内容有：
    start_date = yyyyMMdd
    end_date = yyyyMMdd
    exchange = ['SSE', ...]

    Returns:
        dict: 交易日历信息字典
    """
    try:
        session = get_session()
        first_bar = session.query(sqlalchemy.func.min(OdsTushareTradeCal.cal_date)).scalar()
        last_bar = session.query(sqlalchemy.func.max(OdsTushareTradeCal.cal_date)).scalar()
        exchanges = session.query(sqlalchemy.distinct(OdsTushareTradeCal.exchange)).all()
        exchange_list = []
        for record in exchanges:
            exchange_list.append(record[0])
        res = {
            "start_date": first_bar,
            "end_date": last_bar,
            "exchange": exchange_list,
        }
        return res
    except Exception as err:
        get_logger().error("查看交易日历信息，出现异常：" + str(err))
        return None
    finally:
        session.close()


# if __name__ == "__main__":
# #     print(has_data("20181121"))
#     print(get_cal_info())
