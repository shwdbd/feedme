#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   test_ak_cal.py
@Time    :   2022/12/09 23:37:48
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   测试下载Akshare股票数据
'''
import unittest
import com.wdbd.feedme.fd.common.common as tl
from com.wdbd.feedme.fd.orm.ods_tables import OdsAkshareStock, OdsDsStat
from com.wdbd.feedme.fd.ds_akshare.ak_stock import AkCNStockList
from sqlalchemy import func


# A股股票清单
class TestAkCNStockList(unittest.TestCase):
    """ A股股票清单 数据下载 """

    def setUp(self) -> None:
        tl.TEST_MODE = True
        session = tl.get_session()
        session.query(OdsAkshareStock).delete()
        session.commit()
        session.close()
        return super().setUp()

    def test_download(self):
        """ 下载全量 """
        srv = AkCNStockList()
        res = srv.download()
        self.assertTrue(res["result"])

        session = tl.get_session()
        # 检查表中记录数量
        record_count = session.query(func.count(OdsAkshareStock.stock_id)).scalar()
        self.assertTrue(record_count > 5000)
        # 检查统计表信息
        stat = session.query(OdsDsStat).filter(OdsDsStat.ds_id == 'akshare.cnstock_list').one_or_none()
        self.assertIsNotNone(stat)
        self.assertEqual(stat.ds_name, "AkshareA股股票清单")
        self.assertEqual(stat.start_bar, "")
        self.assertEqual(stat.end_bar, tl.today())
        self.assertEqual(stat.missing_bar, "")
        self.assertEqual(stat.notes, "")
        session.close()
