#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   __init__.py
@Time    :   2022/03/27 10:29:35
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   Flask插件注册
'''
from flask import Flask

from .init_sqlalchemy import db as app_db, init_databases
from .init_error_page import init_error_views

# ! 全局数据库对象
db = app_db


def init_plugs(app: Flask) -> None:

    # 注册数据库插件
    init_databases(app)

    # 注册全局错误页面
    init_error_views(app)
