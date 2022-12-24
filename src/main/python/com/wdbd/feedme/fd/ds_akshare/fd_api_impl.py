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
from com.wdbd.feedme.fd.orm.ods_tables import OdsAkshareStock


def get_last_date() -> str:
    """取得当前最新的数据日期

    Returns:
        str: 日期,yyyyMMdd
    """
    # session = get_session()
    # res = session.query(OdsDsStat.end_bar).filter_by(ds_id='tushare.daily').one_or_none()
    # session.close()
    # if not res:
    #     return None
    # else:
    #     return res[0]
    # TODO 待实现
    return None


# 取得最早的数据日期
def get_eldly_date() -> str:
    """取得当前最早的数据日期

    Returns:
        str: 日期,yyyyMMdd
    """
    # session = get_session()
    # res = session.query(OdsTushareTradeCal.start_bar).filter_by(ds_id='tushare.daily').one_or_none()
    # session.close()
    # if not res:
    #     return None
    # else:
    #     return res[0]
    # TODO 待实现
    return None


# 是否交易日
def is_trade_date(date: str, exchange="SSE") -> bool:
    """是否交易日

    Args:
        date (str): 日期,yyyyMMdd
        exchange (str, optional): 交易所. Defaults to "SSE".

    Returns:
        bool: 是否交易日
    """
    # session = get_session()
    # res = session.query(OdsTushareTradeCal.is_open).filter_by(exchange=exchange, cal_date=date).one_or_none()
    # session.close()
    # if not res:
    #     return False
    # elif res[0] == '1':
    #     return True
    # else:
    #     return False
    # TODO 待实现
    return None


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
    # if item.lower() == 'daily':
    #     # 股票日线数据
    #     session = get_session()
    #     res = session.query(sqlalchemy.func.count(OdsTushareDaily.ts_code)).filter(OdsTushareDaily.trade_date == date).one_or_none()
    #     session.close()
    #     if res[0] > 0:
    #         return True
    #     else:
    #         return False
    # else:
    #     return False
    # TODO 待实现
    return None


def get_cal_info() -> dict:
    """ 查看交易日历信息

    返回一个dict，其内容有：
    start_date = yyyyMMdd
    end_date = yyyyMMdd
    exchange = ['SSE', ...]

    Returns:
        dict: 交易日历信息字典
    """
    # try:
    #     session = get_session()
    #     first_bar = session.query(sqlalchemy.func.min(OdsTushareTradeCal.cal_date)).scalar()
    #     last_bar = session.query(sqlalchemy.func.max(OdsTushareTradeCal.cal_date)).scalar()
    #     exchanges = session.query(sqlalchemy.distinct(OdsTushareTradeCal.exchange)).all()
    #     exchange_list = []
    #     for record in exchanges:
    #         exchange_list.append(record[0])
    #     res = {
    #         "start_date": first_bar,
    #         "end_date": last_bar,
    #         "exchange": exchange_list,
    #     }
    #     return res
    # except Exception as err:
    #     get_logger().error("查看交易日历信息，出现异常：" + str(err))
    #     return None
    # finally:
    #     session.close()
    # TODO 待实现
    return None


# 返回全部股票id
def get_stockid(return_type: str = "tushare", exchange: str = None, stock_status: str = None) -> list:
    """ 取得股票id列表

    股票上市状态无效，只能返回全部股票代码

    Args:
        exchange (str, optional): 指定交易所（SSE|SZE|BJE）. Defaults to None，默认是全部交易所.
        stock_status (str, optional): 股票上市状态，L上市 D退市 P暂停上市. Defaults to None，默认仅返.
        return_type (str, optional): 返回样式. Defaults to "tushare"，默认按tushare样式返回，即600016.SH.

    Returns:
        list<str>: 股票代码列表
    """
    # 从数据库表中读取全部
    # 如果参数中指定交易所，则加入判断
    # 如果返回格式为tushare，则进行转换
    # END
    log = get_logger()
    try:
        session = get_session()

        # 查询表
        quy = session.query(OdsAkshareStock.stock_id, OdsAkshareStock.exchange)
        if exchange:
            quy = quy.filter(OdsAkshareStock.exchange == exchange)
        records = quy.order_by(OdsAkshareStock.stock_id).all()

        if len(records) == 0:
            return []

        # 格式转变
        res = []
        for record in records:
            if return_type == 'symbol':
                res.append("{0}".format(record[0]))
            elif return_type == 'pre':
                # sh600016
                if record[1] == 'SSE':
                    exchange_name = "sh"
                elif record[1] == 'SZE':
                    exchange_name = "sz"
                elif record[1] == 'BJE':
                    exchange_name = "bj"
                else:
                    exchange_name = []
                res.append("{0}{1}".format(exchange_name, record[0]))
            else:
                # print(record)
                # if record[1] == 'SSE':
                #     exchange_name = "SH"
                # elif record[1] == 'SZE':
                #     exchange_name = "SZ"
                # elif record[1] == 'BJE':
                #     exchange_name = "BJ"
                # else:
                #     exchange_name = []
                # res.append("{0}.{1}".format(record[0], exchange_name))
                res.append("{0}".format(record[0]))
        return res
    except Exception as err:
        err_msg = "查询Akshare A股股票清单时遇到异常，SQL异常:" + str(err)
        log.error(err_msg)
        session.rollback()
        return []
    finally:
        session.close()


# if __name__ == "__main__":
# #     print(has_data("20181121"))
#     print(get_cal_info())

# if __name__ == "__main__":
#     print(get_stockid())
