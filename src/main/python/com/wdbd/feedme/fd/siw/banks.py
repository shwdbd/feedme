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
            # TODO 异常处理。stock is None

            if ("年报" in result["stock"]["fr_date"]) or ("Q2" in result["stock"]["fr_date"]):
                MAX_PAGE = 50
                with pdfplumber.open(file) as pdf_reader:
                    for page_num, page in enumerate(pdf_reader.pages, start=1):
                        if page_num > MAX_PAGE:    # 超过最大页数则终止解析
                            break
                        page_text = page.extract_text()     # 解析成文本

                        if "主要会计数据和财务指标" in page_text:
                            self.exact_page_22(
                                result, pdf_reader, page_num, page_text)
                        elif "（三）利息净收入及净息差" in page_text:
                            self.exact_page_42(
                                result, pdf_reader, page_num, page)
                        elif "（一）按五级分类划分的贷款分布情况" in page_text:
                            self.exact_page_44(result, page)
                return result
            elif ("Q1" in result["stock"]["fr_date"]) or ("Q3" in result["stock"]["fr_date"]):
                # 季报
                self.exact_q_report(file, result)
                return result
            else:
                log.info("未知格式财报，无法解析")
                return {"result": False, "message": "未知格式财报，无法解析"}

        except Exception as e:
            log.error("解析民生银行财报出现异常，" + str(str))
            return {"result": False, "message": str(e)}

    def exact_q_report(self, file, result):
        # 提取季报信息
        MAX_PAGE = 20
        result["index"]["票据规模占比"] = None
        result["index"]["非利息净收入"] = None
        result["index"]["生息资产"] = None
        result["index"]["同业资产占比"] = None
        result["index"]["贷款规模"] = None
        result["index"]["票据规模占比"] = None
        result["index"]["证券投资规模"] = None
        result["index"]["付息负债"] = None
        result["index"]["同业负债占比"] = None
        result["index"]["存款规模"] = None
        result["index"]["对公活期存款占比"] = None
        result["index"]["活期储蓄占比"] = None
        result["index"]["应付债券规模"] = None
        with pdfplumber.open(file) as pdf_reader:
            for page_num, page in enumerate(pdf_reader.pages, start=1):
                if page_num > MAX_PAGE:    # 超过最大页数则终止解析
                    break
                page_text = page.extract_text()     # 解析成文本
                if "主要会计数据和财务指标" in page_text:
                    self.exact_q_report_table_1(
                        result, pdf_reader, page_num, page_text)
                elif "资本充足率与杠杆率情况" in page_text:
                    self.exact_q_report_table_2(
                        result, pdf_reader, page_num, page_text)

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

    def exact_q_report_table_1(self, result, pdf_reader, page_num, page_text):
        """ 季度报告，主要会计数据和财务指标 表 """
        # 表：一、主要会计数据和财务指标
        for line in page_text.split("\n"):
            if "资产总额" == line.split(" ")[0]:
                result["index"]["总资产"] = to_number(line.split(" ")[1], "百万")
            elif "不良贷款总额" == line.split(" ")[0]:
                result["index"]["不良贷款规模"] = to_number(line.split(" ")[1], "百万")
            elif "不良贷款率" == line.split(" ")[0]:
                result["index"]["不良贷款率"] = to_number(line.split(" ")[1])
            elif "拨备覆盖率" == line.split(" ")[0]:
                result["index"]["拨备覆盖率"] = to_number(line.split(" ")[1])
            elif "贷款拨备率" == line.split(" ")[0]:
                result["index"]["贷款拨备率"] = to_number(line.split(" ")[1])
        # 下一页
        next_table_page = pdf_reader.pages[page_num]
        for line in next_table_page.extract_text().split("\n"):
            if "归属于本行股东的净利润" == line.split(" ")[0]:
                result["index"]["净利润"] = to_number(line.split(" ")[1], "百万")
            elif "营业收入" == line.split(" ")[0]:
                result["index"]["营业收入"] = to_number(line.split(" ")[1], "百万")
            elif "利息净收入" == line.split(" ")[0]:
                result["index"]["利息净收入"] = to_number(line.split(" ")[1], "百万")
            elif "成本收入比" == line.split(" ")[0]:
                result["index"]["成本收入比"] = to_number(line.split(" ")[1])
            elif "净息差（年化）" == line.split(" ")[0]:
                result["index"]["净息差"] = to_number(line.split(" ")[1])

    def exact_q_report_table_2(self, result, pdf_reader, page_num, page_text):
        """ 季度报告，资本充足率与杠杆率情况  表 """
        # 表：（二）资本充足率与杠杆率情况
        for line in page_text.split("\n"):
            # print(line.split(" ")[0])
            if "核心一级资本充足率（%）" == line.split(" ")[0]:
                result["index"]["核心一级资本充足率"] = to_number(line.split(" ")[1])
            elif "一级资本充足率（%）" == line.split(" ")[0]:
                result["index"]["一级资本充足率"] = to_number(line.split(" ")[1])
            elif "资本充足率（%）" == line.split(" ")[0]:
                result["index"]["资本充足率"] = to_number(line.split(" ")[1])

    def exact_page_22(self, result, pdf_reader, page_num, page_text):
        """ 解析22页 """
        # 表：一、主要会计数据和财务指标
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
            elif ("净息差" == line.split(" ")[0]) or ("净息差（年化）" == line.split(" ")[0]):
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


