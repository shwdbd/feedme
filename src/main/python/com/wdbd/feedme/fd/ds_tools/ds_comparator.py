#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   ds_comparator.py
@Time    :   2022/12/09 23:50:18
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   数据源比较器，提供一系列得数据源比较函数

返回值：
{
    "result": True/False,   比较结果
    "summary": str,         比较结果概要
    "msg": [str],           详细比较结果
}

'''
from com.wdbd.feedme.fd.common.common import get_logger, get_session
from com.wdbd.feedme.fd.orm.ods_tables import OdsAkshareTradeCal, OdsTushareTradeCal, OdsTushareStockBasic, OdsAkshareStock
import sqlalchemy
from sqlalchemy import func


# 返回空结果
def get_result():
    return {
        "result": True,
        "summary": "",
        "msg": []
    }


# 比较Tushare和Akshare数据源的 交易日历数据
def compare_cal_ak_ts():
    """ 比较Tushare和Akshare数据源的 交易日历数据 """
    # 规则：
    # 1. Akshare日期格式转成yyyyMMdd格式
    # 2. 先比较时间范围，注意Tushare中仅检查交易日范围
    # 3. 检查Ts中非交易日，在Ak中是否存在
    # 4. 检查Ts中交易日，是否在Ak中不存在
    # END
    log = get_logger()
    res = get_result()
    try:
        session = get_session()

        # 比较交易日期范围
        is_date_range_same = False
        # Tushare的交易日开始结束日期
        first_bar = session.query(sqlalchemy.func.min(OdsTushareTradeCal.cal_date)).filter(
            OdsTushareTradeCal.exchange == "SSE", OdsTushareTradeCal.is_open == "1").scalar()
        last_bar = session.query(sqlalchemy.func.max(OdsTushareTradeCal.cal_date)).filter(
            OdsTushareTradeCal.exchange == "SSE", OdsTushareTradeCal.is_open == "1").scalar()
        ts_cal = [first_bar, last_bar]
        # Akshare的交易日开始结束日期
        first_bar = session.query(sqlalchemy.func.min(
            sqlalchemy.func.replace(OdsAkshareTradeCal.trade_date, "-", ""))).scalar()
        last_bar = session.query(sqlalchemy.func.max(
            sqlalchemy.func.replace(OdsAkshareTradeCal.trade_date, "-", ""))).scalar()
        ak_cal = [first_bar, last_bar]
        if ts_cal == ak_cal:
            is_date_range_same = True
        else:
            is_date_range_same = False
            res["summary"] += "交易日范围不同;"
            error_msg = "交易日范围不同。Tushare的交易日范围是{0}，Akshare的交易日范围是{1}".format(
                ts_cal, ak_cal)
            res["msg"].append(error_msg)

        # 判断是否存在Tushare中是交易日，Akshare中不是交易日的情况
        is_diff_trade_date = False
        subquery_ak = session.query(sqlalchemy.func.replace(OdsAkshareTradeCal.trade_date, "-", "")
                                    ).distinct(sqlalchemy.func.replace(OdsAkshareTradeCal.trade_date, "-", ""))
        diff_query = session.query(OdsTushareTradeCal.cal_date).filter(OdsTushareTradeCal.is_open == '1').filter(
            OdsTushareTradeCal.exchange == 'SSE').filter(OdsTushareTradeCal.cal_date.notin_(subquery_ak)).all()
        if len(diff_query) > 0:
            is_diff_trade_date = False
            res["summary"] += "Ts中有{0}个交易日在Ak中为非交易日;".format(len(diff_query))
            for d in diff_query:
                error_msg = "日期{d}，Tushare是交易日，Akshare非交易日".format(d=d[0])
                res["msg"].append(error_msg)
        else:
            is_diff_trade_date = True

        # 汇总结果
        res["result"] = is_date_range_same & is_diff_trade_date

        return res
    except Exception as err:
        err_msg = "比较交易日历时出现异常，SQL异常:" + str(err)
        log.error(err_msg)
        session.rollback()
        return res
    finally:
        session.close()


# 比较Tushare和Akshare数据源的 股票清单数据
def compare_stocklist_ak_ts():
    """ 比较Tushare和Akshare数据源的 股票清单数据 """
    # 规则：
    # 1. 先比较股票数量
    # 2. 检查Ts中股票，是否都在Ak存在
    # 3. 检查Ak中股票，是否都在Ts存在
    # END
    log = get_logger()
    res = get_result()
    try:
        session = get_session()

        # 比较股票数量
        is_count_same = False
        count_tushare = session.query(func.count(OdsTushareStockBasic.ts_code)).one_or_none()
        count_akshare = session.query(func.count(OdsAkshareStock.stock_id)).one_or_none()
        if count_tushare == count_akshare:
            is_count_same = True
        else:
            is_count_same = False
            res["summary"] += "股票数量不同;"
            error_msg = "股票数量不同。Tushare股票{0}支，Akshare股票{1}支".format(
                count_tushare[0], count_akshare[0])
            res["msg"].append(error_msg)

        is_lack = True
        # 找出Ts有，Ak没有的股票
        subquery_ak = session.query(OdsAkshareStock.stock_id)
        diff_query = session.query(OdsTushareStockBasic.ts_code, OdsTushareStockBasic.name).filter(OdsTushareStockBasic.symbol.notin_(subquery_ak)).all()
        if len(diff_query) > 0:
            is_lack = False
            res["summary"] += "Tushare有{0}支股票未在Akshare中;".format(len(diff_query))
            for record in diff_query:
                error_msg = "【Akshare缺】{id} {name}".format(id=record[0], name=record[1])
                res["msg"].append(error_msg)
        # 找出Ak有，Ts没有的股票
        subquery_ts = session.query(OdsTushareStockBasic.symbol)
        diff_query = session.query(OdsAkshareStock.stock_id, OdsAkshareStock.name).filter(OdsAkshareStock.stock_id.notin_(subquery_ts)).all()
        if len(diff_query) > 0:
            is_lack = False
            res["summary"] += "Akshare有{0}支股票未在Tushare中;".format(len(diff_query))
            for record in diff_query:
                error_msg = "【Tushare缺】{id} {name}".format(id=record[0], name=record[1])
                res["msg"].append(error_msg)

        # 汇总结果
        res["result"] = is_count_same & is_lack

        return res
    except Exception as err:
        err_msg = "比较Tushare和Akshare数据源时出现异常，SQL异常:" + str(err)
        log.error(err_msg)
        session.rollback()
        return res
    finally:
        session.close()


# if __name__ == "__main__":
#     res = compare_cal_ak_ts()
#     print(res)

if __name__ == "__main__":
    res = compare_stocklist_ak_ts()
    print(res)
