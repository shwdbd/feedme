#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   init_scripts.py
@Time    :   2022/03/27 11:06:10
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   Flask 命令行工具
'''
import click
# 即使不用到，也需要引用
from app.extensions import db
from .load_data.load_admin import load_dept_and_user, load_admin_menu
from .load_data.load_dev_data import load_dev_data


def init_command(app):
    """ 全局脚本  """

    @app.cli.command("myaction", help="试验")
    def myaction():
        print("My Action")

    # 初始化数据库
    @app.cli.command("init-db", help="初始化数据库")
    def init_database():
        click.echo("数据库初始化")
        if click.confirm('本操作会清除现有数据，是否继续？'):
            db.drop_all()
            click.echo("数据表全部清除！")
            db.create_all()
            click.echo("数据库表重建完毕！")

    # 加载初始数据
    @app.cli.command("load-data", help="加载初始数据")
    # @click.option('--moni', is_flag=True, help='加载模拟数据')  # 设置选项
    def load_data():
        """ 数据库环境初始化, 并建立初始Admin账号 """
        click.echo("加载初始数据 ... ")

        # 部门和人员
        load_dept_and_user()
        click.echo("加载部门、员工")

        # 菜单
        load_admin_menu()
        click.echo("加载主菜单")

        # 开发数据
        load_dev_data()
        click.echo("加载开发模拟数据")

        click.echo("加载完成")
