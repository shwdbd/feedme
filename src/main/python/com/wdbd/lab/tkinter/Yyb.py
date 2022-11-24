#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   Yyb.py
@Time    :   2022/11/22 13:18:57
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   营业部UI
'''
import tkinter as tk


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.set_window()
        self.create_top()
        self.create_body()
        self.create_bottom()

    # 设置窗口
    def set_window(self):
        self.title("测试窗口")
        self.geometry("500x300")     # 窗口大小
        self.resizable(True, True)

    # 创建顶部部件
    def create_top(self):
        self.label_text = tk.StringVar()
        self.label_text.set("旧值")
        self.label_a = tk.Label(self, text="Top", textvariable=self.label_text)
        self.label_a.pack()

    # 创建主体部件
    def create_body(self):
        self.input = tk.StringVar()
        tk.Entry(self, textvariable=self.input).pack()

    # 创建底部部件
    def create_bottom(self):
        tk.Button(self, text="按钮, 内容打印到控制台", command=self.btn_onclick).pack()

    # 按钮回调函数
    def btn_onclick(self):
        """按钮点击
        """
        print("输入值:{0}".format(self.input.get()))
        self.label_text.set("新值")


if __name__ == "__main__":
    app = App()
    app.mainloop()
