#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   dws_service.py
@Time    :   2022/04/08 22:13:59
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   展示层数据公共服务函数
'''
from app.models.ft_mis.dws_model import Customer, Account, Loan
# from app.extensions import db
# from app import app


# 根据核心客户号返回客户对象
def get_cust(cust_id: str) -> Customer:
    # TODO 待测试
    c = Customer.query.filter(Customer.id == cust_id).first()
    if c:
        return c
    else:
        return None


# 根据账号返回存款账户对象
def get_acct(acct_id: str) -> Account:
    # TODO 待测试
    c = Account.query.filter(Account.acct_id == acct_id).first()
    if c:
        return c
    else:
        return None


# 根据借据号返回借据对象
def get_loan(loan_id: str) -> Loan:
    # TODO 待测试
    c = Loan.query.filter(Loan.loan_id == loan_id).first()
    if c:
        return c
    else:
        return None
