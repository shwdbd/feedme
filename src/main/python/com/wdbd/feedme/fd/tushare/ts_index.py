#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   ts_index.py
@Time    :   2021/08/15 19:36:55
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   Tushare 指数数据下载单元

本模块中涉及内容包括：
- Ts指数基本信息
- Ts指数日线

'''
from gtp.fd.base.data_tools import TushareFixedDataUnit, TushareDailyDataUnit
from gtp.fd.datagateway.tushare_gateway import TushareGateWay
# from gtp.fd.base.base import DataUnitConfig
import gtp.fd.tools.mg_utils as mg_utils
import gtp.fd.common as tl
import gtp.fd.fdapi as fdapi


class TsIndexBasic(TushareFixedDataUnit):
    """ 指数基本信息 """

    def __init__(self, name, config):
        super().__init__(name=name, config=config, table_name="ts_index_basic",
                         fields_id="index_basic")

    def rebuild(self):
        # drop and create table
        tl.get_logger().info("重建【{label}】数据环境".format(label=self.name))
        index = [{"name": self.table_name+"_pk",
                  "fields": ["ts_code"], "unique": True}]
        return mg_utils.create_table(table_name=self.table_name, index=index)

    def load_data(self):
        """ 加载数据 """
        gw = TushareGateWay()
        self.data = gw.call(gw.api.index_basic,
                            fields=self.fields, return_type="dict")


class TsIndexDaily(TushareDailyDataUnit):
    """ 指数日线 """

    def __init__(self, name, config):
        super().__init__(name=name, config=config, table_name="ts_index_daily",
                         date_field="trade_date", fields_id="index_daily")

    def rebuild(self):
        """ 重构表结构 """
        index = [{"name": self.table_name+"_pk",
                  "fields": ["ts_code", "trade_date"], "unique": True}]
        index.append({"name": self.table_name+"_trade_date",
                      "fields": ["trade_date"], "unique": False})
        return mg_utils.create_table(table_name=self.table_name, index=index)

    def load_data(self, date):
        """ 加载数据 """
        gw = TushareGateWay()

        # 获取数据
        self.data = []
        index_list = fdapi.get_indexid_list()
        for index in index_list:
            record = gw.call(gw.api.index_daily, ts_code=index,
                             trade_date=date, fields=self.fields, return_type="dict")
            if record != []:
                self.data.append(record[0])
        print("数据加载完毕")


# if __name__ == "__main__":
#     # # 全量
#     # cfg = DataUnitConfig(name="指数信息")
#     # data_unit = TsIndexBasic(name="指数信息", config=cfg)
#     # # 重建表
#     # r = data_unit.rebuild()
#     # print("执行结果 = " + str(r))
#     # # 全量下载
#     # r = data_unit.download_all()
#     # print("执行结果 = " + str(r))
#     # # 增量下载
#     # r = data_unit.download_bydate(date="20210812")
#     # print("执行结果 = " + str(r))

#     # 增量
#     cfg = DataUnitConfig(name="指数日线")
#     data_unit = TsIndexDaily(name="指数日线", config=cfg)
#     # 重建表
#     r = data_unit.rebuild()
#     print("执行结果 = " + str(r))

#     # # 存量下载
#     # r = data_unit.download_all(from_date="20210811")
#     # print("执行结果 = " + str(r))

#     # 增量下载
#     r = data_unit.download_bydate(date="20210812")
#     print("执行结果 = " + str(r))
#     r = data_unit.query()
#     print("执行结果 = " + str(r))
