#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   test_db.py
@Time    :   2023/12/20 10:47:49
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   测试数据库功能
'''
import unittest
import com.wdbd.fd.common.tl as tl
import com.wdbd.fd.model.db as db
import com.wdbd.fd.model.db.db_services as db_tool
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
# from com.wdbd.fd.collector.server import DTServer
# from sqlalchemy import desc


# 测试数据库连接
class TestDbConnect(unittest.TestCase):

    def test_get_engine(self):
        """ 测试取得数据库引擎 """
        tl.ENVIRONMENT = 'test'
        engine = db.get_engine()
        print(engine.url)
        self.assertTrue("fd_test" in engine.url)


# # 测试 下载服务开关
# class TestDbBizFunc_OpenShundown_server(unittest.TestCase):
#     """ 测试 下载服务开关 """

#     def setUp(self) -> None:
#         tl.ENVIRONMENT = 'test'
#         self.engine = db.get_engine()
#         return super().setUp()

#     # 测试 新注册一次服务运行
#     def test_open_server(self):
#         """ 测试 新注册一次服务运行 """
#         try:
#             # 清空comm_server表
#             with self.engine.connect() as connection:
#                 connection.execute(text("DELETE FROM comm_server"))
#                 connection.commit()

#             # 执行：
#             res = db_tool.open_server()
#             self.assertTrue(res)

#             Session = sessionmaker(bind=self.engine)
#             session = Session()
#             # 检查comm_server表
#             t_comm_server = db.table_objects_pool.get("comm_server")
#             record = session.query(t_comm_server.c.status, t_comm_server.c.start_dt, t_comm_server.c.end_dt).first()
#             self.assertEqual(DTServer.SERVER_STAUTS_OPEN, record[0])
#             self.assertIsNotNone(record[1])
#             self.assertEqual("", record[2])
#             session.close()

#         except Exception as e:
#             print(f"An error occurred:\n {e}")
#             self.fail()

#     # 测试已有服务在启动的情况
#     def test_open_server_serverAlreadRunning(self):
#         """ 测试 新注册一次服务运行(服务已启动的情况) """
#         try:
#             # 清空comm_server表
#             with self.engine.connect() as connection:
#                 connection.execute(text("DELETE FROM comm_server"))
#                 connection.execute(text("INSERT INTO comm_server (status) values ('{0}') ".format(DTServer.SERVER_STAUTS_OPEN)))
#                 connection.commit()

#             # 执行：
#             res = db_tool.open_server()
#             self.assertFalse(res)

#         except Exception as e:
#             print(f"An error occurred:\n {e}")
#             self.fail()

#     # 测试已有服务在启动的情况
#     def test_server_shundown(self):
#         """ 测试 关闭服务(服务已启动的情况) """
#         try:
#             # 清空comm_server表
#             with self.engine.connect() as connection:
#                 connection.execute(text("DELETE FROM comm_server"))
#                 # connection.execute(text("INSERT INTO comm_server (status) values ('{0}') ".format(DTServer.SERVER_STAUTS_OPEN)))
#                 connection.commit()

#             # 执行：
#             db_tool.open_server()
#             res = db_tool.server_shundown()
#             self.assertTrue(res, "返回值错误")

#             # 检查状态
#             Session = sessionmaker(bind=self.engine)
#             session = Session()
#             # 检查comm_server表
#             t_comm_server = db.table_objects_pool.get("comm_server")
#             record = session.query(t_comm_server.c.status, t_comm_server.c.end_dt).order_by(t_comm_server.c.id.desc()).first()
#             self.assertEqual(DTServer.SERVER_STAUTS_CLOSING, record[0])
#             self.assertEqual("", record[1])
#             session.close()

#         except Exception as e:
#             print(f"An error occurred:\n {e}")
#             self.fail()

#     # 测试已有服务在启动的情况
#     def test_server_shundown_noserver_running(self):
#         """ 测试 关闭服务(没有运行中的服务状态) """
#         try:
#             # 清空comm_server表
#             with self.engine.connect() as connection:
#                 connection.execute(text("DELETE FROM comm_server"))
#                 connection.execute(text("INSERT INTO comm_server (status) values ('{0}') ".format(DTServer.SERVER_STAUTS_SHUNDOWN)))
#                 connection.commit()

#             # 执行：
#             res = db_tool.server_shundown()
#             self.assertFalse(res)

#         except Exception as e:
#             print(f"An error occurred:\n {e}")
#             self.fail()
