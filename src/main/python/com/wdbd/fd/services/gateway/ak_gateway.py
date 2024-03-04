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
import akshare as ak
from com.wdbd.fd.common.tl import ENVIRONMENT as ENVIRONMENT, d2viewstr
import logging.config
from com.wdbd.fd.services.gateway import DataException


# 获取数据网关 对外接口
def get_ak_gateway(mode: str = None):
    if mode is not None and "mock" in mode.lower():
        return AkGatewayMock()
    else:
        return AkshareGateWay()


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
        """ 标准化入参, 资产ID """
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
            self.gw_logger.info("接口={api_name}, 参数[{p}], 结果=SUCCESS".format(api_name=callback.__name__, p=str(kargs)))
            # 数据清洗(无)
            return df
        except Exception as err:
            self.gw_logger.error("接口={api_name}, 参数[{p}], 结果=FAILED".format(api_name=callback.__name__, p=str(kargs)))
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

    # 加载专用日志管理器
    def _init_log_gw(self):
        """ 加载专用日志管理器 """
        if ENVIRONMENT == 'test':
            config_file_path = r"src\\test\\config\\gw\\akshare.conf"
        else:
            config_file_path = r"src\\main\\config\\gw\\akshare.conf"
        logging.config.fileConfig(config_file_path, disable_existing_loggers=False)
        return logging.getLogger('akshare')


class AkGatewayMock(AkshareGateWay):

    def symbol_2_tscode(self, symbol) -> str:
        return "600016.SH"


if __name__ == "__main__":
    # gw = get_ak_gateway()
    # print(gw.symbol_2_tscode("sh00001"))
    # gw = get_ak_gateway(mode='mock')
    # print(gw.symbol_2_tscode("sh00001"))

    # 调用：
    gw = get_ak_gateway()
    # print(gw)
    df = gw.call(callback=ak.stock_zh_a_hist, symbol="600016", start_date="20240225", end_date="20240228")
    # df = gw.call(callback=ak.stock_zh_a_hist_xxx, symbol="600016", start_date="20240225", end_date="20240228")
    df = gw.call(callback=ak.stock_zh_a_hist, symbol="aaaaaa", start_date="20240225", end_date="20240228")
    print(df)
    
    # # 单独日志
    # gw = AkshareGateWay()
