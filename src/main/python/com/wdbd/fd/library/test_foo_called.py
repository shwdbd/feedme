from unittest import mock


# 假设有一个Cop类，其中leader_speak方法会调用Person类的say函数
class Person:
    """  """

    def __init__(self):
        """
        初始化函数，创建一个空的列表对象作为 context 属性。
        
        Args:
            无
        
        Returns:
            无
        
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
        for i in range(10):
            self.leader.say("这是第%d句讲话" % i)


# == 单元测试 =============
def test_foo_called():
    Person.say = mock.Mock(return_value="Mock, 说话")

    apple = Cop()
    apple.leader_speak()
    # 回显leader_speak中调用的say函数次数
    print(f"say()函数被调用总次数：{Person.say.call_count}")    # .call_count是mock.Mock的属性，用于统计被调用次数
    assert True, Person.say.assert_called()     # 断言say函数被调用
    assert True, Person.say.assert_called_with(context="这是第3句讲话")      # 断言：曾经被调用过一次，并传入参数 context="这是第3句讲话"
    # with mock.patch("com.wdbd.fd.library.test_foo_called.Person") as Person:
    #     Person.say = mock.Mock(return_value="Mock, 说话")
    #     apple = Cop()
    #     apple.leader_speak()
    # assert False, Person.say.assert_called_once()     # 断言say函数被仅仅调用一次| 这次会抛出异常


if __name__ == "__main__":
    test_foo_called()
