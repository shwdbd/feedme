import akshare as ak


# 交易日历
def trade_cal():
    df = ak.tool_trade_date_hist_sina()
    print(df)


# 新闻联播
def news_cctv():
    df = ak.news_cctv(date="20221206")
    print(df)


# 股票实时行情数据
def stock_zh_a_spot_em():
    df = ak.stock_zh_a_spot_em()
    print(df.info())
    print(df[['代码', '名称']].head())


# 股票新浪日线
def stock_dbar_sina():
    # df = ak.stock_zh_a_daily(symbol="sz000002", start_date="20221201", end_date="20221228", adjust="qfq")
    df = ak.stock_zh_a_hist(symbol="000002", start_date="20221201", end_date="20221228", adjust="qfq")
    print(df.info())
    print(df)


# 股票东财日线
def stock_dbar_dc():
    df = ak.stock_zh_a_hist(symbol="603777", start_date="20221101", end_date="20221228", adjust="qfq", period="monthly")
    print(df.info())
    print(df)


if __name__ == "__main__":
    # news_cctv()
    # trade_cal()
    stock_zh_a_spot_em()
    # stock_dbar_sina()
    # stock_dbar_dc()
