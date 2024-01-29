#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   test_db_services.py
@Time    :   2024/01/29 15:17:03
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   None
'''
import unittest
from com.wdbd.fd.model.db import get_engine, table_objects_pool as DB_POOL
from com.wdbd.fd.model.dt_model import ActionGroup, ActionConfig
from com.wdbd.fd.model.db.db_services import log_group
from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_


class TestServerDbService(unittest.TestCase):
    """ 测试数据运行引起方面的服务功能 """

    def setUp(self) -> None:
        self.engine = get_engine()
        t_group = DB_POOL.get("comm_action_group_log")
        with self.engine.connect() as connection:
            connection.execute(t_group.delete())
            connection.commit()
        return super().setUp()

    def tearDown(self) -> None:
        return super().tearDown()

    def test_log_group(self):
        """ 测试 登记ActionGroup日志 """
        # 记录Group日志
        group = ActionGroup()
        group.name = "测试组AB"
        group.set_interval_minutes("5s")
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

        # 首次登记
        log_group(group=group)
        # 检查：
        Session = sessionmaker(bind=self.engine)
        session = Session()
        t_group = DB_POOL.get("comm_action_group_log")
        rs = session.query(t_group).filter(and_(t_group.c.group_name == group.name, t_group.c.status == ActionGroup.RUNNING))
        self.assertEqual(1, rs.count())
        glog = rs[0]
        self.assertEqual(ActionGroup.RUNNING, glog.status)
        self.assertTrue("动作B" in glog.actions)

        # 记录结果
        log_group(group=group, result=False, msg="xxxyyy")
        rs = session.query(t_group).filter(t_group.c.group_name == group.name)
        self.assertEqual(1, rs.count())
        glog = rs[0]
        self.assertEqual(ActionGroup.FAILED, glog.status)
        self.assertEqual("xxxyyy", glog.msg)

        session.close()
