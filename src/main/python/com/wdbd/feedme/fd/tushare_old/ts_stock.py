#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   ts_stock.py
@Time    :   2021/08/15 11:35:45
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   Tushare A股数据下载单元

本模块中涉及内容包括：
- Ts股票清单
- Ts股票日线
- Ts股票每日指标

'''
from gtp.fd.base.data_tools import TushareFixedDataUnit, TushareDailyDataUnit
from gtp.fd.datagateway.tushare_gateway import TushareGateWay
from gtp.fd.base.base import DataUnitConfig
import gtp.fd.tools.mg_utils as mg_utils
import gtp.fd.common as tl


class TsStockBasic(TushareFixedDataUnit):
    """ 股票基本信息 """

    def __init__(self, name, config):
        super().__init__(name=name, config=config, table_name="ts_stock_basic",
                         fields_id="stock_basic")

    def rebuild(self):
        # drop and create table
        tl.get_logger().info("重建{label}数据环境".format(label=self.name))
        index = [{"name": self.table_name+"_pk", "fields": ["ts_code"], "unique": True}]
        return mg_utils.create_table(table_name=self.table_name, index=index)

    def load_data(self):
        """ 加载数据 """
        gw = TushareGateWay()
        self.data = gw.call(gw.api.stock_basic, fields=self.fields, return_type="dict")


class TsStockDaily(TushareDailyDataUnit):
    """ 股票日线数据 """

    def __init__(self, name, config):
        super().__init__(name=name, config=config, table_name="ts_stock_daily",
                         date_field="trade_date", fields_id="daily")

    def rebuild(self):
        # drop and create table
        tl.get_logger().info("重建{label}数据环境".format(label=self.name))
        index = [{"name": self.table_name+"_pk", "fields": ["ts_code", "trade_date"], "unique": True}]
        index.append({"name": self.table_name+"_trade_date", "fields": ["trade_date"], "unique": False})
        return mg_utils.create_table(table_name=self.table_name, index=index)

    def load_data(self, date):
        """ 加载数据 """
        gw = TushareGateWay()
        self.data = gw.call(gw.api.daily, trade_date=date, fields=self.fields, return_type="dict")


class TsStockDailyBasic(TushareDailyDataUnit):
    """ 股票每日指标 """

    def __init__(self, name, config):
        super().__init__(name=name, config=config, table_name="ts_stock_daily_basic",
                         date_field="trade_date", fields_id="daily_basic")

    def rebuild(self):
        """ 重构表结构 """
        index = [{"name": self.table_name+"_pk", "fields": ["ts_code", "trade_date"], "unique": True}]
        index.append({"name": self.table_name+"_trade_date", "fields": ["trade_date"], "unique": False})
        return mg_utils.create_table(table_name=self.table_name, index=index)

    def load_data(self, date):
        """ 加载数据 """
        gw = TushareGateWay()
        self.data = gw.call(gw.api.daily_basic, trade_date=date, fields=self.fields, return_type="dict")


if __name__ == "__main__":
    # # 全量
    # cfg = DataUnitConfig(name="股票信息")
    # data_unit = TsStockBasic(name="股票信息", config=cfg)
    # # # 重建表
    # # r = data_unit.rebuild()
    # # print("执行结果 = " + str(r))
    # # # 全量下载
    # # r = data_unit.download_all()
    # # print("执行结果 = " + str(r))
    # # 增量下载
    # r = data_unit.download_bydate(date="20210812")
    # print("执行结果 = " + str(r))

    # 增量
    cfg = DataUnitConfig(name="股票每日指标")
    data_unit = TsStockDailyBasic(name="股票每日指标", config=cfg)
    # 重建表
    r = data_unit.rebuild()
    print("执行结果 = " + str(r))

    # 全量下载
    r = data_unit.download_all(from_date="20210811")
    print("执行结果 = " + str(r))

    # # 增量下载
    # r = data_unit.download_bydate(date="20210812")
    # print("执行结果 = " + str(r))
    # r = data_unit.query()
    # print("执行结果 = " + str(r))
