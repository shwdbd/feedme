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
from com.wdbd.fd.model.dt_model import AbstractAction, ActionConfig
from com.wdbd.fd.common.tl import Result
from com.wdbd.fd.services.gateway.ak_gateway import get_ak_gateway, DataException
import akshare as ak
from com.wdbd.fd.model.db import get_engine, table_objects_pool as DB_POOL
from sqlalchemy.orm import sessionmaker
import com.wdbd.fd.common.tl as tl
from sqlalchemy.exc import SQLAlchemyError as SQLAlchemyError
from loguru import logger
import pandas as pd


# 市场总貌|上海证券交易所
class Ak_SSE_Summary(AbstractAction):
    """
    市场总貌|上海证券交易所

    DOC: https://lxhcvhnie6k.feishu.cn/docx/DrErdGaWBodRRIxFMVYcTB0rnBf#M6zmdZRMJotFngx9DTOcPCnrnhf
    """

    def __init__(self) -> None:
        super().__init__()
        self.gw = get_ak_gateway()  # 数据网关
        if not self.name:
            self.name = "AK 上海证券交易所|市场总貌"
            self.log = logger.bind(action_name=self.name)   # 参数绑定

    def check_environment(self) -> bool:
        """检查环境，检查当前是否可以进行数据下载

        通常子类中会检查需要下载的数据是否已准备好
        Returns:
            bool: 检查结果
        """
        return Result()

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
            data["trade_date"] = trade_date
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

            # 删除现有的数据
            t_ods_akshare_stock_sse_summary = DB_POOL.get("ods_akshare_stock_sse_summary")
            session.query(t_ods_akshare_stock_sse_summary).filter(t_ods_akshare_stock_sse_summary.c.trade_date == trade_date).delete()
            session.commit()

            # 写入数据库, Write to the database
            data.to_sql(name='ods_akshare_stock_sse_summary', con=engine, if_exists='append', index=False)

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
        # self.log.info("下载 Akshare 市场总貌|上海证券交易所 概要数据")
        # # 提取数据
        # data = self.extract_data()

        # # 转换数据（清洗等）
        # data_transformed = self.transform_data(data)

        # # 加载数据（存储）
        # self.load_data(data_transformed)

        # return tl.Result()
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
            self.load_data(data_transformed)
            self.log.info("Data loaded successfully")

            return tl.Result(result=True, msg="Downloading Akshare market overview | SSE summary data successfully")  # 返回一个具体的对象，表示操作成功
        except Exception as e:
            self.log.exception("An error occurred during data handling")
            return tl.Result(result=False, msg=f"An error occurred during data handling | {str(e)}")

    def rollback(self) -> bool:
        """错误发生时，回滚动作函数

        Returns:
            bool: 回滚操作执行结果
        """
        return Result()


