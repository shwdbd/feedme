#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   __init__.py
@Time    :   2023/06/01 13:55:22
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   SIW 股票指标观测器 子项目
'''


class FinanceReportExactor:
    """银行股股票指标 读取器
    """
    def load_by_file(self, filename) -> dict:
        """
        读取单个文件并将解析到数据存入FD数据库
        需要做的事情有：
        1. 解析文件
        2. 数据存入数据库
        3. 文件归档

        返回值：
        正确则返回：
        {
          "result": True,
          "messages": "",
          "index": {"指标1": "abc", "指标2": "efg"}
        }
        错误返回：
        {
          "result": False,
          "messages": "出错信息"
        }
        """
        # TODO 待实现
        # TODO 1. 解析文件，如果错误则返回
        # TODO 2. 解析文件内容
        # TODO 3. 备份文件
        # TODO 4. 写入数据库
        # END
        
        
        return None

    def load_by_dir(self, foloder_path) -> dict:
        """
        读取某个文件夹下的所有财报单个文件并将解析到数据存入FD数据库

        返回值：
        正确则返回：
        {
          "result": True,
          "messages": "",
          "files": {
              "文件1": {
                "result": True,
                "messages": "",
                "index": {"指标1": "abc", "指标2": "efg"}
              },
              "文件2": {
                "result": True,
                "messages": "",
                "index": {"指标1": "abc", "指标2": "efg"}
              },
          }
        }
        错误返回：
        {
          "result": False,
          "messages": "出错信息",
          "files": {
              "文件1": {
                "result": True,
                "messages": "xxxx"},
              "文件2": {
                "result": True,
                "messages": "xxxx"},
          }
        }
        """
        # TODO 待实现
        return None


class AbstractStockExactor:
    """单一股票财报提取器(抽象基类)
    """

    def exact_pdf_file(self, file: str) -> dict:
        """从pdf格式的财报提取数据

        Args:
            file (_type_): pdf数据文件路径

        Returns:
            dict: 以字典格式返回提取到的指标，如果出错，则只返回{"result": False, "messages": ""}
                正确则返回：{"result": True, "messages": "", "index": {"指标1": "abc", "指标2": "efg"}}
        """
        return {}


class FinanceReport:
    """ 财报信息 """

    def __init__(self):
        self.stock_id = ""          # SH600016
        self.stock_name = ""        # 民生银行
        self.fr_date = ""           # 2022年年报


# class BasicService:
#     """ 通用服务类 """

#     def archive_file(self, file: str) -> bool:
#         """文件归档

#         Args:
#             file (str): 文件路径

#         Returns:
#             bool: 是否归档
#         """
#         # TODO 待处理
#         return None

#     def index_save_to_db(self, index: dict) -> bool:
#         """_summary_

#         Args:
#             index (dict): _description_

#         Returns:
#             bool: _description_
#         """
#         return False
