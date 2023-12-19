#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   test_server_utils.py
@Time    :   2023/12/18 09:07:14
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   测试 server.py 中工具类函数功能
'''
import unittest
import os
from com.wdbd.fd.collector.server import DTServer, ActionGroup, Action


class TestDRServer_GroupDefineFile(unittest.TestCase):

    def test_load_group_define_file(self):
        """ 测试 读取 动作组 配置文件 """
        server = DTServer()
        # 测试用配置文件
        THIS_PATH = os.path.dirname(os.path.realpath(__file__))
        group = server._load_group_define_file(
            os.path.join(THIS_PATH, "开发测试用.json"))
        self.assertIsInstance(group, ActionGroup)
        # check ActionGroup
        self.assertEqual("开发用组", group.name)
        self.assertEqual("关于这个组的说明", group.desc)
        self.assertEqual([], group.get_windows())
        # check Action
        actions = group.actions
        self.assertIsInstance(actions, dict)
        action = group.actions.get("Tushare_A股清单")
        self.assertIsInstance(action, Action)
        self.assertEqual("Tushare_A股清单", action.name)
        self.assertEqual("下载股票清单", action.desc)
        self.assertEqual([["1000", "1230"],
                          ["1600", "2000"]], action.get_windows())
        self.assertEqual(group, action.get_group())
        # 检查其他自定义参数
        self.assertEqual("abc", action.p.get("自定义1"))
        self.assertEqual(12345, action.p.get("自定义2"))

        # 默认路径情况
        res = server._load_group_define_file("tushare_daily.json")
        self.assertIsInstance(res, ActionGroup)

        # 件不存在情况
        res = server._load_group_define_file("akshare_daily.json")
        self.assertIsNone(res)
