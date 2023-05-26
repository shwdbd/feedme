#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   pdfplumber_hi.py
@Time    :   2023/05/22 14:30:53
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   None
'''
import pdfplumber

filename = 'C:/Users/wang/OneDrive/3_Work/GTP01 A股财报/SH601398 工商银行 2021年年报.pdf'   # 文件名
reader = pdfplumber.open(filename)         # 读取文件
first_page = reader.pages[81-1]           # 获得文档的第一页
# tables = first_page.extract_tables()   # 提取该页的所有表格

tables = first_page.extract_tables(
    {
        "vertical_strategy": "text",
        "horizontal_strategy": "lines"
        })   # 提取该页的所有表格

first_table = tables[0]                # 获得第一个表格
# second_table = tables[1]               # 获得第二个表格

print(first_table)                     # 打印第一个表格
