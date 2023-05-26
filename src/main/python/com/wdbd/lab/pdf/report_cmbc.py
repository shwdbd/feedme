#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   report_cmbc.py
@Time    :   2023/05/22 15:36:02
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   民生银行财报 数据提取
'''
import pdfplumber

# TODO 一个Class，针对一种报表（比如：）；


def get_jlc(filename):
    """解析返回净利差
    Args:
        filename (_type_): 文件路径
    Returns:
        _type_: _description_
    """
    reader = pdfplumber.open(filename)         # 读取文件
    
    # 找到这一页
    page = None
    for page in reader.pages:
        if "一、 主要会计数据和财务指标" in page.extract_text_simple():
            print("OK")
            page = page
            break

    tables = page.extract_tables(
        {
            "vertical_strategy": "text",
            "horizontal_strategy": "text"
            })   # 提取该页的所有表格

    data_table = tables[0]                # 获得第一个表格
    for line in data_table:
        if line[1] == '净息差':
            return line[2]
    return None


def extract_reports():
    filename = 'C:/Users/wang/OneDrive/3_Work/GTP01 A股财报/SH600016 民生银行 2021年年报.pdf'   # 文件名
    # filename = 'C:/Users/wang/OneDrive/3_Work/GTP01 A股财报/SH600016 民生银行 2022年年报.pdf'   # 文件名

    # 净利差
    data = get_jlc(filename)
    print(data)


if __name__ == "__main__":
    extract_reports()
