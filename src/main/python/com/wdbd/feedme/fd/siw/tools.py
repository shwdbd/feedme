#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   tools.py
@Time    :   2023/06/01 14:32:28
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   基础工具
'''
# TODO 文件归档
import os
import shutil
import logging.config
from com.wdbd.feedme.fd.common.common import TEST_MODE


def get_exception_logger():
    """ 返回异常日志器 """
    if TEST_MODE:
        config_file_path = r"src/test/config/siw_log.cfg"
    else:
        config_file_path = r"src/main/config/siw_log.cfg"

    logging.config.fileConfig(config_file_path)
    return logging.getLogger('gtp')
    return None


# 异常日志
log = get_exception_logger()


def to_number(number_str: str, unit: str = None) -> float:
    """把数字字符串转成数字

    Args:
        number_str (str): 数字字符串
        unit (str): 单位：千、百万，亿，默认为个位数

    Returns:
        _type_: 数字
    """
    number_str = number_str.replace(",", "")
    res = float(number_str)
    if unit == '千':
        res = res * 1000
    elif unit == '百万':
        res = res * 100 * 10000
    return round(res, 2)


def check_rpfile_format(filename: str) -> bool:
    """检查 财报文件名 是否符合要求

    Args:
        filename (str): 文件名（非文件路径）

    Returns:
        bool: 检测结果
    """
    # 文件名是否符合规定
    # SH600016 民生银行 2023年Q1.pdf
    if not filename or filename == '':
        return False

    # 检查文件后缀
    if os.path.splitext(filename)[-1] != '.pdf':
        print(os.path.splitext(filename))
        print("not pdf file!")
        return False

    file_parts = os.path.splitext(filename)[0].split(" ")
    # 检查股票代码部分
    exchange = file_parts[0][:2]
    if exchange not in ['SH', 'SZ', 'BJ']:
        print("错误的交易所" + exchange)    # TODO 使用异常输出
        return False

    # 检查年报
    rp_type = file_parts[2]
    if rp_type.split("年")[1] not in ['Q1', 'Q2', 'Q3'] and rp_type[-3:] != '年年报':
        return False
    return True


def get_stock_info(filename: str) -> dict:
    """ 根据文件名，解析股票代码、期数等信息 """
    # 正确返回示范：{"id": "SH600016"， "name": "民生银行", "fr_date": "2023Q1"}
    # 错误返回示范: None

    if check_rpfile_format(filename) is False:
        return None

    result = {}
    result["id"] = filename.split(".")[0].split(" ")[0]
    result["name"] = filename.split(".")[0].split(" ")[1]
    frdate = filename.split(".")[0].split(" ")[2]
    result["fr_date"] = frdate

    return result


# 文件备份
def archive_file(filename) -> bool:
    """ 文件备份 """
    # TODO 待备份
    if os.path.exists(filename) is False:
        return False

    shutil.copyfile(filename, "C:/下载/SH600016 民生银行 2022年年报.pdf")
    

    return False

if __name__ == "__main__":
    # print(to_number("12,345.67"))
    # print(check_rpfile_format("SH600016 民生银行 2023年Q1.pdf"))
    # print(check_rpfile_format("SH600016 民生银行 2023年报.pdf"))
    # log.info("This is Info")
    archive_file('C:/Users/wang/OneDrive/3_Work/GTP01 A股财报/SH600016 民生银行 2022年年报.pdf')
