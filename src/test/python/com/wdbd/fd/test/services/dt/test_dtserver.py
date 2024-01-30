#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   test_dtserver.py
@Time    :   2024/01/25 14:22:06
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   None
'''
import unittest
from com.wdbd.fd.services.dt.server import BasicEngine, ServerUtils
from com.wdbd.fd.model.dt_model import ActionGroup, ActionConfig
from com.wdbd.fd.model.db import get_engine, table_objects_pool as DB_POOL


class TestActionGroupRunning(unittest.TestCase):
    """ 测试ActionGroup单个线程的执行流程 """

    def setUp(self) -> None:
        self.engine = get_engine()
        t_group_log = DB_POOL.get("comm_action_group_log")
        t_action_log = DB_POOL.get("comm_actions_log")
        with self.engine.connect() as connection:
            connection.execute(t_group_log.delete())
            connection.execute(t_action_log.delete())
            connection.commit()
        return super().setUp()

    def tearDown(self) -> None:
        return super().tearDown()

    def test_thead_run(self):
        """ 测试ActionGroup单个线程的执行流程 """
        engine = BasicEngine(groups=[])
        group = ActionGroup()
        group.name = "测试组AB"
        group.set_interval_minutes("5s")
        # 模拟新线程
        engine.threads[group.name] = "s"
        # 加载Action
        action_A = ActionConfig()
        action_A.name = "动作A"
        action_A.class_url = "com.wdbd.fd.services.dt.actions.test_actions.DemoActionA"
        action_A.set_windows([])
        action_A.set_once_on_day(True)
        group.append_action(action_A)
        action_B = ActionConfig()
        action_B.name = "动作B"
        action_B.class_url = "com.wdbd.fd.services.dt.actions.test_actions.DemoActionB"
        action_B.set_windows([])
        action_B.set_once_on_day(True)
        group.append_action(action_B)
        print("测试参数准备完毕！")

        # 执行
        engine._start_group_threads(group=group, _test_mode=True)


class TestServerUtils(unittest.TestCase):

    def test_load_group(self):
        """ 测试 根据配置文件（内容）读取一个Group配置 """
        context = { 
            "name": "组A",
            "desc": "关于这个组的说明",
            "rules": {
                "run_windows": [["0900", "1030"], ["1600", "1700"]],
                "on_error": "continue",
                "interval_time": "2h"
            },
            "actions": {
                "动作A": {
                    "desc": "下载股票清单",
                    "class": "com.wdbd.fd.services.dt.actions.test_actions.DemoActionA",
                    "rules": {
                        "run_windows": [
                            ["1000", "1230"],
                            ["1600", "2000"]
                            ],
                        "daily_once": True
                    }
                },
                "动作B": {
                    "desc": "下载股票清单",
                    "class": "com.wdbd.fd.services.dt.actions.test_actions.DemoActionB",
                    "rules": {
                        "run_windows": [
                            ["1000", "1230"],
                            ["1600", "2000"]
                            ],
                        "daily_once": True
                    }
                }
            }
        }
        group = ServerUtils.load_group(context)
        self.assertIsNotNone(group)
        self.assertEqual(2*60, group.get_interval_minutes())

    def test_load_group_with_wrong_classpath(self):
        """ 测试 根据配置文件（内容）读取一个Group配置 """
        context = { 
            "name": "组A",
            "desc": "关于这个组的说明",
            "rules": {
                "run_windows": [["0900", "1030"], ["1600", "1700"]],
                "on_error": "continue",
                "interval_time": "30m"
            },
            "actions": {
                "Tushare_A股清单": {
                    "desc": "下载股票清单",
                    "class": "com.xxx.DemoAction_A",
                    "rules": {
                        "run_windows": [
                            ["1000", "1230"],
                            ["1600", "2000"]
                            ],
                        "daily_once": True
                    }
                },
                "清单2": {
                    "desc": "下载股票清单",
                    "class": "com.xxx.DemoAction_A",
                    "rules": {
                        "run_windows": [
                            ["1000", "1230"],
                            ["1600", "2000"]
                            ],
                        "daily_once": True
                    }
                }
            }
        }
        group = ServerUtils.load_group(context)
        self.assertIsNone(group)    # 因为class错误

    def test__is_in_action_windows(self):
        # 测试 判断当前时间是否在Action的运行窗口内

        # 在区段内
        self.assertTrue(ServerUtils.is_in_action_windows(windows=[["0900", "0930"], ["1000", "1030"]], _test_time="0913"))
        # 在区段外
        self.assertFalse(ServerUtils.is_in_action_windows(windows=[["0900", "0930"], ["1000", "1030"]], _test_time="0800"))

        # 空
        self.assertTrue(ServerUtils.is_in_action_windows(windows=[], _test_time="080000"))
