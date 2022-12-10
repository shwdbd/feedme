#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   ak_stock.py
@Time    :   2022/12/10 16:28:18
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   Akshare 股票类数据下载
'''
import akshare as ak
from com.wdbd.feedme.fd.common.common import get_logger, get_session, records2objlist, today
from com.wdbd.feedme.fd.orm.ods_tables import OdsAkshareStock
import sqlalchemy
from com.wdbd.feedme.fd.common.data_gateway import DsStatTool
import pandas as pd


class AkCNStockList:
    """ Akshare A股股票清单数据下载 """

    def __init__(self):
        self.DS_ID = "akshare.cnstock_list"    # 数据源ID

    def download(self):
        """ 下载并更新本地ods表ods_akshare_tool_trade_date_hist_sina """
        log = get_logger()

        try:
            # 取得数据
            df_sh = ak.stock_sh_a_spot_em()[['代码', '名称']]
            df_sh["exchange"] = "SSE"
            df_sz = ak.stock_sz_a_spot_em()[['代码', '名称']]
            df_sz["exchange"] = "SZE"
            df_bj = ak.stock_bj_a_spot_em()[['代码', '名称']]
            df_bj["exchange"] = "BJE"
            df = pd.concat([df_sh, df_sz, df_bj])
            if df is None or df.shape[0] == 0:
                err_msg = "接口返回空数据，下载失败！"
                log.error(err_msg)
                return {"result": False, "msg": [err_msg]}
            df.rename(columns={"代码": "stock_id", "名称": "name"}, inplace=True)
            obj_list = records2objlist(df, OdsAkshareStock)

            # 如果有数据，则del and insert数据库
            try:
                session = get_session()
                session.query(OdsAkshareStock).delete()      # 清除表数据
                session.bulk_save_objects(obj_list)
                session.commit()

                # 更新统计表
                DsStatTool.log(id=self.DS_ID, end_bar=today(), start_bar="")

                count_of_stock = session.query(sqlalchemy.func.count(OdsAkshareStock.exchange)).one_or_none()
                nums = sqlalchemy.func.count('*').label('c')
                results = session.query(OdsAkshareStock.exchange, nums).group_by(OdsAkshareStock.exchange).all()
                msg = "下载股票{0}支，各交易所股票数量为：{1}".format(count_of_stock[0], results)
                log.debug(msg)
                return {"result": True, "msg": [msg]}
            except Exception as err:
                err_msg = "下载Akshare A股股票清单时遇到异常，SQL异常:" + str(err)
                log.error(err_msg)
                session.rollback()
                return {"result": False, "msg": [err_msg]}
            finally:
                session.close()
        except Exception as err:
            err_msg = "下载Akshare A股股票清单时遇到异常，" + str(err)
            log.error(err_msg)
            return {"result": False, "msg": [err_msg]}


if __name__ == "__main__":
    srv = AkCNStockList()
    res = srv.download()
    print(res)