# 交易日历
class Ak_Stock_Cal(AbstractAction):
    """
    交易日历

    DOC: https://lxhcvhnie6k.feishu.cn/docx/DrErdGaWBodRRIxFMVYcTB0rnBf#part-I36ndQh0Fo3d4sxyUvCcZeg2nxc
    """

    def __init__(self) -> None:
        self.gw = get_ak_gateway()  # 数据网关
        self.DOWNLOAD_ALL = False    # 全量参数
        super().__init__()
        if not self.name:
            self.name = "AK 交易日历"
            self.log = logger.bind(action_name=self.name)   # 参数绑定

    def check_environment(self) -> bool:
        """检查环境，检查当前是否可以进行数据下载

        通常子类中会检查需要下载的数据是否已准备好
        Returns:
            bool: 检查结果
        """
        return Result()

    def _get_year_to_down(self, db_session):
        # 判断到底更新哪一年的数据
        # 如果这年有数据，且大于200，则不用更新
        year_to_down = None   # 拟下载的数据年份
        today = tl.today()
        year = today[:4]
        month = today[4:6]

        t_cal = DB_POOL.get("ods_akshare_tool_trade_date_hist_sina")

        if int(month) in [11, 12]:
            count = db_session.query(t_cal).filter(t_cal.c.trade_date >= (str(int(year) + 1)+"0101")).filter(t_cal.c.trade_date <= (str(int(year) + 1)+"1231")).count()
            # print(count)
            if count < 200:
                year_to_down = str(int(year) + 1)   # 下一年 
        else:
            count = db_session.query(t_cal).filter(t_cal.c.trade_date >= (year+"0101")).filter(t_cal.c.trade_date <= (year+"1231")).count()
            # print(count)
            if count < 200:
                year_to_down = year     # 今年
        # print("year_to_down = " + year_to_down)
        return year_to_down

    def handle(self) -> bool:
        """数据处理函数，子类必须实现

        Returns:
            bool: 执行结果
        """
        # TEST 待测试
        # 用于单独运行时候
        if self.log is None:
            self.log = tl.get_action_logger(action_name=self.name)
            # self.log = tl.get_logger()

        self.log.info("下载 股票交易日历")
        try:
            engine = get_engine()
            Session = sessionmaker(bind=engine)
            session = Session()

            if self.DOWNLOAD_ALL is False:
                year_to_down = self._get_year_to_down(session)     # 判断是否要更新数据
                self.log.info("更新数据年份：" + str(year_to_down))

            # 取得全量数据
            df = self.gw.call(callback=ak.tool_trade_date_hist_sina)
            # 数据清洗
            df = df.astype({'trade_date': str})
            df["trade_date"] = df["trade_date"].apply(tl.d2dbstr)
            # print(df)

            if df.empty:    # 如果返回为空
                return Result(result=False, msg="数据返回为空！")
            # 过滤符合条件的df数据
            if self.DOWNLOAD_ALL:
                # 全量下载，现删除现有数据
                t_cal = DB_POOL.get("ods_akshare_tool_trade_date_hist_sina")
                session.query(t_cal).delete()
                session.commit()
            elif year_to_down is not None:
                # 过滤后只剩余特定年饭的数据
                self.log.debug("只更新{0}年数据".format(year_to_down))
                start_dt = "{0}0101".format(year_to_down)
                end_dt = "{0}1231".format(year_to_down)
                t_cal = DB_POOL.get("ods_akshare_tool_trade_date_hist_sina")
                session.query(t_cal).filter(t_cal.c.trade_date >= start_dt).filter(t_cal.c.trade_date <= end_dt).delete()
                session.commit()
                # df = df.astype({'trade_date': str})
                df = df[(df['trade_date'] >= start_dt) & (df['trade_date'] <= end_dt)]
            else:
                # 不更新本地数据
                df = None

            # 写入数据库
            if df is not None:
                df.to_sql(name='ods_akshare_tool_trade_date_hist_sina', con=engine, if_exists='append', index=False)
                self.log.info("下载交易日历{0}条数据数据".format(df.shape[0]))
            else:
                self.log.info("不更新交易日历数据")

            return Result()
        except DataException as dwe:
            msg = "Akshare获取数据异常，" + str(dwe)
            self.log.error(msg)
            return tl.Result(result=False, msg=msg)
        except SQLAlchemyError as sqle:
            msg = "SQL异常" + str(sqle)
            self.log.error(msg)
            return tl.Result(result=False, msg=msg)
        finally:
            session.close()

    def rollback(self) -> bool:
        """错误发生时，回滚动作函数

        Returns:
            bool: 回滚操作执行结果
        """
        return Result()


