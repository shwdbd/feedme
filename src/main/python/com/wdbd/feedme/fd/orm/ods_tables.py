#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   ods_tables.py
@Time    :   2022/11/23 17:36:54
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   ODS层的数据库表
'''
from com.wdbd.feedme.fd.common.common import Base
from sqlalchemy import Column, String, DECIMAL


class OdsTushareTradeCal(Base):
    """ Tushare交易日历 """

    __tablename__ = 'ods_tushare_trade_cal'

    exchange = Column(String(20), primary_key=True)
    cal_date = Column(String(8), primary_key=True)
    is_open = Column(String(1))
    pretrade_date = Column(String(8))

    def __repr__(self) -> str:
        return "Tushare交易日历[{0}, {1}] ".format(self.exchange, self.cal_date)


class OdsAkshareTradeCal(Base):
    """ Akshare 交易日历 """

    __tablename__ = 'ods_akshare_tool_trade_date_hist_sina'

    trade_date = Column(String(20), primary_key=True)

    def __repr__(self) -> str:
        return "Akshare 交易日历 [{0}] ".format(self.trade_date)


class OdsDsStat(Base):
    """ 数据源数据统计表 """

    __tablename__ = 'ods_ds_stat'

    ds_id = Column(String(50), primary_key=True)
    ds_name = Column(String(50))
    start_bar = Column(String(20))
    end_bar = Column(String(20))
    missing_bar = Column(String(500))
    notes = Column(String(500))

    def __repr__(self) -> str:
        return "数据源统计表[{0}, {1}, {2}:{3}] ".format(self.ds_name, self.end_bar, self.start_bar, self.end_bar)


class OdsTushareStockBasic(Base):
    """ Tushare A股股票基础信息 """

    __tablename__ = 'ods_tushare_stock_basic'

    ts_code = Column(String(50), primary_key=True)
    symbol = Column(String(50))
    name = Column(String(20))
    area = Column(String(20))
    industry = Column(String(50))
    fullname = Column(String(50))
    enname = Column(String(50))
    cnspell = Column(String(50))
    market = Column(String(50))
    exchange = Column(String(50))
    curr_type = Column(String(50))
    list_status = Column(String(2))
    list_date = Column(String(8))
    delist_date = Column(String(8))
    is_hs = Column(String(1))

    def __repr__(self) -> str:
        return "Tushare A股[{0}, {1}] ".format(self.ts_code, self.name)


class OdsTushareDaily(Base):
    """ tushare A股日线行情（未复权） """

    __tablename__ = 'ods_tushare_daily'

    ts_code = Column(String(50), primary_key=True)
    trade_date = Column(String(50), primary_key=True)
    p_open = Column(DECIMAL(10, 2))
    p_high = Column(DECIMAL(10, 2))
    p_low = Column(DECIMAL(10, 2))
    p_close = Column(DECIMAL(10, 2))
    pre_close = Column(DECIMAL(10, 2))
    p_change = Column(DECIMAL(10, 2))
    pct_chg = Column(DECIMAL(10, 2))
    vol = Column(DECIMAL(10, 2))
    amount = Column(DECIMAL(10, 4))

    def __repr__(self) -> str:
        return "Tushare A股日线[{0}, {1}] ".format(self.ts_code, self.trade_date)


class OdsAkshareStockDaily_163(Base):
    """ akshare A股日线行情（网易，未复权） """

    __tablename__ = 'ods_akshare_stock_zh_a_hist_163'

    trade_date = Column(String(50), primary_key=True)
    symbol = Column(String(50), primary_key=True)
    p_close = Column(DECIMAL(10, 2))
    p_high = Column(DECIMAL(10, 2))
    p_low = Column(DECIMAL(10, 2))
    p_open = Column(DECIMAL(10, 2))
    pre_close = Column(DECIMAL(10, 2))
    pct_change = Column(DECIMAL(10, 2))
    turnover_rat = Column(DECIMAL(10, 2))
    volume_h = Column(DECIMAL(10, 2))
    volume = Column(DECIMAL(10, 2))
    tmv = Column(DECIMAL(10, 2))
    cmv = Column(DECIMAL(10, 2))

    def __repr__(self) -> str:
        return "Akshare A股日线[{0}, {1}] ".format(self.symbol, self.trade_date)


class OdsAkshareStockDaily_EM(Base):
    """ akshare A股日线行情（东方财富，未复权） """

    __tablename__ = 'ods_akshare_stock_stock_zh_a_hist'

    trade_date = Column(String(50), primary_key=True)
    symbol = Column(String(50), primary_key=True)
    p_open = Column(DECIMAL(10, 2))
    p_close = Column(DECIMAL(10, 2))
    p_high = Column(DECIMAL(10, 2))
    p_low = Column(DECIMAL(10, 2))
    volume_h = Column(DECIMAL(10, 2))
    volume = Column(DECIMAL(10, 2))
    amp = Column(DECIMAL(10, 2))
    pct_change = Column(DECIMAL(10, 2))
    p_change = Column(DECIMAL(10, 2))
    turnover_rat = Column(DECIMAL(10, 2))

    def __repr__(self) -> str:
        return "Akshare A股日线[{0}, {1}] ".format(self.symbol, self.trade_date)


class OdsAkshareStock(Base):
    """ Akshare股票清单表 """

    __tablename__ = 'ods_akshare_stock_list'

    stock_id = Column(String(20), primary_key=True)
    name = Column(String(20))
    exchange = Column(String(20))

    def __repr__(self) -> str:
        return "Akshare股票 [{0} {1}, {2}] ".format(self.stock_id, self.name, self.exchange)

# if __name__ == "__main__":
#     session = get_session()
#     cal = OdsTushareTradeCal(exchange="SSE", cal_date="20221122", is_open='1', pretrade_date='00000000')
#     data = [cal]
#     session.add_all(data)
#     session.commit()
#     session.close()
