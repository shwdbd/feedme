#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   test_dt_model.py
@Time    :   2024/01/25 14:05:35
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   None
'''
import unittest
from com.wdbd.fd.model.dt_model import ActionGroup


class TestActionGroup(unittest.TestCase):

    def test_interval_time(self):
        """ 测试 interval_time 间隔时间的转换 """
        group = ActionGroup()
        self.assertEqual(30, group.get_interval_minutes())
        # 设置一个分钟
        group = ActionGroup()
        group.set_interval_minutes("15m")
        print(group.p)
        self.assertEqual(15, group.get_interval_minutes())
        # 设置一个小时
        group = ActionGroup()
        group.set_interval_minutes("2h")
        self.assertEqual(2*60, group.get_interval_minutes())
        # 设置10秒
        group = ActionGroup()
        group.set_interval_minutes("10s")
        self.assertEqual(10/60, group.get_interval_minutes())
        # 设置一个非法字符
        group = ActionGroup()
        group.set_interval_minutes("3x")
        self.assertEqual(30, group.get_interval_minutes())
