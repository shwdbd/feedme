#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   data_dateway.py
@Time    :   2022/06/19 21:00:49
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   Tushare数据源网关

数据网关的目的是把数据源api进行封装, 用户只要调用这里的api, 不用关心底层的实现

目前实现的网关有：
- tushare网关
- Baostock网关

目前的问题：
1、对于fd.comm.tl的依赖
2、对于tushare包的需求
3、对于tushare配置文件的依赖

'''
import com.wdbd.feedme.fd.common.common as tl
import tushare as ts
import time
import json
import baostock as bs
# import pandas as pd


class TushareGateWay:
    """ Tushare数据网关 """

    def __init__(self):
        # tushare配置参数
        self.api = self._get_api()

    def _get_api(self, new_token: str = None):
        """返回Tuhsare API访问接口
        """
        if new_token:
            token = new_token
        else:
            token = tl.get_cfg("tushare", "TOKEN")
        try:
            ts.set_token(token)
            return ts.pro_api()
        except Exception as err:
            tl.get_logger().error("Tuhare访问错误, {0}".format(err))
            return None

    def call(self, callback, return_type: str = "dataframe", is_offset: bool = False, *args, **kargs):
        """调用tushare api

        相对直接调用Tushare API，本函数有几项优势：
        1. 支持连接超时，反复读取
        2. 一定不抛出异常
        3. 每一次的调用，都有日志记录

        Args:
            callback (function): [description]
            dataframe (str) : dataframe or dict的返回值

        Returns:
            [type]: [description]
        """
        # TODO 添加对于offset的支持
        logger = tl.get_logger()
        # tushare配置参数
        try_count = int(tl.get_cfg("tushare", "TRY_COUNT"))
        retry_wating_time = int(tl.get_cfg("tushare", "WAIT_SECOND"))

        while try_count > 0:
            try:
                df = callback(*args, **kargs)

                # 不同返回格式
                if return_type == "dict":
                    return df.to_dict('records')
                else:
                    # 默认dataframe格式
                    return df
            except Exception as err:
                logger.debug(
                    "【Tushare错误】调用出现异常，错误原因:{err}".format(err=str(err)))
                logger.info("暂停{0}秒".format(retry_wating_time))
                time.sleep(retry_wating_time)
                retry_wating_time = retry_wating_time - 1
                logger.info("暂停结束，重新连接")
        return None

    def get_fields(self, api_name, json_file_path=tl.get_cfg("tushare", "fields_file_path")):
        """读取api中的字段信息

        Args:
            api_name ([type]): [description]

        Returns:
            [type]: [description]
        """
        try:
            with open(json_file_path, encoding='utf-8') as f:
                json_obj = json.loads(f.read())
                return json_obj[api_name]

        except Exception as err:
            tl.get_logger().error("读取数据单元配置文件时出现问题，Exp={err}".format(err=err))
            return None


class BaostockGateWay:

    # 系统返回值
    RES_SUCCESS = "0"     # 成功

    # 数据线频率
    FRQ_DAY = "d"       # 数据周期：日K线
    FRQ_WEEK = "w"      # 数据周期：周K线
    FRQ_MONTH = "m"     # 数据周期：月K线
    FRQ_5MIN = "5"      # 数据周期：5分钟K线
    FRQ_15MIN = "15"     # 数据周期：15分钟K线
    FRQ_30MIN = "30"     # 数据周期：30分钟K线
    FRQ_60MIN = "60"     # 数据周期：60分钟K线

    # 复权方式
    ADJ_BACK = "1"          # 后复权
    ADJ_BEFORE = "2"          # 前复权
    ADJ_NO = "3"          # 不复权

    # 字段清单
    # 日线指标：
    FIELDS_DAY = "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,isST"
    # 分钟线指标：
    FIELDS_MINUTE = "date,time,code,open,high,low,close,volume,amount,adjustflag"
    # 周月线指标：
    FIELDS_WEEK = "date,code,open,high,low,close,volume,amount,adjustflag,turn,pctChg"

    def __init__(self):
        pass

    def connect(self) -> bool:
        """连通性测试

        Returns:
            bool: [description]
        """
        logger = tl.get_logger()
        try:
            lg = bs.login()
            if lg.error_code != BaostockGateWay.RES_SUCCESS:
                logger.error("登录baostock失败，失败原因：{0}".format(lg.error_msg))
                return False
            return True
        except Exception as err:
            logger.debug(
                "Baostock访问失败，错误原因:{err}".format(err=str(err)))
            return False
        finally:
            bs.logout()

    def call(self, callback, return_type="dataframe", *args, **kargs):
        """调用baostock api

        要实现的功能：
        - 每次调用，日志记录
        - 统一抛出异常

        Args:
            callback (function): baostock调用接口
            return_type (str, optional): str. 返回数据的格式。Defaults to "dataframe".

        Returns:
            [type]: 查询后返回数据
        """
        logger = tl.get_logger()

        try:
            lg = bs.login()
            if lg.error_code != BaostockGateWay.RES_SUCCESS:
                logger.error("登录baostock失败，失败原因：{0}，传入参数：{1}".format(lg.error_msg, kargs))
                return None

            rs = callback(*args, **kargs)
            if rs is None:
                logger.error("调用baostock失败，传入参数：{0}".format(kargs))
                return None

            data_list = []
            if rs.error_code == BaostockGateWay.RES_SUCCESS:
                while rs.next():
                    data_list.append(rs.get_row_data())
            else:
                logger.error("调用baostock失败，失败原因：{0}，传入参数：{1}".format(rs.error_msg, kargs))
                return None

            # 不同返回格式
            if return_type == "list":
                return data_list
            else:
                # 默认dataframe格式
                res_df = pd.DataFrame(data_list, columns=rs.fields)
                return res_df
        except Exception as err:
            logger.debug(
                "【Baostock错误】调用出现异常，错误原因:{err}".format(err=str(err)))
            return None
        finally:
            bs.logout()

    def code_bs2ts(self, bs_code: str) -> str:
        # 错误格式，返回None
        # sh.600001 => 600001.SH

        if not bs_code or len(bs_code) != 9:
            return None
        return bs_code[3:] + "." + bs_code[:2].upper()

    def code_ts2bs(self, ts_code: str) -> str:
        # 600001.SH ==> sh.600001
        if not ts_code or len(ts_code) != 9:
            return None
        return ts_code[-2:].lower() + "." + ts_code[:6]

    def date_bs2ts(self, date_bs_formatter: str) -> str:
        # 2021-07-01 -> 20210101
        if not date_bs_formatter or len(date_bs_formatter) != 10:
            return None
        # return date_bs_formatter[:4] + date_bs_formatter[5:7] + date_bs_formatter[-2:]
        return date_bs_formatter.replace("-", "")

    def date_ts2bs(self, date_ts_formatter: str) -> str:
        # 20210101 -> 2021-07-01
        if not date_ts_formatter or len(date_ts_formatter) != 8:
            return None
        return date_ts_formatter[:4] + "-" + date_ts_formatter[4:6] + "-" + date_ts_formatter[-2:]


# if __name__ == "__main__":
#     gw = TushareGateWay()
#     # r = gw.call(gw.api.daily, start_date="20180101", end_date="20210401", return_type="dict")
#     # print(len(r))
#     # # print(gw.get_fields("fund_basic"))
#     # # 读取
#     # print(gw.get_fields("stock_basic"))

#     # dict格式返回
#     r = gw.call(gw.api.daily, start_date="20180810", end_date="20180811", ts_code="600016.SH", return_type="dict")
#     print(r)
#     # r = gw.call(gw.api.daily, start_date="20180810", end_date="20180811", ts_code="600016.SH", return_type="dataframe")
#     # print(type(r))
#     # print(r)
#     # print(r is pd.core.frame.DataFrame)
#     # print(isinstance(r, pd.core.frame.DataFrame))
#     # # print(r.info())
#     # # print(r.to_dict('records'))

if __name__ == "__main__":
    print(tl.get_p())