# 股票清单
class Ak_Stock_List(AbstractAction):
    """
    股票清单

    DOC: https://lxhcvhnie6k.feishu.cn/docx/DrErdGaWBodRRIxFMVYcTB0rnBf#MLO3d1sYCoOzpMxpyXYcLFuJnKd
    """

    def __init__(self) -> None:
        self.name = "股票清单"
        self.gw = get_ak_gateway()  # 数据网关
        self.DOWNLOAD_ALL = True    # 全量参数
        super().__init__()

    def check_environment(self) -> bool:
        """检查环境，检查当前是否可以进行数据下载

        通常子类中会检查需要下载的数据是否已准备好
        Returns:
            bool: 检查结果
        """
        return Result()

    def handle(self) -> bool:
        """数据处理函数，子类必须实现

        Returns:
            bool: 执行结果
        """
        # TEST 待测试
        # 用于单独运行时候
        if self.log is None:
            self.log = tl.get_action_logger(action_name=self.name)
            # self.log = tl.get_logger()

        self.log.info("下载 股票交易日历")
        try:
            engine = get_engine()
            Session = sessionmaker(bind=engine)
            session = Session()

            # 刷新sh
            self.update_sh(engine)
            # 刷新sz
            self.update_sz(engine)
            # 刷新bj
            self._update_bj(engine)

            # TODO 更新汇总清单

            return Result()
        except DataException as dwe:
            msg = "Akshare获取数据异常，" + str(dwe)
            self.log.error(msg)
            return tl.Result(result=False, msg=msg)
        except SQLAlchemyError as sqle:
            msg = "SQL异常" + str(sqle)
            self.log.error(msg)
            return tl.Result(result=False, msg=msg)
        finally:
            session.close()

    # 刷新北京交易所数据
    def _update_bj(self, engine):
        Session = sessionmaker(engine)
        session = Session()

        t_sh = DB_POOL.get("ods_akshare_stock_info_bj_name_code")
        # 清空数据库
        session.query(t_sh).delete()
        session.commit()

        # 取得数据
        df = self.gw.call(callback=ak.stock_info_bj_name_code)
        # 数据清洗
        df = df.astype({'证券代码': str, "上市日期": str, "报告日期": str})
        column_names = {'证券代码': 'symbol',
                        '证券简称': 'stock_name',
                        '总股本': 'zgb',
                        '流通股本': 'ltgb',
                        '上市日期': 'ipo_date',
                        '所属行业': 'sshy',
                        '地区': 'dq',
                        '报告日期': 'bgrq',
                        }
        df["上市日期"] = df["上市日期"].apply(tl.d2dbstr)
        df["报告日期"] = df["报告日期"].apply(tl.d2dbstr)
        df["证券代码"] = df["证券代码"].apply(self.gw.symbol_exchange_2_tscode, exchange="BJ")
        df = df.rename(columns=column_names)
        try:
            df["zgb"] = df["zgb"].str.replace(",", "")
            df["tlgb"] = df["tlgb"].str.replace(",", "")
        except Exception:
            pass
        # print(df)

        if df is not None:
            df.to_sql(name='ods_akshare_stock_info_bj_name_code', con=engine, if_exists='append', index=False)
            self.log.info("下载北交所股票{0}条数据数据".format(df.shape[0]))
        session.close()

    # 刷新上交所数据
    def update_sh(self, engine):
        Session = sessionmaker(engine)
        session = Session()

        t_sh = DB_POOL.get("ods_akshare_stock_info_sh_name_code")
        # 清空数据库
        session.query(t_sh).delete()
        session.commit()

        # 轮询下载几个板块
        board_list = ["主板A股", "主板B股", "科创板"]
        for board in board_list:
            # 取得数据
            df = self.gw.call(callback=ak.stock_info_sh_name_code, symbol=board)
            # 数据清洗
            df["board"] = board
            df = df.astype({'证券代码': str, "上市日期": str})
            column_names = {'证券代码': 'symbol',
                            '证券简称': 'stock_name',
                            '公司全称': 'total_name',
                            '上市日期': 'ipo_date',
                            }
            df["上市日期"] = df["上市日期"].apply(tl.d2dbstr)
            df["证券代码"] = df["证券代码"].apply(self.gw.symbol_exchange_2_tscode, exchange="SH")
            df = df.rename(columns=column_names)
            # print(df)

            if df is not None:
                df.to_sql(name='ods_akshare_stock_info_sh_name_code', con=engine, if_exists='append', index=False)
                self.log.info("下载上交所股票{0}条数据数据 {1}".format(df.shape[0], board))
        session.close()

    # 刷新深圳交所数据
    def update_sz(self, engine):
        Session = sessionmaker(engine)
        session = Session()

        t_sz = DB_POOL.get("ods_akshare_stock_info_sz_name_code")
        # 清空数据库
        session.query(t_sz).delete()
        session.commit()

        # 轮询下载几个板块
        # stock_type_list = ["A股列表", "B股列表", "CDR列表", "AB股列表"]
        stock_type_list = ["A股列表", "B股列表", "AB股列表"]
        for stock_type in stock_type_list:
            # 取得数据
            df = self.gw.call(callback=ak.stock_info_sz_name_code, symbol=stock_type)
            # print(df)
            # 数据清洗
            df["stock_type"] = stock_type.replace("列表", "")
            # 根据不同种类，进行分别处理
            if stock_type in ["A股列表"]:
                df = df.astype({'A股代码': str, "A股上市日期": str})
                column_names = {'A股代码': 'symbol',
                                'A股简称': 'stock_name',
                                'A股上市日期': 'ipo_date',
                                'A股总股本': 'zgb',
                                'A股流通股本': 'tlgb',
                                '所属行业': 'sshy',
                                '板块': 'board',
                                }
                df = df.rename(columns=column_names)
            elif stock_type in ["AB股列表"]:
                df = df[['板块', "A股代码", "A股简称", 'A股上市日期', '所属行业', 'stock_type']]
                df["zgb"] = "0"
                df["tlgb"] = "0"
                df = df.astype({'A股代码': str, "A股上市日期": str})
                column_names = {'A股代码': 'symbol',
                                'A股简称': 'stock_name',
                                'A股上市日期': 'ipo_date',
                                '所属行业': 'sshy',
                                '板块': 'board',
                                }
                df = df.rename(columns=column_names)
            elif stock_type in ["B股列表"]:
                df = df.astype({'B股代码': str, "B股上市日期": str})
                column_names = {'B股代码': 'symbol',
                                'B股简称': 'stock_name',
                                'B股上市日期': 'ipo_date',
                                'B股总股本': 'zgb',
                                'B股流通股本': 'tlgb',
                                '所属行业': 'sshy',
                                '板块': 'board',
                                }
                df = df.rename(columns=column_names)
            # print(df.head())
            df["ipo_date"] = df["ipo_date"].apply(tl.d2dbstr)
            df["symbol"] = df["symbol"].apply(self.gw.symbol_exchange_2_tscode, exchange="SZ")
            try:
                df["zgb"] = df["zgb"].str.replace(",", "")
                df["tlgb"] = df["tlgb"].str.replace(",", "")
            except Exception:
                pass
            # print(df)

            if df is not None:
                df.to_sql(name='ods_akshare_stock_info_sz_name_code', con=engine, if_exists='append', index=False)
                self.log.info("下载 深圳 交易所股票{0}条数据数据 <{1}>".format(df.shape[0], stock_type))
        session.close()

    def rollback(self) -> bool:
        """错误发生时，回滚动作函数

        Returns:
            bool: 回滚操作执行结果
        """
        return Result()


