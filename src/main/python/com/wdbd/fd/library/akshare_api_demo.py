#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   akshare_api_demo.py
@Time    :   2023/12/27 09:29:46
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   Akshare API接口调用示例
'''
import akshare as ak


# 交易日历
def tool_trade_date_hist_sina():
    # Pandas 升级到 2.1.0 及以上版本
    # Python 升级到 3.9 及以上版本！
    tool_trade_date_hist_sina_df = ak.tool_trade_date_hist_sina()
    print(tool_trade_date_hist_sina_df)
    # Return:
    #   trade_date
    # 0     1990-12-19
    # 1     1990-12-20
    # 2     1990-12-21
    # 3     1990-12-24
    # 4     1990-12-25
    # ...          ...
    # 8308  2024-12-25
    # 8309  2024-12-26
    # 8310  2024-12-27
    # 8311  2024-12-30
    # 8312  2024-12-31
    return


def stock_zh_a_spot_em():
    """ 单次返回所有沪深京 A 股上市公司的实时行情数据 """
    df = ak.stock_zh_a_spot_em()
    print(df[['代码', '名称']])
#           代码    名称
# 0     603004   N鼎龙
# 1     872190  雷神科技
# 2     300264  佳创视讯
# 3     300608   思特奇
# 4     301383  天键股份
# ...      ...   ...
# 5568  832471  美邦科技
# 5569  430300  辰光医疗
# 5570  871642  通易航天
# 5571  301526  C国际复
# 5572  300949  奥雅股份
# [5573 rows x 2 columns]
    return


def stock_zh_a_hist():
    """ 历史行情数据-东财 """
    # stock_zh_a_hist_df = ak.stock_zh_a_hist(symbol="600016", period="daily", start_date="20231225", end_date='20231226', adjust="")
    # print(stock_zh_a_hist_df)
    stock_zh_a_hist_df = ak.stock_zh_a_hist(symbol="600016", period="daily", adjust="")
    print(stock_zh_a_hist_df)


# 历史行情数据-新浪
def stock_zh_a_daily():
    """ 历史行情数据-新浪 """
    # stock_zh_a_daily_qfq_df = ak.stock_zh_a_daily(symbol="sh600016", start_date="20230101", end_date="20231027", adjust="qfq")
    # print(stock_zh_a_daily_qfq_df)
    stock_zh_a_daily_qfq_df = ak.stock_zh_a_daily(start_date="20230101", end_date="20230105", adjust="qfq")
    print(stock_zh_a_daily_qfq_df)
#            date  open  high   low  close      volume       amount  outstanding_share  turnover
# 0    2023-01-03  3.27  3.27  3.23   3.25  58477549.0  201231771.0       3.546212e+10  0.001649
# 1    2023-01-04  3.26  3.29  3.25   3.28  55369288.0  192063423.0       3.546212e+10  0.001561
# 2    2023-01-05  3.28  3.30  3.28   3.29  51002064.0  177603825.0       3.546212e+10  0.001438
# 3    2023-01-06  3.30  3.30  3.26   3.28  50040998.0  173473525.0       3.546212e+10  0.001411
# 4    2023-01-09  3.28  3.29  3.26   3.27  52517759.0  182102932.0       3.546212e+10  0.001481
# ..          ...   ...   ...   ...    ...         ...          ...                ...       ...
# 192  2023-10-23  3.65  3.68  3.61   3.64  57901940.0  211102011.0       3.546212e+10  0.001633
# 193  2023-10-24  3.64  3.66  3.58   3.59  80547790.0  290327483.0       3.546212e+10  0.002271
# 194  2023-10-25  3.61  3.66  3.59   3.66  64747201.0  234989232.0       3.546212e+10  0.001826
# 195  2023-10-26  3.64  3.70  3.63   3.69  58483570.0  215009804.0       3.546212e+10  0.001649
# 196  2023-10-27  3.69  3.70  3.66   3.66  42027107.0  154515471.0       3.546212e+10  0.001185
    return



def stock_zh_a_hist_tx():
    stock_zh_a_hist_tx_df = ak.stock_zh_a_hist_tx(symbol="sh600016", start_date="20230101", end_date="20230105", adjust="")
    print(stock_zh_a_hist_tx_df)


# 实时行情数据-新浪
def stock_zh_a_spot():
    """ 实时行情数据-新浪 """
    # stock_zh_a_spot_df = ak.stock_zh_a_spot()
    # print(stock_zh_a_spot_df)
    stock_zh_a_spot_df = ak.stock_zh_a_spot()
    print(stock_zh_a_spot_df)
#             代码    名称    最新价    涨跌额     涨跌幅     买入     卖出     昨收     今开     最高     最低         成交量          成交额       时间戳
# 0     bj430017  星昊医药  15.25   0.14   0.927  15.23  15.25  15.11  15.16  15.58  15.16   1373831.0   21137005.0  10:18:00
# 1     bj430047  诺思兰德  15.35   0.18   1.187  15.35  15.36  15.17  15.05  15.68  15.05    319872.0    4923688.0  10:18:00
# 2     bj430090  同辉信息   5.36  -0.12  -2.190   5.36   5.37   5.48   5.59   5.60   5.30  10316637.0   56168553.0  10:18:00
# 3     bj430139  华岭股份  14.36  -0.50  -3.365  14.36  14.40  14.86  14.65  14.85  14.16   3009851.0   43362363.0  10:18:00
# 4     bj430198  微创光电  10.50  -0.23  -2.144  10.49  10.50  10.73  10.85  10.87  10.50   3164685.0   33834912.0  10:18:00
# ...        ...   ...    ...    ...     ...    ...    ...    ...    ...    ...    ...         ...          ...       ...
# 5328  sz301555  惠柏新材  41.80   0.31   0.747  41.79  41.82  41.49  41.16  42.09  40.88   1400373.0   58031860.0  10:18:45
# 5329  sz301558  三态股份  14.52   0.08   0.554  14.50  14.52  14.44  14.35  14.56  14.09   5057744.0   72419468.0  10:18:45
# 5330  sz301559  中集环科  18.68   0.26   1.412  18.66  18.67  18.42  18.40  18.68  18.33    824756.0   15259396.0  10:18:45
# 5331  sz301568   思泰克  44.40   0.50   1.139  44.38  44.41  43.90  44.94  45.20  43.34   2784683.0  122858124.0  10:18:45
# 5332  sz301578   N辰奕  79.79  30.85  63.036  79.79  79.98  48.94  80.00  85.00  76.51   5692236.0  452292843.0  10:18:45
    return


# def stock_zh_a_hist():
#     pass


# 历史行情数据-东财
def stock_zh_a_hist():
    # DOC： https://akshare.akfamily.xyz/data/stock/stock.html#id22

    symbol = "300226"
    period = "monthly"
    # df = ak.stock_zh_a_hist(symbol=symbol, period=period, start_date='20240320', end_date='20240326', adjust="")
    # print(df.head(1))
    # df = ak.stock_zh_a_hist(symbol=symbol, period=period, start_date='20240320', end_date='20240326', adjust="qfq")
    # print(df.head(1))
    # print(df.info())

    # 如果不提供日期，则返回全部
    df = ak.stock_zh_a_hist(symbol=symbol, period=period, adjust="")
    print(df.head(1))
    print(df.shape)

    pass


if __name__ == "__main__":
    # stock_zh_a_hist_tx()
    stock_zh_a_hist()
