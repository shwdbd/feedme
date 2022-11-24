#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   ts_news.py
@Time    :   2021/08/16 06:53:45
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   Tushare新闻类数据下载单元

本模块中涉及内容包括：
- TsCCTV新闻

'''
from com.wdbd.feedme.fd.common.data_tools import TushareDailyDataUnit
from com.wdbd.feedme.fd.common.data_dateway import TushareGateWay
from gtp.fd.base.base import DataUnitConfig
import gtp.fd.tools.mg_utils as mg_utils


class TsCCTVNews(TushareDailyDataUnit):
    """ CCTV每日新闻 """

    def __init__(self, name, config):
        super().__init__(name=name, config=config, table_name="ts_cctv_news",
                         date_field="date", fields_id="cctv_news")

    def rebuild(self):
        # drop and create table
        index = [{"name": self.table_name+"_pk",
                  "fields": ["date"], "unique": False}]
        return mg_utils.create_table(table_name=self.table_name, index=index)

    def load_data(self, date):
        """ 加载数据 """
        gw = TushareGateWay()
        self.data = gw.call(callback=gw.api.cctv_news, date=date, fields=self.fields, return_type="dict")


# if __name__ == "__main__":
#     # 增量
#     cfg = DataUnitConfig(name="CCTV每日新闻")
#     data_unit = TsCCTVNews(name="CCTV每日新闻", config=cfg)
#     # 重建表
#     r = data_unit.rebuild()
#     print("执行结果 = " + str(r))

#     # 存量下载
#     r = data_unit.download_all(from_date="20210811")
#     print("执行结果 = " + str(r))

#     # 增量下载
#     r = data_unit.download_bydate(date="20210812")
#     print("执行结果 = " + str(r))
#     r = data_unit.query()
#     print("执行结果 = " + str(r))
