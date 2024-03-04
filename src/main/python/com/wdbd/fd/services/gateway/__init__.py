
def get_ak_gateway():
    """ 返回 Akshare 网关对象 """
    # TODO 实现
    return None


class DataException(Exception):
    """ 数据访问异常 """

    def __init__(self, message: str = None):
        # 调用父类（即Exception）的初始化方法
        super().__init__(message)
