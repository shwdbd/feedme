#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   auth_view.py
@Time    :   2022/03/23 22:55:47
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   框架权限控制模块 Views
'''
from flask import (
    Blueprint, flash, jsonify, redirect, render_template, request, session, url_for
)
from app.models.auth import AdminUser
from flask_login import login_user, logout_user, current_user
from flask import current_app as app
from app.extensions import db
from app.commons.utils.flask_utils import AjaxResponse
from app.service.admin_srv import get_menu_dict


# 构建蓝图
bp = Blueprint('auth', __name__, url_prefix='/auth')


# 欢迎页面
@bp.route('/welcome')
def welcome():
    return render_template('auth/welcome.html')


# 系统登录
@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        user = AdminUser.query.get(username)
        app.logger.debug("数据库中查询用户{0}".format(user))

        if user is None:
            error = '无效的用户名'
        elif not user.validate_password(password):
            error = '密码错误'

        if error is None:
            login_user(user)    # 登记用户登录
            return render_template('index.html')

        app.logger.error("登录失败, error = {0}".format(error))
        flash(error)

    return render_template('auth/login.html')


# 系统登出
@bp.route('/logout')
def logout():
    session.clear()
    logout_user()
    return redirect(url_for('auth.login'))


# 返回菜单数据
@bp.route('/menu_data', methods=('GET', 'POST'))
def menu_data():
    """ 返回菜单数据 """
    menu_d = get_menu_dict()
    menu_data = {
        "code": 0,
        "msg": "",
        "count": len(menu_d),
        "data": menu_d
    }
    # menu_data = {
    #     "code": 0,
    #     "msg": "",
    #     "count": 3,
    #     "data": [
    #         {
    #             "authorityId": 100,
    #             "authorityName": "系统管理",
    #             "menuUrl": '',
    #             "isMenu": 0,
    #             "parentId": -1,
    #             "data": [
    #                 {
    #                     "authorityId": 101,
    #                     "authorityName": "部门维护",
    #                     "menuUrl": "/admin/dept",
    #                     "isMenu": 1,
    #                     "parentId": 100,
    #                 },
    #                 {
    #                     "authorityId": 102,
    #                     "authorityName": "人员维护",
    #                     "menuUrl": "/admin/user",
    #                     "isMenu": 1,
    #                     "parentId": 100,
    #                 }
    #             ]
    #         }
    #     ]
    # }

    return jsonify(menu_data)


# @bp.route('/menu')
# def to_menu():
#     return render_template('auth/new_menu.html')


# 关于我
@bp.route('/about')
def about_me():
    return render_template('auth/about.html')


# 修改密码
@bp.route('/reset_password')
def reset_password():
    return render_template('auth/reset_password.html')


@bp.route('/reset_password_action', methods=(['POST']))
def reset_password_action():
    # TODO 待测试
    # 直接更新密码
    if request.method == 'POST':
        new_password = request.form['password']
        user = AdminUser.query.get(current_user.id)
        if user is None:
            flash("用户id无效")
        user.set_password(new_password)
        db.session.commit()
        app.logger.info("用户{0}({1})密码已修改".format(current_user.name, current_user.id))

        return jsonify(AjaxResponse(message="重置密码成功").to_json())

    flash("系统错误")