# 股票历史数据(东财)
class AkStockHistoryData(AbstractAction):
    """
    股票历史数据(东财)

    DOC: https://lxhcvhnie6k.feishu.cn/docx/DrErdGaWBodRRIxFMVYcTB0rnBf#YBG6dncEmotMaLxbyJycHAQanCb

    实现需求：
    1. 存放包括 各交易所、各周期、各复权模式的数据
    2. 日期格式:yyyyMMdd, 股票代码:600016
    3. 股票清单从: ods_akshare_stock_list 表获取
    4. 采用覆盖式更新数据

    p中的参数：
    - DOWNLOAD_ALL: bool [defualt: false]   是否全量下载
    - trade_date: str [default: None]       指定日期下载
    - start_date: str [default: None]       指定日期段下载,开始日期
    - end_date: str [default: None]         指定日期段下载,结束日期
    - symbol_list: list of str [dfault: None]   指定股票代码列表
    """

    def __init__(self) -> None:
        self.name = "交易日历"
        self.gw = get_ak_gateway()  # 数据网关
        # 初始化Action日志
        self.__init_log()
        super().__init__()

    def __init_log():
        # 初始化Action日志
        pass

    def check_environment(self) -> bool:
        return Result()

    # 获取全部股票代码
    def _query_symol(self):
        """
        从 ods_akshare_stock_list 表查询返回全部股票清单，格式 600016
        
        如果参数中有, 则返回symbol_list参数
        """
        # TODO 待实现
        if self.p.get("symbol_list", None) is not None:
            return self.p.get("symbol_list")
        else:
            # 从数据库表中查询
            try:
                engine = get_engine()
                Session = sessionmaker(bind=engine)
                session = Session()

                t_stock = DB_POOL.get("ods_akshare_stock_list")
                records = session.query(t_stock).all()
                print(records)

                return []
            except DataException as dwe:
                msg = "Akshare获取数据异常，" + str(dwe)
                self.log.error(msg)
                return tl.Result(result=False, msg=msg)
            except SQLAlchemyError as sqle:
                msg = "SQL异常" + str(sqle)
                self.log.error(msg)
                return tl.Result(result=False, msg=msg)
            finally:
                session.close()
        

    def handle(self) -> bool:
        """数据处理函数，子类必须实现

        Returns:
            bool: 执行结果
        """
        if self.log is None:
            self.log = tl.get_action_logger(action_name=self.name)
            # self.log = tl.get_logger()

        # 参数
        adjust_list = ['none', 'qfq', 'hfq']    # 复权模式
        period_list = ['daily', 'weekly', 'monthly']    # 数据周期

        self.log.info("下载股票存量数据 [数据源：东财]")
        p_DOWNLOAD_ALL = self.p.get("DOWNLOAD_ALL", False)
        p_trade_date = self.p.get("trade_date", None)
        p_start_date = self.p.get("start_date", None)
        p_end_date = self.p.get("end_date", None)
        self.log.debug("DOWNLOAD_ALL= {0}".format(p_DOWNLOAD_ALL))
        self.log.debug("trade_date= {0}".format(p_trade_date))
        self.log.debug("start_date= {0}".format(p_start_date))
        self.log.debug("end_date= {0}".format(p_end_date))

        try:
            engine = get_engine()
            Session = sessionmaker(bind=engine)
            session = Session()

            symbol_list = self._query_symol()   # TODO 获取全部股票代码
            for symbol in symbol_list:
                # 按需要处理的日期数据，分为三种模式进行处理
                # TODO 按需删除处理
                self._remove_data(symbol=symbol, trade_date=p_trade_date, start_date=p_start_date, end_date=self.p["end_date"])

                for period in period_list:
                    for adjust in adjust_list:
                        if p_DOWNLOAD_ALL:
                            # 全量下载
                            df = ak.stock_zh_a_hist(symbol=symbol, period=period, adjust=adjust)
                            self.log.debug("下载 {symbol} 全日期 数据 [复权={adjust}, 周期={period}]".format(symbol=symbol, period=period, adjust=adjust))
                        elif self.p["start_date"] and self.p["end_date"]:
                            # 规定起止日期的情况:
                            df = ak.stock_zh_a_hist(symbol=symbol, period=period, start_date=p_start_date, end_date=p_end_date, adjust=adjust)
                            self.log.debug("下载 {symbol} 数据 [复权={adjust}, 周期={period}, 日期: {start_date} ~ {end_date}]".format(symbol=symbol, period=period, adjust=adjust, start_date=p_start_date, end_date=p_end_date))
                        else:
                            # 特定日期下载
                            df = ak.stock_zh_a_hist(symbol=symbol, period=period, start_date=p_trade_date, end_date=p_trade_date, adjust=adjust)
                            self.log.debug("下载 {symbol} 数据 [复权={adjust}, 周期={period}, 日期: {trade_date}]".format(symbol=symbol, period=period, adjust=adjust, trade_date=p_trade_date))
                        # TODO 数据清理
                        df = self._data_clean(df)
                        # TODO 写入数据库
                        self._save_to_db(df)
                self.log.debug("股票{symbol} 完成 ... ".format(symbol=symbol))

            self.log.info("股票历史数据全部下载完成")

            return Result()
        except DataException as dwe:
            msg = "Akshare获取数据异常，" + str(dwe)
            self.log.error(msg)
            return tl.Result(result=False, msg=msg)
        except SQLAlchemyError as sqle:
            msg = "SQL异常" + str(sqle)
            self.log.error(msg)
            return tl.Result(result=False, msg=msg)
        finally:
            session.close()

    def rollback(self) -> bool:
        """错误发生时，回滚动作函数

        Returns:
            bool: 回滚操作执行结果
        """
        return Result()


if __name__ == "__main__":
    action = Ak_SSE_Summary()
    res = action.handle()
    print(res.result)


# if __name__ == "__main__":
#     # 股票存量下载
#     cfg = ActionConfig()
#     cfg.p["DOWNLOAD_ALL"] = True
#     action = AkStockHistoryData()
#     action.set_action_parameters(cfg)
#     action.handle()


# if __name__ == "__main__":
    # # ENVIRONMENT = ""
    # # 
    # action = Ak_SSE_Summary()
    # res = action.handle()
    # print(res.result)

    # # tl.get_action_logger("ABC").info("Action日志")

    # # 下载股票交易日历
    # action = Ak_Stock_Cal()
    # res = action.handle()
    # print(res.result)

    # # 股票清单
    # action = Ak_Stock_List()
    # res = action.handle()
    # print(res.result)

    # stock_type_list = ["A股列表", "B股列表", "CDR列表", "AB股列表"]
    # gw = get_ak_gateway()
    # df = gw.call(callback=ak.stock_info_bj_name_code)
    # print(df.head())
    # # for type in stock_type_list:
    # #     df = gw.call(callback=ak.stock_info_sz_name_code, symbol=type)
    # #     print(df.head(3))
