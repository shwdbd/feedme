#!/usr/bin/python
# 单元测试示例
import unittest
from com.wdbd.app import App
# import com.my_app.app as app


class TestApp(unittest.TestCase):

    def test_app(self):
        app = App()
        self.assertEqual("Hello App", app.say("App"))
