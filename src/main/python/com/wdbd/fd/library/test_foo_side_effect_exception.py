#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   test_foo_side_effect.py
@Time    :   2024/04/10 16:00:14
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   尝试使用mock.Mock的side_effect属性，模拟异常发生
'''
from unittest import mock


# 假设有一个Cop类，其中leader_speak方法会调用Person类的say函数
class Person:
    """  """

    def __init__(self):
        """
        初始化函数，创建一个空的列表对象作为 context 属性。
        """
        self.context = []

    def say(self, context):
        """
        向self.context列表中添加一个字符串，并将其打印出来

        Args:
            self: 类的实例对象
            context: 要添加的字符串

        Returns:
            无返回值  
        """
        self.context.append(context)
        print(context)


class Cop:

    def leader_speak(self):
        self.leader = Person()
        self.leader.say("这是第1句讲话")


# == 单元测试 =============

def test_foo_side_effect_with_exception():
    Person.say = mock.Mock(side_effect=KeyError("mock 异常"))

    apple = Cop()
    try:
        apple.leader_speak()
    except KeyError as keyerr:
        print(f"KeyError: {keyerr}")
        print(f"apple.leader.context:  {apple.leader.context}")


if __name__ == "__main__":
    test_foo_side_effect_with_exception()
