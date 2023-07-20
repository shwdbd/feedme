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
# from com.wdbd.feedme.fd.ds_akshare.ak_cal import AkTradeCal
from com.wdbd.feedme.fd.ds_akshare import download_ak_cal, download_ak_stock_list
from com.wdbd.feedme.fd.tools.data_comparor import datasouce_stat
from com.wdbd.feedme.fd.ds_tushare.ts_stock import TsTradeCal, TsStockDaily, TsStockList
import com.wdbd.feedme.fd.common.common as tl
from com.wdbd.feedme.fd.siw.cli import siw


# 数据源清单
DATA_SOURCE = ['tushare', 'baostock', 'akshare']


# 数据下载
@click.command()
@click.option('--source', '-s', help='数据源, 可以选择baostock|efinance|tushare', type=click.Choice(DATA_SOURCE), default="tushare")
@click.option('--item', '-i', help='数据项目, 如: trade_cal', type=click.STRING)
@click.option('--date', '-d', help='开始日期', type=click.STRING)
@click.option('--date2', '-d2', help='终止日期，默认为系统日期今天', type=click.STRING, default=tl.today())
@click.option('--recover', '-r', help='已有数据是否覆盖, 默认为False', type=click.BOOL, default=False)
def dd(source: str, date: str, date2: str = None, item: str = None, recover: bool = False):
    """下载证券数据

    Args:
        source (str): 数据源, 可以选择baostock|efinance
        from_date (str): 开始日期时间
        to_date (str, optional): 终止日期时间. Defaults to None，默认为系统日期今天.
        recover (bool, optional): 是否用新数据覆盖现有数据. Defaults to False.
    """
    # click.echo('下载A股股票数据')
    click.secho('下载A股股票数据', fg='red')

    click.echo("source={0}".format(source))
    click.echo("item={0}".format(item))
    click.echo("date={0}".format(date))
    click.echo("date2={0}".format(date2))
    click.echo("recover={0}".format(recover))

    # if not source:
    #     click.echo('数据源参数为空。请使用 --help 观看提示')
    #     return
    # elif source.lower() == 'tushare' or source.lower() == 'ts':
    #     if not data:
    #         click.echo(
    #             '请选择合法的数据项目（允许多选，用|分隔）。目前可以选择的是：\n- cal 交易日历\n- stock-list 股票清单\n- stock-daily 股票日线')
    #         return
    #     elif data.lower() == 'trade_cal' or data.lower() == 'cal':
    #         # # 下载Tushare交易日历
    #         # unit = TsTradeCal()
    #         # res = unit.download_all()
    #         click.echo("下载Tushare全量交易日历数据")   # FIXME 实现功能
    #         return
    #     elif data.lower() == 'stock_daily' or data.lower() == 'daily':
    #         # # 下载Tushare A股日线数据
    #         # if not from_date or from_date == '':
    #         #     click.echo("from_date参数必须提供！")
    #         #     return
    #         # unit = TsStockDaily()
    #         # res = unit.download_by_date(trade_date=from_date)
    #         click.echo("下载Tushare全量交易日历数据")   # FIXME 实现功能
    #         return
    #     else:
    #         click.echo(
    #             '请选择合法的数据项目（允许多选，用|分隔）。目前可以选择的是：\n- cal 交易日历\n- stock-list 股票清单\n- stock-daily 股票日线')
    # elif source.lower() == 'baostock' or source.lower() == 'bs':
    #     if not data:
    #         # # 默认下载资产清单
    #         # srv = bs_SecurityListUnit()
    #         # res = srv.download_all()
    #         # if res:
    #         #     click.echo('下载成功')
    #         # else:
    #         #     click.echo('下载失败')
    #         click.echo(
    #             '请选择合法的数据项目（允许多选，用|分隔）。目前可以选择的是：\n- stock-list 股票清单\n- stock-daily 股票日线（默认）')
    #         # TODO 这里允许使用默认
    #         return
    #     # elif data.lower() == 'dk' or data.lower() == 'dk':
    #     #     # 日线数据
    #     #     unit = bs_CnStockDailyK()
    #     #     res = unit.download_all()
    #     #     return
    #     # elif data.lower() == 'stock-list' or data.lower() == 'sl':
    #     #     # 股票和资产清单
    #     #     srv = ef_SecurityListUnit()
    #     #     res = srv.download_all()
    #     #     if res:
    #     #         click.echo('下载成功')
    #     #     else:
    #     #         click.echo('下载失败')
    #     #     return
    #     else:
    #         click.echo(
    #             '请选择合法的数据项目（允许多选，用|分隔）。目前可以选择的是：\n- stock-list 股票清单\n- stock-daily 股票日线（默认）')
    #         return
    # elif source.lower() == 'akshare' or source.lower() == 'ak':
    #     if not data:
    #         click.echo(
    #             '请选择合法的数据项目（允许多选，用|分隔）。目前可以选择的是：\n- stock-list 股票清单\n- stock-daily 股票日线（默认）')
    #         # TODO 这里允许使用默认
    #         return
    #     else:
    #         # TODO 无法对未知data参数进行提示
    #         if not (set(data.split("|")) <= set(["stock-list", "stock-daily"])):
    #             click.echo(
    #                 '请选择合法的数据项目（允许多选，用|分隔）。目前可以选择的是：\n- stock-list 股票清单\n- stock-daily 股票日线（默认）')
    #             # TODO 这里允许使用默认
    #             return
    #         for data_item in data.split("|"):
    #             if data_item.lower() == 'stock-list':
    #                 click.echo('开始下载Akshare股票清单全量')
    #                 # TODO 待实现
    #                 # TODO 使用工厂方法，实例化Unit，并调用download进行操作，注入部分参数（日期，是否覆盖等）
    #                 return
    #             elif data_item.lower() == 'stock-daily':
    #                 click.echo('开始下载Akshare股票股票日线全量')
    #                 # TODO 待实现
    #                 return
    # else:
    #     click.echo('请录入合法的数据源名称。目前可以选择的是：Tushare（ts）、Baostock（bs）、Akshare（ak）')


