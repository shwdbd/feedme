#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   test_commons.py
@Time    :   2021/08/13 13:14:59
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   针对gtp.fd.commons.py功能的单元测试

'''
import unittest
import com.wdbd.feedme.fd.common.common as tl


class TestSQL3_SQLAlchemy(unittest.TestCase):
    """ ORM数据库连接测试 """

    def test_conn(self):
        """ 测试ORM数据库连接 """
        tl.TEST_MODE = True
        engine = tl.get_engine()
        self.assertIsNotNone(engine)
        session = tl.get_session()
        self.assertIsNotNone(session)
        session.close()


class TestCommonsConfigFile(unittest.TestCase):
    """ 测试读取配置文件 """

    def setUp(self) -> None:
        tl.TEST_MODE = True
        return super().setUp()

    def test_read_config(self):
        """ 通用配置文件 """
        self.assertEqual('999', tl.get_cfg(section="fdserver", key="server.sleep"))

    def test_read_server_config(self):
        """ 服务器 配置 """
        self.assertEqual('999', tl.get_server_cfg("server.sleep"))

    def test_read_monogodb_config(self):
        """ Mongo数据库连接 配置 """
        self.assertEqual('99999', tl.get_mongo_cfg("db_port"))


# class TestMongodbConnect(unittest.TestCase):
#     """ 测试连接Mongodb数据库 """

#     def test_connect(self):
#         """ 数据库连接 """
#         client = tl.get_mgconn()
#         self.assertIsNotNone(client)

#         self.assertIsNotNone(tl.get_mgdb())


class TestLog(unittest.TestCase):
    """ 测试日志记录 """

    def setUp(self) -> None:
        tl.TEST_MODE = True
        return super().setUp()

    def test_log(self):
        """ 日志记录 """
        log = tl.get_logger()
        self.assertIsNotNone(log)
        log.info("测试 test")


class TestDateAndTime(unittest.TestCase):
    """ 时间与日期工具 """

    def setUp(self) -> None:
        tl.TEST_MODE = True
        return super().setUp()

    def test_today(self):
        """ 今日 """
        self.assertIsNotNone(tl.today())
        self.assertIsNotNone(tl.now())


class TestOtherToolsFunc(unittest.TestCase):
    """ 测试其他工具函数 """

    class DataStruct:
        
        def __init__(self):
            self.id = ""
            self.age = 100

    def test_record2object(self):
        """ 测试 DataFrame转成的dict格式，转成数据对象"""
        d = {"id": "值1", "age": 200}
        # 成功转换情况
        obj = tl.record2object(record=d, obj=self.DataStruct())
        self.assertIsNotNone(obj)
        self.assertEqual("值1", obj.id)
        self.assertEqual(200, obj.age)

        # dict有的字段，对象中无对应的属性
        d = {"id": "值1", "age": 100, "sex": "female"}
        obj = tl.record2object(record=d, obj=self.DataStruct())
        self.assertIsNotNone(obj)

        # record中字段不够的情况
        d = {"id": "值1"}
        obj = tl.record2object(record=d, obj=self.DataStruct())
        self.assertIsNotNone(obj)
        self.assertEqual(100, obj.age)

        # dict为空，或者None，或者不是dict类型
        obj = tl.record2object(record=None, obj=self.DataStruct)
        self.assertIsNone(obj)
        obj = tl.record2object(record=[], obj=self.DataStruct)
        self.assertIsNone(obj)
   