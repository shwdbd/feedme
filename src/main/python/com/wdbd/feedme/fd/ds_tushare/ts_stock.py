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
from com.wdbd.feedme.fd.orm.ods_tables import OdsTushareTradeCal
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
        log.info("下载更新Tushare交易日历全量数据 [{0} : {1}]".format(start_date, end_date))

        # 交易所 SSE上交所,SZSE深交所,CFFEX 中金所,SHFE 上期所,CZCE 郑商所,DCE 大商所,INE 上能源
        exchanges = ['SSE', 'SZSE', 'CFFEX', 'SHFE', 'CZCE', ',DCE', ',INE']
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
        except Exception as err:
            log.error("SQL异常:" + str(err))
            session.rollback()
        finally:
            session.close()

        # 检查插入数据库记录是否与下载的记录数一致
        record_count = session.query(sqlalchemy.func.count(OdsTushareTradeCal.cal_date)).scalar()
        if record_count != df.shape[0]:
            err_msg = "存入数据库记录数量({0})不等于下载数据量({1})".format(record_count, df.shape[0])
            log.error(err_msg)
            return {"result": False, "msg": [err_msg]}

        # 更新统计表
        DsStatTool.log(id=self.DS_ID, end_bar=last_bar, start_bar=first_bar)

        log.info("下载更新完成")
        return {"result": True, "msg": []}


# A股股票清单
class TsStockList:
    """ A股股票清单 """

    # 全量下载更新
    def download(self):
        # TODO 待实现
        pass


# A股股票清单
class TsStockDaily:
    """ tushareA股日线行情（未复权） """

    # TODO tushare字段与数据库字段不一一匹配的问题

    # 按日期下载全部股票日线数据
    def download_by_date(self, trade_date: str):
        # TODO 待实现
        pass

    # 按股票下载全部历史数据
    def download_by_stock(self, ts_code: str, start_date: str = None, end_date: str = None):
        # TODO 待实现
        pass


# if __name__ == "__main__":
#     srv = TsTradeCal()
#     res = srv.download_all()
#     print(res)
