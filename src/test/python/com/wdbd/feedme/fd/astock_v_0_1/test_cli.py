#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   test_cli.py
@Time    :   2023/07/09 10:47:04
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   关于命令行接口的单元测试
'''
import unittest
from click.testing import CliRunner
import com.wdbd.feedme.fd.fd_cli as fd_cli


class TestAStockCLI(unittest.TestCase):
    """ 测试Astock工具 """

    def test_astock_dlall(self):
        """ 测试 下载历史存量数据 """
        runner = CliRunner()
        result = runner.invoke(fd_cli.cli, ['astock', 'dl-all', '-s', 'tushare',
                               '-i', 'list', '-d', '20210101', '-d2', '20231231'], terminal_width=60)
        self.assertEqual(0, result.exit_code)
        self.assertTrue("下载证券历史存量数据" in result.output)

    def test_astock_omit(self):
        """ 查询数据缺失情况 """
        runner = CliRunner()
        result = runner.invoke(fd_cli.cli, [
                               'astock', 'omit', '-s', 'tushare', '-d', '20210101', '-d2', '20231231'])
        self.assertEqual(0, result.exit_code)
        self.assertTrue("查询数据缺失情况" in result.output)

    def test_astock_check(self):
        """ 查询数据源之间数据冲突情况 """
        runner = CliRunner()
        result = runner.invoke(fd_cli.cli, [
                               'astock', 'check', '-s', 'tushare', '-d', '20210101', '-d2', '20231231'])
        self.assertEqual(0, result.exit_code)
        self.assertTrue("查询数据源之间数据冲突情况" in result.output)


# if __name__ == "__main__":
#     runner = CliRunner()
#     # result = runner.invoke(fd_cli.cli, ['astock', 'omit', '-d2', '9999000011'], terminal_width=60, input='20040822\n')
#     result = runner.invoke(fd_cli.cli, ['astock', 'dl-all', '-s', 'tushare',
#                            '-i', 'list', '-d', '20210101', '-d2', '20231231'], terminal_width=60)
#     print(result)
#     print(result.exit_code)
#     print(result.output)
