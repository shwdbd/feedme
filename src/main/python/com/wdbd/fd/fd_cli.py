#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   fd_cli.py
@Time    :   2022/07/23 22:46:29
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   FD模块的命令行接口程序
'''
import click
from com.wdbd.fd.main import run_server


@click.command()
def server_start():
    """
    启动数据下载服务
    
    Args:
        无
    
    Returns:
        无
    
    """
    """启动数据下载服务

    Args:
        date (str): 指定交易日期
    """
    click.echo("下载服务启动")
    run_server()

# ==============================================


@click.group()
def cli():
    pass


cli.add_command(cmd=server_start, name="start")


if __name__ == "__main__":
    cli()
