import unittest
import pandas as pd
from unittest.mock import patch, MagicMock
from com.wdbd.fd.services.dt.actions.akshare_action import AkSSESummaryDataDownloader, AkStockInfoShNameCode, AkStockCalDownloader, AkStockInfoBjNameCode, AkStockInfoSzNameCode
from com.wdbd.fd.common.tl import Result
from com.wdbd.fd.common.db_utils import DbUtils
import os


class Test_Ak_SSE_Summary(unittest.TestCase):
    """ 测试 Ak_SSE_Summary """

    def test_handle(self):
        """ 测试从真实网络API调用 """
        # 模拟网关gw
        mock_file_path = "src/test/python/com/wdbd/fd/test/services/dt/actions/ak_test_data_files/ak_sse_summary.csv"
        mock_df = pd.read_csv(filepath_or_buffer=mock_file_path)
        gw_mock = MagicMock()
        # 设置网关 gw.call 的返回值
        gw_mock.return_value = mock_df

        action = AkSSESummaryDataDownloader()
        action.gw.call = gw_mock
        result = action.handle()
        # 检查返回值
        self.assertTrue(isinstance(result, Result))
        self.assertTrue(result.result)
        self.assertEqual(result.msg, "Downloading Akshare market overview | SSE summary data successfully")
        # TODO 引入Mock，并检查数据库表数据是否正确

    @patch('akshare.stock_sse_summary')
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
        gw_mock.return_value = mock_df

        # 创建一个实例，并设置gw属性为mock对象
        action = AkSSESummaryDataDownloader()
        action.gw.call = gw_mock     # 模拟网关
        # 调用extract_data方法并获取结果
        result = action.extract_data()

        # 验证结果是否是预期的DataFrame
        self.assertTrue(isinstance(result, pd.DataFrame))
        self.assertEqual(result.shape, mock_df.shape)
        self.assertEqual(result.columns.tolist(), mock_df.columns.tolist())
        self.assertEqual(result.values.tolist(), mock_df.values.tolist())
        # 验证gw.call方法被调用了一次
        gw_mock.assert_called_once_with(callback=mock_stock_sse_summary)

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
        action = AkSSESummaryDataDownloader()
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
            action = AkSSESummaryDataDownloader()
            action.transform_data(empty_data)

    def test_data_transformed_with_invalid_dataframe(self):
        # 创建非DataFrame输入
        invalid_data = []

        # 调用方法并验证抛出TypeError
        with self.assertRaises(TypeError):
            # 执行测试
            action = AkSSESummaryDataDownloader()
            action.transform_data(invalid_data)

    def test_data_transformed_with_missing_columns(self):
        # 创建缺少必要列的DataFrame输入
        missing_columns_data = pd.DataFrame({
            '缺失列': [1, 2, 3]
        })

        # 调用方法并验证抛出KeyError
        with self.assertRaises(KeyError):
            # 执行测试
            action = AkSSESummaryDataDownloader()
            action.transform_data(missing_columns_data)

    def test_load_data_success(self):
        action = AkSSESummaryDataDownloader()
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


class Test_Ak_Stock_Cal(unittest.TestCase):
    """ 测试 Ak_Stock_Cal """

    # def tearDown(self) -> None:
    #     DbUtils.clear_table_data(table_name="ods_akshare_tool_trade_date_hist_sina")
    #     return super().tearDown()

    def setUp(self) -> None:
        DbUtils.clear_table_data(table_name="ods_akshare_tool_trade_date_hist_sina")
        return super().setUp()

    def test_handle_downloadall(self):
        """ 测试全量下载日历数据 """
        mock_data = pd.DataFrame({
            "trade_date": ['1991-01-02', '1991-01-08']
        })
        gw_mock = MagicMock()
        # 设置网关 gw.call 的返回值
        gw_mock.return_value = mock_data

        action = AkStockCalDownloader()
        action.DOWNLOAD_ALL = True
        action.gw.call = gw_mock    # 模拟Akshare
        result = action.handle()
        # 检查返回值
        self.assertTrue(isinstance(result, Result))
        self.assertTrue(result.result)
        self.assertEqual(result.msg, "Akshare 新浪交易日历 下载成功")
        # 数据库结果检查
        self.assertEqual(2, DbUtils.count(table_name="ods_akshare_tool_trade_date_hist_sina"))


