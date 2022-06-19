#!/usr/bin/python
# 示例用代码

class App:

    def say(self, name):
        """ 示例方法 """
        # TODO 待完成事项
        # FIXME 修正事项
        # TEST 测试事项
        print("Hello {0}".format(name))
        return ("Hello {0}".format(name))


if __name__ == "__main__":
    app = App()
    print(app.say("App"))
