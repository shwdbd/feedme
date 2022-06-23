#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   fd_cli.py
@Time    :   2021/08/16 15:02:38
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   FD数据下载命令行接口
'''
import click
from gtp.fd.base.data_service import DataService
from gtp.fd.base.dlserver import DLServer


@click.group()
def main():
    """ 总入口 """
    pass


@main.group(name="download", help='数据下载')
def download():
    pass


@main.group(name="server", help='服务器')
def server():
    pass


main.add_command(download)
main.add_command(server)

# ==========================================
# 数据下载类命令
@download.command(name="all", help='存量数据下载')
@click.option('-s', '--start_date', help='数据开始日期,yyyyMMdd格式', type=click.STRING, default=None)
@click.option('-r', '--rebuild', help='是否重建数据环境', type=click.BOOL, default=True)
@click.option('-t', '--set_name', help='组合名', type=click.STRING, default=None)
def download_all(start_date: str = None, rebuild: bool = True, set_name: str = None):
    """存量数据下载

    Args:
        start_date (str, optional): 数据开始日期,yyyyMMdd格式. Defaults to None.
        rebuild (bool, optional): 是否重建数据环境. Defaults to True.
        set_name (str, optional): 组合名. Defaults to None.
    """
    srv = DataService()
    res = srv.download_all(set_name=set_name, rebuild=rebuild, start_date=start_date)
    if res:
        click.echo("全部下载完毕")
    else:
        click.echo(click.style("下载失败", fg='red'))


@download.command(name="bydate", help='按日期下载数据')
@click.option('-u', '--unit_name', help='数据单元名称', type=click.STRING, default=None)
@click.option('-d', '--date', help='指定日期，yyyyMMdd格式', type=click.STRING, default=None)
@click.option('-d1', '--start', help='时间段开始，yyyyMMdd格式', type=click.STRING, default=None)
@click.option('-d2', '--end', help='时间段结束，yyyyMMdd格式', type=click.STRING, default=None)
@click.option('-s', '--set_name', help='组合名', type=click.STRING, default=None)
def download_bydate(unit_name: str = None, date: str = None, start: str = None, end: str = None, set_name: str = None):
    """ 按日期下载数据 """
    srv = DataService()
    res = srv.download_bydate(unit_name=unit_name, set_name=set_name, date=date, start_date=start, end_date=end)
    if res:
        click.echo("全部下载完毕")
    else:
        click.echo(click.style("下载失败", fg='red'))


@download.command(name="query", help='查询下载情况')
@click.option('-u', '--unit_name', help='数据单元名称', type=click.STRING, default=None)
@click.option('-m', '--missing', help='查询是否查询缺失日期', type=click.BOOL, default=False)
@click.option('-s', '--set_name', help='组合名', type=click.STRING, default=None)
@click.option('-d1', '--start', help='时间段开始，yyyyMMdd格式', type=click.STRING, default=None)
@click.option('-d2', '--end', help='时间段结束，yyyyMMdd格式', type=click.STRING, default=None)
def download_query(unit_name: str = None, missing: bool = False, set_name: str = None, start: str = None, end: str = None):
    # TODO 待实现
    print("查询下载情况")


# ==========================================
# 数据服务器类命令
@server.command(name="start", help='服务启动')
@click.option('-s', '--set_name', help='组合名', type=click.STRING, default=None)
def server_start(set_name: str = None):
    # 服务器启动
    srv = DLServer(set_name=set_name)
    res = srv.start()
    if res:
        click.echo("全部下载完毕")
    else:
        click.echo(click.style("下载失败", fg='red'))


@server.command(name="shundown", help='服务关闭')
def server_shundown():
    srv = DLServer()
    srv.shutdown()


if __name__ == "__main__":
    main()
