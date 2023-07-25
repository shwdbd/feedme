#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   ak_news.py
@Time    :   2023/07/24 14:10:24
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   新闻类数据下载
'''
import akshare as ak
from com.wdbd.feedme.fd.common.common import get_logger, get_session, records2objlist
from com.wdbd.feedme.fd.orm.ods_tables import OdsAkshareCCTVNews
from com.wdbd.feedme.fd.common.data_gateway import DsStatTool
import com.wdbd.feedme.fd.common.common as tl
import com.wdbd.feedme.fd.fd_api as fd_api


class AkCCTVNews:
    """ Akshare 新闻联播文字稿 """

    def __init__(self):
        self.DS_ID = "akshare.cctv_news"    # 数据源ID

    def download_bydate(self, date: str, is_log_stat: bool = False):
        """按日下载数据

        Args:
            date (str): 日期
            is_log_stat (bool, optional): 是否记录统计数据 Defaults to False.

        Returns:
            _type_: 返回结果
        """
        # EFFECTS:
        # 1. 按日取得数据，并覆盖本地数据
        # END
        log = get_logger()
        log.debug("下载Akshare 新闻联播文字稿（{0}）".format(date))

        try:
            # 取得数据
            df = ak.news_cctv(date)
            if df is None or df.shape[0] == 0:
                err_msg = "新闻联播文字稿 接口返回空数据"
                log.error(err_msg)
                return tl.get_failed_result(msg=err_msg)
            # 数据清理：（转换日期格式）
            df["trade_date"] = df["date"]
            # 转成Object
            obj_list = records2objlist(df, OdsAkshareCCTVNews)

            # 如果有数据，则del and insert数据库
            try:
                session = get_session()
                session.query(OdsAkshareCCTVNews).filter(OdsAkshareCCTVNews.trade_date == date).delete()
                session.bulk_save_objects(obj_list)
                session.commit()

                if is_log_stat:
                    # 记录统计数据
                    DsStatTool.log(id=self.DS_ID, end_bar=date, start_bar=date)
                msg = "下载Akshare新闻联播文字稿，日期={d}，新闻条数={c}".format(d=date, c=len(obj_list))
                log.info(msg)
                return tl.get_success_result(msg=msg)
            except Exception as err:
                err_msg = "下载Akshare新闻联播文字稿(date={d}) 时遇到异常，异常:{err}".format(d=date, err=str(err))
                log.error(err_msg)
                session.rollback()
                return tl.get_failed_result(msg=err_msg)
            finally:
                session.close()
        except Exception as err:
            err_msg = "下载Akshare新闻联播文字稿(date={d})时发生异常，异常:{err}".format(d=date, err=str(err))
            log.error(err_msg)
            return tl.get_failed_result(msg=err_msg)

    def download_all(self, start_date: str = "20160330", end_date: str = tl.today()):
        """_summary_

        Args:
            start_date (str, optional): _description_. Defaults to "20160330".
            end_date (str, optional): _description_. Defaults to tl.today().

        Returns:
            _type_: _description_
        """
        # EFFECTS:
        # 1. 逐日下载，完成全量数据下载
        # END
        log = get_logger()
        log.info("下载Akshare 新闻联播文字稿 【全量, {0} - {1}】".format(start_date, end_date))

        try:
            count_of_success = 0    # 下载成功天数
            res_data = []
            # 取得数据
            dates = fd_api.get_dates(start=start_date, end=end_date, is_trade_date_only=False)
            for day in dates:
                res = self.download_bydate(day)
                if res["result"]:
                    count_of_success += 1
                else:
                    res_data.append({"date": day, "err": res["message"]})
            # 全量下载完成后，要刷新统计数据
            DsStatTool.log(id=self.DS_ID, end_bar=end_date, start_bar=start_date)

            msg = "下载Akshare新闻联播文字稿完成！ 【全量, {0} - {1}】".format(start_date, end_date)
            log.info(msg)
            return tl.get_success_result(msg=msg)
        except Exception as err:
            err_msg = "下载Akshare全量新闻联播文字稿时发生异常，" + str(err)
            log.error(err_msg)
            return tl.get_failed_result(msg=err_msg)


if __name__ == "__main__":
    tl.TEST_MODE = True
    srv = AkCCTVNews()
    res = srv.download_bydate("20230724", is_log_stat=True)
    print(res)
    # res = srv.download_all(start_date="20230721")
    # print(res)
