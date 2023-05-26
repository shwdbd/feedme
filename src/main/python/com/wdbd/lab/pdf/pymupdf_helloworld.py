#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   pymupdf_helloworld.py
@Time    :   2023/05/22 13:29:50
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   测试代码
'''

import fitz
print(fitz.__doc__)

filename = 'C:/Users/wang/OneDrive/3_Work/GTP01 A股财报/SH600016 民生银行 2021年年报.pdf'

doc = fitz.open(filename)  # or fitz.Document(filename)

# 页总数
print(doc.page_count)

# 页面元数据
print(doc.metadata)

# 目录表格
print(doc.get_toc())

# ------------------------
# 获取Page
p24 = doc.load_page(24-1)
print(p24)
text = p24.get_text("text")
print(text)
# 文本查找
# areas = p24.search_for("利息净收入")
# print(areas)

doc.close()
