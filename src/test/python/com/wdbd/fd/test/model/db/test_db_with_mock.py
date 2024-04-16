import unittest
from unittest.mock import patch, MagicMock
from com.wdbd.fd.model.db.db_services import shundown_server, SERVER_STAUTS_OPEN
import com.wdbd.fd.common.tl as tl


# 模拟的数据库引擎和会话
engine = MagicMock()
Session = MagicMock()
session = MagicMock()

# 模拟的数据库池
DB_POOL = {'comm_server': MagicMock()}

# 模拟的t_comm_server表
t_comm_server = MagicMock()
t_comm_server.c = MagicMock()
t_comm_server.c.status = MagicMock()

# 模拟的tl.now函数
tl.now = MagicMock(return_value="mocked_now")


# 模拟的tl.Result类
class MockResult:
    def __init__(self, result, msg=None):
        self.result = result
        self.msg = msg


tl.Result = MockResult


# 模拟的日志记录器
mock_logger = MagicMock()
tl.get_logger = MagicMock(return_value=mock_logger)


# 模拟的get_engine函数
def mock_get_engine():
    return engine


# 初始化模拟的数据库会话
def init_session():
    session.execute = MagicMock()
    session.commit = MagicMock()
    session.close = MagicMock()


# 假设的SERVER_STAUTS_OPEN值
SERVER_STAUTS_OPEN = 'OPEN'
SERVER_STAUTS_CLOSING = 'CLOSING'


class TestShundownServer(unittest.TestCase):

    # @patch('com.wdbd.fd.model.db.get_engine', mock_get_engine)
    @patch('sqlalchemy.orm.sessionmaker', return_value=Session)
    # @patch('com.wdbd.fd.model.db.table_objects_pool', DB_POOL)
    # @patch('com.wdbd.fd.common.tl')
    def test_shundown_server_success(self):
    # def test_shundown_server_success(self, mocked_tl):
        # 初始化模拟的数据库会话
        init_session()

        # 假设条件：有一个OPEN状态的服务器
        t_comm_server.c.status.return_value = SERVER_STAUTS_OPEN

        # # 执行被测试的函数
        # result = shundown_server()

        # # 断言
        # self.assertTrue(result.result)
        # self.assertIsNone(result.msg)
        # session.execute.assert_called_once()
        # session.commit.assert_called_once()
        # session.close.assert_called_once()
        # t_comm_server.c.status.assert_called_once()
        # t_comm_server.c.end_dt.assert_called_once()
        # t_comm_server.update.assert_called_once()
        # mocked_tl.now.assert_called_once()
        # tl.get_logger.assert_not_called()  # 如果没有错误，不应该调用日志记录器

    # @patch('com.wdbd.fd.model.db.get_engine', mock_get_engine)
    # @patch('sqlalchemy.orm.sessionmaker', return_value=Session)
    # @patch('com.wdbd.fd.model.db.table_objects_pool', DB_POOL)
    # @patch('com.wdbd.fd.common.tl')
    # def test_shundown_server_exception(self, mocked_tl):
    #     # 初始化模拟的数据库会话
    #     init_session()

    #     # 模拟数据库执行时抛出异常
    #     session.execute.side_effect = Exception("Mocked database exception")

    #     # 执行被测试的函数
    #     result = shundown_server()

    #     # 断言
    #     self.assertFalse(result.result)
    #     self.assertTrue("关闭新服务时遇到问题。" in result.msg)
    #     self.assertTrue("Mocked database exception" in result.msg)
    #     session.commit.assert_not_called()  # 如果捕获到异常，不应该调用commit
    #     session.close.assert_called_once()
    #     tl.get_logger.assert_called_once()  # 如果有错误，应该调用日志记录器
    #     mock_logger.error.assert_called_once()


if __name__ == "__main__":
    unittest.main()
