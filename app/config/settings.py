#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   settings.py
@Time    :   2022/04/14 22:05:40
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   应用配置文件
'''
SECRET_KEY = "dev"

# 日志配置

# 数据库配置
SQLALCHEMY_DATABASE_URI = "---"
SQLALCHEMY_TRACK_MODIFICATIONS = False  # 关闭对模型修改的监控
SQLALCHEMY_ECHO = False
SQLALCHEMY_RECORD_QUERIES = True

# 加载本地参数：
try:
    from .localsettings import *
except Exception:
    print("本地配置文件(localsettings.py)未找到！")
