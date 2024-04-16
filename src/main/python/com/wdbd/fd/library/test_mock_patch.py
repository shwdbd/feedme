import unittest
from unittest import mock


# file_operations.py
def read_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()


# print(read_file("c://END"))

class TestFileOperations(unittest.TestCase):

    @mock.patch('builtins.open')  # 注意这里使用了builtins.open，因为我们在mock整个内置的open函数
    def test_read_file(self, mock_open):
        # 设置mock_open的行为
        mock_file = mock_open().__enter__()  # 获取mock文件对象
        mock_file.read.return_value = "This is a test file content."

        # 调用函数
        result = read_file('some_file_path.txt')

        # 断言结果
        self.assertEqual(result, "This is a test file content.")
        # 验证mock_open是否被调用，并且参数是否正确
        # mock_open.assert_called_once_with('some_file_path.txt', 'r')

    def test_2(self):
        mock_file_content = "This is a test file content."
        with mock.patch('builtins.open') as mocked_open:
            # 模拟open函数，并设置mock文件对象的read方法返回值
            mocked_open.return_value.__enter__.return_value.read.return_value = mock_file_content

            # 调用函数
            result = read_file('some_file_path.txt')

            # 断言结果
            self.assertEqual(result, mock_file_content)
            # 验证mock_open(builtins.open)是否被调用，并且参数是否正确
            mocked_open.assert_called_once_with('some_file_path.txt', 'r') 


if __name__ == '__main__':
    unittest.main()
