#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   load_dev_data.py
@Time    :   2022/04/15 19:00:03
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   加载开发用模拟业务数据
'''
from app.models.ft_mis.dws_model import DWSFactory
from app.extensions import db


def load_dev_data():
    fct = DWSFactory()

    # 加载DWS层面数据
    # 加载一批模拟客户
    fct.new_customer("C0001", "客户A")
    fct.new_customer("C0002", "客户B")

    # Account
    fct.new_acct("N00001", "C0001", "客户A")
    fct.new_acct("N00002", "C0001", "客户A")
    fct.new_acct("N00010", "C0002", "客户B")

    # Loan
    fct.new_loan("100001", "C0001", "客户A")
    fct.new_loan("100002", "C0001", "客户A")
    fct.new_loan("100010", "C0002", "客户B")

    # TODO 余额
    # TODO 归属数据

    db.session.commit()
