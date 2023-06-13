#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   test_fr_exactor.py
@Time    :   2023/06/05 22:13:19
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   测试 财报读取器
'''
import unittest
from com.wdbd.feedme.fd.siw import FinanceReportExactor
import com.wdbd.feedme.fd.common.common as tl
from com.wdbd.feedme.fd.orm.ods_tables import OdsBankstockIndex, OdsBankstockFrHandleLog
import os
from sqlalchemy import and_


class TestFrExactor(unittest.TestCase):
    """ 测试财报读取器功能 """

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

    def test_load_by_file(self):
        """ 测试读取指定文件 """
        # 测试正确情况
        file_name = self.file_dir + 'SH600016 民生银行 2022年年报.pdf'
        srv = FinanceReportExactor()
        res = srv.load_by_file(file_name)
        self.assertIsNotNone(res)
        # 检查返回值
        print(res)
        self.assertTrue(res["result"])
        self.assertEqual("", res["message"])
        self.assertIsNotNone(res["stock"])  # 股票信息
        self.assertEqual("SH600016", res["stock"]["id"])
        self.assertEqual("民生银行", res["stock"]["name"])
        self.assertEqual("2022年年报", res["stock"]["fr_date"])
        # 检查股票指标
        self.assertIsNotNone(res["index"])
        # 检查备份文件
        self.assertTrue(os.path.exists(
            tl.get_cfg(section="fd.siw", key="bak_folder") + 'SH600016 民生银行 2022年年报.pdf'))
        # 检查数据库
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

        # 测试错误情况
        # 情况1，文件不存在
        res = srv.load_by_file(None)
        self.assertIsNotNone(res)
        self.assertDictEqual({'result': False, 'message': '文件不存在！None'}, res)
        file_name = 'xxxx.pdf'
        res = srv.load_by_file(file_name)
        self.assertIsNotNone(res)
        self.assertDictEqual({'result': False, 'message': '文件不存在！xxxx.pdf'}, res)
        # 情况2，文件错误（使用其他银行文件）
        file_name = self.file_dir + "SH999999 XX银行 2022年年报.pdf"
        res = srv.load_by_file(file_name)
        self.assertIsNotNone(res)
        self.assertDictEqual({'result': False, 'message': '未知银行,XX银行'}, res)


if __name__ == "__main__":
    unittest.main(verbosity=2)
