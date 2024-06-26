#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   akshare_action.py
@Time    :   2024/03/06 15:27:20
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   Akshare 数据源处理
'''
from com.wdbd.fd.model.dt_model import AbstractAction
from com.wdbd.fd.common.tl import Result
from com.wdbd.fd.services.gateway.ak_gateway import get_ak_gateway, DataException
import akshare as ak
from com.wdbd.fd.model.db import get_engine, table_objects_pool as DB_POOL
from sqlalchemy.orm import sessionmaker
import com.wdbd.fd.common.tl as tl
from com.wdbd.fd.common.db_utils import DbUtils
from sqlalchemy.exc import SQLAlchemyError as SQLAlchemyError
from loguru import logger
import pandas as pd
from sqlalchemy import text


# 基类
class AkshareLoadAction(AbstractAction):
    """Akshare 数据源下载模块
    """

    def __init__(self) -> None:
        self.gw = get_ak_gateway()  # Ak数据网关
        super().__init__()

    def check_environment(self) -> tl.Result:
        """
        检查与数据网关的连接是否正常。

        Args:
            无
        Returns:
            tl.Result: 返回一个Result对象，表示连接是否成功。
        """
        if self.gw is None:
            return Result(result=False, msg="数据网关对象未初始化")

        if self.gw.check_connection():
            return Result(result=True)
        else:
            return Result(result=False, msg="Ak数据网关连接失败")

    def handle(self) -> tl.Result:
        return tl.Result()

    def rollback(self) -> tl.Result:
        return Result(result=True)

    def extract_data(self) -> pd.DataFrame:
        return None

    def transform_data(self, data: pd.DataFrame) -> pd.DataFrame:
        return None

    def load_data(self, data: pd.DataFrame) -> tl.Result:
        return None


# 市场总貌|上海证券交易所
class AkSSESummaryDataDownloader(AkshareLoadAction):
    """
    市场总貌|上海证券交易所 数据下载

    说明：
    从 ak.stock_sse_summary 获取最新数据, 存入ods_akshare_stock_sse_summary表, 每天3条交流
    """

    def __init__(self) -> None:
        super().__init__()
        if not self.name:
            self.name = "AK 上海证券交易所|市场总貌"
            self.log = logger.bind(action_name=self.name)   # 参数绑定

    def extract_data(self) -> pd.DataFrame:
        """
        从股票行情数据接口获取上证指数汇总数据，并返回 pandas DataFrame 格式的数据。

        Args:
            无
        Returns:
            pd.DataFrame: 包含上证指数汇总数据的 pandas DataFrame。
        """
        df = self.gw.call(callback=ak.stock_sse_summary)
        return df

    def transform_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        对数据进行清洗、转换等操作。

        Args:
            data (pd.DataFrame): 原始数据，DataFrame类型。
        Returns:
            pd.DataFrame: 清洗后的数据，DataFrame类型。
        Raises:
            TypeError: 当输入数据不是pd.DataFrame类型时，抛出类型错误异常。
        """
        if not isinstance(data, pd.DataFrame):
            raise TypeError("数据类型错误")

        if data.empty:  # 如果数据为空
            raise TypeError("获取数据为空")

        # 数据清洗
        data = data.set_index('项目')
        data = data.T
        data = data.reset_index()   # 将索引列变为第一列
        # 修改列名，与db中一致
        new_column_names = {
            'index': 'market',
            '流通股本': 'ltgb',
            '总市值': 'zsz',  # 修正了重复的键
            '平均市盈率': 'pjsyl',
            '上市公司': 'ssgs',
            '上市股票': 'ssgp',
            '流通市值': 'tlsz',
            '总股本': 'zgb',
        }
        data = data.rename(columns=new_column_names)

        # 添加对'报告时间'列存在性和非空性的检查
        if '报告时间' in data.columns and not data['报告时间'].empty:
            trade_date = data['报告时间'][0]  # 报告日期
            data["trade_date"] = str(trade_date)
            data.drop('报告时间', axis=1, inplace=True)
        else:
            # 根据实际需求处理，这里可以添加一个警告或者设置一个默认值
            print("警告：'报告时间'列不存在或为空。")
            # raise TypeError("警告：'报告时间'列不存在或为空。")

        return data

    def load_data(self, data: pd.DataFrame) -> tl.Result:
        """
        从 pandas DataFrame 加载数据到数据库

        Args:
            data (pd.DataFrame): 包含要加载到数据库的数据的 pandas DataFrame
        Returns:
            None
        Raises:
            DataException: Akshare获取数据异常
            SQLAlchemyError: SQLAlchemy数据库异常
        """
        session = None
        try:
            engine = get_engine()
            Session = sessionmaker(bind=engine)
            session = Session()

            trade_date = data['trade_date'][0]
            # print(trade_date)

            # 删除现有的数据
            t_ods_akshare_stock_sse_summary = DB_POOL.get(
                "ods_akshare_stock_sse_summary")
            session.query(t_ods_akshare_stock_sse_summary).filter(
                t_ods_akshare_stock_sse_summary.c.trade_date == trade_date).delete()
            session.commit()

            # 写入数据库, Write to the database
            data.to_sql(name='ods_akshare_stock_sse_summary',
                        con=engine, if_exists='append', index=False)

            self.log.info("表 ods_akshare_stock_sse_summary 更新完成")

            return Result(True, "")
        except DataException as dwe:
            msg = "Akshare获取数据异常，" + str(dwe)
            self.log.error(msg)
            return tl.Result(result=False, msg=msg)
        except SQLAlchemyError as sqle:
            msg = "SQL异常" + str(sqle)
            self.log.error(msg)
            return tl.Result(result=False, msg=msg)
        finally:
            if session:  # Check if session is defined before closing
                session.close()

    def handle(self) -> tl.Result:
        """
        下载 Akshare 市场概述 | SSE 汇总数据

        Args:
            无
        Returns:
            tl.Result: 返回一个具体的对象，表示操作是否成功
        """
        self.log.info("Downloading Akshare market overview | SSE summary data")

        try:
            # 提取数据
            data = self.extract_data()
            if data is None:
                self.log.error("Failed to extract data")
                return tl.Result(result=False, msg="Failed to extract data")

            # 转换数据（清洗等）
            data_transformed = self.transform_data(data)
            if data_transformed is None:
                self.log.error("Failed to transform data")
                return tl.Result(result=False, msg="Failed to transform data")

            # 加载数据（存储）
            result = self.load_data(data_transformed)

            if result and result.result:
                self.log.info("Akshare market overview Data loaded successfully")
                return tl.Result(result=True, msg="Downloading Akshare market overview | SSE summary data successfully")
            else:
                self.log.error("Akshare market overview Data 下载失败！")
                return tl.Result(result=False, msg=f"Downloading Akshare market overview | SSE summary data Failed. {result.msg}")
        except Exception as e:
            self.log.exception("An error occurred during data handling")
            return tl.Result(result=False, msg=f"An error occurred during data handling | {str(e)}")


# 交易日历
class AkStockCalDownloader(AkshareLoadAction):
    """
    下载Ak交易日历数据

    规则：
    1. 参数DOWNLOAD_ALL, 如果为True，则全量覆盖下载
    2. 每年11、12月下载下一年数据。
    """

    def __init__(self) -> None:
        self.gw = get_ak_gateway()  # 数据网关
        super().__init__()
        if not self.name:
            self.name = "AK 交易日历"
            self.log = logger.bind(action_name=self.name)   # 参数绑定
        self.DOWNLOAD_ALL = False    # 全量参数

    def _get_year_to_down(self):
        """
        获取需要下载的年份

        Args:
            无
        Returns:
            Union[str, None]: 需要下载的年份，如果不需要下载，则返回None
        """
        # 判断到底更新哪一年的数据
        # 如果这年有数据，且大于200，则不用更新
        today = tl.today()
        year = today[:4]
        month = today[4:6]

        engine = None
        try:
            engine = get_engine()
            Session = sessionmaker(bind=engine)
            session = Session()

            t_trade_calendar = DB_POOL.get("ods_akshare_tool_trade_date_hist_sina")

            if int(month) in [11, 12]:
                # 如果当前时间为11月或12月，则根据库中下一年的数据是否存在，判断是否要下载下一年数据
                count = session.query(t_trade_calendar).filter(t_trade_calendar.c.trade_date >= (str(int(
                    year) + 1)+"0101")).filter(t_trade_calendar.c.trade_date <= (str(int(year) + 1)+"1231")).count()
                if count < 200:
                    # 如果下一年库中下一年的日历数据少于200，则需要重新下载
                    return str(int(year) + 1)   # 下一年
                else:
                    return None
            else:
                # 如果当前日期不是11月、12月（年末），则根据库中下今年的数据是否存在，判断是否要下载今年数据
                count = session.query(t_trade_calendar).filter(t_trade_calendar.c.trade_date >= (
                    year+"0101")).filter(t_trade_calendar.c.trade_date <= (year+"1231")).count()
                # print(count)
                if count < 200:
                    return year     # 今年
                else:
                    return None
        except (DataException, SQLAlchemyError) as e:
            msg = f"获取数据时发生异常: {e}"
            self.log.error(msg)
            return None  # 根据函数定义，这里应该返回 None 或 str 类型，而不是 tl.Result
        finally:
            if engine:
                session.close()

    def extract_data(self) -> pd.DataFrame:
        data = self.gw.call(callback=ak.tool_trade_date_hist_sina)
        return data

    def transform_data(self, data: pd.DataFrame, year_to_down: str) -> pd.DataFrame:
        # 数据清洗
        data = data.astype({'trade_date': str})
        data["trade_date"] = data["trade_date"].apply(tl.d2dbstr)

        if not self.DOWNLOAD_ALL and year_to_down:
            self.log.debug(f"只更新{year_to_down}年数据")
            # 只保留这一年的数据
            start_dt = f"{year_to_down}0101"
            end_dt = f"{year_to_down}1231"
            data = data[(data['trade_date'] >= start_dt) & (data['trade_date'] <= end_dt)]
        return data

    def load_data(self, data: pd.DataFrame, year_to_down: str) -> tl.Result:
        # if self.DOWNLOAD_ALL is False or not year_to_down:
        #     self.log.info("不更新交易日历数据")
        #     return tl.Result(result=True, msg="No need to update data")
        engine = None
        try:
            engine = get_engine()
            Session = sessionmaker(bind=engine)
            session = Session()

            # 如果是全量更新:
            if self.DOWNLOAD_ALL:
                t_cal = DB_POOL.get("ods_akshare_tool_trade_date_hist_sina")
                # 全表删除
                session.query(t_cal).delete()
                session.commit()
                data.to_sql(name='ods_akshare_tool_trade_date_hist_sina', con=engine, if_exists='append', index=False)
                self.log.info(f"全量下载交易日历{data.shape[0]}条数据数据")
                return Result(result=True, msg="【全量】日历数据更新完毕")

            if year_to_down:
                # 仅删除这一年的数据
                start_dt = f"{year_to_down}0101"
                end_dt = f"{year_to_down}1231"
                t_cal = DB_POOL.get("ods_akshare_tool_trade_date_hist_sina")
                session.query(t_cal).filter(t_cal.c.trade_date >= start_dt).filter(
                    t_cal.c.trade_date <= end_dt).delete()
                session.commit()
                data.to_sql(name='ods_akshare_tool_trade_date_hist_sina', con=engine, if_exists='append', index=False)
                self.log.info(f"全量下载交易日历{data.shape[0]}条数据数据")
                return Result(result=True, msg="【全量】日历数据更新完毕")

            return tl.Result(result=True, msg="No need to update data")
        except DataException as dwe:
            msg = "Akshare获取数据异常，" + str(dwe)
            self.log.error(msg)
            return tl.Result(result=False, msg=msg)
        except SQLAlchemyError as sqle:
            msg = "SQL异常" + str(sqle)
            self.log.error(msg)
            return tl.Result(result=False, msg=msg)
        finally:
            if engine:
                session.close()

    def handle(self) -> bool:
        """数据处理函数，子类必须实现

        Returns:
            bool: 执行结果
        """
        self.log.info("Downloading Akshare 新浪交易日历")

        # 计算所需要的
        year_to_down = self._get_year_to_down()
        self.log.debug(f"year_to_down={year_to_down}")

        try:
            # 提取数据
            data = self.extract_data()
            if data is None:
                self.log.error("Failed to extract data")
                return tl.Result(result=False, msg="Failed to extract data")
            self.log.debug(f"Orginal data = {data.shape}")

            # 转换数据（清洗等）
            data_transformed = self.transform_data(data, year_to_down)
            if data_transformed is None:
                self.log.error("Failed to transform data")
                return tl.Result(result=False, msg="Failed to transform data")
            self.log.debug(f"Transformed data = {data_transformed.shape}")

            # 加载数据（存储）
            result = self.load_data(data_transformed, year_to_down)

            if result and result.result:
                self.log.info("Akshare 新浪交易日历 Data loaded successfully")
                return tl.Result(result=True, msg="Akshare 新浪交易日历 下载成功")
            else:
                self.log.error("Akshare 新浪交易日历 Data 下载失败！")
                return tl.Result(result=False, msg=f"Akshare 新浪交易日历 下载失败. {result.msg}")
        except Exception as e:
            self.log.exception("An error occurred during data handling")
            return tl.Result(result=False, msg=f"An error occurred during data handling | {str(e)}")


# 下载 上海交易所股票清单 数据 (stock_info_sh_name_code)
class AkStockInfoShNameCode(AkshareLoadAction):

    def __init__(self) -> None:
        super().__init__()
        if not self.name:
            self.name = "AK | 上海交易所股票清单"
            self.log = logger.bind(action_name=self.name)   # 参数绑定

    def handle(self) -> tl.Result:
        """ 下载沪市 """
        self.log.info("Downloading Akshare stock list | 上海交易所")

        try:
            # 提取数据
            data = self.extract_data()
            if data is None:
                self.log.error("Failed to extract data")
                return tl.Result(result=False, msg="Failed to extract data")

            # 转换数据（清洗等）
            data_transformed = self.transform_data(data)
            if data_transformed is None:
                self.log.error("Failed to transform data")
                return tl.Result(result=False, msg="Failed to transform data")

            # 加载数据（存储）
            res = self.load_data(data_transformed)

            # 返回一个具体的对象，表示操作成功
            if res and res.result is True:
                self.log.info(
                    "Downloading Akshare stock list | 上海交易所 successfully")
                return tl.Result(result=True, msg="Downloading Akshare stock list | 上海交易所 successfully")
            else:
                return res
        except Exception as e:
            self.log.exception("An error occurred during data handling")
            return tl.Result(result=False, msg=f"An error occurred during data handling | {str(e)}")

    def extract_data(self) -> pd.DataFrame:
        """ 获取 上海交易所 股票清单原始数据 """
        board_list = ["主板A股", "主板B股", "科创板"]
        df_list = []
        for board in board_list:
            df = None
            # 取得数据
            df = self.gw.call(
                callback=ak.stock_info_sh_name_code, symbol=board)
            if df is None:
                continue
            # 加入板块字段
            df["board"] = board
            df_list.append(df)
        return pd.concat(df_list)

    def transform_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """ 清洗 上海交易所 股票清单原始数据 """
        data = data.astype({'证券代码': str, "上市日期": str})
        data["上市日期"] = data["上市日期"].apply(tl.d2dbstr)

        data["证券代码"] = data["证券代码"].apply(lambda x: self.gw.symbol_exchange_2_tscode(x, exchange="SH"))
        column_names_mapping = {
            '证券代码': 'symbol',
            '证券简称': 'stock_name',
            '公司全称': 'total_name',
            '上市日期': 'ipo_date',
        }
        data = data.rename(columns=column_names_mapping)
        return data

    def load_data(self, data: pd.DataFrame) -> tl.Result:
        """ 存储 上海交易所 股票清单原始数据 """
        session = None
        try:
            engine = get_engine()
            Session = sessionmaker(bind=engine)
            session = Session()

            # 删除现有的数据
            t_ods_akshare_stock_info_sh_name_code = DB_POOL.get(
                "ods_akshare_stock_info_sh_name_code")
            session.query(t_ods_akshare_stock_info_sh_name_code).delete()
            session.commit()

            # 插入数据
            data.to_sql(name='ods_akshare_stock_info_sh_name_code',
                        con=engine, if_exists='append', index=False)

            return Result(True, "")
        except DataException as dwe:
            msg = "Akshare获取数据异常，" + str(dwe)
            self.log.error(msg)
            return tl.Result(result=False, msg=msg)
        except SQLAlchemyError as sqle:
            msg = "SQL异常" + str(sqle)
            self.log.error(msg)
            return tl.Result(result=False, msg=msg)
        finally:
            if session:  # Check if session is defined before closing
                session.close()


# 下载 北京交易所股票清单 数据 (stock_info_bj_name_code)
class AkStockInfoBjNameCode(AkshareLoadAction):

    def __init__(self) -> None:
        super().__init__()
        if not self.name:
            self.name = "AK | 北京交易所股票清单"
            self.log = logger.bind(action_name=self.name)   # 参数绑定

    def handle(self) -> tl.Result:
        """ 下载沪市 """
        self.log.info("Downloading 北京交易所 股票清单")

        try:
            # 提取数据
            data = self.extract_data()
            if data is None:
                self.log.error("Failed to extract data")
                return tl.Result(result=False, msg="Failed to extract data")

            # 转换数据（清洗等）
            data_transformed = self.transform_data(data)
            if data_transformed is None:
                self.log.error("Failed to transform data")
                return tl.Result(result=False, msg="Failed to transform data")

            # 加载数据（存储）
            res = self.load_data(data_transformed)

            # 返回一个具体的对象，表示操作成功
            if res and res.result is True:
                self.log.info(
                    "Downloading 北京交易所 股票清单 successfully")
                return tl.Result(result=True, msg="Downloading 北京交易所 股票清单 successfully")
            else:
                return res
        except Exception as e:
            self.log.exception("An error occurred during data handling")
            return tl.Result(result=False, msg=f"An error occurred during data handling | {str(e)}")

    def extract_data(self) -> pd.DataFrame:
        """ 获取 北京交易所 股票清单原始数据 """
        return self.gw.call(callback=ak.stock_info_bj_name_code)

    def transform_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """ 清洗 北京交易所 股票清单原始数据 """
        data = data.astype({'上市日期': str, "报告日期": str, "证券代码": str}) 
        column_names_mapping = {
            '证券代码': 'symbol',
            '证券简称': 'stock_name',
            '总股本': 'zgb',
            '流通股本': 'ltgb',
            '上市日期': 'ipo_date',
            '所属行业': 'sshy',
            '地区': 'dq',
            '报告日期': 'bgrq',
        }
        data["上市日期"] = data["上市日期"].apply(tl.d2dbstr)
        data["报告日期"] = data["报告日期"].apply(tl.d2dbstr)
        data["证券代码"] = data["证券代码"].apply(
            self.gw.symbol_exchange_2_tscode, exchange="BJ")
        data = data.rename(columns=column_names_mapping)
        try:
            data["zgb"] = data["zgb"].str.replace(",", "")
            data["tlgb"] = data["tlgb"].str.replace(",", "")
        except Exception:
            pass
        return data

    def load_data(self, data: pd.DataFrame) -> tl.Result:
        """ 存储 北京交易所 股票清单原始数据 """
        session = None
        try:
            engine = get_engine()
            Session = sessionmaker(bind=engine)
            session = Session()

            # 删除现有的数据
            t_ods_akshare_stock_info_bj_name_code = DB_POOL.get(
                "ods_akshare_stock_info_bj_name_code")
            session.query(t_ods_akshare_stock_info_bj_name_code).delete()
            session.commit()

            # 插入数据
            data.to_sql(name='ods_akshare_stock_info_bj_name_code',
                        con=engine, if_exists='append', index=False)

            return Result(True, "")
        except SQLAlchemyError as sqle:
            msg = "SQL异常" + str(sqle)
            self.log.error(msg)
            return tl.Result(result=False, msg=msg)
        finally:
            if session:  # Check if session is defined before closing
                session.close()


# 下载 深圳交易所股票清单 数据 (stock_info_bj_name_code)
class AkStockInfoSzNameCode(AkshareLoadAction):

    def __init__(self) -> None:
        super().__init__()
        if not self.name:
            self.name = "AK | 深圳交易所股票清单"
            self.log = logger.bind(action_name=self.name)   # 参数绑定

    def handle(self) -> tl.Result:
        self.log.info("Downloading 深圳交易所 股票清单")

        try:
            # 提取数据
            df_a = self.get_stock_info_a()
            df_b = self.get_stock_info_b()
            df_ab = self.get_stock_info_ab()
            data_transformed = pd.concat([df_a, df_b, df_ab])

            # 通用字段清洗
            data_transformed["ipo_date"] = data_transformed["ipo_date"].apply(tl.d2dbstr)   # 日期格式调整
            try:
                # 把千分位号删除
                data_transformed["zgb"] = data_transformed["zgb"].str.replace(",", "")
                data_transformed["tlgb"] = data_transformed["tlgb"].str.replace(",", "")
                data_transformed["symbol"] = pd.Series(data_transformed["symbol"]).apply(
                    self.gw.symbol_exchange_2_tscode, exchange="SZ")
            except Exception:
                pass

            if data_transformed is None:
                self.log.error("Failed to extract data")
                return tl.Result(result=False, msg="Failed to extract data")

            # data_transformed.to_csv("abc.csv", index=False)
            # print(data_transformed.head(2))
            # 加载数据（存储）
            res = self.load_data(data_transformed)

            # 返回一个具体的对象，表示操作成功
            if res and res.result is True:
                self.log.info(
                    "Downloading 深圳交易所 股票清单 successfully")
                return tl.Result(result=True, msg="Downloading 深圳交易所 股票清单 successfully")
            else:
                return res
        except Exception as e:
            self.log.exception("An error occurred during data handling")
            return tl.Result(result=False, msg=f"An error occurred during data handling | {str(e)}")

    def get_stock_info_a(self) -> pd.DataFrame:
        """ 下载沪市 """
        self.log.info("Downloading 深圳交易所（A股） 股票清单")
        # A股
        data = self.extract_data_bytype("A股列表")
        if data is None:
            self.log.error("Failed to extract data A股")
            return tl.Result(result=False, msg="Failed to extract data A股")
        # 转换数据（清洗等）
        data_transformed = self.transform_data_a(data)
        if data_transformed is None:
            self.log.error("Failed to transform data")
            return tl.Result(result=False, msg="Failed to transform data A股")

        return data_transformed

    def get_stock_info_b(self) -> pd.DataFrame:
        self.log.info("Downloading 深圳交易所（B股） 股票清单")
        # B股
        data = self.extract_data_bytype("B股列表")
        if data is None:
            self.log.error("Failed to extract data B股")
            return tl.Result(result=False, msg="Failed to extract data B股")
        # 转换数据（清洗等）
        data_transformed = self.transform_data_b(data)
        if data_transformed is None:
            self.log.error("Failed to transform data")
            return tl.Result(result=False, msg="Failed to transform data B股")

        return data_transformed

    def get_stock_info_ab(self) -> pd.DataFrame:
        self.log.info("Downloading 深圳交易所（AB股） 股票清单")
        # B股
        data = self.extract_data_bytype("AB股列表")
        if data is None:
            self.log.error("Failed to extract data AB股")
            return tl.Result(result=False, msg="Failed to extract data AB股")
        # 转换数据（清洗等）
        data_transformed = self.transform_data_ab(data)
        if data_transformed is None:
            self.log.error("Failed to transform data")
            return tl.Result(result=False, msg="Failed to transform data B股")

        return data_transformed

    def extract_data_bytype(self, type: str) -> pd.DataFrame:
        """ 获取 深圳交易所 股票清单原始数据 """
        return self.gw.call(callback=ak.stock_info_sz_name_code, symbol=type)

    def transform_data_a(self, data: pd.DataFrame) -> pd.DataFrame:
        """ 清洗 深圳交易所（A股） 股票清单原始数据 """
        data["stock_type"] = "A股"
        data = data.astype({'A股代码': str, "A股上市日期": str})
        column_names_mapping = {
            'A股代码': 'symbol',
            'A股简称': 'stock_name',
            'A股上市日期': 'ipo_date',
            'A股总股本': 'zgb',
            'A股流通股本': 'tlgb',
            '所属行业': 'sshy',
            '板块': 'board',
        }
        data = data.rename(columns=column_names_mapping)
        return data

    def transform_data_b(self, data: pd.DataFrame) -> pd.DataFrame:
        """ 清洗 深圳交易所（B股） 股票清单原始数据 """
        data["stock_type"] = "B股"
        data = data.astype({'B股代码': str, "B股上市日期": str})
        column_names_mapping = {
            'B股代码': 'symbol',
            'B股简称': 'stock_name',
            'B股上市日期': 'ipo_date',
            'B股总股本': 'zgb',
            'B股流通股本': 'tlgb',
            '所属行业': 'sshy',
            '板块': 'board',
        }
        data = data.rename(columns=column_names_mapping)
        return data

    def transform_data_ab(self, data: pd.DataFrame) -> pd.DataFrame:
        """ 清洗 深圳交易所（AB股） 股票清单原始数据 """
        data["stock_type"] = "AB股"
        data = data[['板块', "A股代码", "A股简称", 'A股上市日期', '所属行业', 'stock_type']]

        data["zgb"] = "0"
        data["tlgb"] = "0"
        data = data.astype({'A股代码': str, "A股上市日期": str})
        column_names_mapping = {
            'A股代码': 'symbol',
            'A股简称': 'stock_name',
            'A股上市日期': 'ipo_date',
            '所属行业': 'sshy',
            '板块': 'board',
        }
        data = data.rename(columns=column_names_mapping)
        return data

    def load_data(self, data: pd.DataFrame) -> tl.Result:
        """ 存储 深圳交易所 股票清单原始数据 """
        session = None
        try:
            engine = get_engine()
            Session = sessionmaker(bind=engine)
            session = Session()

            # 删除现有的数据
            t_ods_akshare_stock_info_bj_name_code = DB_POOL.get(
                "ods_akshare_stock_info_sz_name_code")
            session.query(t_ods_akshare_stock_info_bj_name_code).delete()
            session.commit()

            data.to_sql(name='ods_akshare_stock_info_sz_name_code',
                        con=engine, if_exists='append', index=False)

            return Result(True, "")
        except DataException as dwe:
            msg = "Akshare获取数据异常，" + str(dwe)
            self.log.error(msg)
            return tl.Result(result=False, msg=msg)
        except SQLAlchemyError as sqle:
            msg = "SQL异常" + str(sqle)
            self.log.error(msg)
            return tl.Result(result=False, msg=msg)
        finally:
            if session:  # Check if session is defined before closing
                session.close()


class AkshareStockList(AkshareLoadAction):
    """ 根据三个交易所股票清单生成汇总股票清单表 """

    def __init__(self) -> None:
        super().__init__()
        if not self.name:
            self.name = "AK | 合并股票清单"
            self.log = logger.bind(action_name=self.name)   # 参数绑定

    def handle(self) -> tl.Result:
        """ 合并股票清单列表 """
        session = None
        try:
            engine = get_engine()
            Session = sessionmaker(bind=engine)
            session = Session()

            with engine.connect() as connection:
                trans = connection.begin()
                connection.execute(text("delete from ods_akshare_stock_list"))
                connection.execute(text("insert into ods_akshare_stock_list select symbol,'SH',board from ods_akshare_stock_info_sh_name_code"))
                connection.execute(text("insert into ods_akshare_stock_list select symbol,'SZ',board from ods_akshare_stock_info_sz_name_code where stock_type<>'AB股'"))
                connection.execute(text("insert into ods_akshare_stock_list select symbol,'BJ','' from ods_akshare_stock_info_bj_name_code"))
                trans.commit()

            # 提交更改
            session.commit()

            count_of_stock = DbUtils.count(table_name="ods_akshare_stock_list")
            msg = f"A股股票清单合并完成，共计{count_of_stock}支股票"

            self.log.info(msg)
            return Result(True, msg)
        except (DataException, SQLAlchemyError) as dse:
            msg = "Akshare获取数据异常，" + str(dse)
            self.log.error(msg)
            return tl.Result(result=False, msg=msg)
        except Exception as err:
            msg = "异常" + str(err)
            self.log.error(msg)
            return tl.Result(result=False, msg=msg)
        finally:
            if session:  # Check if session is defined before closing
                session.close()


# 股票历史数据(东财)
class AkStockHistoryData(AkshareLoadAction):
    """
    股票历史数据(东财)

    DOC: https://lxhcvhnie6k.feishu.cn/docx/DrErdGaWBodRRIxFMVYcTB0rnBf#YBG6dncEmotMaLxbyJycHAQanCb

    实现需求：
    1. 存放包括 各交易所、各周期、各复权模式的数据
    2. 日期格式:yyyyMMdd, 股票代码:600016
    3. 股票清单从: ods_akshare_stock_list 表获取, 或从参数中传入 symbol_list
    4. 采用覆盖式更新数据

    按股票，逐一获取数据，并存储到数据库中


    p中的参数:
    - DOWNLOAD_ALL: bool [defualt: false]   是否全量下载
    - trade_date: str [default: None]       指定日期下载
    - start_date: str [default: None]       指定日期段下载,开始日期
    - end_date: str [default: None]         指定日期段下载,结束日期
    - symbol_list: list of str [dfault: None]   指定股票代码列表
    """

    def __init__(self) -> None:
        super().__init__()
        self.gw = get_ak_gateway()
        if not self.name:
            self.name = "AK | 股票历史日线数据(东财)"
            self.log = logger.bind(action_name=self.name)   # 参数绑定
        # adjust_list = ['none', 'qfq', 'hfq']    # 复权模式
        # period_list = ['daily', 'weekly', 'monthly']    # 数据周期

    # 获取全部股票代码
    def _query_symbol(self, stock_id_list: list = None):
        """
        从 ods_akshare_stock_list 表查询返回全部股票清单，返回格式 600016

        如果参数中有股票清单, 则返回symbol_list参数
        """
        gw = get_ak_gateway()
        if stock_id_list is not None:
            return [gw.tscode_2_symbol(stockid) for stockid in stock_id_list]

        # 从数据库表中查询
        try:
            engine = get_engine()
            Session = sessionmaker(bind=engine)

            with Session() as session:
                t_stock = DB_POOL.get("ods_akshare_stock_list")
                records = session.query(t_stock).all()

                # 假设 t_stock 对象有一个名为 "symbol" 的字段来存储股票代码
                symbol_list = [gw.tscode_2_symbol(record.stock_id) for record in records]

                return symbol_list
        except DataException as dwe:
            msg = "Akshare获取数据异常，" + str(dwe)
            self.log.error(msg)
            return None
        except SQLAlchemyError as sqle:
            msg = "SQL异常" + str(sqle)
            self.log.error(msg)
            return None

    def _print_p(self):
        """ 参数打印 """
        self.log.debug("-"*20)
        for p_name in self.p.keys():
            self.log.debug(f"{p_name} = {self.p.get(p_name)}")
        self.log.debug("-"*20)

    def extract_data(self, symbol: str) -> pd.DataFrame:
        """ 获取单个股票的数据 """
        data_list = []
        try:
            # 按不同时间线下载
            for period in self.p.get("period_list", ["daily"]):
                # 按不同复权模式下载
                for adjust_mode in self.p.get("adjust_list", [""]):
                    # 全量下载
                    if self.p.get("DOWNLOAD_ALL", False):
                        df = self.gw.call(callback=ak.stock_zh_a_hist, symbol=symbol, period=period, adjust=adjust_mode)
                    # 指定日期
                    elif self.p.get("trade_date", None):
                        df = self.gw.call(callback=ak.stock_zh_a_hist, symbol=symbol, period=period, start_date=self.p.get("trade_date"), end_date=self.p.get("trade_date"), adjust=adjust_mode)
                    # 指定日期段
                    elif self.p.get("start_date", None):
                        df = self.gw.call(callback=ak.stock_zh_a_hist, symbol=symbol, period=period, start_date=self.p.get("start_date"), end_date=self.p.get("end_date"), adjust=adjust_mode)
                    else:
                        self.log.error("未知时间模式")
                        return None
                    # 打标签
                    df["数据周期"] = period
                    df["复权模式"] = adjust_mode
                    data_list.append(df)
        except DataException as der:
            self.log.error(f"读取Aksahre失败，{str(der)}")
            return None

        if len(data_list) == 0:
            return None
        else:
            return pd.concat(data_list)

    def transform(self, data: str, symbol: str) -> pd.DataFrame:
        """ 数据清洗 """
        if data is None:
            return None
        if data.empty:
            return data

        try:
            # 替换 未复权
            mapping_adjust = {'': '不复权', 'qfq': '前复权', 'hfq': '后复权'}
            data['复权模式'] = data['复权模式'].map(mapping_adjust)

            # 字段整理
            data["证券代码"] = symbol
            data = data.astype({'日期': str, "证券代码": str})
            data["日期"] = data["日期"].apply(tl.d2dbstr)
            # 字段名更新
            data["证券代码"] = data["证券代码"].apply(lambda x: self.gw.symbol_exchange_2_tscode(x, exchange=self.gw.judge_stock_exchange(x)[0]))
            column_names_mapping = {
                '证券代码': 'symbol',
                '日期': 'trade_date',
                '开盘': 'p_open',
                '收盘': 'p_close',
                '最高': 'p_high',
                '最低': 'p_low',
                '成交量': 'volume',
                '成交额': 'amount',
                '振幅': 'volatility',
                '涨跌幅': 'price_chg',
                '涨跌额': 'price_chg_amt',
                '换手率': 'turnover',
                '数据周期': 'period',
                '复权模式': 'adjust'
            }
            data = data.rename(columns=column_names_mapping)
            return data
        except Exception:
            self.log.error(data)
            raise

    def save_to_db(self, stock_id, data: pd.DataFrame) -> tl.Result:
        """
        将获取到的股票数据保存到数据库中
        Args:
            stock_id (str): 股票代码, 600016格式
            data (pd.DataFrame): 获取到的股票数据
        Returns:
            tl.Result: 操作结果
        """
        if data is None or data.empty:
            self.log.warning(f"{stock_id} 数据为空")
            return tl.Result(result=True, msg="数据为空")

        ts_code = self.gw.symbol_exchange_2_tscode(stock_id, exchange=self.gw.judge_stock_exchange(stock_id)[0])
        session = None
        try:
            engine = get_engine()
            Session = sessionmaker(bind=engine)
            session = Session()

            # 删除现有的数据
            t_ods_akshare_stock_zh_a_hist = DB_POOL.get(
                "ods_akshare_stock_zh_a_hist")
            stmt = session.query(t_ods_akshare_stock_zh_a_hist).filter(
                t_ods_akshare_stock_zh_a_hist.c.symbol == ts_code)

            if self.p.get("DOWNLOAD_ALL", False):
                pass
            # 指定日期
            elif self.p.get("trade_date", None):
                stmt = stmt.filter(t_ods_akshare_stock_zh_a_hist.c.trade_date == self.p.get("trade_date"))
            # 指定日期段
            elif self.p.get("start_date", None):
                stmt = stmt.filter(t_ods_akshare_stock_zh_a_hist.c.trade_date >= self.p.get("start_date"))
                stmt = stmt.filter(t_ods_akshare_stock_zh_a_hist.c.trade_date <= self.p.get("end_date"))
            else:
                self.log.error("未知时间模式")
                return None

            stmt.delete()
            session.commit()

            # 插入数据
            data.to_sql(name='ods_akshare_stock_zh_a_hist',
                        con=engine, if_exists='append', index=False)

            return Result(True, "")
        except DataException as dwe:
            msg = "Akshare获取数据异常，" + str(dwe)
            self.log.error(msg)
            return tl.Result(result=False, msg=msg)
        except SQLAlchemyError as sqle:
            msg = "SQL异常" + str(sqle)
            self.log.error(msg)
            return tl.Result(result=False, msg=msg)
        finally:
            if session:  # Check if session is defined before closing
                session.close()

    def handle(self) -> bool:
        """
        获取股票历史数据

        根据股票清单，逐一股票获取数据（获取并存储）
        """
        # 参数
        self.log.info("下载股票存量数据 [数据源：东财]")
        self.p["adjust_list"] = ['', 'qfq', 'hfq']    # 复权模式
        # self.p["period_list"] = ['daily', 'weekly', 'monthly']    # 数据周期
        self.p["period_list"] = ['daily']    # 数据周期
        self._print_p()

        # 待下载的股票代码
        symbol_list = self._query_symbol(self.p.get("symbol_list"))
        self.log.info(f"拟下载{len(symbol_list)}支股票")
        for idx, symbol in enumerate(symbol_list, start=1):
            self.log.info(f"[{idx} / {len(symbol_list)}] {symbol} : ")
            data = self.extract_data(symbol=symbol)
            # self.log.info(data)
            transformed_data = self.transform(data, symbol)
            # self.log.info(transformed_data)
            result = self.save_to_db(symbol, transformed_data)
            if not result or not result.result:
                msg = f"{symbol} 下载失败 "
                self.log.error(msg)
                return tl.Result(result=False, msg=msg)
        self.log.info("全部下载完毕")

        return tl.Result(result=True, msg="全部股票日线数据下载完毕")
