#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   download_main.py
@Time    :   2022/11/29 15:29:17
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   下载操作图形界面主窗口
'''
import tkinter as tk
import tkinter.messagebox as msgbox
from com.wdbd.feedme.fd.common.common import get_cfg
import com.wdbd.feedme.fd.fd_api as fd_api
import com.wdbd.feedme.fd.common.common as tl
import dateutil
from com.wdbd.feedme.fd.common.data_gateway import TushareGateWay
from com.wdbd.feedme.fd.ds_tushare.ts_stock import TsStockList, TsStockDaily, TsTradeCal


# 主界面
class App(tk.Tk):
    """ 下载图形界面 """

    def __init__(self):
        super().__init__()

        self.set_window()
        self.create_mainframe()
        self.create_menu()

    # 设置窗口
    def set_window(self):
        self.title("Feedme download")
        win_width = 500
        win_height = 300
        self.geometry("{0}x{1}+{2}+{3}".format(win_width, win_height, int((self.winfo_screenwidth() -
                      win_width)/2), int((self.winfo_screenheight()-win_height)/2)))     # 窗口大小
        self.resizable(False, False)

    # 创建主体部件
    def create_mainframe(self):
        # 日志内容框
        self.status_list = tk.Listbox(self, width=40, height=10)
        self.status_list.grid(row=0, column=0, sticky=tk.N)
        self.reflash_status()    # 初始化列表
        tk.Button(self, text="刷新", command=self.reflash_status).grid(
            row=0, column=1, sticky=tk.N)

    def reflash_status(self):
        """ 初始化状态列表 """
        self.status_list.delete(0, tk.END)
        self.status_list.insert(tk.END, "最新数据日期:{0}".format(
            tl.d2viewstr(fd_api.get_last_date())))
        # 交易日历情况
        cal_info = fd_api.get_cal_info()
        self.status_list.insert(tk.END, "交易日历: [{start} - {end}, 交易所：{ex}]".format(start=cal_info.get("start_date"),
                                                                                   end=cal_info.get("end_date"), ex=cal_info.get("exchange")))

    # 创建菜单
    def create_menu(self):
        """ 创建菜单 """
        menu = tk.Menu(self)
        # 下载菜单组
        download_menu = tk.Menu(menu, tearoff=False)
        download_menu.add_command(
            label="下载今日数据", command=self.menu_download_today_onclick)
        download_menu.add_separator()
        # 历史数据下载
        download_history_data_menu = tk.Menu(download_menu, tearoff=False)
        download_history_data_menu.add_command(
            label="Tushare 股票日线数据", command=self.menu_download_his_onclick)
        download_menu.add_cascade(
            label="历史数据下载", menu=download_history_data_menu)
        # 交易日历下载
        download_menu.add_command(
            label="下载交易日历", command=self.menu_download_cal_onclick)
        menu.add_cascade(label="下载", menu=download_menu)

        # About菜单组
        menu.add_command(label="About", command=self.menu_about_onclick)
        self.config(menu=menu)

    def menu_download_his_onclick(self):
        """ 菜单：下载历史数据 """
        msgbox.showinfo(title="建设中", message="功能尚在建设中")

    def menu_download_cal_onclick(self):
        """ 菜单：下载交易日历 """
        DownloadCalWin(parent=self, )

    def menu_download_today_onclick(self):
        """ 菜单：下载今日数据 """
        DownloadTodayWin(parent=self)

    def menu_about_onclick(self):
        """ 菜单：关于 """
        AboutWin(parent=self)


# 日历数据下载窗口
class DownloadCalWin(tk.Toplevel):

    def __init__(self, parent):
        tk.Toplevel.__init__(self, parent)
        self.set_window()
        self.init_tk()

    def set_window(self):
        self.title("下载交易日历数据")
        win_width = 600
        win_height = 300
        self.geometry("{0}x{1}+{2}+{3}".format(win_width, win_height, int((self.winfo_screenwidth() -
                      win_width)/2), int((self.winfo_screenheight()-win_height)/2)))     # 窗口大小
        self.resizable(False, False)

    def log(self, message):
        # 输出到日志栏
        self.txt_log.insert(tk.INSERT, "{0}\n".format(message))

    def download(self):
        # 下载交易日历数据
        srv = TsTradeCal()
        res = srv.download_all()
        if not res or not res["result"]:
            self.log("下载失败, {0}".format(res["msg"]))
        else:
            self.log("下载成功, {0}".format(res["msg"]))

    def init_tk(self):
        """ 布局界面 """
        self.leftFrame = tk.Frame(self, width="300")
        self.txt_log = tk.Text(self.leftFrame, width=50)
        self.txt_log.pack()
        self.leftFrame.grid(row=0, column=0, sticky=tk.NW)

        self.rightFrame = tk.Frame(self, width="300", padx=20, pady=20)
        tk.Button(self.rightFrame, text="下载", command=self.download).pack()
        self.rightFrame.grid(row=0, column=1, sticky=tk.NE)


# "关于"窗口
class AboutWin(tk.Toplevel):
    """ 关于 窗口 """

    def __init__(self, parent):
        tk.Toplevel.__init__(self, parent)
        self.set_window()
        self.add_version()

    def set_window(self):
        self.title = "关于"
        win_width = 200
        win_height = 200
        self.geometry("{0}x{1}+{2}+{3}".format(win_width, win_height, int((self.winfo_screenwidth() -
                      win_width)/2), int((self.winfo_screenheight()-win_height)/2)))     # 窗口大小
        self.resizable(False, False)

    def add_version(self):
        """ 添加部件 """
        tk.Label(self, text="").pack()
        tk.Label(self, text="Feedme {ver}".format(
            ver=get_cfg("feedme", "version"))).pack()
        tk.Label(self, text="").pack()
        tk.Label(self, text="数据库配置文件地址：\n{path}".format(
            path=get_cfg("sqlite3", "db.path"))).pack()


# 当日数据下载窗口
class DownloadTodayWin(tk.Toplevel):

    def __init__(self, parent):
        tk.Toplevel.__init__(self, parent)
        self.set_window()
        self.init_tk()

    def set_window(self):
        self.title = "下载今日数据"
        win_width = 600
        win_height = 300
        self.geometry("{0}x{1}+{2}+{3}".format(win_width, win_height, int((self.winfo_screenwidth() -
                      win_width)/2), int((self.winfo_screenheight()-win_height)/2)))     # 窗口大小
        self.resizable(False, False)

    def init_tk(self):
        """ 布局界面 """
        self.topFrame = tk.Frame(self)
        tk.Label(self.topFrame, text="系统日期: ").grid(
            row=0, column=0, sticky=tk.EW)
        tk.Label(self.topFrame, text=tl.today()).grid(
            row=0, column=1, sticky=tk.W)
        tk.Label(self.topFrame, text="数据日期:").grid(
            row=1, column=0, sticky=tk.EW)
        # self.txt_date = tk.Entry(self, validate="focusout", validatecommand=self.validate_txt_date)
        self.txt_date = tk.Entry(self.topFrame)
        self.txt_date.insert(tk.INSERT, tl.today())
        # TODO 输入检验 validatecommand=(f, s1, s2, ...) va
        self.txt_date.grid(row=1, column=1, sticky=tk.EW)
        tk.Button(self.topFrame, text="下载", command=self.download).grid(
            row=1, column=3, sticky=tk.EW)
        self.topFrame.pack()

        self.logFrame = tk.Frame(self)
        self.txt_log = tk.Text(self.logFrame, width="80")
        self.txt_log.pack()
        self.logFrame.pack()

    def validate_txt_date(self):
        """ 日期空间，校验 """
        # print(self.txt_date.get())
        try:
            # s = datetime.datetime.strptime(self.txt_date.get(), tl.DATE_FORMAT)
            # print(s)
            dateutil.parser.parse(self.txt_date.get())
            return False
        except Exception:
            self.txt_date.delete(0, tk.END)
            return False

    def log(self, message):
        # 输出到日志栏
        self.txt_log.insert(tk.INSERT, "{0}\n".format(message))

    # 按日下载数据动作
    def _download_by_date(self, trade_date):
        """ 按日下载数据动作 """
        self.log("开始下载{0}的数据".format(trade_date))
        srv = TsStockList()
        res = srv.download()
        if res["result"]:
            self.log("股票清单更新完毕")
        else:
            self.log("股票清单更新失败!")
            return

        srv = TsStockDaily()
        res = srv.download_by_date(trade_date=trade_date)
        if res["result"]:
            self.log("股票日线数据更新完毕")
            for message in res["msg"]:
                self.log(message)
            return True
        else:
            self.log("股票日线数据更新失败!")
            for message in res["msg"]:
                self.log(message)
            return False

    def download(self):
        """ 执行下载当日数据操作 """
        # 1. 如果没有指定日期，则日期为当前系统日期
        # 2. 判断是否为交易日，如果否则终止
        # 3. 判断当日Tushare数据是否提供，未提供则终止
        # 4. 设置 按钮为 Disabled
        # 5. 如果当日已有数据，则弹出确认窗口，用户确认后覆盖更新，否则下载终止；
        # 6. 完成每一项数据下载，在日志栏中输出。(专用函数)
        # END

        # 交易日期
        trade_date = self.txt_date.get()
        print(trade_date)
        if trade_date.strip() == '':
            trade_date = tl.today()

        # 判断是否为交易日
        if not fd_api.is_trade_date(date=trade_date):
            # 非交易日
            self.log("{0}为非交易日，下载终止".format(trade_date))
            self.log("-"*20)
            return

        # 判断当日Tushare数据是否提供，未提供则终止
        gw = TushareGateWay()
        if not gw.has_data(callback=gw.api.daily, trade_date=trade_date):
            # API无数据
            self.log("{0} 网络接口尚未提供数据，下载终止".format(trade_date))
            self.log("-"*20)
            return

        # 如果当日已有数据，则弹出确认窗口，用户确认后覆盖更新，否则下载终止:
        if fd_api.has_data(date=trade_date, item="daily", ds="tushare"):
            # msgbox.showinfo(title="fdafda", message="内容")
            if not msgbox.askokcancel(title="数据覆盖？", message="日期{0}数据已存在，是否重新下载并覆盖本地？".format(trade_date)):
                self.log("用户选择终止。")
                self.log("-"*20)
                return
            else:
                # 开始实施下载
                self._download_by_date(trade_date)
        else:
            # 开始实施下载
            self._download_by_date(trade_date)
        self.log("-"*20)
        return
