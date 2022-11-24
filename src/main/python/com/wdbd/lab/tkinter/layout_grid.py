#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   layout_grid.py
@Time    :   2022/11/22 11:15:48
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   部件布局之Grid模式

- 简单 3*3 布局
- 第一行是两个Label
- 第二行左边是一个高Text, 右边是一组3个按钮

'''
import tkinter as tk


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.set_window()
        self.create_compont()

    # 设置窗口
    def set_window(self):
        self.title("Grid布局")
        self.geometry("300x400")     # 窗口大小
        self.resizable(True, True)

    # 创建顶部部件
    def create_compont(self):
        # self.grid_columnconfigure(1, weight=2)
        # self.grid_rowconfigure(1, weight=1)
        # 第一行：
        tk.Label(self, text="Label 1*1").grid(row=1, column=1, sticky=tk.NSEW, pady=10)
        tk.Label(self, text="Label 1*1").grid(row=1, column=2, sticky=tk.NSEW)
        # 第二行
        tk.Text(self, width=20, height=10).grid(row=2, column=1, sticky=tk.NSEW)
        # 一组Frame
        self.f22 = tk.Frame(self, relief="solid", bd=2)
        self.f22.grid(row=2, column=2, sticky=tk.NSEW)
        tk.Button(self.f22, text="按钮1").pack()
        tk.Button(self.f22, text="按钮2").pack()
        tk.Button(self.f22, text="按钮3").pack()


if __name__ == "__main__":
    app = App()
    app.mainloop()
