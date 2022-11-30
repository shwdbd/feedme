#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   ts_stock.py
@Time    :   2022/11/23 18:18:29
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   股票数据下载
'''
from com.wdbd.feedme.fd.common.data_gateway import TushareGateWay, DsStatTool
from com.wdbd.feedme.fd.ds_tushare.ts_ci import FIELDS
from com.wdbd.feedme.fd.common.common import records2objlist, get_session, get_logger
from com.wdbd.feedme.fd.orm.ods_tables import OdsTushareTradeCal, OdsTushareStockBasic, OdsTushareDaily
import pandas as pd
import sqlalchemy


# 交易所 交易日历
class TsTradeCal:
    """ 交易日历下载类 """

    def __init__(self):
        self.DS_ID = "tushare.trade_cal"    # 数据源ID

    def download_all(self, start_date: str = "19000101", end_date: str = "21001231") -> dict:
        """下载更新全部日历数据

        Args:
            start_date (str, optional): 开始日期（含）. Defaults to None.
            end_date (str, optional): 结束日期（含）. Defaults to None.

        Returns:
            dict: 执行情况 {"result": True, "msg": []}
        """
        # 1. 读取ts接口的dataframe，转成dict格式
        # 2. 每个dict，转成obj
        # 3. 依次写入数据库中（insert_or_update）
        log = get_logger()

        # 起始日期
        log.debug("下载更新Tushare交易日历全量数据 [{0} : {1}]".format(start_date, end_date))

        # 交易所 SSE上交所,SZSE深交所,CFFEX 中金所,SHFE 上期所,CZCE 郑商所,DCE 大商所,INE 上能源
        exchanges = ['SSE', 'SZSE', 'CFFEX', 'SHFE', 'CZCE', 'DCE', 'INE']
        log.debug("交易所: {0}".format(exchanges))

        gw = TushareGateWay()
        df_list = []
        for exchange in exchanges:
            df_e = gw.call(gw.api.trade_cal, exchange=exchange, start_date=start_date, end_date=end_date, fields=FIELDS["trade_cal"])
            df_list.append(df_e)
        df = pd.concat(df_list)
        log.debug("Tushare网关获取{0}条数据".format(df.shape[0]))
        # 数据清洗
        df.fillna(value="", inplace=True)
        obj_list = records2objlist(df, OdsTushareTradeCal)

        # 写入数据库
        try:
            session = get_session()
            session.query(OdsTushareTradeCal).delete()      # 清除表数据
            session.bulk_save_objects(obj_list)
            session.commit()
            first_bar = session.query(sqlalchemy.func.min(OdsTushareTradeCal.cal_date)).scalar()
            last_bar = session.query(sqlalchemy.func.max(OdsTushareTradeCal.cal_date)).scalar()

            # 检查插入数据库记录是否与下载的记录数一致
            record_count = session.query(sqlalchemy.func.count(OdsTushareTradeCal.cal_date)).scalar()
            if record_count != df.shape[0]:
                err_msg = "存入数据库记录数量({0})不等于下载数据量({1})".format(record_count, df.shape[0])
                log.error(err_msg)
                return {"result": False, "msg": [err_msg]}

            # 更新统计表
            DsStatTool.log(id=self.DS_ID, end_bar=last_bar, start_bar=first_bar)

            log.debug("下载更新完成")
            return {"result": True, "msg": []}
        except Exception as err:
            err_msg = "下载Tushare交易日历时遇到异常，SQL异常:" + str(err)
            log.error(err_msg)
            session.rollback()
            return {"result": False, "msg": [err_msg]}
        finally:
            session.close()


# A股股票清单
class TsStockList:
    """ A股股票清单 """

    def __init__(self) -> None:
        self.DS_ID = "tushare.stock_basic"

    # 全量下载更新
    def download(self):
        # 下载更新全量
        log = get_logger()

        # 起始日期
        log.debug("下载更新Tushare A股票清单全量数据")

        gw = TushareGateWay()
        df = gw.call(gw.api.stock_basic, fields=FIELDS["stock_basic"])
        log.debug("Tushare网关获取{0}条数据".format(df.shape[0]))
        # 数据清洗
        obj_list = records2objlist(df, OdsTushareStockBasic)

        # 写入数据库
        try:
            session = get_session()
            session.query(OdsTushareStockBasic).delete()      # 清除表数据
            session.bulk_save_objects(obj_list)
            session.commit()

            # 检查插入数据库记录是否与下载的记录数一致
            record_count = session.query(sqlalchemy.func.count(OdsTushareStockBasic.ts_code)).scalar()
            if record_count != df.shape[0]:
                err_msg = "存入数据库记录数量({0})不等于下载数据量({1})".format(record_count, df.shape[0])
                log.error(err_msg)
                return {"result": False, "msg": [err_msg]}

            # 更新统计表
            DsStatTool.log(id=self.DS_ID, end_bar="", start_bar="")

            log.debug("下载更新完成")
            return {"result": True, "msg": []}
        except Exception as err:
            err_msg = "下载Tushare A股清单时遇到异常，SQL异常:" + str(err)
            log.error(err_msg)
            session.rollback()
            return {"result": False, "msg": [err_msg]}
        finally:
            session.close()


# A股股票清单
class TsStockDaily:
    """ tushareA股日线行情（未复权） """

    def __init__(self) -> None:
        self.DS_ID = "tushare.daily"

    # 按日期下载全部股票日线数据
    def download_by_date(self, trade_date: str, stock_id: str = None):
        # 下载更新
        log = get_logger()
        if not trade_date:
            log.error("交易日期为空，下载终止！")
            return {"result": False, "msg": ["交易日期为空"]}

        log.debug("下载更新Tushare A股日线数据 [date={0}]".format(trade_date))

        gw = TushareGateWay()
        if stock_id:
            df = gw.call(gw.api.daily, fields=FIELDS["daily"], trade_date=trade_date, ts_code=stock_id)
        else:
            df = gw.call(gw.api.daily, fields=FIELDS["daily"], trade_date=trade_date)
        log.debug("Tushare网关获取{0}条数据".format(df.shape[0]))

        # 数据清洗(字段翻译)
        df.rename(columns={"open": "p_open",
                           "high": "p_high",
                           "low": "p_low",
                           "close": "p_close",
                           "change": "p_change"}, inplace=True)
        obj_list = records2objlist(df, OdsTushareDaily)

        if len(obj_list) == 0:
            err_msg = "当日未找到符合条件的数据, date={0}".format(trade_date)
            log.debug(err_msg)
            return {"result": False, "msg": [err_msg]}

        # 写入数据库
        try:
            session = get_session()
            session.query(OdsTushareDaily).filter(OdsTushareDaily.trade_date == trade_date).delete()      # 清除表数据
            session.bulk_save_objects(obj_list)
            session.commit()

            # 更新统计表
            DsStatTool.log(id=self.DS_ID, end_bar=trade_date)

            log.debug("下载更新完成")
            return {"result": True, "msg": []}
        except Exception as err:
            err_msg = "下载Tushare A股股票日线时遇到异常，SQL异常:" + str(err)
            log.error(err_msg)
            session.rollback()
            return {"result": False, "msg": [err_msg]}
        finally:
            session.close()

    # 按股票下载全部历史数据
    def download_by_stock(self, ts_code: str, trade_date: str = None, start_date: str = None, end_date: str = None):
        log = get_logger()

        log.debug("下载更新Tushare A股日线数据 [id={0}]".format(ts_code))

        gw = TushareGateWay()
        if trade_date:
            df = gw.call(gw.api.daily, fields=FIELDS["daily"], ts_code=ts_code, trade_date=trade_date)
        elif start_date:
            df = gw.call(gw.api.daily, fields=FIELDS["daily"], ts_code=ts_code, start_date=start_date, end_date=end_date)
        else:
            df = gw.call(gw.api.daily, fields=FIELDS["daily"], ts_code=ts_code)
        log.debug("Tushare网关获取{0}条数据".format(df.shape[0]))

        # 数据清洗(字段翻译)
        df.rename(columns={"open": "p_open",
                           "high": "p_high",
                           "low": "p_low",
                           "close": "p_close",
                           "change": "p_change"}, inplace=True)
        obj_list = records2objlist(df, OdsTushareDaily)

        if len(obj_list) == 0:
            err_msg = "当日未找到符合条件的数据, date={0}".format(trade_date)
            log.debug(err_msg)
            return {"result": False, "msg": [err_msg]}

        # 写入数据库
        try:
            session = get_session()
            session.query(OdsTushareDaily).filter(OdsTushareDaily.ts_code == ts_code).delete()      # 清除表数据
            # TODO 按条件删除
            session.bulk_save_objects(obj_list)
            session.commit()

            # 更新统计表
            DsStatTool.log(id=self.DS_ID, end_bar=trade_date)

            log.debug("下载更新完成")
            return {"result": True, "msg": []}
        except Exception as err:
            err_msg = "下载Tushare A股股票日线时遇到异常，SQL异常:" + str(err)
            log.error(err_msg)
            session.rollback()
            return {"result": False, "msg": [err_msg]}
        finally:
            session.close()

    # 下载全部历史数据
    def download_all(self, stockid_test: str = None) -> None:
        """ 下载全量历史数据

        Args:
            stockid_test (str, optional): 单元测试用股票id，如600016.SH. Defaults to None.
        """
        # 按股票清单，逐一股票下载
        log = get_logger()

        try:
            session = get_session()
            # 取得股票清单id列表
            if stockid_test:
                log.info("【单元测试】仅下载测试用股票：{0}".format(stockid_test))
                stocks = [(stockid_test, "测试股票名",)]
            else:
                stocks = session.query(OdsTushareStockBasic.ts_code, OdsTushareStockBasic.name).order_by(OdsTushareStockBasic.ts_code.desc()).all()      # 清除表数据
            count_of_stocks = len(stocks)
            log.info("共计有{0}支股票历史日线数据开始下载，请等待较长时间 ...".format(count_of_stocks))
            for idx, stock in enumerate(stocks, start=1):
                log.debug(stock)
                log.debug("{idx}/{all} {id}:{name}".format(idx=idx, all=count_of_stocks, id=stock[0], name=stock[1]))
                self.download_by_stock(ts_code=stock[0])

            # 统计信息记录
            first_bar = session.query(sqlalchemy.func.min(OdsTushareDaily.trade_date)).scalar()
            last_bar = session.query(sqlalchemy.func.max(OdsTushareDaily.trade_date)).scalar()
            DsStatTool.log(id=self.DS_ID, start_bar=first_bar, end_bar=last_bar)

            log.debug("全部下载完成！")
        except Exception as err:
            err_msg = "下载Tushare A股股票历史全量日线时遇到异常，SQL异常:" + str(err)
            log.error(err_msg)
            session.rollback()
        finally:
            session.close()


# if __name__ == "__main__":
#     # srv = TsStockList()
#     # srv.download()

#     srv = TsStockDaily()
#     res = srv.download_all()
#     print(res)

# if __name__ == "__main__":
#     srv = TsStockDaily()
#     res = srv.download_by_stock("600016.SH")
#     print(res)
