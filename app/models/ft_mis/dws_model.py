#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   dws_model.py
@Time    :   2022/03/31 14:49:08
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   数仓对外服务层数据模型
'''
from app.extensions import db


# ++++++++++++++++++++++++++++++++
# 基础数据表
# ++++++++++++++++++++++++++++++++
# 客户表: dws_customer
class Customer(db.Model):
    __tablename__ = 'dws_customer'

    id = db.Column(db.String(20), primary_key=True)         # 核心客户号
    name = db.Column(db.String(100))                        # 户名
    group = db.Column(db.String(100))                       # 所属集团名
    flag_active = db.Column(db.Boolean, default=False)      # 有效户标识


# 账户表: dws_account
class Account(db.Model):
    __tablename__ = 'dws_account'

    acct_id = db.Column(db.String(20), primary_key=True)    # 账号
    name = db.Column(db.String(100))                        # 户名
    customer_id = db.Column(db.String(20), db.ForeignKey('dws_customer.id'), nullable=True)     # 核心客户号
    orgid = db.Column(db.String(4))                         # 机构号, A7, A9
    currency = db.Column(db.String(4))                      # 币种
    subject = db.Column(db.String(20))                      # 科目
    # 分类
    # 状态


# 借据表: dws_loan
class Loan(db.Model):
    __tablename__ = 'dws_loan'

    loan_id = db.Column(db.String(20), primary_key=True)         # 借据号
    name = db.Column(db.String(20))                         # 户名
    customer_id = db.Column(db.String(20), db.ForeignKey('dws_customer.id'), nullable=False)     # 核心客户号
    account_id = db.Column(db.String(20))                   # 账号
    # 状态
    currency = db.Column(db.String(4), default='01')                      # 币种


# 账户余额表 : dws_acct_balance
class AccountBalance(db.Model):
    __tablename__ = 'dws_acct_balance'

    id = db.Column(db.String(20), primary_key=True)         # 账号
    trade_date = db.Column(db.String(8), primary_key=True)  # 日期
    name = db.Column(db.String(20))                         # 户名
    balance = db.Column(db.Float(16, 2))                    # 余额
    bala_nrj = db.Column(db.Float(16, 2))                    # 年日均余额
    bala_jrj = db.Column(db.Float(16, 2))                    # 季日均余额
    bala_yrj = db.Column(db.Float(16, 2))                    # 月日均余额


# 借据余额表: dws_loan_balance
class LoanBalance(db.Model):
    __tablename__ = 'dws_loan_balance'

    id = db.Column(db.String(20), primary_key=True)         # 账号
    trade_date = db.Column(db.String(8), primary_key=True)  # 日期
    name = db.Column(db.String(20))                         # 户名
    balance = db.Column(db.Float(16, 2))                    # 余额
    bala_nrj = db.Column(db.Float(16, 2))                    # 年日均余额
    bala_jrj = db.Column(db.Float(16, 2))                    # 季日均余额
    bala_yrj = db.Column(db.Float(16, 2))                    # 月日均余额


# ==========================
# 归属
# ==========================
# 客户号归属表: dws_belong_customer
class CustomerBelong(db.Model):
    __tablename__ = 'dws_belong_customer'

    cust_id = db.Column(db.String(20), primary_key=True)        # 客户号
    cust_name = db.Column(db.String(20))                        # 户名
    dept_id = db.Column(db.String(20), primary_key=True)        # 部门号
    dept_name = db.Column(db.String(20))                        # 部门名
    user_id = db.Column(db.String(20))                          # 员工号
    user_name = db.Column(db.String(20))                        # 员工姓名
    belong_date = db.Column(db.String(8))                       # 归属日期


# 账号归属表：dws_belong_account
class AccountBelong(db.Model):
    __tablename__ = 'dws_belong_account'

    acct_id = db.Column(db.String(20), primary_key=True)        # 账号
    cust_name = db.Column(db.String(20))                        # 户名
    dept_id = db.Column(db.String(20), nullable=False)          # 部门号
    dept_name = db.Column(db.String(20))                        # 部门名
    user_id = db.Column(db.String(20), primary_key=True)        # 员工号
    user_name = db.Column(db.String(20))                        # 员工姓名
    percent = db.Column(db.Integer, default=100, nullable=False)    # 归属百分比
    belong_date = db.Column(db.String(8))                       # 归属日期


# 借据号归属表
class LoanBelong(db.Model):
    __tablename__ = 'dws_belong_loan'

    loan_id = db.Column(db.String(20), primary_key=True)        # 借据号
    cust_name = db.Column(db.String(20))                        # 户名
    dept_id = db.Column(db.String(20), nullable=False)          # 部门号
    dept_name = db.Column(db.String(20))                        # 部门名
    user_id = db.Column(db.String(20), primary_key=True)        # 员工号
    user_name = db.Column(db.String(20))                        # 员工姓名
    percent = db.Column(db.Integer, default=100, nullable=False)    # 归属百分比
    belong_date = db.Column(db.String(8))                       # 归属日期


# 归属变动记录表
class BelongChangeLog(db.Model):
    __tablename__ = 'dws_belong_change_log'

    TYPE_CUST = "cust"  # 类型：客户号
    TYPE_ACCT = "acct"  # 类型：存款账号
    TYPE_LOAN = "cust"  # 类型：贷款借据

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)    # 顺序号
    type = db.Column(db.String(10), default=TYPE_CUST)                  # 类型，客户号cust,存款账号acct，贷款借据号loan
    biz_no = db.Column(db.String(50), nullable=False)                   # 业务编号
    change_time = db.Column(db.String(20))                              # 变动时间
    reason = db.Column(db.String(200))                                  # 变动原因
    bg_before = db.Column(db.String(200))                               # 变动前情况
    bg_after = db.Column(db.String(200))                                # 变动后情况
    notes = db.Column(db.String(200))                                   # 备注


# 归属申报单
class BelongRequestForm(db.Model):
    __tablename__ = 'dws_belong_req_form'

    STAUS_DRAFT = 1    # 状态：草稿
    STAUS_DEPT = 3    # 状态：部门审批
    STAUS_CANCEL = 0    # 状态：作废
    STAUS_WFR = 5    # 状态：待执行
    STAUS_DONE = 9    # 状态：执行完成

    form_id = db.Column(db.String(50), primary_key=True)        # 申请单编号
    status = db.Column(db.Integer, default=STAUS_DRAFT)      # 状态
    applicant_id = db.Column(db.String(20))             # 申请人id
    applicant_name = db.Column(db.String(20))             # 申请姓名
    applicant_time = db.Column(db.String(20))            # 申请时间
    submit_time = db.Column(db.String(20))            # 提交时间
    leader_id = db.Column(db.String(20))        # 审批人id
    leader_name = db.Column(db.String(20))      # 审批人姓名
    approval_result = db.Column(db.Boolean)     # 审批结果
    approval_note = db.Column(db.String(100))    # 审批意见
    approval_time = db.Column(db.String(20))    # 审批时间
    notes = db.Column(db.String(200))           # 备注

    def to_dict(self):
        dict = self.__dict__
        if "_sa_instance_state" in dict:
            del dict["_sa_instance_state"]
        return dict


# 归属申报单条目
class BelongRequestFormItem(db.Model):
    __tablename__ = 'dws_belong_req_form_item'

    TYPE_CUST = "cust"  # 类型：客户号
    TYPE_ACCT = "acct"  # 类型：存款账号
    TYPE_LOAN = "loan"  # 类型：贷款借据

    STAUS_WAIT = 0    # 状态：待执行
    STAUS_SUCCESS = 9    # 状态：执行成功
    STAUS_FAILED = -1    # 状态：执行失败

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)        # 申请单编号
    form_id = db.Column(db.String(50), db.ForeignKey('dws_belong_req_form.form_id'))        # 申请单编号
    type = db.Column(db.String(10), default=TYPE_CUST)    # 类型，客户号cust,存款账号acct，贷款借据号loan
    status = db.Column(db.Integer, default=STAUS_WAIT)      # 状态
    biz_no = db.Column(db.String(50), nullable=False)       # 业务编号
    cust_name = db.Column(db.String(50))            # 户名

    dept_id_1 = db.Column(db.String(20))            # 归属部门1编号
    dept_name_1 = db.Column(db.String(20))          # 归属部门1名
    user_id_1 = db.Column(db.String(20))            # 归属人1编号
    user_name_1 = db.Column(db.String(20))          # 归属人1姓名
    per_1 = db.Column(db.Integer, default=100)      # 归属人1归属比例
    dept_id_2 = db.Column(db.String(20))            # 归属部门2编号
    dept_name_2 = db.Column(db.String(20))          # 归属部门2名
    user_id_2 = db.Column(db.String(20))            # 归属人2编号
    user_name_2 = db.Column(db.String(20))          # 归属人2姓名
    per_2 = db.Column(db.Integer, default=0)        # 归属人2归属比例
    dept_id_3 = db.Column(db.String(20))            # 归属部门3编号
    dept_name_3 = db.Column(db.String(20))          # 归属部门3名
    user_id_3 = db.Column(db.String(20))            # 归属人3编号
    user_name_3 = db.Column(db.String(20))          # 归属人3姓名
    per_3 = db.Column(db.Integer, default=0)        # 归属人3归属比例
    dept_id_4 = db.Column(db.String(20))            # 归属部门4编号
    dept_name_4 = db.Column(db.String(20))          # 归属部门4名
    user_id_4 = db.Column(db.String(20))            # 归属人4编号
    user_name_4 = db.Column(db.String(20))          # 归属人4姓名
    per_4 = db.Column(db.Integer, default=0)        # 归属人4归属比例
    dept_id_5 = db.Column(db.String(20))            # 归属部门5编号
    dept_name_5 = db.Column(db.String(20))          # 归属部门5名
    user_id_5 = db.Column(db.String(20))            # 归属人5编号
    user_name_5 = db.Column(db.String(20))          # 归属人5姓名
    per_5 = db.Column(db.Integer, default=0)        # 归属人5归属比例
    notes = db.Column(db.String(200))               # 备注

    def get_type_name(self):
        if self.type == BelongRequestFormItem.TYPE_CUST:
            return "客户号"
        elif self.type == BelongRequestFormItem.TYPE_ACCT:
            return "存款账号"
        elif self.type == BelongRequestFormItem.TYPE_LOAN:
            return "借据号"
        else:
            return ""

    def belong_str(self):
        """ 返回归属字符串 """
        blstr = ""
        if self.dept_id_1:
            blstr += "{dept_name} {user_name} {per}%; ".format(dept_name=self.dept_name_1, user_name=self.user_name_1, per=self.per_1)
        if self.dept_id_2:
            blstr += "{dept_name} {user_name} {per}%; ".format(dept_name=self.dept_name_2, user_name=self.user_name_2, per=self.per_2)
        if self.dept_id_3:
            blstr += "{dept_name} {user_name} {per}%; ".format(dept_name=self.dept_name_3, user_name=self.user_name_3, per=self.per_3)
        if self.dept_id_4:
            blstr += "{dept_name} {user_name} {per}%; ".format(dept_name=self.dept_name_4, user_name=self.user_name_4, per=self.per_4)
        if self.dept_id_5:
            blstr += "{dept_name} {user_name} {per}%; ".format(dept_name=self.dept_name_5, user_name=self.user_name_5, per=self.per_5)
        return blstr

    def to_dict(self):
        dict = self.__dict__
        if "_sa_instance_state" in dict:
            del dict["_sa_instance_state"]
        return dict


class DWSFactory:
    """ dws层对象工厂 """

    @staticmethod
    def new_customer(id, name) -> Customer:
        """ 返回空客户 """
        cust = Customer()
        cust.id = id
        cust.name = name
        db.session.add(cust)
        return cust

    @staticmethod
    def new_acct(acct_id, cust_id, cust_name) -> Account:
        """ 返回空客户 """
        acct = Account()
        acct.acct_id = acct_id
        acct.customer_id = cust_id
        acct.name = cust_name
        db.session.add(acct)
        return acct

    @staticmethod
    def new_loan(loan_id, cust_id, cust_name, acct_id="12345") -> Loan:
        """ 返回空客户 """
        loan = Loan()
        loan.loan_id = loan_id
        loan.customer_id = cust_id
        loan.name = cust_name
        loan.account_id = acct_id
        db.session.add(loan)
        return loan