# 工商银行
class ICBC(AbstractStockExactor):
    """ 工商银行 """

    def exact_pdf_file(self, file: str) -> dict:
        """从pdf格式的财报提取数据

        Args:
            file (_type_): pdf数据文件路径

        Returns:
            dict: 以字典格式返回提取到的指标，如果出错，则只返回{"result": False, "messages": ""}
                正确则返回：{"result": True, "messages": "", "index": {"指标1": "abc", "指标2": "efg"}}
        """
        try:
            result = {"result": True, "message": "", "index": {}}
            # 解析文件名，填写返回值
            stock = get_stock_info(os.path.basename(file))
            result["stock"] = stock
            # TODO 异常处理。stock is None

            if ("年报" in result["stock"]["fr_date"]) or ("Q2" in result["stock"]["fr_date"]):
                # 年报、半年报
                self.exact_annual(file, result)
                return result
            elif ("Q1" in result["stock"]["fr_date"]) or ("Q3" in result["stock"]["fr_date"]):
                # 季报
                self.exact_q_report(file, result)       # TODO 工商银行，季报
                return result
            else:
                log.info("未知格式财报，无法解析")
                return {"result": False, "message": "未知格式财报，无法解析"}

        except Exception as e:
            log.error("解析民生银行财报出现异常，" + str(str))
            return {"result": False, "message": str(e)}

    def exact_annual(self, file, result):
        # 提取年报、半年报数据
        MAX_PAGE = 85
        with pdfplumber.open(file) as pdf_reader:
            for page_num, page in enumerate(pdf_reader.pages, start=1):
                if page_num > MAX_PAGE:    # 超过最大页数则终止解析
                    break
                page_text = page.extract_text()     # 解析成文本

                if ("财务数据" in page_text) and ("分季度财务数据" not in page_text):
                    log.debug("表：财务数据 解析..")
                    self.exact_annual_t1(
                        result, pdf_reader, page_num, page_text)
                    log.debug("表：财务数据 解析完成")
                elif "利润表主要项目变动" in page_text:
                    self.exact_annual_t2(result, pdf_reader, page_num, page)
                    log.debug("表：利润表主要项目变动 解析完成")
                elif "贷款五级分类分布情况" in page_text:
                    log.debug("表：贷款五级分类分布情况 ...")
                    self.exact_annual_t4(result, pdf_reader, page_num, page)
                    log.debug("表：贷款五级分类分布情况 解析完成")
                elif "生息资产平均收益率和计息负债平均付息率" in page_text:
                    log.debug("表：生息资产平均收益率和计息负债平均付息率 ...")
                    self.exact_annual_t3(result, pdf_reader, page_num, page)
                    log.debug("表：生息资产平均收益率和计息负债平均付息率 解析完成")
                elif "按产品类型划分的存款平均成本分析" in page_text:
                    log.debug("表：按产品类型划分的存款平均成本分析 ...")
                    self.exact_annual_t5(result, pdf_reader, page_num, page)
                    log.debug("表：按产品类型划分的存款平均成本分析 解析完成")
        log.debug("pdf 解析完成")

    def exact_annual_t5(self, result, pdf_reader, page_num, page_text):
        """ 年报，按产品类型划分的存款平均成本分析 """
        table_style = {
            "vertical_strategy": "text",        # 竖线
            "horizontal_strategy": "lines"      # 横线
        }

        # 第1页表格
        if result["stock"]["fr_date"] == '2021年年报':
            table1 = pdf_reader.pages[page_num-1].extract_tables(table_style)[0]
            table2 = pdf_reader.pages[page_num].extract_tables(table_style)[0]
            table = table1 + table2
        else:
            table1 = pdf_reader.pages[page_num-1].extract_tables(table_style)[0]
            table = table1

        corp_flag = False   # 是否处理完对公业务标识
        corp_balance = 0
        corp_float_balance = 0
        person_float_balance = 0
        person_balance = 0
        for idx, row in enumerate(table, 1):
            if not corp_flag:
                if "活期" == row[1]:
                    corp_float_balance = to_number(row[2], "百万")
                elif "小计" == row[1]:
                    corp_balance = to_number(row[2], "百万")
                    corp_flag = True
            else:
                if "活期" == row[1]:
                    person_float_balance = to_number(row[2], "百万")
                elif "小计" == row[1]:
                    person_balance = to_number(row[2], "百万")
        result["index"]["对公活期存款占比"] = round(corp_float_balance * 100 / corp_balance, 2)
        result["index"]["活期储蓄占比"] = round(person_float_balance * 100 / person_balance, 2)

    def exact_annual_t3(self, result, pdf_reader, page_num, page_text):
        """ 年报，生息资产平均收益率和计息负债平均付息率 """
        table_style = {
            "vertical_strategy": "text",        # 竖线
            "horizontal_strategy": "lines"      # 横线
        }

        # 第1页表格
        table1 = pdf_reader.pages[page_num-1].extract_tables(table_style)[0]
        table2 = pdf_reader.pages[page_num].extract_tables(table_style)[0]
        table = table1 + table2

        for idx, row in enumerate(table, 1):
            if "2021年年报" == result["stock"]["fr_date"]:
                # 2021年年报特殊处理
                row[1] = '{0}{1}'.format(row[0], row[1])
                row.pop(0)
                # 特殊
                result["index"]["证券投资规模"] = None
                result["index"]["应付债券规模"] = None
 
            try:
                if "总生息资产" == row[0]:
                    result["index"]["生息资产"] = to_number(row[1], "百万")
                elif "总计息负债" == row[0]:
                    result["index"]["付息负债"] = to_number(row[1], "百万")
                elif "客户贷款及垫款" == row[0]:
                    result["index"]["贷款规模"] = to_number(row[1], "百万")
                elif "存款" == row[0]:
                    result["index"]["存款规模"] = to_number(row[1], "百万")
                elif row[0] and "存放和拆放同业及其他\n金融机构款项" in row[0]:
                    result["index"]["同业资产占比"] = to_number(row[1], "百万")
                elif row[0] and "同业及其他金融机构存\n放和拆入款项" in row[0]:
                    result["index"]["同业负债占比"] = to_number(row[1], "百万")
                elif row[0] and "投资" == row[0]:
                    result["index"]["证券投资规模"] = to_number(row[1], "百万")
                elif row[0] and "已发行债务证券和存款" in row[0]:
                    result["index"]["应付债券规模"] = to_number(row[1], "百万")
            except Exception as err:
                log.error(str(err))
                break
        if result["index"]["生息资产"] != 0:
            result["index"]["同业资产占比"] = round(result["index"]["同业资产占比"] * 100 / result["index"]["生息资产"], 2)
        if result["index"]["付息负债"] != 0:
            result["index"]["同业负债占比"] = round(result["index"]["同业负债占比"] * 100 / result["index"]["付息负债"], 2)
        result["index"]["票据规模占比"] = None

    def exact_annual_t4(self, result, pdf_reader, page_num, page_text):
        """ 年报，贷款五级分类分布情况 """
        table_style = {
            "vertical_strategy": "text",        # 竖线
            "horizontal_strategy": "lines"      # 横线
        }

        # 第1页表格
        table1 = pdf_reader.pages[page_num-1].extract_tables(table_style)[0]
        table = table1
        for idx, row in enumerate(table, 1):
            if result["stock"]["fr_date"] == '2021年年报':
                # [None, '不良贷款', '', '', '2', '93,429', '', '1.4', '2', '293,9', '78', '', None, None]
                row[3] = '{0}{1}'.format(row[3], row[4])

            if "不良贷款" == row[1]:
                result["index"]["不良贷款规模"] = to_number(row[3], "百万")

    def exact_annual_t2(self, result, pdf_reader, page_num, page_text):
        """ 年报，利润表主要项目变动 """
        table_style = {
            "vertical_strategy": "text",        # 竖线
            "horizontal_strategy": "lines"      # 横线
        }

        # 第1页表格
        table1 = pdf_reader.pages[page_num-1].extract_tables(table_style)[0]
        table = table1

        for idx, row in enumerate(table, 1):
            if "非利息收入" == row[0]:
                result["index"]["非利息净收入"] = to_number(row[1], "百万")

    def exact_annual_t1(self, result, pdf_reader, page_num, page_text):
        """ 年报，财务数据 表 """
        table_style = {
            "vertical_strategy": "text",        # 竖线
            "horizontal_strategy": "lines"      # 横线
        }

        # 第1页表格
        table1 = pdf_reader.pages[page_num-1].extract_tables(table_style)[0]
        table2 = pdf_reader.pages[page_num].extract_tables(table_style)[0]
        table3 = pdf_reader.pages[page_num+1].extract_tables(table_style)[0]
        table = table1 + table2 + table3
        # 剔除 分季度财务数据表内容
        limit_line = len(table)
        for idx, row in enumerate(table, 1):
            if row[0] == "风险加权资产占总资产比率":
                limit_line = idx
        table = table[: limit_line]

        for idx, row in enumerate(table, 1):
            if "归属于母公司股东的净利润" == row[0]:
                result["index"]["净利润"] = to_number(row[1], "百万")
            elif "营业收入" == row[0]:
                result["index"]["营业收入"] = to_number(row[1], "百万")
            elif "利息净收入" == row[0]:
                result["index"]["利息净收入"] = to_number(row[1], "百万")
            elif "资产总额" == row[0]:
                result["index"]["总资产"] = to_number(row[1], "百万")
            elif "成本收入比" in (row[1]+row[2]):
                result["index"]["成本收入比"] = to_number(row[4])
            elif "净利息差" in (row[1]+row[2]):
                result["index"]["净息差"] = to_number(row[4])
            elif ("资本充足率" in row[0]) and ("一级资本充足率" not in row[0]) and ("核心一级资本充足率" not in row[0]) and (row[1] != ''):
                result["index"]["资本充足率"] = to_number(row[1])
            elif ("一级资本充足率" in row[0]) and ("核心一级资本充足率" not in row[0]):
                result["index"]["一级资本充足率"] = to_number(row[1])
            elif ("核心一级资本充足率" in row[0]):
                result["index"]["核心一级资本充足率"] = to_number(row[1])
            elif ("不良贷款率" in row[0]):
                result["index"]["不良贷款率"] = to_number(row[1])
                result["index"]["不良率"] = to_number(row[1])
            elif ("拨备覆盖率" in row[0]):
                result["index"]["拨备覆盖率"] = to_number(row[1].split(" ")[0])
            elif ("贷款拨备率" in row[0]):
                result["index"]["贷款拨备率"] = to_number(row[1])


