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
import os
from pathlib import Path
import com.wdbd.fd.common.tl as tl


class TestTLD2DBStr(unittest.TestCase):
    """ 测试d2dbstr函数 """

    def test_valid_date(self):
        """ 测试有效的日期字符串 """
        view_str = "2023-10-23"
        expected_result = "20231023"
        result = tl.d2dbstr(view_str)
        self.assertEqual(result, expected_result)

    def test_empty_string(self):
        """ 测试空字符串输入 """
        view_str = ""
        expected_result = ""
        result = tl.d2dbstr(view_str)
        self.assertEqual(result, expected_result)

    def test_invalid_date(self):
        """ 测试无效的日期字符串 """
        view_str = "2023-13-32"
        expected_result = view_str  # 错误则返回原值
        result = tl.d2dbstr(view_str)
        self.assertEqual(result, expected_result)

    def test_none_date(self):
        """ 测试None作为输入 """
        view_str = None
        expected_result = ""
        result = tl.d2dbstr(view_str)
        self.assertEqual(result, expected_result)


class TestTLConfigFile(unittest.TestCase):
    """ 测试配置文件工具类功能 """

    def setUp(self):
        tl.ENVIRONMENT = "test"

    # 测试配置文件工具类功能
    def test_get_cfg_valid_section_and_key(self):
        """ 测试有效的section和key """
        result = tl.get_cfg('Section1', 'key1')
        self.assertEqual(result, 'value1')

    def test_get_cfg_invalid_section(self):
        """ 测试无效的section """
        result = tl.get_cfg('NonExistentSection', 'key1')
        self.assertIsNone(result)

    def test_get_cfg_invalid_key(self):
        """ 测试无效的key """
        result = tl.get_cfg('Section1', 'nonExistentKey')
        self.assertIsNone(result)

    def test_get_cfg_exception(self):
        """ 测试当配置文件不存在时的情况 """
        result = tl.get_cfg('Section1', 'key1', config_file_path="error_file.cfg")
        self.assertIsNone(result)


class TestTLGetConfigDir(unittest.TestCase):
    """ 测试获取配置文件目录工具类功能 """

    def setUp(self) -> None:
        tl.ENVIRONMENT = "test"
        return super().setUp()

    def test_get_config_dir(self):
        """ 测试获取配置文件目录 """
        result = tl.get_config_dir()
        expected_result = os.path.join(Path().cwd(), "src/test/config/")
        self.assertEqual(result, expected_result)
        self.assertTrue(os.path.exists(tl.get_config_dir()))


class TestTLLogger(unittest.TestCase):
    """ 测试日志工具类功能  """

    def test_get_logger(self):
        """ 测试获取日志对象 """
        self.assertIsNotNone(tl.get_logger())

    def test_get_logger_test_mode(self):
        """ 测试获取日志对象 """
        tl.ENVIRONMENT = "test"
        self.assertIsNotNone(tl.get_logger())
        tl.ENVIRONMENT = ""


class TestTLDateConversion(unittest.TestCase):
    """测试日期转换工具类功能
    """

    def test_d2viewstr_valid_date(self):
        """ 测试有效的日期字符串 """
        db_str = "20230315"
        expected_view_str = "2023-03-15"
        result = tl.d2viewstr(db_str)
        self.assertEqual(result, expected_view_str)

    def test_d2viewstr_empty_string(self):
        """ 测试空字符串 """
        db_str = ""
        expected_view_str = ""
        result = tl.d2viewstr(db_str)
        self.assertEqual(result, expected_view_str)

    def test_d2viewstr_invalid_date(self):
        """ 测试无效的日期字符串 """
        db_str = "invalid_date"
        expected_view_str = ""
        result = tl.d2viewstr(db_str)
        self.assertEqual(result, expected_view_str)


if __name__ == "__main__":
    unittest.main()
