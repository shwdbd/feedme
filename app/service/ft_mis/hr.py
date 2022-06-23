#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   hr.py
@Time    :   2022/04/02 08:20:26
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   机构与人员业务逻辑
'''
from app.models.auth import AdminUser, AdminDepartment, InvaidIdException
from app.extensions import db
from sqlalchemy import or_
# from app import app


# 根据部门编号，返回部门公共的虚拟用户
def get_dept_public_user(dept_id: str) -> AdminUser:
    dept = AdminDepartment.query.filter(AdminDepartment.id == dept_id).with_entities(AdminDepartment.name).first()
    if dept:
        user_id = "N{id}00".format(id=dept_id)
        user_name = "{0}公共".format(dept.name)
        return user_id, user_name
    else:
        None, None


# 根据部门id返回部门名
def query_dept_name(id: str) -> str:
    # TODO 待测试
    d = AdminDepartment.query.filter(AdminDepartment.id == id).with_entities(AdminDepartment.name).first()
    if d:
        return d.name
    else:
        return None


# 根据用户id返回姓名
def query_user_name(id: str) -> str:
    # TODO 待测试
    u = AdminUser.query.filter(AdminUser.id == id).with_entities(AdminUser.name).first()
    if u:
        return u.name
    else:
        return None


# 新增加部门
def create_dept(dept_id: str, name: str, type: int = AdminDepartment.TYPE_ADMIN) -> AdminDepartment:
    """新建一个部门

    新建后，自动添加 部门公共、部门未落 两个虚拟用户

    如果部门编号已存在，则抛出Exception InvaidIdException

    Args:
        dept_id (str): _description_
        name (str): _description_
        type (int, optional): _description_. Defaults to AdminDepartment.TYPE_ADMIN.

    Raises:
        InvaidIdException: ID错误

    Returns:
        AdminDepartment: 新部门
    """
    # 检查是否存在
    dept_exist = AdminDepartment.query.filter(AdminDepartment.id == dept_id).first()
    if dept_exist:
        raise InvaidIdException("部门{name}({id})已存在，无法新建".format(id=dept_id, name=dept_exist.name))
    try:
        # 新增部门表
        dept = AdminDepartment()
        dept.id = dept_id
        dept.name = name
        dept.dept_type = type
        db.session.add(dept)
        # 部门公共
        user_00 = AdminUser()
        user_00.id = "N{id}00".format(id=dept_id)
        user_00.name = "{0}公共".format(dept.name)
        user_00.dept_id = dept_id
        user_00.is_virtual = True
        db.session.add(user_00)
        # 部门未落
        user_99 = AdminUser()
        user_99.id = "N{id}99".format(id=dept_id)
        user_99.name = "{0}未落".format(dept.name)
        user_99.dept_id = dept_id
        user_99.is_virtual = True
        db.session.add(user_99)

        # 提交数据库
        db.session.commit()
        # app.logger.info("新建部门{0}".format(name))
    except Exception as e:
        print(str(e))
        db.session.rollback()
        print("回滚！")
    dept = AdminDepartment.query.filter(AdminDepartment.id == dept_id).first()

    return dept


# 新建用户
def create_user(oa_id: str, name: str, dept_id: str, password: str = "12345", is_virtual: bool = False, worker_id: str = "", level: int = AdminUser.LEVEL_PERSON) -> AdminUser:
    """新建真实员工账号

    Args:
        oa_id (str): 10位员工号
        name (str): 姓名
        dept_id (str): 部门编号
        password (str, optional): 初始密码. Defaults to None，默认密码 10位员工号_oa账号.

    Returns:
        AdminUser: 新建的账号对象
    """
    # 检查是否存在
    user_exist = AdminUser.query.filter(AdminUser.id == oa_id).first()
    if user_exist:
        raise InvaidIdException("员工账号 {id} 已存在，无法新建".format(id=oa_id))
    try:
        # 新增部门表
        user = AdminUser()
        user.id = oa_id
        user.oa_id = oa_id
        user.name = name
        user.is_virtual = is_virtual
        user.dept_id = dept_id
        user.worker_id = worker_id
        user.level = level
        user.set_password(password)     # 密码
        db.session.add(user)

        # 提交数据库
        db.session.commit()
        # app.logger.info("新建部门{0}".format(name))
    except Exception as e:
        print(str(e))
        db.session.rollback()
        print("回滚！")
    user = AdminUser.query.filter(AdminUser.id == oa_id).first()

    return user


# 根据工号、OA、姓名查询单一用户
def query_user(worker_id: str = None, oa_id: str = None, name: str = None) -> AdminUser:
    """ 根据工号或OA账号查询员工信息 """
    # 各条件之间是OR关系，都是LIKE查询
    # TODO 待测试
    query_list = []
    if name:
        query_list.append(AdminUser.name.like('%{0}%'.format(name)))
    if worker_id:
        query_list.append(AdminUser.worker_id.like('%{0}%'.format(worker_id)))
    if oa_id:
        query_list.append(AdminUser.oa_id.like('%{0}%'.format(oa_id)))
    query_condition = or_(*query_list)
    users = AdminUser.query.filter(query_condition).order_by(AdminUser.oa_id.desc()).all()
    return users


# if __name__ == "__main__":
#     # with app.app_context():
#         # # 新部门
#         # new_dept = create_dept(dept_id="05", name="新部门名", type=AdminDepartment.TYPE_FRONT)
#         # 查询
#         users = query_user(name="ad")
#         print(users)
