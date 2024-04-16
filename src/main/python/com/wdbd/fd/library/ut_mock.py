from unittest import mock


class Person:

    def say(self, name):
        return f"Hello, {name}!"

    def eat(self, food):
        return f"Eat, {food}!"


class Cop:

    def leader_speak(self):
        self.leader = Person()
        return self.leader.say(name="JOBS")


def first_mock_demo():
    """
    最简单的Mock方法，把一个对象的函数Mock掉，并测试Mock函数是否工作正常。
    同时展示如何Mock掉一个类的函数，并进行断言测试。

    Args:
        无
    Returns:
        无
    """
    # 最简单的Mock方法，把一个对象的函数Mock掉
    jack = Person()
    jack.say = mock.Mock(return_value="Hello, Jack!")
    # Test:
    assert jack.say("Jack") == "Hello, Jack!"

    # 把一个类的函数Mock掉
    apple = Cop()
    Person.say = mock.Mock(return_value="Hello, JOBS!")
    Person.eat = mock.Mock(return_value="Eat, bananas")
    assert apple.leader_speak() == "Hello, JOBS!"
    # assert_called_with
    Person.say.assert_called()      # 断言：曾经被调用过一次
    Person.say.assert_called()      # 断言：曾经被调用过恰巧一次
    Person.say.assert_called_with(name="JOBS")      # 断言：曾经被调用过一次，并传入参数 name="JOBS"
    Person.eat.assert_not_called()  # 断言：从未被调用(必须先要Mock)


def test_cop_with_class_mock():
    """
    使用mock库将Person类的say函数Mock掉，并测试Cop类的leader_speak方法返回的是否为Mock后的结果    
    """
    # 把Person类的say函数给Mock掉：
    Person.say = mock.Mock(return_value="Hello, JOBS!")
    apple = Cop()
    assert apple.leader_speak() == "Hello, JOBS!"
    # 此处Cop实现应该返回“王二狗”，但由于Person.say被Mock掉，返回的是JOBS


def test_cop_with_object_mock():
    """
    使用unittest.mock库对Person类的实例Jack的say函数进行Mock，并测试其返回值和类的函数是否受影响
    """
    # 把Person类的实例Jack的say函数给Mock掉：
    jack = Person()
    jack.say = mock.Mock(return_value="Hello, Black Jack!")
    assert jack.say() == "Hello, Black Jack!"
    # 类的函数不受影响
    mike = Person()
    assert mike.say("Mike") == "Hello, Mike!"

    # 此处仅仅Mock的对象的函数，类函数不受影响：
    apple = Cop()
    assert apple.leader_speak() == "Hello, JOBS!"


def test_cop_with_patch():
    """
    使用unittest.mock库对Person类的say函数进行Mock，并测试其返回值和类的函数是否受影响
    """
    # 把Person类的say函数给Mock掉：
    m_say = mock.patch('ut_mock.Person.say', new="Hello, Mike!")
    m_say.start()
    mike = Person()
    assert mike.say("Mike") == "Hello, Mike!"
    # 类的函数不受影响
    jack = Person()

# 如何使用side_effect来Mock一个函数




# 如何使用side_effect来Mock一个函数
# def mock_with_side_effect():
#     # 使用mock库模拟Person类的say方法，并设置side_effect属性为一个列表
#     # 每次调用say方法时，会依次返回列表中的元素
#     Person.say = mock.Mock(side_effect=["Hello, JOBS!", "Hello, Jack!"])
#     # 创建一个Person类的实例
#     jack = Person()
#     # 断言jack调用say方法时返回的结果为"Hello, JOBS!"
#     assert jack.say("Jack") == "Hello, JOBS!"
#     # 断言jack调用say方法时返回的结果为"Hello, Jack!"
#     assert jack.say("Jack2") == "Hello, Jack!"


#     # 使用mock库模拟Person类的say方法，并设置side_effect属性为一个KeyError异常
#     Person.say = mock.Mock(side_effect=KeyError("这是一个异常"))
#     try:
#         # 调用jack的say方法
#         jack.say("Jack")
#         # 如果未抛出异常，则打印"应抛异常，但未抛出"
#         print("应抛异常，但未抛出")
#     except KeyError:
#         # 如果捕获到KeyError异常，则不执行任何操作
#         pass
#     except Exception as e:
#         # 如果捕获到其他类型的异常，则打印异常类型
#         print(f"异常类型错误 {e}")


# 模拟一个函数，并使用side_effect来模拟函数的返回值
def mock_with_patch():
    m_say = mock.patch('ut_mock.Person.say', new="Hello, Mike!")

    m_say.start()
    # assert jack.say("Nathan") == "Hello, Mike!", jack.say("Nathan")
    jack = Person()
    result = jack.say("Nathan")
    print(result)
    m_say.stop()


if __name__ == "__main__":
    # first_mock_demo()
    # mock_with_side_effect()
    # mock_with_patch()
    test_cop_with_object_mock()



