#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   ak_gateway.py
@Time    :   2024/01/30 16:29:17
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   Akshare数据网关
'''
import socket
import logging.config
from abc import ABC, abstractmethod
import requests
from com.wdbd.fd.common.tl import ENVIRONMENT, d2viewstr
from com.wdbd.fd.services.gateway import DataException


class AkshareGateWayError(Exception):
    """自定义的AkshareGateWay错误类"""

    def __init__(self, message="Akshare 网关错误", code=0):
        """
        初始化异常类实例
        Args:
            message (str, optional): 异常信息. 默认为 "Akshare 网关错误".
            code (int, optional): 异常码. 默认为 0.
            *args: 其他初始化参数.
            **kwargs: 其他初始化参数.
        Returns:
            None
        """
        self.message = message
        super().__init__(message)
        self.code = code

    def __str__(self):
        """
        返回异常信息的字符串表示形式，格式为：异常信息（错误码：错误码值）。

        Args:
            无
        Returns:
            str: 异常信息的字符串表示形式，格式为：异常信息（错误码：错误码值）。
        """
        return f"{self.message} (Code: {self.code})"


def get_ak_gateway():
    """
    获取Akshare网关对象实例。使用单例模式以避免重复创建对象，同时增加了异常处理逻辑。

    Args:
        无
    Returns:
        AkshareGateWay: AkshareGateWay对象实例
    Raises:
        AkshareGateWayError: 如果无法创建AkshareGateWay对象，将抛出此错误。
    """
    # # 采用单例模式
    # try:
    #     if not hasattr(get_ak_gateway, "_instance"):
    #         get_ak_gateway._instance = AkshareGateWay()
    #     return get_ak_gateway._instance
    # except Exception as e:
    #     # 自定义异常处理，提供更友好的错误信息
    #     error_message = f"无法创建AkshareGateWay对象: {str(e)}"
    #     raise AkshareGateWayError(error_message)
    # 采用单例模式
    _instance = "__instance"
    try:
        if not hasattr(get_ak_gateway, _instance):
            setattr(get_ak_gateway, _instance, AkshareGateWay())
        return getattr(get_ak_gateway, _instance)
    except Exception as e:
        # 自定义异常处理，提供更友好的错误信息
        error_message = f"无法创建AkshareGateWay对象: {str(e)}"
        raise AkshareGateWayError(error_message) from e


class AbstarctAkshareGateWay(ABC):
    """ 抽象Akshare网关类 """    

    @abstractmethod
    def symbol_2_tscode(self, symbol) -> str:
        """
        将股票代码从sh600016格式转换为600016.SH格式。
        
        Args:
            symbol (str): 待转换的股票代码，格式为sh600016。
        
        Returns:
            str: 转换后的股票代码，格式为600016.SH。
        
        """


class AkshareGateWay(AbstarctAkshareGateWay):
    """ Akshare 数据网关
    目前只提供格式转换功能
    """

    def __init__(self):
        self.gw_logger = self._init_log_gw()     # 加载专用日志

    def standardize_symbol(self, symbol: str) -> str:
        """
        标准化资产ID字符串。

        Args:
            symbol (str): 待标准化的资产ID字符串, 格式为 600016.SH
        Returns:
            str: 标准化后的资产ID字符串, 格式为 600016。

        """
        if "." in symbol:
            return symbol[: symbol.find(".")]
        else:
            return symbol

    def _standardize_date(self, date: str) -> str:
        """ 标准化入参, 日期字段 """
        if "-" in date:
            return date
        else:
            return d2viewstr(date)

    def call(self, callback, *args, **kargs):
        """ Akshare API调用

        Args:
            callback (function): 调用的API，如 ak.stock_zh_a_hist

        Raises:
            DataException: 调用发生异常

        Returns:
            pd.DataFrame: 取得的数据集
        """
        # 入参校验
        if "symbol" in kargs:
            kargs['symbol'] = self.standardize_symbol(kargs['symbol'])
        elif "start_date" in kargs:
            kargs['start_date'] = self._standardize_date(kargs['start_date'])
        elif "end_date" in kargs:
            kargs['end_date'] = self._standardize_date(kargs['end_date'])

        try:
            df = callback(*args, **kargs)
            # 登记API日志
            # 入参控制，日期型号，统一成 yyyy-MM-dd
            self.gw_logger.debug("接口=%s, 参数[%s], 结果= SUCCESS", callback.__name__, str(kargs))
            # 数据清洗(无)
            return df
        except Exception as err:
            self.gw_logger.error("接口=%s, 参数[%s], 结果= FAILED", callback.__name__, str(kargs))
            raise DataException(message=f"Akshare访问异常, {err}") from err

    def _symbol_2_default(self, symbol: str) -> str:
        """将sh600016格式转为600016.SH格式

        Args:
            symbol (str): 600016.SH 格式的资产编号

        Returns:
            str: 600016格式的资产编号
        """
        # if not symbol or len(symbol) < 8:
        #     return symbol

        # return "{s}.{exchange}".format(s=symbol[2:], exchange=symbol[:2].upper())
        if not symbol or len(symbol) < 8:
            raise ValueError("股票代码格式不正确，应至少包含8个字符")

        exchange_prefix = symbol[:2].lower()
        if exchange_prefix not in {'sh', 'sz'}:
            raise ValueError("股票代码的交易所前缀不正确，应为'sh'或'sz'")

        stock_code = symbol[2:]
        if not stock_code.isdigit() or len(stock_code) != 6:
            raise ValueError("股票代码部分应只包含6位数字")

        return f"{stock_code}.{exchange_prefix.upper()}"

    def symbol_2_tscode(self, symbol) -> str:
        """
        将股票代码从sh600016格式转换为600016.SH格式。
        
        Args:
            symbol (str): 待转换的股票代码，格式为sh600016。
        
        Returns:
            str: 转换后的股票代码，格式为600016.SH。
        
        """
        if not symbol or len(symbol) < 8:
            print("股票代码格式不正确，应至少包含8个字符")
            return symbol

        exchange_prefix = symbol[:2]
        if exchange_prefix.lower() not in {'sh', 'sz'}:
            raise ValueError("股票代码的交易所前缀不正确，应为'sh'或'sz'")

        stock_code = symbol[2:]
        if not stock_code.isdigit() or len(stock_code) != 6:
            raise ValueError("股票代码部分应只包含6位数字")

        return f"{stock_code}.{exchange_prefix.upper()}"

    def symbol_exchange_2_tscode(self, symbol, exchange) -> str:
        """
        将股票代码与交易所信息拼接成完整的股票代码（包括后缀）。
        
        Args:
            symbol (str): 股票代码，如 "600016"。
            exchange (str): 交易所信息，如 "SH"。
        
        Returns:
            str: 拼接后的完整股票代码，格式为 "{股票代码}.{交易所}"，如 "600016.SH"。
        
        """
        # 添加输入验证
        if not isinstance(symbol, str) or not symbol.isdigit() or len(symbol) != 6:
            return symbol  # 或者可以抛出异常或返回特殊值以指示错误
        if not isinstance(exchange, str) or not exchange.isalpha() or len(exchange) != 2:
            return symbol  # 或者可以抛出异常或返回特殊值以指示错误

        # 拼接股票代码和交易所信息
        return f"{symbol}.{exchange}"

    def tscode_2_symbol(self, tscode: str) -> str:
        """
        将股票交易代码转换为股票代码。
        
        Args:
            tscode (str): 股票交易代码，格式为“六位数字.交易所后缀”。
        
        Returns:
            str: 股票代码，格式为“六位数字”。
        
        """
        # try:
        #     if not tscode or len(tscode) < 9:
        #         return tscode
        #     else:
        #         return tscode[:6]
        # except Exception as e:
        #     print(f"转换失败，tscode={tscode}, err = {e}")
        #     return tscode
        if not tscode or len(tscode) < 9:
            return tscode
        else:
            return tscode[:6]

    # 加载专用日志管理器
    def _init_log_gw(self):
        """
        初始化日志管理器。
        
        Args:
            无参数。
        
        Returns:
            返回 `logging.Logger` 类型的对象，表示名为 'akshare' 的日志记录器。
        
        """
        if ENVIRONMENT == 'test':
            config_file_path = r"src/test/config/gw/akshare.conf"
        else:
            config_file_path = r"src/main/config/gw/akshare.conf"
        logging.config.fileConfig(config_file_path, disable_existing_loggers=False)
        return logging.getLogger('akshare')

    def check_connection(self) -> bool:
        """ 检测连接 """
        try:
            response = requests.get("https://akshare.akfamily.xyz/", timeout=5)  # 设置超时时间，避免长时间等待
            return response.status_code == 200
        except (requests.exceptions.RequestException, socket.timeout):
            return False

    def judge_stock_exchange(self, stock_code: str) -> tuple[str, str]:
        """
        根据A股股票代码判断其所属的交易所和板块

        参数:
            stock_code (str): A股股票代码，如'600000'或'000001'

        返回:
            tuple[str, str]: 交易所代码和板块类型，例如('SH', '主板')或('SZ', '创业板')
        """
        if not isinstance(stock_code, str) or len(stock_code) != 6:
            return "无效的股票代码", ""
        if not stock_code.isdigit():
            return "无效的股票代码", ""

        # 提取股票代码的前缀
        first_digit = stock_code[:1]
        prefix = stock_code[:3]

        # 初始化返回值
        exchange, board = "", ""

        # 判断所属交易所和板块
        if first_digit == '6':
            exchange = "SH"  # 上海证券交易所
            if prefix.startswith('60'):
                board = "主板"
            elif prefix.startswith('68'):
                board = "科创板"
        elif first_digit == '0':
            exchange = "SZ"  # 深圳证券交易所
            if prefix.startswith('00'):
                board = "主板/中小板"  # 由于中小板已经合并到主板，可以合并标注
            elif prefix.startswith('03'):  # 实际上并不存在03开头的深交所股票代码，此处仅作为示例
                board = "未知板块"  # 实际情况下，应处理或删除不存在的代码段
        elif first_digit == '3':
            exchange = "SZ"  # 深圳证券交易所
            board = "创业板"
        elif first_digit in ['4', '8']:
            # 注意：此处简化了北京证券交易所股票代码的判断逻辑，实际上需要更复杂的判断条件
            exchange = "BJ"  # 北京证券交易所（新三板和老三板实际上由全国股转公司管理）
            if prefix.startswith('40'):
                board = "老三板"
            elif prefix.startswith('43') or first_digit == '8':
                board = "新三板"

        return exchange, board
