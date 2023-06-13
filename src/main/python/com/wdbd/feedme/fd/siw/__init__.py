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
import os
from com.wdbd.feedme.fd.siw.tools import get_stock_info, check_rpfile_format, log as err_log, archive_file, save_to_db
from com.wdbd.feedme.fd.siw.banks import CMBC


class FinanceReportExactor:
    """银行股股票指标 读取器
    """
    def load_by_file(self, filename: str) -> dict:
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
          "stock": {"id": "SH600016', 'name': 'xxxx', 'fr_date': '2023年年报'}
          "index": {"指标1": "abc", "指标2": "efg"}
        }
        错误返回：
        {
          "result": False,
          "messages": "出错信息"
        }

        Args:
            filename (str): 文件完整路径

        Returns:
            dict: 执行结果
        """
        # 1. 解析文件，如果错误则返回
        # 2. 解析文件内容
        # 3. 备份文件
        # 4. 写入数据库
        # END
        err_log.info("读取财报文件, {0}".format(filename))

        if not filename or os.path.exists(filename) is False:
            err_log.info("读取财报文件失败！, 文件未找到。{0}".format(filename))
            return {"result": False, "message": "文件不存在！{0}".format(filename)}

        try:
            # 解析文件，如果错误则返回
            if not check_rpfile_format(os.path.basename(filename)):
                err_log.info("读取财报文件失败！, 财报文件名格式不正确！{0}".format(filename))
                return {"result": False, "message": "财报文件名格式不正确！{0}".format(filename)}

            # 初始化返回值
            res = {"result": True, "message": ""}
            res_stock = get_stock_info(os.path.basename(filename))
            if not res_stock:
                err_log.info("读取财报文件失败！, 财报文件名格式不正确！{0}".format(filename))
                return {"result": False, "message": "财报文件名格式不正确！{0}".format(filename)}
            res["stock"] = res_stock
            # print(res)

            # 解析文件内容，加载解析器
            if res_stock["name"] == '民生银行':
                exactor = CMBC()
            else:
                err_log.error("未知银行," + res_stock["name"])
                return {"result": False, "message": "未知银行," + res_stock["name"]}

            # 执行操作
            res_data = exactor.exact_pdf_file(filename)
            if not res_data["result"]:
                err_log.error("读取财报文件失败！")
                return {"result": False, "message": "文件归档失败"}
            else:
                err_log.info("解析财报文件成功")
                if not archive_file(filename):  # 文件备份
                    err_log.error("读取财报文件失败！文件归档失败")
                    return {"result": False, "message": "文件归档失败"}
                if not save_to_db(res_data):  # 写数据库
                    err_log.error("读取财报文件失败！数据库保存错误")
                    return {"result": False, "message": "数据库保存错误"}

                return res_data
        except Exception as err:
            err_log.info("读取财报文件失败！, 异常:{0}".format(str(err)))
            return {"result": False, "message": "读取财报文件失败！, 异常:{0}".format(str(err))}

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


class FinanceReport:
    """ 财报信息 """

    def __init__(self):
        self.stock_id = ""          # SH600016
        self.stock_name = ""        # 民生银行
        self.fr_date = ""           # 2022年年报


if __name__ == "__main__":
    file_name = 'C:/Users/wang/OneDrive/3_Work/GTP01 A股财报/SH600016 民生银行 2022年年报.pdf'
    srv = FinanceReportExactor()
    res = srv.load_by_file(None)
    print(res)
