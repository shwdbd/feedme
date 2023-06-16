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
import os
import shutil
import logging.config
from com.wdbd.feedme.fd.common.common import TEST_MODE, get_cfg
import com.wdbd.feedme.fd.common.common as tl
from com.wdbd.feedme.fd.orm.ods_tables import OdsBankstockIndex, OdsBankstockFrHandleLog
from sqlalchemy import and_


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


# 把数字字符串转成数字
def to_number(number_str: str, unit: str = None) -> float:
    """把数字字符串转成数字

    Args:
        number_str (str): 数字字符串
        unit (str): 单位：千、百万，亿，默认为个位数

    Returns:
        _type_: 数字
    """
    try:
        number_str = number_str.replace(",", "")
        res = float(number_str)
        if unit == '千':
            res = res * 1000
        elif unit == '百万':
            res = res * 100 * 10000
        elif unit == '亿':
            res = res * 10000 * 10000
        return round(res, 2)
    except Exception:
        print('Exception occurred! ' + str(number_str))
        return None


# 检查 财报文件名 是否符合要求
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
    if not filename:
        return None
    if check_rpfile_format(os.path.basename(filename)) is False:
        print("错误的文件格式，" + filename)
        return None

    result = {}
    result["id"] = filename.split(".")[0].split(" ")[0]
    result["name"] = filename.split(".")[0].split(" ")[1]
    frdate = filename.split(".")[0].split(" ")[2]
    result["fr_date"] = frdate

    return result


# 文件备份
def archive_file(filename: str) -> bool:
    """ 将财报文件执行备份

    Args:
        filename (str): 文件完整路径

    Returns:
        bool: 执行结果
    """

    if os.path.exists(filename) is False:
        return False
    try:
        bak_folder = get_cfg(section="fd.siw", key="bak_folder")
        shutil.copyfile(filename, (bak_folder + os.path.basename(filename)))
        return True
    except Exception as err:
        log.error("备份文件{0}时出错！{1}".format(
            os.path.basename(filename), str(err)))
        return False


# 指标存入数据库
def save_to_db(bank_index_dict: dict) -> bool:
    """指标存入数据库

    Args:
        bank_index_dict (dict): _description_

    Returns:
        bool: _description_
    """
    # with tl.SQLiteDb() as db:
    #     db.execute()
    #     print(db)
    # EFFECTS:
    # 1. 找出 股票信息
    # 2. 删除 ods_bankstock_index、ods_bankstock_fr_handle_log 表内容
    # 3. 添加 ods_bankstock_index、ods_bankstock_fr_handle_log 表内容
    # 4. 事务提交
    # 5. 返回结果
    # END
    log = get_exception_logger()

    try:
        session = tl.get_session()
        # 股票信息
        stock_info = bank_index_dict["stock"]
        stock_id = stock_info.get("id")
        stock_name = stock_info.get("name")
        fr_date = stock_info.get("fr_date")
        print(stock_info["fr_date"])
        # 指标清单
        index_names = ",".join(bank_index_dict["index"].keys())
        print(index_names)

        # 删除现有数据
        session.query(OdsBankstockIndex).filter(and_(
            OdsBankstockIndex.stockid == stock_id, OdsBankstockIndex.fr_date == fr_date)).delete()
        session.query(OdsBankstockFrHandleLog).filter(and_(
            OdsBankstockFrHandleLog.stockid == stock_id, OdsBankstockFrHandleLog.fr_date == fr_date)).delete()

        # 更新指标：
        for index_id in bank_index_dict["index"]:
            index = OdsBankstockIndex()
            index.stockid = stock_id
            index.stock_name = stock_name
            index.fr_date = fr_date
            index.index_id = index_id
            index.index_name = index_id
            index.index_value = bank_index_dict["index"].get(index_id)
            session.add(index)
        # 更新指标记录
        log = OdsBankstockFrHandleLog()
        log.stockid = stock_id
        log.stock_name = stock_name
        log.fr_date = fr_date
        log.handled = '1'
        log.index_names = index_names
        log.last_modifed_dt = tl.today()
        session.add(log)
        # 事务提交
        session.commit()

        return True
    except Exception as err:
        log.error("指标写入数据库时出错, " + str(err))
        session.rollback()
        log.error("事务已回滚")
        return False
    finally:
        session.close()


if __name__ == "__main__":
    # print(to_number("12,345.67"))
    # print(check_rpfile_format("SH600016 民生银行 2023年Q1.pdf"))
    # print(check_rpfile_format("SH600016 民生银行 2023年报.pdf"))
    # log.info("This is Info")
    # res = archive_file('C:/Users/wang/OneDrive/3_Work/GTP01 A股财报/SH600016 民生银行 2022年年报.pdf')
    # print(res)

    tl.TEST_MODE = True
    # data = {'result': True, 'message': '', 'index': {'营业收入': 142476000000.0, '利息净收入': 107463000000.0}, 'stock': {'id': 'SH600016', 'name': '民生银行', 'fr_date': '2022年年报'}}
    # res = save_to_db(data)
    # print(res)
