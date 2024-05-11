#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   test_os_path.py
@Time    :   2024/05/10 11:17:15
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   None
'''
import unittest
from pathlib import Path


class TestPathForOs(unittest.TestCase):

    # def test_path(self):
    #     # 项目的根目录
    #     print(f"项目根目录：{Path().cwd()}")
    #     print(f"项目根目录：{Path().absolute()}")
    #     # /Users/junjiewang/python_prj/projects/feedme
    #     print(f"当前操作系统用户根目录：{Path().home()}")
    #     # /Users/junjiewang
        
    #     print(Path("Users/junjiewang/python_prj/projects/feedme").is_file())
    #     print(Path("/Users/junjiewang/python_prj/projects/feedme").stat())
    def test_path(self):
        # 使用一个变量存储 Path 对象以避免重复创建
        project_path = Path()
        
        # 使用变量来获取项目的根目录
        project_cwd = project_path.cwd()
        self.assertTrue(project_cwd.exists(), msg="项目根目录不存在")
        
        # 获取绝对路径并进行断言，以验证其存在
        project_absolute = project_path.absolute()
        self.assertTrue(project_absolute.exists(), msg="绝对路径不存在")
        
        # 获取当前操作系统用户根目录并进行断言
        home_path = project_path.home()
        self.assertTrue(home_path.exists(), msg="用户根目录不存在")
        
        # 使用原始字符串定义路径，并检查是否为文件
        file_path = Path(r"Users/junjiewang/python_prj/projects/feedme")
        self.assertFalse(file_path.is_file(), msg="该路径不应指向一个文件")
        
        # 检查特定路径的文件状态，并进行断言
        directory_path = Path("/Users/junjiewang/python_prj/projects/feedme")
        if directory_path.exists():
            file_stats = directory_path.stat()
            self.assertTrue(file_stats.st_size > 0, msg="目录应为非空")
        else:
            self.fail(msg="指定的目录路径不存在")



if __name__ == "__main__":
    unittest.main()
