#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   test_tushare.py
@Time    :   2023/07/20 10:43:58
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   测试Tushare数据源数据接口
'''
import unittest
import com.wdbd.feedme.fd.common.common as tl
from com.wdbd.feedme.fd.orm.ods_tables import OdsDsStat, OdsTushareDaily
from com.wdbd.feedme.fd.ds_tushare.ts_stock import TsStockDaily
from sqlalchemy import func


# Tushare日线数据
class TestTsDaily(unittest.TestCase):
    """ 测试 Tushare日线数据 数据下载 """

    def setUp(self) -> None:
        tl.TEST_MODE = True
        session = tl.get_session()
        session.query(OdsTushareDaily).delete()
        session.commit()
        session.close()
        return super().setUp()

    def test_download_by_date(self):
        """ 按日期下载 """
        record_count = 5219         # 下载后的记录数量
        trade_date = "20230719"
        srv = TsStockDaily()
        res = srv.download_by_date(trade_date=trade_date)
        msg = "按日下载Tushare股票日线数据完毕，共计{0}支股票".format(record_count)
        self.assertDictEqual({"result": True, "message": msg, 'data': []}, res)

        session = tl.get_session()
        # 检查表中记录数量
        record_count = session.query(func.count(OdsTushareDaily.trade_date)).scalar()
        self.assertEqual(record_count, record_count)
        # 检查 表中内容
        p_open = session.query(OdsTushareDaily.p_open).filter(OdsTushareDaily.ts_code == '836208.BJ').one_or_none()
        self.assertEqual(p_open[0], 31.5)
        # 检查统计表信息
        stat = session.query(OdsDsStat).filter(OdsDsStat.ds_id == 'tushare.daily').one_or_none()
        self.assertIsNotNone(stat)
        self.assertEqual(stat.ds_name, "tushareA股日线行情（未复权）")
        self.assertEqual(stat.start_bar, '')
        self.assertEqual(stat.end_bar, trade_date)
        self.assertEqual(stat.missing_bar, "")
        self.assertEqual(stat.notes, "")
        session.close()
