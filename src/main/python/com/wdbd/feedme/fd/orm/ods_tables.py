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
from sqlalchemy import Column, String


class OdsTushareTradeCal(Base):
    """ Tushare交易日历 """

    __tablename__ = 'ods_tushare_trade_cal'

    exchange = Column(String(20), primary_key=True)
    cal_date = Column(String(8), primary_key=True)
    is_open = Column(String(1))
    pretrade_date = Column(String(8))

    def __repr__(self) -> str:
        return "Tushare交易日历[{0}, {1}] ".format(self.exchange, self.cal_date)


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


# if __name__ == "__main__":
#     session = get_session()
#     cal = OdsTushareTradeCal(exchange="SSE", cal_date="20221122", is_open='1', pretrade_date='00000000')
#     data = [cal]
#     session.add_all(data)
#     session.commit()
#     session.close()
