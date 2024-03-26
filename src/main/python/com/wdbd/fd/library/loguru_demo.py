

'''
需求场景：
不同的Action, 有一个name参数, 日志系统要根据name, 生成不同的格式的stderr输出, 并输出到不同文件名的日志文件中

实现原理：
1. logger绑定一个extra参数action_name, 然后通过filter控制只针对有action_name的日志进行输出 

'''
from loguru import logger
import sys


# logger.filter函数，检查extra中是否含有action_name变量
def is_my_logger(record):
    return "action_name" in record["extra"]


class Action:
    # Action对象

    def __init__(self, name):
        self.name = name
        self.logger = logger.bind(action_name=name)

    def func_call(self, message):
        # 程序执行
        self.logger.info(message)


if __name__ == "__main__":
    logger.remove()     # 清空全部的日志器

    # 初始化日志配置
    logger.add(sys.stderr, format="【{extra[action_name]}】 - {message}", filter=is_my_logger)
    # 日志文件名不能使用bind的变量，
    logger.add("log\\Action日志.log", rotation="8:00", format="{time:YYYY-MM-DD HH:mm:ss} 【{extra[action_name]}】 - {message}", filter=is_my_logger)

    # 日志输出
    logger.info("普通的日志输出")       # 未通过Filter，不输出日志
    # 实际输出
    action_1 = Action(name="动作甲")
    action_2 = Action(name="动作乙")
    action_1.func_call("甲|动作操作")
    action_2.func_call("乙|动作操作")