# TODO 兴业银行待实现
# 兴业银行
class IBC(AbstractStockExactor):
    """ 兴业银行 """

    def exact_pdf_file(self, file: str) -> dict:
        """从pdf格式的财报提取数据

        Args:
            file (_type_): pdf数据文件路径

        Returns:
            dict: 以字典格式返回提取到的指标，如果出错，则只返回{"result": False, "messages": ""}
                正确则返回：{"result": True, "messages": "", "index": {"指标1": "abc", "指标2": "efg"}}
        """
        try:
            result = {"result": True, "message": "", "index": {}}
            # 解析文件名，填写返回值
            stock = get_stock_info(os.path.basename(file))
            result["stock"] = stock
            # TODO 异常处理。stock is None

            if ("年报" in result["stock"]["fr_date"]) or ("Q2" in result["stock"]["fr_date"]):
                # 年报、半年报
                self.exact_annual(file, result)
                return result
            elif ("Q1" in result["stock"]["fr_date"]) or ("Q3" in result["stock"]["fr_date"]):
                # 季报
                self.exact_q_report(file, result)       # TODO 工商银行，季报
                return result
            else:
                log.info("未知格式财报，无法解析")
                return {"result": False, "message": "未知格式财报，无法解析"}

        except Exception as e:
            log.error("解析民生银行财报出现异常，" + str(str))
            return {"result": False, "message": str(e)}

    def exact_annual(self, file, result):
        # 提取年报、半年报数据
        MAX_PAGE = 85
        with pdfplumber.open(file) as pdf_reader:
            for page_num, page in enumerate(pdf_reader.pages, start=1):
                if page_num > MAX_PAGE:    # 超过最大页数则终止解析
                    break
                page_text = page.extract_text()     # 解析成文本

                if ("财务数据" in page_text) and ("分季度财务数据" not in page_text):
                    log.debug("表：财务数据 解析..")
                    self.exact_annual_t1(
                        result, pdf_reader, page_num, page_text)
                    log.debug("表：财务数据 解析完成")
                elif "利润表主要项目变动" in page_text:
                    self.exact_annual_t2(result, pdf_reader, page_num, page)
                    log.debug("表：利润表主要项目变动 解析完成")
                elif "贷款五级分类分布情况" in page_text:
                    log.debug("表：贷款五级分类分布情况 ...")
                    self.exact_annual_t4(result, pdf_reader, page_num, page)
                    log.debug("表：贷款五级分类分布情况 解析完成")
                elif "生息资产平均收益率和计息负债平均付息率" in page_text:
                    log.debug("表：生息资产平均收益率和计息负债平均付息率 ...")
                    self.exact_annual_t3(result, pdf_reader, page_num, page)
                    log.debug("表：生息资产平均收益率和计息负债平均付息率 解析完成")
                elif "按产品类型划分的存款平均成本分析" in page_text:
                    log.debug("表：按产品类型划分的存款平均成本分析 ...")
                    self.exact_annual_t5(result, pdf_reader, page_num, page)
                    log.debug("表：按产品类型划分的存款平均成本分析 解析完成")
        log.debug("pdf 解析完成")

    def exact_annual_t5(self, result, pdf_reader, page_num, page_text):
        """ 年报，按产品类型划分的存款平均成本分析 """
        table_style = {
            "vertical_strategy": "text",        # 竖线
            "horizontal_strategy": "lines"      # 横线
        }

        # 第1页表格
        if result["stock"]["fr_date"] == '2021年年报':
            table1 = pdf_reader.pages[page_num-1].extract_tables(table_style)[0]
            table2 = pdf_reader.pages[page_num].extract_tables(table_style)[0]
            table = table1 + table2
        else:
            table1 = pdf_reader.pages[page_num-1].extract_tables(table_style)[0]
            table = table1

        corp_flag = False   # 是否处理完对公业务标识
        corp_balance = 0
        corp_float_balance = 0
        person_float_balance = 0
        person_balance = 0
        for idx, row in enumerate(table, 1):
            if not corp_flag:
                if "活期" == row[1]:
                    corp_float_balance = to_number(row[2], "百万")
                elif "小计" == row[1]:
                    corp_balance = to_number(row[2], "百万")
                    corp_flag = True
            else:
                if "活期" == row[1]:
                    person_float_balance = to_number(row[2], "百万")
                elif "小计" == row[1]:
                    person_balance = to_number(row[2], "百万")
        result["index"]["对公活期存款占比"] = round(corp_float_balance * 100 / corp_balance, 2)
        result["index"]["活期储蓄占比"] = round(person_float_balance * 100 / person_balance, 2)

    def exact_annual_t3(self, result, pdf_reader, page_num, page_text):
        """ 年报，生息资产平均收益率和计息负债平均付息率 """
        table_style = {
            "vertical_strategy": "text",        # 竖线
            "horizontal_strategy": "lines"      # 横线
        }

        # 第1页表格
        table1 = pdf_reader.pages[page_num-1].extract_tables(table_style)[0]
        table2 = pdf_reader.pages[page_num].extract_tables(table_style)[0]
        table = table1 + table2

        for idx, row in enumerate(table, 1):
            if "2021年年报" == result["stock"]["fr_date"]:
                # 2021年年报特殊处理
                row[1] = '{0}{1}'.format(row[0], row[1])
                row.pop(0)
                # 特殊
                result["index"]["证券投资规模"] = None
                result["index"]["应付债券规模"] = None
 
            try:
                if "总生息资产" == row[0]:
                    result["index"]["生息资产"] = to_number(row[1], "百万")
                elif "总计息负债" == row[0]:
                    result["index"]["付息负债"] = to_number(row[1], "百万")
                elif "客户贷款及垫款" == row[0]:
                    result["index"]["贷款规模"] = to_number(row[1], "百万")
                elif "存款" == row[0]:
                    result["index"]["存款规模"] = to_number(row[1], "百万")
                elif row[0] and "存放和拆放同业及其他\n金融机构款项" in row[0]:
                    result["index"]["同业资产占比"] = to_number(row[1], "百万")
                elif row[0] and "同业及其他金融机构存\n放和拆入款项" in row[0]:
                    result["index"]["同业负债占比"] = to_number(row[1], "百万")
                elif row[0] and "投资" == row[0]:
                    result["index"]["证券投资规模"] = to_number(row[1], "百万")
                elif row[0] and "已发行债务证券和存款" in row[0]:
                    result["index"]["应付债券规模"] = to_number(row[1], "百万")
            except Exception as err:
                log.error(str(err))
                break
        if result["index"]["生息资产"] != 0:
            result["index"]["同业资产占比"] = round(result["index"]["同业资产占比"] * 100 / result["index"]["生息资产"], 2)
        if result["index"]["付息负债"] != 0:
            result["index"]["同业负债占比"] = round(result["index"]["同业负债占比"] * 100 / result["index"]["付息负债"], 2)
        result["index"]["票据规模占比"] = None

    def exact_annual_t4(self, result, pdf_reader, page_num, page_text):
        """ 年报，贷款五级分类分布情况 """
        table_style = {
            "vertical_strategy": "text",        # 竖线
            "horizontal_strategy": "lines"      # 横线
        }

        # 第1页表格
        table1 = pdf_reader.pages[page_num-1].extract_tables(table_style)[0]
        table = table1
        for idx, row in enumerate(table, 1):
            if result["stock"]["fr_date"] == '2021年年报':
                # [None, '不良贷款', '', '', '2', '93,429', '', '1.4', '2', '293,9', '78', '', None, None]
                row[3] = '{0}{1}'.format(row[3], row[4])

            if "不良贷款" == row[1]:
                result["index"]["不良贷款规模"] = to_number(row[3], "百万")

    def exact_annual_t2(self, result, pdf_reader, page_num, page_text):
        """ 年报，利润表主要项目变动 """
        table_style = {
            "vertical_strategy": "text",        # 竖线
            "horizontal_strategy": "lines"      # 横线
        }

        # 第1页表格
        table1 = pdf_reader.pages[page_num-1].extract_tables(table_style)[0]
        table = table1

        for idx, row in enumerate(table, 1):
            if "非利息收入" == row[0]:
                result["index"]["非利息净收入"] = to_number(row[1], "百万")

    def exact_annual_t1(self, result, pdf_reader, page_num, page_text):
        """ 年报，财务数据 表 """
        table_style = {
            "vertical_strategy": "text",        # 竖线
            "horizontal_strategy": "lines"      # 横线
        }

        # 第1页表格
        table1 = pdf_reader.pages[page_num-1].extract_tables(table_style)[0]
        table2 = pdf_reader.pages[page_num].extract_tables(table_style)[0]
        table3 = pdf_reader.pages[page_num+1].extract_tables(table_style)[0]
        table = table1 + table2 + table3
        # 剔除 分季度财务数据表内容
        limit_line = len(table)
        for idx, row in enumerate(table, 1):
            if row[0] == "风险加权资产占总资产比率":
                limit_line = idx
        table = table[: limit_line]

        for idx, row in enumerate(table, 1):
            if "归属于母公司股东的净利润" == row[0]:
                result["index"]["净利润"] = to_number(row[1], "百万")
            elif "营业收入" == row[0]:
                result["index"]["营业收入"] = to_number(row[1], "百万")
            elif "利息净收入" == row[0]:
                result["index"]["利息净收入"] = to_number(row[1], "百万")
            elif "资产总额" == row[0]:
                result["index"]["总资产"] = to_number(row[1], "百万")
            elif "成本收入比" in (row[1]+row[2]):
                result["index"]["成本收入比"] = to_number(row[4])
            elif "净利息差" in (row[1]+row[2]):
                result["index"]["净息差"] = to_number(row[4])
            elif ("资本充足率" in row[0]) and ("一级资本充足率" not in row[0]) and ("核心一级资本充足率" not in row[0]) and (row[1] != ''):
                result["index"]["资本充足率"] = to_number(row[1])
            elif ("一级资本充足率" in row[0]) and ("核心一级资本充足率" not in row[0]):
                result["index"]["一级资本充足率"] = to_number(row[1])
            elif ("核心一级资本充足率" in row[0]):
                result["index"]["核心一级资本充足率"] = to_number(row[1])
            elif ("不良贷款率" in row[0]):
                result["index"]["不良贷款率"] = to_number(row[1])
                result["index"]["不良率"] = to_number(row[1])
            elif ("拨备覆盖率" in row[0]):
                result["index"]["拨备覆盖率"] = to_number(row[1].split(" ")[0])
            elif ("贷款拨备率" in row[0]):
                result["index"]["贷款拨备率"] = to_number(row[1])


