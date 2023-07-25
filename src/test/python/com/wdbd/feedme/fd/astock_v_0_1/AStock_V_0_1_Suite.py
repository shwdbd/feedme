#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   AStock_V_0_1_Suite.py
@Time    :   2023/07/07 13:49:01
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   AStock V0.1 单元测试套件
'''
import unittest
import com.wdbd.feedme.fd.common.common as tl


def get_suite():
    # 指定目录，指定文件
    loader = unittest.TestLoader()
    return loader.discover(start_dir="src\\test\\python\\com\\wdbd\\feedme\\fd\\astock_v_0_1\\", pattern="test_*.py")


if __name__ == "__main__":
    tl.TEST_MODE = True
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(get_suite())

    # 文本文件
    # with open('UnittestTextReport.txt', 'a', encoding="UTF-8") as f:
    #     runner = unittest.TextTestRunner(stream=f, verbosity=2)
    #     runner.run(get_suite())
