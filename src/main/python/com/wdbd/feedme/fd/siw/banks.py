#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   banks.py
@Time    :   2023/06/01 13:58:53
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   None
'''
# from com.wdbd.feedme.fd.siw import AbstractStockExactor
import pdfplumber
from com.wdbd.feedme.fd.siw.tools import to_number, get_stock_info, log
import os


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


# ==================================================
class CMBC(AbstractStockExactor):
    """ 民生银行 """
    # TODO 解析季报

    def exact_pdf_file(self, file: str) -> dict:
        """从pdf格式的财报提取数据

        Args:
            file (_type_): pdf数据文件路径

        Returns:
            dict: 以字典格式返回提取到的指标，如果出错，则只返回{"result": False, "messages": ""}
                正确则返回：{"result": True, "messages": "", 'stock': {'id': 'SH600016', 'name': '民生银行', 'fr_date': '2022年年报'}, "index": {"指标1": "abc", "指标2": "efg"}}
        """
        # EFFECTS:
        # 1. 读取文件
        # 2. 按页，顺序读取各个页面，直到终止页
        # 3. 如果遇到有某个内容的页，然后进行解析
        # 返回值
        try:
            result = {"result": True, "message": "", "index": {}}
            # 解析文件名，填写返回值
            stock = get_stock_info(os.path.basename(file))
            result["stock"] = stock

            MAX_PAGE = 50
            with pdfplumber.open(file) as pdf_reader:
                for page_num, page in enumerate(pdf_reader.pages, start=1):
                    if page_num > MAX_PAGE:    # 超过最大页数则终止解析
                        break
                    page_text = page.extract_text()     # 解析成文本

                    if "一、 主要会计数据和财务指标" in page_text:
                        self.exact_page_22(result, pdf_reader, page_num, page_text)
                    elif "（三）利息净收入及净息差" in page_text:
                        self.exact_page_42(result, pdf_reader, page_num, page)
                    elif "（一）按五级分类划分的贷款分布情况" in page_text:
                        self.exact_page_44(result, page)
            return result
        except Exception as e:
            log.error("解析民生银行财报出现异常，" + str(str))
            return {"result": False, "message": str(e)}

    def exact_page_44(self, result, page):
        for line in page.extract_text().split("\n"):
            if "不良贷款" == line.split(" ")[0]:
                result["index"]["不良贷款规模"] = to_number(line.split(" ")[1], "百万")

    def exact_page_42(self, result, pdf_reader, page_num, page):
        """ 解析 """
        for line in page.extract_text().split("\n"):
            if "合计" == line.split(" ")[0]:
                result["index"]["生息资产"] = to_number(line.split(" ")[1], "百万")
            elif "拆放同业及其他金融机构款项" == line.split(" ")[0]:
                tyzc = to_number(line.split(" ")[1], "百万")
            elif "发放贷款和垫款总额" == line.split(" ")[0]:
                result["index"]["贷款规模"] = to_number(line.split(" ")[1], "百万")
            elif "金融投资" == line.split(" ")[0]:
                result["index"]["证券投资规模"] = to_number(line.split(" ")[1], "百万")
        result["index"]["同业资产占比"] = round(tyzc*100/result["index"]["生息资产"], 2)
        result["index"]["票据规模占比"] = None

        # 下一页
        next_table_page = pdf_reader.pages[page_num]
        hq_flag = 0     # 活期标识
        gscz = 0
        grcz = 0
        corp_hq = 0
        gr_hq = 0
        for line in next_table_page.extract_text().split("\n"):
            # print(line)
            if "合计" == line.split(" ")[0]:
                result["index"]["付息负债"] = to_number(line.split(" ")[1], "百万")
            elif "吸收存款" == line.split(" ")[0]:
                result["index"]["存款规模"] = to_number(line.split(" ")[1], "百万")
            elif "应付债券" == line.split(" ")[0]:
                result["index"]["应付债券规模"] = to_number(line.split(" ")[1], "百万")
            elif "同业及其他金融机构存放款项" == line.split(" ")[0]:
                cfty = to_number(line.split(" ")[1], "百万")
            elif "其中：公司存款" == line.split(" ")[0]:
                gscz = to_number(line.split(" ")[1], "百万")
            elif "个人存款" == line.split(" ")[0]:
                grcz = to_number(line.split(" ")[1], "百万")
            elif "活期" == line.split(" ")[0]:
                if hq_flag == 0:
                    corp_hq = to_number(line.split(" ")[1], "百万")     # 对公活期
                    hq_flag = 1
                else:
                    gr_hq = to_number(line.split(" ")[1], "百万")     # 个人活期
        # result["index"]["资本充足率"] = to_number(line.split(" ")[1])
        result["index"]["同业负债占比"] = round(cfty*100/result["index"]["付息负债"], 2)
        result["index"]["对公活期存款占比"] = round(corp_hq*100/gscz, 2)
        result["index"]["活期储蓄占比"] = round(gr_hq*100/grcz, 2)

    def exact_page_22(self, result, pdf_reader, page_num, page_text):
        """ 解析22页 """
        for line in page_text.split("\n"):
            if "归属于本行股东的净利润" == line.split(" ")[0]:
                result["index"]["净利润"] = to_number(line.split(" ")[1], "百万")
            elif "营业收入" == line.split(" ")[0]:
                result["index"]["营业收入"] = to_number(line.split(" ")[1], "百万")
            elif "利息净收入" == line.split(" ")[0]:
                result["index"]["利息净收入"] = to_number(line.split(" ")[1], "百万")
            elif "非利息净收入" == line.split(" ")[0]:
                result["index"]["非利息净收入"] = to_number(line.split(" ")[1], "百万")
            elif "成本收入比" == line.split(" ")[0]:
                result["index"]["成本收入比"] = to_number(line.split(" ")[1])
            elif "净息差" == line.split(" ")[0]:
                result["index"]["净息差"] = to_number(line.split(" ")[1])

        # 下一页
        next_table_page = pdf_reader.pages[page_num]
        for line in next_table_page.extract_text().split("\n"):
            if "不良贷款率" == line.split(" ")[0]:
                result["index"]["不良贷款率"] = to_number(line.split(" ")[1])
            elif "资产总额" == line.split(" ")[0]:
                result["index"]["总资产"] = to_number(line.split(" ")[1], "百万")
            elif "资本充足率(%)" == line.split(" ")[0]:
                result["index"]["资本充足率"] = to_number(line.split(" ")[1])
            elif "拨备覆盖率" == line.split(" ")[0]:
                result["index"]["拨备覆盖率"] = to_number(line.split(" ")[1])
            elif "一级资本充足率(%)" == line.split(" ")[0]:
                result["index"]["一级资本充足率"] = to_number(line.split(" ")[1])
            elif "资本充足率(%)" == line.split(" ")[0]:
                result["index"]["资本充足率"] = to_number(line.split(" ")[1])
            elif "核心一级资本充足率(%)" in line.split(" ")[0]:
                result["index"]["核心一级资本充足率"] = to_number(line.split(" ")[1])
            elif "拨备覆盖率" == line.split(" ")[0]:
                result["index"]["拨备覆盖率"] = to_number(line.split(" ")[1])
            elif "贷款拨备率" == line.split(" ")[0]:
                result["index"]["贷款拨备率"] = to_number(line.split(" ")[1])


# class ICBC(AbstractStockExactor):
#     """ 工商银行 """

#     def exact_pdf_file(self, file: str) -> dict:
#         """从pdf格式的财报提取数据

#         Args:
#             file (_type_): pdf数据文件路径

#         Returns:
#             dict: 以字典格式返回提取到的指标，如果出错，则只返回{"result": False, "messages": ""}
#                 正确则返回：{"result": True, "messages": "", "index": {"指标1": "abc", "指标2": "efg"}}
#         """
#         # TODO 待实现
#         return {}


# TODO 兴业银行待实现

if __name__ == "__main__":
    file_name = 'C:/Users/wang/OneDrive/3_Work/GTP01 A股财报/SH600016 民生银行 2022年年报.pdf'
    cmbc = CMBC()
    res = cmbc.exact_pdf_file(file_name)
    print(res)
    print("净利润 = {0}".format(res["index"]["净利润"]))
    print("营业收入 = {0}".format(res["index"]["营业收入"]))
    print("生息资产 = {0}".format(res["index"]["生息资产"]))
    print("同业资产占比 = {0}".format(res["index"]["同业资产占比"]))
    print("同业资产占比 = {0}".format(res["index"]["同业资产占比"]))
