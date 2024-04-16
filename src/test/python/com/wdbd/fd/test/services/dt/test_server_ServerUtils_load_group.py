import unittest
from unittest.mock import Mock, patch
from typing import Dict
from com.wdbd.fd.services.dt.server import ServerUtils
from com.wdbd.fd.model.dt_model import AbstractAction


# 假设的ActionGroup和ActionConfig类定义
class ActionGroup:
    def __init__(self):
        self.name = None
        self.desc = None
        self.parameters = {}
        self.actions = []

    def append_action(self, action):
        self.actions.append(action)


class ActionConfig:
    def __init__(self, group):
        self.group = group
        self.name = None
        self.class_url = None
        self.parameters = {}

    @staticmethod
    def check_classname():
        # 在测试中总是返回True
        return True


class TestActionClass1(AbstractAction):

    def __init__(self) -> None:
        super().__init__()
        if not self.name:
            self.name = "测试Action1"


class TestActionClass2(AbstractAction):

    def __init__(self) -> None:
        super().__init__()
        if not self.name:
            self.name = "测试Action2"


# 测试用例
class TestLoadGroup(unittest.TestCase):

    @patch('path.to.module.get_logger')  # 替换get_logger为mock对象
    def test_load_group_success(self, mock_logger):
        # 准备测试数据
        group_context = {
            "name": "TestGroup",
            "desc": "Test Group Description",
            "rules": {
                "rule1": "value1",
                "rule2": "value2"
            },
            "actions": {
                "action1": {
                    "class": "com.wdbd.fd.test.services.dt.server.TestActionClass1"
                },
                "action2": {
                    "class": "com.wdbd.fd.test.services.dt.server.TestActionClass2"
                }
            }
        }
        # 调用被测试函数
        result = ServerUtils.load_group(group_context)

        # 验证结果
        self.assertIsNotNone(result)
        self.assertEqual(result.name, "TestGroup")
        self.assertEqual(result.desc, "Test Group Description")
        self.assertEqual(result.parameters, {"rule1": "value1", "rule2": "value2"})
        self.assertEqual(len(result.actions), 2)

        # 验证actions
        action1, action2 = result.actions
        self.assertEqual(action1.name, "action1")
        self.assertEqual(action1.class_url, "TestActionClass1")
        self.assertEqual(action1.parameters, {"rule1": "value1", "rule2": "value2"})
        self.assertEqual(action2.name, "action2")
        self.assertEqual(action2.class_url, "TestActionClass2")
        self.assertEqual(action2.parameters, {"rule1": "value1", "rule2": "value2"})

        # # 验证get_logger没有被调用（因为我们希望不出现错误）
        # mock_logger.assert_not_called()

    # @patch('path.to.module.get_logger')  # 替换get_logger为mock对象
    # def test_load_group_with_invalid_classname(self, mock_logger):
    #     # 准备测试数据，其中包含一个无效的类名
    #     group_context = {
    #         "actions": {
    #             "action1": {
    #                 "class": "InvalidClass"
    #             }
    #         }
    #     }

    #     # 模拟ActionConfig的check_classname方法返回False
    #     ActionConfig.check_classname = Mock(return_value=False)

    #     # 调用被测试函数
    #     result = load_group(group_context)

    #     # 验证结果是否为None，因为类名无效
    #     self.assertIsNone(result)

    #     # 验证get_logger被调用并记录了一个错误
    #     mock_logger.error.assert_called_once()


# 运行测试
if __name__ == '__main__':
    unittest.main()
