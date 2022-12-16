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
from com.wdbd.feedme.fd.common.common import get_logger, get_session, now
from com.wdbd.feedme.fd.orm.ods_tables import OdsAkshareTradeCal, OdsTushareTradeCal, OdsTushareStockBasic, OdsAkshareStock, OdsAkshareStockDaily_EM, OdsTushareDaily
import sqlalchemy
from sqlalchemy import func


# 执行比对
def do_compare(export_file: str = "export/数据比对结果.txt") -> None:
    """执行数据比对

    Args:
        export_file (str): 执行文件

    Returns:
        _type_: _description_
    """
    ENCODING = "utf-8"

    res_list = []

    # 核对日历
    res_list.append(compare_cal_ak_ts())
    # 股票清单
    res_list.append(compare_stocklist_ak_ts())

    _write_text_file(results=res_list, export_file=export_file, encoding=ENCODING)


def _write_text_file(results: list, export_file: str, encoding: str = "utf-8") -> None:
    """将核对结果，写入文本文件

    Args:
        results (list): 核对结果列表
        export_file (str): 输出文件路径
    Returns:
        _type_: _description_
    """
    log = get_logger()
    log.debug("结果导出到文件")
    with open(export_file, mode="w+", encoding=encoding) as f:
        f.writelines("核对时间：{0}\n".format(now()))
        count_success = 0
        count_fail = 0
        for r in results:
            if r["result"]:
                count_success += 1
            else:
                count_fail += 1
        f.writelines("核对项目：共核对{c}个项目，其中通过{s}项，有{f}项目存在问题。\n".format(c=len(results), s=count_success, f=count_fail))
        # 逐一项目输出
        for idx, res in enumerate(results, start=1):
            f.writelines("-" * 80 + "\n")
            f.writelines("【项目{id}/{count}】{name}\n".format(id=idx, count=len(results), name=res["name"]))
            f.writelines("核对结果：{r}\n".format(r=res["result"]))
            f.writelines("\n概要：\n")
            f.writelines("{summary}\n".format(summary=res["summary"]))
            f.writelines("\n详细信息({0})：\n".format(len(res["msg"])))
            for idx, item in enumerate(res["msg"], start=1):
                f.writelines("<{no}> {m}\n".format(no=idx, m=item))
            f.writelines("\n")
        f.writelines("END")
    log.debug("结果导出完毕")


# 返回空结果
def get_result(name: str = None):
    return {
        "result": True,
        "name": name,
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
    res = get_result("Ts、Ak 交易日历比对")
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
    res = get_result("Ts、Ak 股票清单比对")
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


# 比较Tushare和Akshare数据源的 股票日线数据
def compare_stock_daily_ak_ts():
    """比较Tushare和Akshare数据源的 股票日线数据
    """
    # 规则：
    # 1. 查看Ts中哪些交易日在AK中没有
    # 2. 查看Ak中哪些交易日在Ts中没有
    # 3. 找出Ts、Ak日期交集
    # 4. 顺序读取交集日期，同一日期逐个股票Ts与Ak进行对比
    # END
    log = get_logger()
    res = get_result("Ts、Ak 股票清单比对")
    try:
        session = get_session()

        # 查看Ts中哪些交易日在AK中没有
        is_count_same = False
        subquery_ts = session.query(OdsTushareDaily.trade_date)
        ts_lack_dates = session.query(OdsAkshareStockDaily_EM.trade_date).filter(OdsAkshareStockDaily_EM.trade_date.notin_(subquery_ts)).distinct().all()
        print(ts_lack_dates)
        
        # 查看Ak中哪些交易日在Ts中没有
        subquery_ak = session.query(OdsAkshareStockDaily_EM.trade_date)
        ak_lack_dates = session.query(OdsTushareDaily.trade_date).filter(OdsTushareDaily.trade_date.notin_(subquery_ak)).distinct().all()
        print(ak_lack_dates)
        
        # FIXME 两个数据集，格式不一样问题
        # 找出Ts、Ak日期交集
        # subquery_ak = session.query(OdsAkshareStockDaily_EM.trade_date).distinct()
        # dates = session.query(OdsTushareDaily.trade_date).filter(OdsTushareDaily.trade_date.in_(subquery_ak)).distinct().all()
        # print(dates)
        dates = ['20221209']
        
        for day in dates:
            print(day)
            ts_stocks = session.query(OdsTushareDaily).filter(OdsTushareDaily.trade_date ==  day).all()
            print(ts_stocks)
            # for stock in tss:
            #    find in aks
            #    比较，结果入msg
        
        # if count_tushare == count_akshare:
        #     is_count_same = True
        # else:
        #     is_count_same = False
        #     res["summary"] += "股票数量不同;"
        #     error_msg = "股票数量不同。Tushare股票{0}支，Akshare股票{1}支".format(
        #         count_tushare[0], count_akshare[0])
        #     res["msg"].append(error_msg)

        # is_lack = True
        # # 找出Ts有，Ak没有的股票
        # subquery_ak = session.query(OdsAkshareStock.stock_id)
        # diff_query = session.query(OdsTushareStockBasic.ts_code, OdsTushareStockBasic.name).filter(OdsTushareStockBasic.symbol.notin_(subquery_ak)).all()
        # if len(diff_query) > 0:
        #     is_lack = False
        #     res["summary"] += "Tushare有{0}支股票未在Akshare中;".format(len(diff_query))
        #     for record in diff_query:
        #         error_msg = "【Akshare缺】{id} {name}".format(id=record[0], name=record[1])
        #         res["msg"].append(error_msg)
        # # 找出Ak有，Ts没有的股票
        # subquery_ts = session.query(OdsTushareStockBasic.symbol)
        # diff_query = session.query(OdsAkshareStock.stock_id, OdsAkshareStock.name).filter(OdsAkshareStock.stock_id.notin_(subquery_ts)).all()
        # if len(diff_query) > 0:
        #     is_lack = False
        #     res["summary"] += "Akshare有{0}支股票未在Tushare中;".format(len(diff_query))
        #     for record in diff_query:
        #         error_msg = "【Tushare缺】{id} {name}".format(id=record[0], name=record[1])
        #         res["msg"].append(error_msg)

        # # 汇总结果
        # res["result"] = is_count_same & is_lack

        return res
    except Exception as err:
        err_msg = "比较Tushare和Akshare数据源时出现异常，SQL异常:" + str(err)
        log.error(err_msg)
        session.rollback()
        return res
    finally:
        session.close()



if __name__ == "__main__":
    res = compare_stock_daily_ak_ts()
    print(res)

# if __name__ == "__main__":
#     res = compare_cal_ak_ts()
#     print(res)

# if __name__ == "__main__":
#     res = compare_stocklist_ak_ts()
#     print(res)

# if __name__ == "__main__":
#     # r1 = get_result("项目A")
#     # r1["result"] = False
#     # r1["summary"] = "概要A"
#     # r1["msg"].append("第1行")
#     # r1["msg"].append("第2行")
#     # r2 = get_result("项目B")
#     # r2["result"] = True
#     # r2["summary"] = "概要B"
#     # r2["msg"].append("第1行")
#     # r2["msg"].append("第2行")
#     # res_list = [r1, r2]
#     # _write_text_file(res_list, export_file="export//核对结果.txt")
#     do_compare()