@click.command()
@click.option('--date', '-d', help='指定的交易日期，默认今日', type=str, required=False)
def get_today(date: str = tl.today()):
    """下载今日数据

    Args:
        date (str): 指定交易日期
    """
    click.echo("下载今日数据（{0}）".format(tl.today()))
    # # TODO 补充日志输出等内容
    # if not date:
    #     date = tl.today()
    # print(date)

    # unit = TsStockList()
    # unit.download()

    # unit = TsStockDaily()
    # unit.download_by_date(date)


# @click.command()
# def stat():
#     """ 下载数据统计 """
#     datasouce_stat()


# ==============================================
# A股指令
# ==============================================
@click.group()
def astock():
    """ a股数据指令 """
    pass


# 存量数据下载
@astock.command(name="dl-all")
@click.option('--source', '-s', help='数据源, 可以选择baostock|akshare|tushare', type=click.Choice(DATA_SOURCE), required=True, prompt="请选择数据源")
@click.option('--item', '-i', help='数据项目', type=click.Choice(['cal', 'list', 'daily']), prompt="请选择数据项目")
@click.option('--date', '-d', help='开始日期', type=click.STRING)
@click.option('--date2', '-d2', help='终止日期，默认为系统日期今天', type=click.STRING, default=tl.today(), prompt="请输入截止日期 --date2")
@click.option('--recover', '-r', help='已有数据是否覆盖, 默认为False', type=click.BOOL, default=False)
def dlall(source: str, date: str, date2: str = None, item: str = None, recover: bool = False):
    """下载证券历史存量数据

    Args:
        source (str): 数据源, 可以选择baostock|efinance
        from_date (str): 开始日期时间
        to_date (str, optional): 终止日期时间. Defaults to None，默认为系统日期今天.
        recover (bool, optional): 是否用新数据覆盖现有数据. Defaults to False.
    """
    click.secho("下载证券历史存量数据", fg="red")
    # 根据数据源、数据项目分开处理
    if source.lower() == 'tushare':
        if item.lower() == 'cal':
            pass
    elif source.lower() == 'akshare':
        if item.lower() == 'cal':
            click.secho("下载Akshare，交易日历全量数据", fg="blue")
            res = download_ak_cal()
            if not res or res["result"] is False:
                click.secho("下载失败", fg="red")
                click.secho(res["message"], fg="red")
            else:
                click.secho("下载成功！", fg="blue")
        elif item.lower() == 'list':
            click.secho("下载更新Akshare股票清单", fg="blue")
            res = download_ak_stock_list()
            if not res or res["result"] is False:
                click.secho("下载失败", fg="red")
                click.secho(res["message"], fg="red")
            else:
                click.secho("下载成功！", fg="blue")
        else:
            pass
    elif source.lower() == 'baostock':
        pass
    else:
        click.secho("非法的数据源！{0}".format(source), fg="red")
        return
    # click.echo("source={0}".format(source))
    # click.echo("item={0}".format(item))
    # click.echo("date={0}".format(date))
    # click.echo("date2={0}".format(date2))
    # click.echo("recover={0}".format(recover))


@astock.command()
@click.option('--date', '-d', help='比对开始日期（含）', type=click.STRING, required=True, prompt="请输入开始日期")
@click.option('--date2', '-d2', help='比对结束日期（含）', type=click.STRING, prompt="请输入截止日期", default=tl.today())
@click.option('--source', '-s', help='数据源, 可以选择baostock|efinance|tushare', type=click.Choice(DATA_SOURCE), default="tushare", prompt="请选择数据源")
def omit(date: str, date2: str, source: str):
    """ 查询数据缺失情况 """
    # TODO 待实现
    click.echo('查询数据缺失情况')


# default=tl.today()
# prompt = True,
# 参数个数，nargs=2
@astock.command()
@click.option('--date', '-d', help='比对开始日期（含）', type=click.STRING, required=True, prompt="请输入开始日期 --date")
@click.option('--date2', '-d2', help='比对结束日期（含）', type=click.STRING, default=tl.today(), prompt="请输入截止日期 --date2")
@click.option('--output', '-o', help='结果输出文件路径', type=click.STRING, default="check_result.txt")
@click.option('--source', '-s', help='数据源, 可以选择baostock|efinance|tushare', type=click.Choice(DATA_SOURCE), default="tushare")
def check(date: str, date2: str, output: str, source: str):
    """ 查询数据源之间数据冲突情况 """
    # TODO 待实现
    click.echo(date2)
    click.echo('查询数据源之间数据冲突情况')


# ==============================================


@click.group()
def cli():
    pass


cli.add_command(cmd=dd, name="download")
cli.add_command(cmd=get_today, name="today")
# cli.add_command(stat)
cli.add_command(siw)
cli.add_command(cmd=astock, name="astock")


if __name__ == "__main__":
    cli()
