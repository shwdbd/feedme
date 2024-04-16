#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   test_foo_side_effect.py
@Time    :   2024/04/10 16:00:14
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   尝试使用mock.Mock的side_effect属性，模拟一个函数调用过程
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
        self.leader.say("这是第2句讲话")
        for i in range(5):
            self.leader.say("这是第%d句讲话" % i)


# == 单元测试 =============

def my_mock_foo(context):
    """
    Mock函数，模拟foo函数的行为。

    Args:
        context (str): 传递给模拟函数的上下文信息。
    Returns
        str: 模拟函数返回的字符串，格式为"Mock say, {context}"。
    """
    print(f"Mock side_effect 函数被调用, context: {context}")
    return f"Mock say, {context}"


def test_foo_side_effect():
    Person.say = mock.Mock(side_effect=my_mock_foo)

    apple = Cop()
    apple.leader_speak()

    # 回显 apple.leader.context 证明say的原生函数没有被调用
    print(apple.leader.context)


if __name__ == "__main__":
    test_foo_side_effect()
