#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   pdfplumber_table.py
@Time    :   2023/05/26 10:18:36
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   pdfplumber 表格数据提取示范


'''
import pdfplumber


# 完整边框表格
def extract_stand_table():
    """解析标准表格（带完整的边框）
    """
    # 华夏银行年报，主要会计数据和财务指标， 21年年报，第10页
    filename = 'C:/Users/wang/OneDrive/3_Work/GTP01 A股财报/SH600015 华夏银行 2021年年报.pdf'

    pdf_reader = pdfplumber.open(filename)         # 读取文件
    page = pdf_reader.pages[10-1]           # 获得文档的第10页
    tables = page.extract_tables(
        {
            "vertical_strategy": "lines",
            "horizontal_strategy": "lines"
        })  # 提取该页的所有表格
    print("找到表{0}个".format(len(tables)))
    table1 = tables[0]   # 第一个表格
    print("表1: 共{0}行".format(len(table1)))
    print("表1: 表头 {0}".format(table1[0]))
    for idx, row in enumerate(table1, 1):
        print("  行{0}: {1}".format(idx, table1[idx-1]))
    print("DONE")


# 民生年报，带彩色，无竖线横线
def extract_cmbc_table():
    """ 民生年报，带彩色，无竖线横线
    """
    # 民生银行22年年报，非经常性损益， 第25页
    filename = 'C:/Users/wang/OneDrive/3_Work/GTP01 A股财报/SH600016 民生银行 2022年年报.pdf'

    pdf_reader = pdfplumber.open(filename)         # 读取文件
    page = pdf_reader.pages[25-1]           # 获得文档的第25页

    # 按文本方式处理
    page_text = page.extract_text()
    lines = page_text.splitlines()  # 解析为行
    for line in lines:
        if "政府补助" in line:
            print("2021年政府补助：{0}".format(float(line.split(" ")[2])))
            print(line)
    print("DONE")


# 只有横线无竖线的表格
def extract_noColLine_table():
    """解析行表格（只有横线无竖线的表格）
    """
    # 工商银行21年年报，近三年普通股现金分红情况如下表， 第154页
    filename = 'C:/Users/wang/OneDrive/3_Work/GTP01 A股财报/SH601398 工商银行 2021年年报.pdf'

    pdf_reader = pdfplumber.open(filename)         # 读取文件
    page = pdf_reader.pages[154-1]           # 获得文档的第154页
    tables = page.extract_tables(
        {
            "vertical_strategy": "text",        # 竖线
            "horizontal_strategy": "lines"      # 横线
        })  # 提取该页的所有表格
    print("找到表{0}个".format(len(tables)))
    table1 = tables[0]   # 第一个表格
    print("表1: 共{0}行".format(len(table1)))
    print("表1: 表头 {0}".format(table1[0]))
    for idx, row in enumerate(table1, 1):
        print("  行{0}: {1}".format(idx, table1[idx-1]))
    print("DONE")


if __name__ == "__main__":
    # extract_stand_table()
    # extract_noColLine_table()
    extract_cmbc_table()
