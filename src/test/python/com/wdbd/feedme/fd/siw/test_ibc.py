#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   test_cmbc.py
@Time    :   2023/06/02 10:22:09
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   测试兴业银行财报解析
'''
import unittest
from com.wdbd.feedme.fd.siw.banks import IBC


# class TestICBCExactor(unittest.TestCase):
#     """ 解析兴业银行财报 """

#     file_dir = "src/test/python/com/wdbd/feedme/fd/siw/files/"

#     # 兴业银行22年年报
#     def test_exactor_2022Annual(self):
#         """ 兴业银行22年年报 """
#         file_name = self.file_dir + 'SH601398 兴业银行 2022年年报.pdf'
#         bank = ICBC()
#         res = bank.exact_pdf_file(file_name)
#         self.assertIsNotNone(res)
#         self.assertEqual(True, res["result"])
#         self.assertEqual("", res["message"])
#         # 股票信息：
#         self.assertDictEqual({
#             "id": "SH601398",
#             "name": "兴业银行",
#             "fr_date": "2022年年报"
#         }, res["stock"])

#         # 指标
#         index = res["index"]
#         # 营收类
#         self.assertEqual(360483*100*10000, index["净利润"])
#         self.assertEqual(917989*100*10000, index["营业收入"])
#         self.assertEqual(693687*100*10000, index["利息净收入"])
#         self.assertEqual(224302*100*10000, index["非利息净收入"])
#         self.assertEqual(25.01, index["成本收入比"])
#         self.assertEqual(1.73, index["净息差"])
#         self.assertEqual(39609657*100*10000, index["总资产"])
#         self.assertEqual(19.26, index["资本充足率"])
#         self.assertEqual(1.38, index["不良贷款率"])
#         # # 规模类
#         self.assertEqual(36108499*100*10000, index["生息资产"])
#         self.assertAlmostEqual((1866884/36108499)*100,
#                                index["同业资产占比"], delta=0.01)
#         self.assertEqual(22248094*100*10000, index["贷款规模"])
#         self.assertEqual(None, index["票据规模占比"])
#         self.assertEqual(9001876*100*10000, index["证券投资规模"])
#         self.assertEqual(32291926*100*10000, index["付息负债"])
#         self.assertAlmostEquals((3794532/32291926)*100,
#                                 index["同业负债占比"], delta=0.01)
#         self.assertEqual(27364627*100*10000, index["存款规模"])
#         self.assertAlmostEquals((7405878/13208952)*100,
#                                 index["对公活期存款占比"], delta=0.01)
#         self.assertAlmostEquals((5407007/13149079)*100,
#                                 index["活期储蓄占比"], delta=0.01)
#         self.assertEqual(1132767*100*10000, index["应付债券规模"])

#         # 风险类
#         self.assertEqual(321170*100*10000, index["不良贷款规模"])
#         self.assertEqual(1.38, index["不良率"])
#         self.assertEqual(209.47, index["拨备覆盖率"])
#         self.assertEqual(2.90, index["贷款拨备率"])
#         # 监管类
#         self.assertEqual(14.04, index["核心一级资本充足率"])
#         self.assertEqual(15.64, index["一级资本充足率"])
#         self.assertEqual(19.26, index["资本充足率"])

#     # 兴业银行21年年报
#     def test_exactor_2021Annual(self):
#         """ 兴业银行21年年报 """
#         file_name = self.file_dir + 'SH601398 兴业银行 2021年年报.pdf'
#         bank = ICBC()
#         res = bank.exact_pdf_file(file_name)
#         self.assertIsNotNone(res)
#         self.assertEqual(True, res["result"], res["message"])
#         self.assertEqual("", res["message"])
#         # 股票信息：
#         self.assertDictEqual({
#             "id": "SH601398",
#             "name": "兴业银行",
#             "fr_date": "2021年年报"
#         }, res["stock"])

#         # 指标
#         index_keys = ['利息净收入', '营业收入', '净利润', '总资产', '净息差', '成本收入比', '不良贷款率', '不良率', '拨备覆盖率', '贷款拨备率', '核心一级资本充足率', '一级资本充足率', '资本充足率',
#                       '非利息净收入', '贷款规模', '证券投资规模', '同业资产占比', '生息资产', '存款规模', '同业负债占比', '应付债券规模', '付息负债', '票据规模占比', '对公活期存款占比', '活期储蓄占比', '不良贷款规模']
#         index_keys.sort()
#         index_names = list(res["index"].keys())
#         index_names.sort()
#         self.assertListEqual(index_keys, index_names)

#     def test_error(self):
#         file_name = 'xxxx.pdf'
#         bank = ICBC()
#         res = bank.exact_pdf_file(file_name)
#         self.assertIsNotNone(res)
#         self.assertEqual(False, res["result"])