if __name__ == "__main__":
    # file_name = 'C:/Users/wang/OneDrive/3_Work/GTP01 A股财报/SH600016 民生银行 2023年Q1.pdf'
    # cmbc = CMBC()
    # res = cmbc.exact_pdf_file(file_name)
    # print(res)
    # print("净利润 = {0}".format(res["index"]["净利润"]))
    # print("营业收入 = {0}".format(res["index"]["营业收入"]))
    # print("生息资产 = {0}".format(res["index"]["生息资产"]))
    # print("同业资产占比 = {0}".format(res["index"]["同业资产占比"]))
    # print("同业资产占比 = {0}".format(res["index"]["同业资产占比"]))
    # print("资本充足率 = {0}".format(res["index"]["资本充足率"]))

    file_name = 'C:/Users/wang/OneDrive/3_Work/GTP01 A股财报/SH601398 工商银行 2021年年报.pdf'
    bank = ICBC()
    res = bank.exact_pdf_file(file_name)
    print(res)
    print("净利润 = {0}".format(res["index"]["净利润"]))
    print("营业收入 = {0}".format(res["index"]["营业收入"]))
    print("非利息净收入 = {0}".format(res["index"]["非利息净收入"]))
    print("利息净收入 = {0}".format(res["index"]["利息净收入"]))
    print("成本收入比 = {0}".format(res["index"]["成本收入比"]))
    print("生息资产 = {0}".format(res["index"]["生息资产"]))
    print("同业资产占比 = {0}".format(res["index"]["同业资产占比"]))
    print("同业资产占比 = {0}".format(res["index"]["同业资产占比"]))
    print("资本充足率 = {0}".format(res["index"]["资本充足率"]))
    print("不良贷款规模 = {0}".format(res["index"]["不良贷款规模"]))
    print("对公活期存款占比 = {0}".format(res["index"]["对公活期存款占比"]))
    print("生息资产 = {0}".format(res["index"]["生息资产"]))

    # log.debug("aaa")
