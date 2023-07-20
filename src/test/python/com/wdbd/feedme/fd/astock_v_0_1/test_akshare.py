#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   test_akshare.py
@Time    :   2023/07/13 16:28:57
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   测试Akahare数据源的数据下载
'''
import unittest
import com.wdbd.feedme.fd.common.common as tl
from com.wdbd.feedme.fd.orm.ods_tables import OdsAkshareTradeCal, OdsDsStat, OdsAkshareStock
from com.wdbd.feedme.fd.ds_akshare.ak_cal import AkTradeCal
from com.wdbd.feedme.fd.ds_akshare.ak_stock import AkCNStockList
from sqlalchemy import func


# 交易日历
class TestAkTradeCal(unittest.TestCase):
    """ 测试 交易日历 数据下载 """

    def setUp(self) -> None:
        tl.TEST_MODE = True
        session = tl.get_session()
        session.query(OdsAkshareTradeCal).delete()
        session.commit()
        session.close()
        return super().setUp()

    def test_download_all(self):
        """ 下载全量 """
        first_date = "19901219"
        end_date = "20231229"
        srv = AkTradeCal()
        res = srv.download()
        msg = "下载Akshare日历全量数据完毕，{0}到{1} 共8070个交易日".format(first_date, end_date)
        self.assertDictEqual({"result": True, "message": msg, 'data': []}, res)

        session = tl.get_session()
        # 检查表中记录数量
        record_count = session.query(func.count(OdsAkshareTradeCal.trade_date)).scalar()
        self.assertEqual(8070, record_count)
        # 检查 表中内容
        trade_date = session.query(OdsAkshareTradeCal.trade_date).filter(OdsAkshareTradeCal.trade_date == '20221216').one_or_none()
        self.assertEqual("20221216", trade_date[0])
        # 检查统计表信息
        stat = session.query(OdsDsStat).filter(OdsDsStat.ds_id == 'akshare.cal').one_or_none()
        self.assertIsNotNone(stat)
        self.assertEqual(stat.ds_name, "Akshare交易日历")
        self.assertEqual(stat.start_bar, first_date)
        self.assertEqual(stat.end_bar, end_date)
        self.assertEqual(stat.missing_bar, "")
        self.assertEqual(stat.notes, "")
        session.close()


# 股票清单
class TestAkStockList(unittest.TestCase):
    """ 测试 交易日历 数据下载 """

    def setUp(self) -> None:
        tl.TEST_MODE = True
        session = tl.get_session()
        session.query(OdsAkshareStock).delete()
        session.commit()
        # 添加一条历史数据
        stock = OdsAkshareStock()
        stock.stock_id = '12345.CH'
        session.add(stock)
        session.close()
        return super().setUp()

    def test_download_all(self):
        """ 下载全量 """
        srv = AkCNStockList()
        res = srv.download()
        msg = "下载股票5475支，各交易所股票数量为：[('BJE', 210), ('SSE', 2334), ('SZE', 2931)]"
        self.assertDictEqual({"result": True, "message": msg, 'data': []}, res)

        session = tl.get_session()
        # 检查表中记录数量
        record_count = session.query(func.count(OdsAkshareStock.stock_id)).scalar()
        self.assertEqual(5475, record_count)
        # 检查 表中内容
        records = session.query(OdsAkshareStock.name).filter(OdsAkshareStock.stock_id == '600016.SH').one_or_none()
        self.assertEqual("民生银行", records[0])
        # 检查统计表信息
        stat = session.query(OdsDsStat).filter(OdsDsStat.ds_id == 'akshare.cnstock_list').one_or_none()
        self.assertIsNotNone(stat)
        self.assertEqual(stat.ds_name, "AkshareA股股票清单")
        self.assertEqual(stat.start_bar, '')
        self.assertEqual(stat.end_bar, tl.today())
        self.assertEqual(stat.missing_bar, "")
        self.assertEqual(stat.notes, "")
        session.close()
        
        # TODO 考虑增量下载，而不是仅仅是当日的数据

# TODO 测试日线数据全量下载

# TODO 测试日线数据增量下载

# TODO 测试日历缺失数据查询

# TODO 测试日线缺失数据查询

# TODO 测试股票清单全量下载


if __name__ == "__main__":
    pass

