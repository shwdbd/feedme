#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   test_ak_cal.py
@Time    :   2022/12/09 23:37:48
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   测试下载Akshare交易日历数据
'''
import unittest
import com.wdbd.feedme.fd.common.common as tl
from com.wdbd.feedme.fd.orm.ods_tables import OdsAkshareTradeCal, OdsDsStat
from com.wdbd.feedme.fd.ds_akshare.ak_cal import AkTradeCal
from sqlalchemy import func


# 交易日历
class TestAkTradeCal(unittest.TestCase):
    """ 交易日历 数据下载 """

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
        msg = "下载完毕，{0}到{1} 共8070个交易日".format(first_date, end_date)
        self.assertDictEqual({"result": True, "msg": [msg]}, res)

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
