#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   cli.py
@Time    :   2023/06/09 13:32:08
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   SIW项目命令行接口
'''
import click


# SIW项目的主入口
@click.group()
def siw():
    """ 股票指标观察器 """
    print("SIW!")


# 命令1：解析财报文件命令
@click.command()
@click.option('--dir', '-d', help=' 按文件夹解析，参数指定目录位置', type=str)
@click.option('--file', '-f', help='按单个文件解析，参数指定文件绝对路径', type=str)
def load(dir: str):
    """ 解析财报文件 """
    # TODO 待实现
    pass


# 命令2：查询指标命令
@click.command()
@click.option('--stock', '-s', help='股票代码或名称，支持模糊查询', type=str)
@click.option('--time', '-t', help='财报期限，支持yyyyQn，或 yyyy年报 或仅 年份yyyy', type=str)
@click.option('--index', '-i', help='指标名称，支持模糊查询', type=str)
def query(dir: str):
    """ 查询指标 """
    # TODO 待实现
    pass


# 命令注册
siw.add_command(load)
