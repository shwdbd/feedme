#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   ak_stock.py
@Time    :   2023/11/08 13:06:24
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   Akshare 股票类接口 Demo
'''
import akshare as ak


# 股票市场总貌 - 上海证券交易所
def test_stock_sse_summary():
    stock_sse_summary_df = ak.stock_sse_summary()
    print(stock_sse_summary_df)


# 个股信息查询
def test_stock_individual_info_em():
    stock_individual_info_em_df = ak.stock_individual_info_em(symbol="600016")
    print(stock_individual_info_em_df)


if __name__ == "__main__":
    test_stock_individual_info_em()


#    item                value    
# 0   总市值  167248838677.639984 
# 1  流通市值  135465310673.659988
# 2    行业                   银行
# 3  上市时间             20001219
# 4  股票代码               600016
# 5  股票简称                 民生银行
# 6   总股本        43782418502.0
# 7   流通股        35462123213.0