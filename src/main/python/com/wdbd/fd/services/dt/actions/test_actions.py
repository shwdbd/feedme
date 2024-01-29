from com.wdbd.fd.model.dt_model import AbstractAction
from com.wdbd.fd.common.tl import Result


# 动作留痕
PROCESS_LIST = {}


class DemoActionA(AbstractAction):

    def __init__(self) -> None:
        PROCESS_LIST["DemoActionA"] = {}
        super().__init__()

    def check_environment(self) -> bool:
        """检查环境，检查当前是否可以进行数据下载

        通常子类中会检查需要下载的数据是否已准备好
        Returns:
            bool: 检查结果
        """
        print("DemoActionA.check_environment")
        PROCESS_LIST["DemoActionA"]["check_environment"] = "OK"
        return Result(result=False, msg="xxxxx")

    def handle(self) -> bool:
        """数据处理函数，子类必须实现

        Returns:
            bool: 执行结果
        """
        print("DemoActionA.handle")
        PROCESS_LIST["DemoActionA"]["handle"] = "OK"
        return Result()

    def rollback(self) -> bool:
        """错误发生时，回滚动作函数

        Returns:
            bool: 回滚操作执行结果
        """
        print("DemoActionA.rollback")
        PROCESS_LIST["DemoActionA"]["rollback"] = "OK"
        return Result()


class DemoActionB(AbstractAction):

    def __init__(self) -> None:
        PROCESS_LIST["DemoActionB"] = {}
        super().__init__()

    def check_environment(self) -> bool:
        """检查环境，检查当前是否可以进行数据下载

        通常子类中会检查需要下载的数据是否已准备好
        Returns:
            bool: 检查结果
        """
        print("DemoActionB.check_environment")
        PROCESS_LIST["DemoActionB"]["check_environment"] = "OK"
        return Result()

    def handle(self) -> bool:
        """数据处理函数，子类必须实现

        Returns:
            bool: 执行结果
        """
        print("DemoActionB.handle")
        PROCESS_LIST["DemoActionB"]["handle"] = "OK"
        return Result()

    def rollback(self) -> bool:
        """错误发生时，回滚动作函数

        Returns:
            bool: 回滚操作执行结果
        """
        print("DemoActionB.rollback")
        PROCESS_LIST["DemoActionB"]["rollback"] = "OK"
        return Result()


# if __name__ == "__main__":
#     action = DemoActionA()
#     action.handle()
#     print(PROCESS_LIST)
