import unittest
import pandas as pd
from unittest.mock import patch, MagicMock
from com.wdbd.fd.services.dt.actions.akshare_action import Ak_SSE_Summary
from com.wdbd.fd.common.tl import Result


class Test_Ak_SSE_Summary(unittest.TestCase):

    def test_handle(self):
        """ 测试从真实网络API调用 """
        action = Ak_SSE_Summary()
        result = action.handle()
        # 检查返回值
        self.assertTrue(isinstance(result, Result))
        self.assertTrue(result.result)
        self.assertEqual(result.msg, "Downloading Akshare market overview | SSE summary data successfully")

    @patch('akshare.stock_sse_summary')  # 替换成正确的导入路径
    def test_extract_data(self, mock_stock_sse_summary):
        """
        测试提取SSE股票行情摘要数据的功能

        Args:
            mock_stock_sse_summary: 用于模拟gw.call方法回调函数的mock对象

        Returns:
            None
        """
        # 在这里，我们假设gw是一个已经实例化的对象，并且有一个call方法
        mock_file_path = "src/test/python/com/wdbd/fd/test/services/dt/actions/ak_test_data_files/ak_sse_summary.csv"
        mock_df = pd.read_csv(filepath_or_buffer=mock_file_path)
        gw_mock = MagicMock()
        # 设置网关 gw.call 的返回值
        gw_mock.call.return_value = mock_df

        # 创建一个YourClass的实例，并设置gw属性为mock对象
        action = Ak_SSE_Summary()
        action.gw = gw_mock     # 模拟网关
        # 调用extract_data方法并获取结果
        result = action.extract_data()

        # 验证结果是否是预期的DataFrame
        self.assertTrue(isinstance(result, pd.DataFrame))
        self.assertEqual(result.shape, mock_df.shape)
        self.assertEqual(result.columns.tolist(), mock_df.columns.tolist())
        self.assertEqual(result.values.tolist(), mock_df.values.tolist())
        # 验证gw.call方法被调用了一次
        gw_mock.call.assert_called_once_with(callback=mock_stock_sse_summary)

    # 测试data_transformed方法(成功)
    def test_data_transformed_with_valid_input(self):
        """
        测试Ak_SSE_Summary类中的data_transformed 数据转换与清洗 函数
        """
        # 模拟的原始数据
        raw_data = {
            '项目': ['流通股本', '总市值', '平均市盈率', '上市公司', '上市股票', '流通市值', '总股本', '报告时间'],
            '数值': [10000, 2000000, 15, 4000, 5000, 1500000, 25000, '2023-03-31']
        }
        # 将模拟数据转换为DataFrame
        df = pd.DataFrame(raw_data)

        # 执行测试
        action = Ak_SSE_Summary()
        transformed_data = action.transform_data(df)

        # 检查数据是否为DataFrame
        assert isinstance(transformed_data, pd.DataFrame)

        # 检查列名是否匹配
        expected_columns = ['market', 'ltgb', 'zsz', 'pjsyl', 'ssgs', 'ssgp', 'tlsz', 'zgb', 'trade_date']
        assert list(transformed_data.columns) == expected_columns

        # 检查数据行数
        assert transformed_data.shape[0] == 1

        # 检查特定值
        assert transformed_data.loc[0, 'ltgb'] == 10000
        assert transformed_data.loc[0, 'zsz'] == 2000000
        assert transformed_data.loc[0, 'pjsyl'] == 15
        assert transformed_data.loc[0, 'ssgs'] == 4000
        assert transformed_data.loc[0, 'ssgp'] == 5000
        assert transformed_data.loc[0, 'tlsz'] == 1500000
        assert transformed_data.loc[0, 'zgb'] == 25000
        assert transformed_data.loc[0, 'trade_date'] == '2023-03-31'

    def test_data_transformed_with_empty_data(self):
        # 创建空的DataFrame输入
        empty_data = pd.DataFrame()

        with self.assertRaises(TypeError):
            # 执行测试
            action = Ak_SSE_Summary()
            action.transform_data(empty_data)

    def test_data_transformed_with_invalid_dataframe(self):
        # 创建非DataFrame输入
        invalid_data = []

        # 调用方法并验证抛出TypeError
        with self.assertRaises(TypeError):
            # 执行测试
            action = Ak_SSE_Summary()
            action.transform_data(invalid_data)

    def test_data_transformed_with_missing_columns(self):
        # 创建缺少必要列的DataFrame输入
        missing_columns_data = pd.DataFrame({
            '缺失列': [1, 2, 3]
        })

        # 调用方法并验证抛出KeyError
        with self.assertRaises(KeyError):
            # 执行测试
            action = Ak_SSE_Summary()
            action.transform_data(missing_columns_data)

    def test_load_data_success(self):
        action = Ak_SSE_Summary()
        # 模拟的原始数据
        raw_data = {
            '项目': ['流通股本', '总市值', '平均市盈率', '上市公司', '上市股票', '流通市值', '总股本', '报告时间'],
            '数值': [10000, 2000000, 15, 4000, 5000, 1500000, 25000, '2023-03-31']
        }
        # 将模拟数据转换为DataFrame
        data = pd.DataFrame(raw_data)
        data = action.transform_data(data)

        # 执行
        result = action.load_data(data)

        # 检查返回值
        # self.assertTrue(isinstance(result, Result))
        self.assertTrue(result.result)
        self.assertEqual(result.msg, "")


if __name__ == '__main__':
    unittest.main(verbosity=2)
    # unittest.main()

    # # 创建测试套件
    # suite = unittest.TestSuite()
    # # 将特定的测试用例添加到套件中
    # suite.addTest(Test_Ak_SSE_Summary('test_load_data_success'))
    # # 使用测试套件运行测试
    # runner = unittest.TextTestRunner()
    # runner.run(suite)
