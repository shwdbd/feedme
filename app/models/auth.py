#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   auth.py
@Time    :   2022/03/23 10:17:31
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   Auth模块的数据模型
'''
from app.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


# 人员表：admin_user
class AdminUser(db.Model, UserMixin):
    __tablename__ = 'admin_user'

    STAUS_NORMAL = 1    # 状态：正常
    STAUS_SUSPEND = 0    # 状态：停用
    STAUS_QUIT = 4    # 状态：离职

    LEVEL_PERSON = 1      # 级别，员工
    LEVEL_DEPT = 5          # 级别，部门
    LEVEL_BRANCH = 9          # 级别，全分行

    id = db.Column(db.String(20), primary_key=True)         # 用户id
    name = db.Column(db.String(20))                         # 姓名
    password = db.Column(db.String(50))                     # 密码，明码
    password_hash = db.Column(db.String(128))               # 密码散列值
    is_virtual = db.Column(db.Boolean(), default=False)     # 是否虚拟用户，默认否
    status = db.Column(db.Integer(), default=STAUS_NORMAL)             # 状态：0停用，1正常，4离职
    level = db.Column(db.Integer(), default=LEVEL_PERSON)   # 员工级别
    # 所属部门
    dept_id = db.Column(db.String(20), db.ForeignKey('admin_dept.id'), nullable=True)
    # OA账号
    oa_id = db.Column(db.String(20), default="")
    # 十位员工号
    worker_id = db.Column(db.String(10), default="")
    # 邮件地址
    email = db.Column(db.String(50), default="")

    # 新建一个实例
    @staticmethod
    def new(id, name, dept_id, is_virtual=False, password="12345"):
        u = AdminUser()
        u.id = id
        u.name = name
        u.dept_id = dept_id
        u.is_virtual = is_virtual
        u.set_password(password)
        return u

    # 状态中文
    def get_status(self) -> str:
        """ 返回状态中文 """
        if self.status == AdminUser.STAUS_NORMAL:
            return "正常"
        elif self.status == AdminUser.STAUS_SUSPEND:
            return "账户停用"
        elif self.status == AdminUser.STAUS_QUIT:
            return "离职"
        else:
            return '--'

    # 层级中文
    def get_level(self) -> str:
        """ 返回层级中文 """
        if self.level == AdminUser.LEVEL_PERSON:
            return "个人级"
        elif self.level == AdminUser.LEVEL_DEPT:
            return "部门级"
        elif self.level == AdminUser.LEVEL_BRANCH:
            return "全行级"
        else:
            return '--'

    def get_dept_name(self):
        """ 返回所属部门名 """
        dept = AdminDepartment.query.filter(AdminDepartment.id == self.dept_id).first()
        if dept:
            return dept.name
        else:
            ''

    def set_password(self, password):
        """ 用来设置密码的方法，接受密码作为参数 """
        if password:
            self.password = password
            self.password_hash = generate_password_hash(password)  # 将生成的密码保持到对应字段

    def validate_password(self, password):
        """ 用于验证密码的方法，接受密码作为参数 """
        return check_password_hash(self.password_hash, password)  # 返回布尔值

    def to_dict(self):
        dict = self.__dict__
        if "_sa_instance_state" in dict:
            del dict["_sa_instance_state"]
        return dict


# 部门表：admin_dept
class AdminDepartment(db.Model):
    __tablename__ = 'admin_dept'

    TYPE_ADMIN = 2      # 部门类型：中后台
    TYPE_FRONT = 1      # 业务部门

    id = db.Column(db.String(20), primary_key=True)     # 部门id
    name = db.Column(db.String(20))                     # 部门名
    dept_type = db.Column(db.Integer, default=TYPE_FRONT)   # 部门类型，中后台还是业务部门

    @staticmethod
    def new(id, name, dept_type=TYPE_ADMIN):
        dept = AdminDepartment()
        dept.id = id
        dept.name = name
        dept.dept_type = dept_type
        return dept

    def get_dept_type_desc(self) -> str:
        """ 返回部门类型的中文 """
        if self.dept_type == AdminDepartment.TYPE_ADMIN:
            return "中后台"
        elif self.dept_type == AdminDepartment.TYPE_FRONT:
            return "业务部门"
        else:
            return "--"

    def to_dict(self):
        dict = self.__dict__
        if "_sa_instance_state" in dict:
            del dict["_sa_instance_state"]
        return dict


class InvaidIdException(Exception):
    """ 编号错误异常 """
    pass
