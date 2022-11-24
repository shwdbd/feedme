#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   sqlalchemy_demo.py
@Time    :   2022/11/22 16:28:32
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   sqlalchemy 试验代码
'''
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, create_engine
from sqlalchemy.orm import sessionmaker


# 连接数据库
def get_conn():
    # C:\github\shwdbd\feedme\db\db_test
    engine = create_engine('sqlite:///C:\\github\\shwdbd\\feedme\\db\\db_test')
    Session = sessionmaker(bind=engine)
    print(type(Session))
    return engine


Base = declarative_base()


class OdsDsStat(Base):
    """ 对应ods_ds_stat表 """

    __tablename__ = 'ods_ds_stat'

    ds_id = Column(String(50), primary_key=True)
    ds_name = Column(String(50))
    start_bar = Column(String(20))
    end_bar = Column(String(20))
    missing_bar = Column(String(500))
    notes = Column(String(500))

    def __repr__(self) -> str:
        return "ds[{0}]".format(self.ds_id)


class TableHandler:
    """ 单表处理类 """

    def __init__(self):
        self.conn = get_conn()

    def add(self):
        """ 增加记录 """
        # 准备数据
        r1 = OdsDsStat(ds_id="ts_stock_2", ds_name="第2个")
        # print(r1)

        Session = sessionmaker(bind=self.conn)
        session = Session()
        session.add(r1)
        session.commit()
        session.close()
        print("增加记录ok")

    def query(self):
        """ 查询记录 """
        Session = sessionmaker(bind=self.conn)
        session = Session()

        rows = session.query(OdsDsStat).filter_by(ds_id='ts_stock_1').all()     # [对象1, 对象2]
        print(rows)
        rows = session.query(OdsDsStat).filter(OdsDsStat.ds_id == 'ts_stock_1').all()     # [对象1, 对象2]
        print(rows)
        # select a,b
        rows = session.query(OdsDsStat.ds_id, OdsDsStat.ds_name).filter(OdsDsStat.ds_id == 'ts_stock_1').all()     # [('第1个',)]
        print(rows)
        rows = session.query(OdsDsStat.ds_id, OdsDsStat.ds_name).filter(OdsDsStat.ds_id == 'ts_stock_1')     # 执行的SQL语句
        print(rows)
        # like
        rows = session.query(OdsDsStat.ds_id, OdsDsStat.ds_name).filter(OdsDsStat.ds_id.like('ts_stock%')).all()     # [('第1个',)]
        print(rows)

        session.close()
        print("查询over")


if __name__ == "__main__":
    # serv = TableHandler()
    # # serv.add()
    # serv.query()
    print(get_conn())
