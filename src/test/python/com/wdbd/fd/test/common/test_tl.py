#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   test_tl.py
@Time    :   2024/04/19 09:35:46
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   测试TL通用工具类功能
'''
import unittest
import com.wdbd.fd.common.tl as tl


class TestTL_D2DBStr(unittest.TestCase):
    # 测试d2dbstr函数

    def test_valid_date(self):
        # 测试有效的日期字符串
        view_str = "2023-10-23"
        expected_result = "20231023"
        result = tl.d2dbstr(view_str)
        self.assertEqual(result, expected_result)

    def test_empty_string(self):
        # 测试空字符串输入
        view_str = ""
        expected_result = ""
        result = tl.d2dbstr(view_str)
        self.assertEqual(result, expected_result)

    def test_invalid_date(self):
        # 测试无效的日期字符串
        view_str = "2023-13-32"
        expected_result = view_str  # 错误则返回原值
        result = tl.d2dbstr(view_str)
        self.assertEqual(result, expected_result)

    def test_none_date(self):
        # 测试None作为输入
        view_str = None
        expected_result = ""
        result = tl.d2dbstr(view_str)
        self.assertEqual(result, expected_result)