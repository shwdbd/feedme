#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   test_tools.py
@Time    :   2023/06/02 16:59:06
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   工具组 单元测试
'''
import unittest
from sqlalchemy import and_
from com.wdbd.feedme.fd.siw.tools import check_rpfile_format, get_stock_info, to_number, log as err_log, archive_file, save_to_db
import os
from com.wdbd.feedme.fd.common.common import get_cfg
import com.wdbd.feedme.fd.common.common as tl
from com.wdbd.feedme.fd.orm.ods_tables import OdsBankstockIndex, OdsBankstockFrHandleLog


class TestSIWTools(unittest.TestCase):
    """ 测试SIW公共工具类功能 """

    file_dir = "src/test/python/com/wdbd/feedme/fd/siw/files/"

    def setUp(self) -> None:
        tl.TEST_MODE = True
        # 初始化数据库
        session = tl.get_session()
        session.query(OdsBankstockIndex).delete()
        session.query(OdsBankstockFrHandleLog).delete()
        session.commit()
        session.close()

        return super().setUp()

    def tearDown(self) -> None:
        # 删除测试用文件
        folder = "dist/fd_siw_bak_folder/"
        files = ["SH600016 民生银行 2023年Q1.pdf"]
        for file in files:
            if os.path.exists(folder + file):
                os.remove(folder + file)
        # 重置数据库
        session = tl.get_session()
        session.query(OdsBankstockIndex).delete()
        session.query(OdsBankstockFrHandleLog).delete()
        session.commit()
        return super().tearDown()

    def test_check_rpfile_format(self):
        """ 测试 检查 财报文件名 是否符合要求 """
        # 正确
        self.assertTrue(check_rpfile_format("SH600016 民生银行 2023年Q1.pdf"))
        self.assertTrue(check_rpfile_format("SH600016 民生银行 2022年年报.pdf"))
        # 错误
        self.assertFalse(check_rpfile_format("600016 xx银行 2023年Q1.pdf"))
        self.assertFalse(check_rpfile_format(
            "SH600016 民生银行 2023年Q1"))     # 无文件后缀
        self.assertFalse(check_rpfile_format(
            "600016 民生银行 2023年Q1.pdf"))   # 无交易所缩写
        self.assertFalse(check_rpfile_format(""))
        self.assertFalse(check_rpfile_format(None))

    def test_get_stock_info(self):
        """ 测试  “根据文件名，解析股票代码、期数等信息”功能 """
        # 正确
        self.assertDictEqual({
            "id": "SH600016",
            "name": "民生银行",
            "fr_date": "2023年Q1",
        }, get_stock_info("SH600016 民生银行 2023年Q1.pdf"))
        self.assertDictEqual({
            "id": "SH600016",
            "name": "民生银行",
            "fr_date": "2022年年报",
        }, get_stock_info("SH600016 民生银行 2022年年报.pdf"))
        # 错误
        self.assertIsNone(get_stock_info(""))
        self.assertIsNone(get_stock_info(None))
        self.assertIsNone(get_stock_info("xxxxxYYYYY 21.pdf"))

    def test_to_number(self):
        """ 测试 把数字字符串转成数字 """
        self.assertEqual(123456.78*1000, to_number("123,456.78", unit="千"))
        self.assertEqual(123456.78*1000*1000,
                         to_number("123,456.78", unit="百万"))
        self.assertEqual(123456.78*10000*10000,
                         to_number("123,456.78", unit="亿"))

    def test_get_exception_logger(self):
        """ 检查 获取异常日志 """
        self.assertIsNotNone(err_log)

    def test_archive_file(self):
        """ 测试文件备份功能 """
        f = "SH600016 民生银行 2023年Q1.pdf"
        res = archive_file(self.file_dir + f)
        self.assertTrue(res)
        # 检查
        self.assertTrue(os.path.exists(
            get_cfg(section="fd.siw", key="bak_folder") + f))

    def test_save_to_db(self):
        """ 测试 添加指标数据到数据库 """
        data = {'result': True, 'message': '', 'index': {'营业收入': 142476000000.0, '利息净收入': 107463000000.0},
                'stock': {'id': 'SH600016', 'name': '民生银行', 'fr_date': '2022年年报'}}
        res = save_to_db(data)
        self.assertTrue(res)
        # 检查内容
        session = tl.get_session()
        index = session.query(OdsBankstockIndex).filter(and_(OdsBankstockIndex.stockid == 'SH600016', OdsBankstockIndex.index_id == '营业收入')
                                                        ).one_or_none()
        self.assertIsNotNone(index)
        self.assertEqual("民生银行", index.stock_name)
        self.assertEqual("2022年年报", index.fr_date)
        self.assertEqual("营业收入", index.index_id)
        self.assertEqual("营业收入", index.index_name)
        self.assertEqual(142476000000.0, index.index_value)
        session.commit()
        session.close()
