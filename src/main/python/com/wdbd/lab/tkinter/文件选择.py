#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   文件选择.py
@Time    :   2022/11/23 16:20:49
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   文件选择框
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

    def upload_file(self):
        # 打开文件选择框（一次选择1个文件）
        # askopenfilenames 一次选择多个文件
        selectFile = tk.filedialog.askopenfilename()
        print(selectFile)

    # 创建顶部部件
    def create_compont(self):
        self.btn = tk.Button(self, text="选择文件", command=self.upload_file).pack()
        self.entry1 = tk.Entry(self, width=40).pack()


if __name__ == "__main__":
    app = App()
    app.mainloop()
