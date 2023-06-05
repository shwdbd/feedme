#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   icbc.py
@Time    :   2023/05/26 13:21:45
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   工商银行
'''
import pdfplumber


def get_index_from_financialReport(filename: str):
    """从财报解析指标

    Args:
        filename (str): 文件路径

    Returns:
        _type_: 解析出来的指标Dict
    """
    # TODO 待实现
    with pdfplumber.open(filename) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text_simple()
            if "全年经营成果" in page_text:
                # tables = page.extract_tables(
                #     {
                #         "vertical_strategy": "lines",
                #         "horizontal_strategy": "text"
                #     })  # 提取该页的所有表格
                tables = page.extract_tables()
                print("找到表{0}个".format(len(tables)))
                print(tables[1])
                
                break   # TODO 所有都完成后，推出循环
            
            
        # .extract_text_simple

    return {}
    




if __name__ == "__main__":
    filename = 'C:/Users/wang/OneDrive/3_Work/GTP01 A股财报/SH601398 工商银行 2021年年报.pdf'
    get_index_from_financialReport(filename)

