#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   ts_news_csv.py
@Time    :   2022/06/21 11:21:45
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   下载CSV格式文件的新闻类数据
'''
from com.wdbd.feedme.fd.common.data_dateway import TushareGateWay


class TsCCTVNews:
    """ CCTV每日新闻 """

    # def __init__(self, name, config):
    #     super().__init__(name=name, config=config, table_name="ts_cctv_news",
    #                      date_field="date", fields_id="cctv_news")

    # def rebuild(self):
    #     # drop and create table
    #     index = [{"name": self.table_name+"_pk",
    #               "fields": ["date"], "unique": False}]
    #     return mg_utils.create_table(table_name=self.table_name, index=index)

    # def load_data(self, date):
    #     """ 加载数据 """
    #     gw = TushareGateWay()
    #     self.data = gw.call(callback=gw.api.cctv_news, date=date, fields=self.fields, return_type="dict")

    def download_bydate(self, date: str, *args, **kwargs) -> bool:
        """数据按日下载函数，本方法需要子类中具体实现

        Args:
            date (str): yyyyMMdd格式日期

        Returns:
            bool: 执行结果
        """
        gw = TushareGateWay()
        self.data = gw.call(callback=gw.api.cctv_news, date=date, return_type="dict")
        print(self.data)
        return False


if __name__ == "__main__":
    step = TsCCTVNews()

    res = step.download_bydate("20220620")
    print(res)
