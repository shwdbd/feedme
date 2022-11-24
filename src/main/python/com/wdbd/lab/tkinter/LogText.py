#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   LogText.py
@Time    :   2022/11/22 13:31:41
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   日志追加的示例

功能：点击按钮，在Text控件最后添加记录

要解决的问题：
1. 按钮触发Text尾部添加一行
2. 添加后，自动滚动到最后一行

'''
import tkinter as tk
import datetime
from tkinter.scrolledtext import ScrolledText


class App(tk.Tk):
    """ 日志模拟 """

    def __init__(self):
        super().__init__()

        self.set_window()
        self.create_ui()

    # 设置窗口
    def set_window(self):
        self.title("日志模拟窗口")
        self.geometry("500x500")     # 窗口大小 宽*高
        self.resizable(False, False)

    # 创建部件
    def create_ui(self):
        # 日志内容框
        self.text_log = ScrolledText(self, height=30, width=20)
        self.text_log.grid(row=1, column=1, sticky=tk.NSEW, columnspan=1)
        # self.text_log.insert(tk.END, "Welcome to apidemos.com\nWelcome to apidemos.com\n")
        tk.Button(self, text="添加内容", command=self.btn_onclick).grid(row=1, column=2, sticky=tk.NSEW)
        tk.Button(self, text="按钮2", command=self.btn_onclick).grid(row=2, column=2, sticky=tk.NSEW)

    # 按钮回调函数
    def btn_onclick(self):
        """按钮点击
        """
        self.text_log.insert(tk.END, "Welcome to apidemos.com\nHa ha ha\n" + str(datetime.datetime.now()))
        self.text_log.see(tk.END)       # 保持在最底一行


if __name__ == "__main__":
    app = App()
    app.mainloop()
