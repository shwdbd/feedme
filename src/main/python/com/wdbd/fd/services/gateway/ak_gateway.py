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
from abc import ABC, abstractmethod
from com.wdbd.fd.common.tl import ENVIRONMENT as ENVIRONMENT, d2viewstr
import logging.config
from com.wdbd.fd.services.gateway import DataException
import requests
import socket


class AkshareGateWayError(Exception):
    """自定义的AkshareGateWay错误类"""

    def __init__(self, message="Akshare 网关错误", code=0, *args, **kwargs):
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
    # 采用单例模式
    try:
        if not hasattr(get_ak_gateway, "_instance"):
            get_ak_gateway._instance = AkshareGateWay()
        return get_ak_gateway._instance
    except Exception as e:
        # 自定义异常处理，提供更友好的错误信息
        error_message = f"无法创建AkshareGateWay对象: {str(e)}"
        raise AkshareGateWayError(error_message)


class AbstarctAkshareGateWay(ABC):

    @abstractmethod
    def symbol_2_tscode(self, symbol) -> str:
        pass


class AkshareGateWay(AbstarctAkshareGateWay):
    """ Akshare 数据网关
    目前只提供格式转换功能
    """

    def __init__(self):
        self.gw_logger = self._init_log_gw()     # 加载专用日志

    def _standardize_symbol(self, symbol: str) -> str:
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
            kargs['symbol'] = self._standardize_symbol(kargs['symbol'])
        elif "start_date" in kargs:
            kargs['start_date'] = self._standardize_date(kargs['start_date'])
        elif "end_date" in kargs:
            kargs['end_date'] = self._standardize_date(kargs['end_date'])

        try:
            df = callback(*args, **kargs)
            # 登记API日志
            # 入参控制，日期型号，统一成 yyyy-MM-dd
            self.gw_logger.info("接口={api_name}, 参数[{p}], 结果= SUCCESS".format(api_name=callback.__name__, p=str(kargs)))
            # 数据清洗(无)
            return df
        except Exception as err:
            self.gw_logger.error("接口={api_name}, 参数[{p}], 结果= FAILED".format(api_name=callback.__name__, p=str(kargs)))
            raise DataException(message="Akshare访问异常, {0}".format(str(err)))

    def _symbol_2_default(self, symbol: str) -> str:
        """将sh600016格式转为600016.SH格式

        Args:
            symbol (str): 600016.SH 格式的资产编号

        Returns:
            str: 600016格式的资产编号
        """
        if not symbol or len(symbol) < 8:
            return symbol

        return "{s}.{exchange}".format(s=symbol[2:], exchange=symbol[:2].upper())

    def symbol_2_tscode(self, symbol) -> str:
        """将sh600016格式转为600016.SH格式

        Args:
            symbol (_type_): _description_

        Returns:
            str: _description_
        """
        if not symbol or len(symbol) < 8:
            return symbol

        return "{s}.{exchange}".format(s=symbol[2:], exchange=symbol[:2].upper())

    def symbol_exchange_2_tscode(self, symbol, exchange) -> str:
        """ 600016 变为 600016.SH """
        return "{s}.{exchange}".format(s=symbol, exchange=exchange)

    # 加载专用日志管理器
    def _init_log_gw(self):
        """ 加载专用日志管理器 """
        if ENVIRONMENT == 'test':
            config_file_path = r"src\\test\\config\\gw\\akshare.conf"
        else:
            config_file_path = r"src\\main\\config\\gw\\akshare.conf"
        logging.config.fileConfig(config_file_path, disable_existing_loggers=False)
        return logging.getLogger('akshare')

    def check_connection(self) -> bool:
        """ 检测连接 """
        try:
            response = requests.get("https://akshare.akfamily.xyz/", timeout=5)  # 设置超时时间，避免长时间等待
            return response.status_code == 200
        except (requests.exceptions.RequestException, socket.timeout):
            return False
