#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   test_mgutils_json2db.py
@Time    :   2021/06/15 13:58:11
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   针对mg_utils中数据库表与json文件互转功能单元测试
'''
# import unittest
# import gtp.fd.tools.mg_utils as mg_utils
# import os
# import json


# class TestMgUtils_Db2Json(unittest.TestCase):
#     """ 测试从mongodb转到json功能 """

#     def setUp(self):
#         # 明确测试文件
#         self.data_file = "test/gtp_fd/commons/test_mgutils_json2db_data.json"
#         self.exp_file = "test/gtp_fd/commons/export.json"
#         mg_utils.clear("ts_stock_daily")
#         # 导入测试数据
#         mg_utils.json2db(json_file_path=self.data_file,
#                          collection_name="ts_stock_daily")
#         return super().setUp()

#     def tearDown(self):
#         mg_utils.clear("ts_stock_daily")
#         os.remove(self.exp_file)
#         return super().tearDown()

#     def test_db2json(self):
#         """ 测试从数据库中导出数据 """
#         where_sql = {"$and": [{"ts_code": "600016.SH"}, {"trade_date": {
#             '$gte': '20210101'}}, {"trade_date": {'$lte': '20210131'}}]}
#         json_file_path = self.exp_file
#         res = mg_utils.db2json(collection_name="ts_stock_daily",
#                                where_sql=where_sql, json_file_path=json_file_path)
#         self.assertTrue(res)
#         self.assertTrue(os.path.exists(self.exp_file))
#         with open(json_file_path, encoding='utf-8') as f:
#             json_obj = json.loads(f.read())
#             self.assertEqual(20, len(json_obj))
