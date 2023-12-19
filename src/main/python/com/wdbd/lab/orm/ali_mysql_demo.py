#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   ali_mysql_demo.py
@Time    :   2023/10/27 10:24:40
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   阿里云 MySQL 数据库连接示例
'''

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
# import pymysql

engine = create_engine(f"mysql+pymysql://wdbd_db_root:Wjj_811016@rm-cn-9lb3gcq6000022bo.rwlb.rds.aliyuncs.com/ft_test")
# print(engine)
print("连接成功")

# 使用反射机制，读取
metadata_obj = MetaData()
# print(metadata_obj)
metadata_obj.reflect(bind=engine)
# print(metadata_obj.tables)
employee_table = metadata_obj.tables["employee"]
print(employee_table)

# 执行查询
Session = sessionmaker(bind=engine)
session = Session()
rows = session.query(employee_table).all()
print(rows)
# 带条件查询
rows = session.query(employee_table).filter(employee_table.c.id == '888').all()     # 字段的引用，要使用table.c.字段名
print(rows)
session.close()