# 测试 下载上海交易所股票代码清单
class Test_AkStockInfoShNameCode(unittest.TestCase):

    def setUp(self):
        # 创建测试用例
        self.mock_file_dir = "src/test/python/com/wdbd/fd/test/services/dt/actions/ak_test_data_files/"

    def test_handle(self):
        mock_df_1 = pd.DataFrame({
            "证券代码": [600000, 600004],
            "证券简称": ['浦发银行', '白云机场'],
            "公司全称": ['上海浦东发展银行股份有限公司', '广州白云国际机场股份有限公司'],
            "上市日期": ['1999-11-10', '2003-04-28']
        })
        mock_df_2 = pd.DataFrame({
            "证券代码": [600010, 600011],
            "证券简称": ['主板A股1', '主板A股2'],
            "公司全称": ['xxxx', 'yyyy'],
            "上市日期": ['1999-11-10', '2003-04-28']
        })
        mock_df_3 = pd.DataFrame({
            "证券代码": [600020, 600021],
            "证券简称": ['科创板1', '科创板2'],
            "公司全称": ['xxxx', 'yyyy'],
            "上市日期": ['1999-11-10', '2003-04-28']
        })
        gw_mock = MagicMock()
        # 设置网关 gw.call 的返回值
        gw_mock.side_effect = [mock_df_1, mock_df_2, mock_df_3]

        # 执行
        action = AkStockInfoShNameCode()
        action.gw.call = gw_mock     # 模拟网关
        result = action.handle()

        # 结果监测
        self.assertTrue(isinstance(result, Result))
        self.assertTrue(result.result)
        self.assertEqual(result.msg, "Downloading Akshare stock list | 上海交易所 successfully")
        self.assertEqual(6, DbUtils.count(table_name="ods_akshare_stock_info_sh_name_code"))

    def test_extract_data(self):
        # 在这里，我们假设gw是一个已经实例化的对象，并且有一个call方法
        mock_file_path = os.path.join(self.mock_file_dir, "akshare_stock_list_sh.csv")
        mock_df = pd.read_csv(filepath_or_buffer=mock_file_path)
        gw_mock = MagicMock()
        # 设置网关 gw.call 的返回值
        gw_mock.side_effect = [mock_df, mock_df, mock_df]

        # 创建一个实例，并设置gw属性为mock对象
        action = AkStockInfoShNameCode()
        action.gw.call = gw_mock     # 模拟网关
        # 调用extract_data方法并获取结果
        result = action.extract_data()

        # 验证结果是否是预期的DataFrame
        self.assertTrue(isinstance(result, pd.DataFrame))
        self.assertEqual(result.shape[1], mock_df.shape[1])
        self.assertEqual(result.shape[0], mock_df.shape[0]*3)
        self.assertEqual(result.columns.tolist(), ['证券代码', '证券简称', '公司全称', '上市日期', 'board'])
        # 验证gw.call方法被调用了3次
        self.assertEqual(gw_mock.call_count, 3)

    def test_transform_data(self):
        """
        测试transform_data_sh函数，将原始数据转换成上交所股票代码格式
        """
        raw_data = pd.DataFrame({
            '证券代码': [600000, 600001, 600002],
            '证券简称': ['浦发银行', '华夏银行', '民生银行'],
            '公司全称': ['上海浦东发展银行股份有限公司', '华夏银行股份有限公司', '中国民生银行股份有限公司'],
            '上市日期': ['1999-11-10', '2003-09-12', '2000-12-19']
        })
        expected_data = pd.DataFrame({
            'symbol': ['600000.SH', '600001.SH', '600002.SH'],
            'stock_name': ['浦发银行', '华夏银行', '民生银行'],
            'total_name': ['上海浦东发展银行股份有限公司', '华夏银行股份有限公司', '中国民生银行股份有限公司'],
            'ipo_date': ['19991110', '20030912', '20001219']
        })

        action = AkStockInfoShNameCode()
        data_transformed = action.transform_data(raw_data)
        self.assertTrue(isinstance(data_transformed, pd.DataFrame))
        self.assertEqual(data_transformed.shape, expected_data.shape)
        self.assertEqual(data_transformed.columns.tolist(), expected_data.columns.tolist())


# 测试 下载北京交易所股票代码清单
class Test_AkStockInfoBjNameCode(unittest.TestCase):

    def test_handle(self):
        mock_df = pd.DataFrame({
            "证券代码": [600000, 600004],
            "证券简称": ['浦发银行', '白云机场'],
            "总股本": [12345, 67890],
            "流通股本": [12345, 67890],
            "上市日期": ['1999-11-10', '2003-04-28'],
            "所属行业": ['A 工业', 'B 农业'],
            "地区": ['A ASH', 'B 广西'],
            "报告日期": ['2022-06-30', '2003-04-28']
        })
        gw_mock = MagicMock()
        # 设置网关 gw.call 的返回值
        gw_mock.return_value = mock_df

        # 执行
        action = AkStockInfoBjNameCode()
        action.gw.call = gw_mock     # 模拟网关
        result = action.handle()

        # 结果监测
        self.assertTrue(isinstance(result, Result))
        self.assertTrue(result.result)
        self.assertEqual(result.msg, "Downloading 北京交易所 股票清单 successfully")
        self.assertEqual(2, DbUtils.count(table_name="ods_akshare_stock_info_bj_name_code"))


# 测试 下载深圳交易所股票代码清单
class Test_AkStockInfoSzNameCode(unittest.TestCase):

    def test_handle(self):
        # mock_df = pd.DataFrame({
        #     "证券代码": [600000, 600004],
        #     "证券简称": ['浦发银行', '白云机场'],
        #     "总股本": [12345, 67890],
        #     "流通股本": [12345, 67890],
        #     "上市日期": ['1999-11-10', '2003-04-28'],
        #     "所属行业": ['A 工业', 'B 农业'],
        #     "地区": ['A ASH', 'B 广西'],
        #     "报告日期": ['2022-06-30', '2003-04-28']
        # })
        # gw_mock = MagicMock()
        # # 设置网关 gw.call 的返回值
        # gw_mock.return_value = mock_df

        # 执行
        action = AkStockInfoSzNameCode()
        # action.gw.call = gw_mock     # 模拟网关
        result = action.handle()

        # 结果监测
        self.assertTrue(isinstance(result, Result))
        self.assertTrue(result.result)
        self.assertEqual(result.msg, "Downloading 深圳交易所 股票清单 successfully")
        self.assertTrue(DbUtils.count(table_name="ods_akshare_stock_info_sz_name_code") > 1000)
        # self.assertEqual(2, DbUtils.count(table_name="ods_akshare_stock_info_bj_name_code"))
        # TODO 需要使用Mock进行测试
