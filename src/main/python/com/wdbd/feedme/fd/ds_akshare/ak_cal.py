#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   ak_cal.py
@Time    :   2022/12/09 22:30:37
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   Akshare日历数据下载
'''
import akshare as ak
from com.wdbd.feedme.fd.common.common import get_logger, get_session, records2objlist
from com.wdbd.feedme.fd.orm.ods_tables import OdsAkshareTradeCal
import sqlalchemy
from com.wdbd.feedme.fd.common.data_gateway import DsStatTool


class AkTradeCal:
    """ Akshare 交易日历数据下载 """

    def __init__(self):
        self.DS_ID = "akshare.cal"    # 数据源ID

    def download(self):
        """ 下载并更新本地ods表ods_akshare_tool_trade_date_hist_sina """
        log = get_logger()

        try:
            # 取得数据
            df = ak.tool_trade_date_hist_sina()
            if df is None or df.shape[0] == 0:
                err_msg = "交易日历接口返回空数据，下载失败！"
                log.error(err_msg)
                return {"result": False, "msg": [err_msg]}
            obj_list = records2objlist(df, OdsAkshareTradeCal)

            # 如果有数据，则del and insert数据库
            try:
                session = get_session()
                session.query(OdsAkshareTradeCal).delete()      # 清除表数据
                session.bulk_save_objects(obj_list)
                session.commit()
                first_bar = session.query(sqlalchemy.func.min(OdsAkshareTradeCal.trade_date)).scalar().replace("-", "")
                last_bar = session.query(sqlalchemy.func.max(OdsAkshareTradeCal.trade_date)).scalar().replace("-", "")

                # 更新统计表
                DsStatTool.log(id=self.DS_ID, end_bar=last_bar, start_bar=first_bar)

                msg = "下载完毕，{s}到{e} 共{c}个交易日".format(s=first_bar, e=last_bar, c=len(obj_list))
                log.debug(msg)
                return {"result": True, "msg": [msg]}
            except Exception as err:
                err_msg = "下载Akshare交易日历时遇到异常，SQL异常:" + str(err)
                log.error(err_msg)
                session.rollback()
                return {"result": False, "msg": [err_msg]}
            finally:
                session.close()
        except Exception as err:
            err_msg = "Akshare取交易日历时发生异常，" + str(err)
            log.error(err_msg)
            return {"result": False, "msg": [err_msg]}


# if __name__ == "__main__":
#     srv = AkTradeCal()
#     res = srv.download()
#     print(res)
