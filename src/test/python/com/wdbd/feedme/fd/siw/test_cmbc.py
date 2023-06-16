#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   test_cmbc.py
@Time    :   2023/06/02 10:22:09
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   测试CMBC民生银行财报解析
'''
import unittest
from com.wdbd.feedme.fd.siw.banks import CMBC


class TestCMBCExactor(unittest.TestCase):
    """ 解析民生银行财报 """

    file_dir = "src/test/python/com/wdbd/feedme/fd/siw/files/"

    def test_exactor_2022Annual(self):
        # 民生银行22年年报
        file_name = self.file_dir + 'SH600016 民生银行 2022年年报.pdf'
        bank = CMBC()
        res = bank.exact_pdf_file(file_name)
        self.assertIsNotNone(res)
        self.assertEqual(True, res["result"])
        self.assertEqual("", res["message"])
        # 股票信息：
        self.assertDictEqual({
            "id": "SH600016",
            "name": "民生银行",
            "fr_date": "2022年年报"
        }, res["stock"])

        # 指标
        index = res["index"]
        # 营收类
        self.assertEqual(35269*100*10000, index["净利润"])
        self.assertEqual(142476*100*10000, index["营业收入"])
        self.assertEqual(107463*100*10000, index["利息净收入"])
        self.assertEqual(35013*100*10000, index["非利息净收入"])
        self.assertEqual(35.61, index["成本收入比"])
        self.assertEqual(1.6, index["净息差"])
        self.assertEqual(7255673*100*10000, index["总资产"])
        self.assertEqual(13.14, index["资本充足率"])
        self.assertEqual(1.68, index["不良贷款率"])
        # 规模类
        self.assertEqual(6729776*100*10000, index["生息资产"])
        self.assertAlmostEqual((205071/6729776)*100,
                               index["同业资产占比"], delta=0.01)
        self.assertEqual(4111246*100*10000, index["贷款规模"])
        self.assertEqual(None, index["票据规模占比"])
        self.assertEqual(1780428*100*10000, index["证券投资规模"])
        self.assertEqual(6483550*100*10000, index["付息负债"])
        self.assertAlmostEquals((1238580/6483550)*100,
                                index["同业负债占比"], delta=0.01)
        self.assertEqual(4065038*100*10000, index["存款规模"])
        self.assertAlmostEquals((1149334/3153083)*100,
                                index["对公活期存款占比"], delta=0.01)
        self.assertAlmostEquals((258276/911955)*100,
                                index["活期储蓄占比"], delta=0.01)
        self.assertEqual(709281*100*10000, index["应付债券规模"])
        # 风险类
        self.assertEqual(69387*100*10000, index["不良贷款规模"])
        self.assertEqual(1.68, index["不良贷款率"])
        self.assertEqual(142.49, index["拨备覆盖率"])
        self.assertEqual(2.39, index["贷款拨备率"])
        # 监管类
        self.assertEqual(9.17, index["核心一级资本充足率"])
        self.assertEqual(10.91, index["一级资本充足率"])
        self.assertEqual(13.14, index["资本充足率"])

    def test_exactor_2022Q2(self):
        # 民生银行22年半年年报
        file_name = self.file_dir + 'SH600016 民生银行 2022年Q2.pdf'
        bank = CMBC()
        res = bank.exact_pdf_file(file_name)
        self.assertIsNotNone(res)
        self.assertEqual(True, res["result"])
        self.assertEqual("", res["message"])
        # 股票信息：
        self.assertDictEqual({
            "id": "SH600016",
            "name": "民生银行",
            "fr_date": "2022年Q2"
        }, res["stock"])

        # 指标
        index = res["index"]
        # 营收类
        self.assertEqual(24638*100*10000, index["净利润"])
        self.assertEqual(74199*100*10000, index["营业收入"])
        self.assertEqual(54823*100*10000, index["利息净收入"])
        self.assertEqual(19376*100*10000, index["非利息净收入"])
        self.assertEqual(28.39, index["成本收入比"])
        self.assertEqual(1.65, index["净息差"])
        self.assertEqual(7320580*100*10000, index["总资产"])
        self.assertEqual(13.21, index["资本充足率"])
        self.assertEqual(1.73, index["不良贷款率"])
        # 规模类
        self.assertEqual(6680156*100*10000, index["生息资产"])
        self.assertAlmostEqual((199485/6680156)*100,
                               index["同业资产占比"], delta=0.01)
        self.assertEqual(4108161*100*10000, index["贷款规模"])
        self.assertEqual(None, index["票据规模占比"])
        self.assertEqual(1747928*100*10000, index["证券投资规模"])
        self.assertEqual(6415641*100*10000, index["付息负债"])
        self.assertAlmostEquals((1280337/6415641)*100,
                                index["同业负债占比"], delta=0.01)
        self.assertEqual(3933146*100*10000, index["存款规模"])
        self.assertAlmostEquals((1151463/3057336)*100,
                                index["对公活期存款占比"], delta=0.01)
        self.assertAlmostEquals((249265/875810)*100,
                                index["活期储蓄占比"], delta=0.01)
        self.assertEqual(694100*100*10000, index["应付债券规模"])
        # 风险类
        self.assertEqual(72737*100*10000, index["不良贷款规模"])
        self.assertEqual(1.73, index["不良贷款率"])
        self.assertEqual(140.74, index["拨备覆盖率"])
        self.assertEqual(2.43, index["贷款拨备率"])
        # 监管类
        self.assertEqual(8.80, index["核心一级资本充足率"])
        self.assertEqual(10.49, index["一级资本充足率"])
        self.assertEqual(13.21, index["资本充足率"])

    def test_exactor_2021Annual(self):
        # 民生银行21年年报
        file_name = self.file_dir + 'SH600016 民生银行 2021年年报.pdf'
        bank = CMBC()
        res = bank.exact_pdf_file(file_name)
        self.assertIsNotNone(res)
        self.assertEqual(True, res["result"], res["message"])
        self.assertEqual("", res["message"])
        # 股票信息：
        self.assertDictEqual({
            "id": "SH600016",
            "name": "民生银行",
            "fr_date": "2021年年报"
        }, res["stock"])

        # 指标
        index = res["index"]
        # 营收类
        self.assertEqual(34381*100*10000, index["净利润"])
        self.assertEqual(168804*100*10000, index["营业收入"])
        self.assertEqual(125775*100*10000, index["利息净收入"])
        self.assertEqual(43029*100*10000, index["非利息净收入"])
        self.assertEqual(29.17, index["成本收入比"])
        self.assertEqual(1.91, index["净息差"])
        self.assertEqual(6952786*100*10000, index["总资产"])
        self.assertEqual(13.64, index["资本充足率"])
        self.assertEqual(1.79, index["不良贷款率"])
        # 规模类
        self.assertEqual(6595881*100*10000, index["生息资产"])
        self.assertAlmostEqual((255355/6595881)*100,
                               index["同业资产占比"], delta=0.01)
        self.assertEqual(3980156*100*10000, index["贷款规模"])
        self.assertEqual(None, index["票据规模占比"])
        self.assertEqual(1728164*100*10000, index["证券投资规模"])
        self.assertEqual(6339133*100*10000, index["付息负债"])
        self.assertAlmostEquals((1184169/6339133)*100,
                                index["同业负债占比"], delta=0.01)
        self.assertEqual(3833771*100*10000, index["存款规模"])
        self.assertAlmostEquals((1302112/3060358)*100,
                                index["对公活期存款占比"], delta=0.01)
        self.assertAlmostEquals((234099/773413)*100,
                                index["活期储蓄占比"], delta=0.01)
        self.assertEqual(749680*100*10000, index["应付债券规模"])
        # 风险类
        self.assertEqual(72338*100*10000, index["不良贷款规模"])
        self.assertEqual(1.79, index["不良贷款率"])
        self.assertEqual(145.30, index["拨备覆盖率"])
        self.assertEqual(2.60, index["贷款拨备率"])
        # 监管类
        self.assertEqual(9.04, index["核心一级资本充足率"])
        self.assertEqual(10.73, index["一级资本充足率"])
        self.assertEqual(13.64, index["资本充足率"])

    def test_exactor_2023Q1(self):
        # 民生银行21年年报
        file_name = self.file_dir + 'SH600016 民生银行 2023年Q1.pdf'
        bank = CMBC()
        res = bank.exact_pdf_file(file_name)
        self.assertIsNotNone(res)
        self.assertEqual(True, res["result"], res["message"])
        self.assertEqual("", res["message"])
        # 股票信息：
        self.assertDictEqual({
            "id": "SH600016",
            "name": "民生银行",
            "fr_date": "2023年Q1"
        }, res["stock"])

        # 指标
        index = res["index"]
        # 营收类
        self.assertEqual(14232*100*10000, index["净利润"])
        self.assertEqual(36773*100*10000, index["营业收入"])
        self.assertEqual(25369*100*10000, index["利息净收入"])
        self.assertEqual(None, index["非利息净收入"])
        self.assertEqual(26.95, index["成本收入比"])
        self.assertEqual(1.49, index["净息差"])
        self.assertEqual(7603107*100*10000, index["总资产"])
        self.assertEqual(12.80, index["资本充足率"])
        self.assertEqual(1.60, index["不良贷款率"])
        # 规模类
        self.assertIsNone(index["生息资产"])
        self.assertIsNone(index["同业资产占比"])
        self.assertIsNone(index["贷款规模"])
        self.assertIsNone(index["票据规模占比"])
        self.assertIsNone(index["证券投资规模"])
        self.assertIsNone(index["付息负债"])
        self.assertIsNone(index["同业负债占比"])
        self.assertIsNone(index["存款规模"])
        self.assertIsNone(index["对公活期存款占比"])
        self.assertIsNone(index["活期储蓄占比"])
        self.assertIsNone(index["应付债券规模"])
        # 风险类
        self.assertEqual(69268*100*10000, index["不良贷款规模"])
        self.assertEqual(1.60, index["不良贷款率"])
        self.assertEqual(144.11, index["拨备覆盖率"])
        self.assertEqual(2.30, index["贷款拨备率"])
        # 监管类
        self.assertEqual(9.04, index["核心一级资本充足率"])
        self.assertEqual(10.7, index["一级资本充足率"])
        self.assertEqual(12.80, index["资本充足率"])

    def test_error(self):
        file_name = 'xxxx.pdf'
        bank = CMBC()
        res = bank.exact_pdf_file(file_name)
        self.assertIsNotNone(res)
        self.assertEqual(False, res["result"])
