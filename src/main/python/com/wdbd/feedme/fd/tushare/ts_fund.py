#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   ts_fund.py
@Time    :   2021/08/15 19:37:11
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   Tushare 公募基金数据下载单元

本模块中涉及内容包括：
- Ts公募基金基本信息
- Ts公募基金日线

'''
from gtp.fd.base.data_tools import TushareFixedDataUnit, TushareDailyDataUnit
from gtp.fd.datagateway.tushare_gateway import TushareGateWay
# from gtp.fd.base.base import DataUnitConfig
import gtp.fd.tools.mg_utils as mg_utils
import gtp.fd.common as tl


class TsFundBasic(TushareFixedDataUnit):
    """ 公募基金基本信息 """

    def __init__(self, name, config):
        super().__init__(name=name, config=config, table_name="ts_fund_basic",
                         fields_id="fund_basic")

    def rebuild(self):
        # drop and create table
        tl.get_logger().info("重建【{label}】数据环境".format(label=self.name))
        index = [{"name": self.table_name+"_pk", "fields": ["ts_code"], "unique": True}]
        return mg_utils.create_table(table_name=self.table_name, index=index)

    def load_data(self):
        """ 加载数据 """
        gw = TushareGateWay()
        self.data = gw.call(gw.api.fund_basic, fields=self.fields, return_type="dict")
        # 场内、场外分别读取
        data_o = gw.call(gw.api.fund_basic, fields=gw.get_fields("fund_basic"), market='O', return_type="dict")
        data_e = gw.call(gw.api.fund_basic, fields=gw.get_fields("fund_basic"), market='E', return_type="dict")
        self.data = data_o+data_e


class TsFundDaily(TushareDailyDataUnit):
    """ 公募基金日线 """

    def __init__(self, name, config):
        super().__init__(name=name, config=config, table_name="ts_fund_daily",
                         date_field="trade_date", fields_id="fund_daily")

    def rebuild(self):
        """ 重构表结构 """
        index = [{"name": self.table_name+"_pk", "fields": ["ts_code", "trade_date"], "unique": True}]
        return mg_utils.create_table(table_name=self.table_name, index=index)

    def load_data(self, date):
        """ 加载数据 """
        gw = TushareGateWay()
        self.data = gw.call(gw.api.fund_daily, trade_date=date, fields=self.fields, return_type="dict")


# if __name__ == "__main__":
#     # # 全量
#     # cfg = DataUnitConfig(name="公募基金信息")
#     # data_unit = TsFundBasic(name="公募基金信息", config=cfg)
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
#     cfg = DataUnitConfig(name="公募基金日线")
#     data_unit = TsFundDaily(name="公募基金日线", config=cfg)
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
