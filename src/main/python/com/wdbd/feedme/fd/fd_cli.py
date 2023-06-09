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
from com.wdbd.feedme.fd.ds_baostock.bs_stock import SecurityListUnit as bs_SecurityListUnit, CnStockDailyK as bs_CnStockDailyK
from com.wdbd.feedme.fd.ds_efinance.ef_stock import SecurityListUnit as ef_SecurityListUnit, CnStockDailyK as ef_CnStockDailyK
from com.wdbd.feedme.fd.tools.data_comparor import datasouce_stat
from com.wdbd.feedme.fd.ds_tushare.ts_stock import TsTradeCal, TsStockDaily, TsStockList
import com.wdbd.feedme.fd.common.common as tl
from com.wdbd.feedme.fd.siw.cli import siw


@click.command()
@click.option('--source', '-s', help='数据源, 可以选择baostock|efinance|tushare', type=str)
@click.option('--data', '-d', help='数据项目', type=str)
@click.option('--from_date', '-f', help='开始日期', type=str)
@click.option('--to_date', '-t', help='终止日期，默认为系统日期今天', type=str)
@click.option('--recover', '-r', help='已有数据是否覆盖, 默认为False', type=bool)
def dd(source: str, from_date: str, to_date: str = None, data: str = None, recover: bool = False):
    """下载证券数据

    Args:
        source (str): 数据源, 可以选择baostock|efinance
        from_date (str): 开始日期时间
        to_date (str, optional): 终止日期时间. Defaults to None，默认为系统日期今天.
        recover (bool, optional): 是否用新数据覆盖现有数据. Defaults to False.
    """
    click.echo('下载数据 ... ')
    if not source:
        click.echo('数据源必须指定')
        return
    elif source.lower() == 'tushare' or source.lower() == 'ts':
        if data.lower() == 'trade_cal' or data.lower() == 'cal':
            # 下载Tushare交易日历
            unit = TsTradeCal()
            res = unit.download_all()
            return
        elif data.lower() == 'stock_daily' or data.lower() == 'daily':
            # 下载Tushare A股日线数据
            if not from_date or from_date == '':
                click.echo("from_date参数必须提供！")
                return
            unit = TsStockDaily()
            res = unit.download_by_date(trade_date=from_date)
            return
    elif source.lower() == 'baostock' or source.lower() == 'bs':
        if not data:
            # 默认下载资产清单
            srv = bs_SecurityListUnit()
            res = srv.download_all()
            if res:
                click.echo('下载成功')
            else:
                click.echo('下载失败')
            return
        elif data.lower() == 'dk' or data.lower() == 'dk':
            # 日线数据
            unit = bs_CnStockDailyK()
            res = unit.download_all()
            return
        elif data.lower() == 'stock-list' or data.lower() == 'sl':
            # 股票和资产清单
            srv = ef_SecurityListUnit()
            res = srv.download_all()
            if res:
                click.echo('下载成功')
            else:
                click.echo('下载失败')
            return
        else:
            click.echo('请显示指定需要下载哪像baostock数据（data参数）')
            return
    elif source.lower() == 'efinance' or source.lower() == 'ef':
        if not data:
            # 存量数据下载
            unit = ef_SecurityListUnit()
            res = unit.download_all()
            return
        elif data.lower() == 'dk' or data.lower() == 'dk':
            # 日线数据
            unit = ef_CnStockDailyK()
            res = unit.download_all()
            return
        elif data.lower() == 'stock-list' or data.lower() == 'sl':
            # 股票清单
            unit = ef_SecurityListUnit()
            res = unit.download_all()
            return
        else:
            click.echo('请显示指定需要下载哪像baostock数据 (data参数) ')
            return
    else:
        click.echo('无效数据源: {}'.format(source))


@click.command()
@click.option('--date', '-d', help='指定的交易日期，默认今日', type=str)
def get_today(date: str = tl.today()):
    """下载今日数据

    Args:
        date (str): 指定交易日期
    """
    # TODO 补充日志输出等内容
    if not date:
        date = tl.today()
    print(date)

    unit = TsStockList()
    unit.download()

    unit = TsStockDaily()
    unit.download_by_date(date)


@click.command()
def stat():
    """ 下载数据统计 """
    datasouce_stat()


@click.group()
def cli():
    pass


cli.add_command(cmd=dd, name="download")
cli.add_command(cmd=get_today, name="today")
cli.add_command(stat)
cli.add_command(siw)


if __name__ == "__main__":
    cli()
