#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   init_flask_login.py
@Time    :   2022/03/24 10:07:05
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   注册flask login组件
'''
from flask_login import LoginManager
from app.models.auth import AdminUser


def init_login_manager(app):
    login_manager = LoginManager(app)  # 实例化扩展类
    login_manager.login_view = 'auth.login'     # 验证失败跳转的界面
    login_manager.login_message = "请先登录"     # 用户重定向到登录页面时闪出的消息
    login_manager.refresh_view = 'auth.login'   # 用户需要重新进行身份验证时要重定向到的视图的名称
    login_manager.needs_refresh_message = "请重新登录"
    # TODO 补充各类的参数

    @login_manager.user_loader
    def load_user(user_id):  # 创建用户加载回调函数，接受用户 ID 作为参数
        user = AdminUser.query.get(user_id)  # 用 ID 作为 User 模型的主键查询对应的用户
        return user  # 返回用户对象
