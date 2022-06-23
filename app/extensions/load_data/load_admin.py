#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   dept_user.py
@Time    :   2022/04/01 14:11:49
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   加载部门、员工数据
'''
import click
from app.models.auth import AdminUser, AdminDepartment
from app.models.admin import Menu
from app.extensions import db
from app.service.ft_mis.hr import create_dept, create_user


def load_dept_and_user():
    """ 加载部门、员工数据  """
    # 加载部门
    create_dept("00", "分行公共")
    create_dept("01", "综合管理部")
    create_dept("02", "信贷管理部")
    create_dept("03", "金融同业部")
    create_dept("04", "授信评审部")
    create_dept("05", "纪检监察室")
    create_dept("06", "公司业务部")
    create_dept("07", "交易银行部")
    create_dept("08", "营业部")
    create_dept("09", "跨境金融服务部")
    create_dept("10", "法律合规部")
    create_dept("11", "财务管理部")
    create_dept("51", "投资银行部", type=AdminDepartment.TYPE_FRONT)
    create_dept("52", "自贸业务一部", type=AdminDepartment.TYPE_FRONT)
    create_dept("53", "自贸业务二部", type=AdminDepartment.TYPE_FRONT)
    create_dept("54", "临港金融部", type=AdminDepartment.TYPE_FRONT)

    # 添加默认的Admin账号
    admin_id = click.prompt('管理员账号', type=str, default="admin")
    admin_password = click.prompt('管理员密码', type=str, default="12345")
    create_user(oa_id=admin_id, name="超级管理员", dept_id="00", password=admin_password, level=AdminUser.LEVEL_BRANCH)


def load_admin_menu():
    """ 加载菜单  """
    r200 = Menu(200, "业绩归属", "", parent_id=-1, )
    db.session.add(r200)
    r200_1 = Menu(201, "申报单", "/ftmis/belongs/form_list", parent_id=200, )
    db.session.add(r200_1)
    r200_2 = Menu(202, "归属查询", "/ftmis/belongs/query", parent_id=200, )
    db.session.add(r200_2)

    r1 = Menu(9900, "系统管理", "", parent_id=-1, )
    db.session.add(r1)
    r1_1 = Menu(9901, "部门维护", "/admin/dept", parent_id=9900, )
    db.session.add(r1_1)
    r1_2 = Menu(9902, "人员维护", "/admin/user", parent_id=9900, )
    db.session.add(r1_2)

    db.session.commit()
