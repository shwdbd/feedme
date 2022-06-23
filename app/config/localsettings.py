#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   localsettings.py
@Time    :   2022/04/14 22:06:21
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   本地配置文件
'''
# 数据库配置
SQLALCHEMY_DATABASE_URI = 'sqlite:///C:\\gitee\\shwdbd\\ftmis\\db\\ftmis.db'

# Sqlite配置
SQLITE_DB_PATH = r"C:\gitee\shwdbd\ftmis\db\ftmis.db"

# 数据库连接池参数
DBPOOL_MINCACHED = 1            # 连接池中最小空闲连接数
DBPOOL_MAXCACHED = 4            # 连接池中最大空闲连接数
DBPOOL_MAXCONNECTIONS = 4       # 允许的最大连接数
DBPOOL_BLOCKING = True          # 设置为true，则阻塞并等待直到连接数量减少，false默认情况下将报告错误。
DBPOOL_PING = 1                 # 默认=1表示每当从池中获取时，使用ping()检查连接
