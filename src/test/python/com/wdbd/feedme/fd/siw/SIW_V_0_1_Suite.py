#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   SIW_V_0_1_Suite.py
@Time    :   2023/06/09 17:42:59
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   SIW V0.1 单元测试
'''
import unittest


def get_suite():
    # 指定目录，指定文件
    # dis = unittest.defaultTestLoader.discover("src\\test\\python\\com\\wdbd\\feedme\\fd\\siw\\", "test_*.py")
    # suite = unittest.TestSuite(dis)
    # return suite
    loader = unittest.TestLoader()
    return loader.discover(start_dir="src\\test\\python\\com\\wdbd\\feedme\\fd\\siw\\", pattern="test_*.py")


if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(get_suite())

    # TODO 学习如何将日志输出到文本文件、HTML文件中
    # 文本文件
    # with open('UnittestTextReport.txt', 'a', encoding="UTF-8") as f:
    #     runner = unittest.TextTestRunner(stream=f, verbosity=2)
    #     runner.run(get_suite())
