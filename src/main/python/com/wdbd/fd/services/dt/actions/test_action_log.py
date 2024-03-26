from com.wdbd.fd.model.dt_model import AbstractAction, ActionConfig
from com.wdbd.fd.common.tl import Result
from loguru import logger


# 测试
class LogTestAction(AbstractAction):
    """
    """

    def __init__(self, name: str = None) -> None:
        super().__init__()
        if name:
            self.name = name
            self.log = logger.bind(action_name=self.name)   # 参数绑定

    # def __init__(self) -> None:
    #     super().__init__()

    def check_environment(self) -> bool:
        return Result()

    def handle(self) -> bool:
        """数据处理函数，子类必须实现

        Returns:
            bool: 执行结果
        """
        self.log.info("动作 handle, {0}".format(self.name))
        return Result()

    def rollback(self) -> bool:
        """错误发生时，回滚动作函数

        Returns:
            bool: 回滚操作执行结果
        """
        return Result()


if __name__ == "__main__":
    # # 单独使用
    # a1 = LogTestAction("AAA")
    # a1.handle()
    # b1 = LogTestAction("BBB")
    # b1.handle()

    # 使用Action Config
    config = ActionConfig()
    config.name = "测试用Action"
    a1 = LogTestAction()
    a1.set_action_parameters(config)
    a1.handle()
