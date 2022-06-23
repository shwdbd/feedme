#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   init_error_page.py
@Time    :   2022/03/29 21:31:58
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   初始化全局错误页面
'''
from flask import render_template


def init_error_views(app):

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    # @app.errorhandler(500)
    # def internal_server_error(e):
    #     return render_template('errors/500.html'), 500
