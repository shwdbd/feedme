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
from com.wdbd.feedme.fd.common.common import get_logger, get_session, records2objlist, today, d2dbstr
from com.wdbd.feedme.fd.orm.ods_tables import OdsAkshareStock, OdsAkshareStockDaily_EM
import sqlalchemy
from com.wdbd.feedme.fd.common.data_gateway import DsStatTool
import pandas as pd
import com.wdbd.feedme.fd.common.common as tl
import com.wdbd.feedme.fd.fd_api as fd_api
from com.wdbd.feedme.fd.common.data_gateway import AkshareGateWay


# 股票清单
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
            df_sh["代码"] = df_sh["代码"] + ".SH"
            df_sh["exchange"] = "SSE"
            df_sz = ak.stock_sz_a_spot_em()[['代码', '名称']]
            df_sz["代码"] = df_sz["代码"] + ".SZ"
            df_sz["exchange"] = "SZE"
            df_bj = ak.stock_bj_a_spot_em()[['代码', '名称']]
            df_bj["代码"] = df_bj["代码"] + ".BJ"
            df_bj["exchange"] = "BJE"
            df = pd.concat([df_sh, df_sz, df_bj])
            if df is None or df.shape[0] == 0:
                err_msg = "接口返回空数据，下载失败！"
                log.error(err_msg)
                return tl.get_failed_result(msg=err_msg)
            df.rename(columns={"代码": "stock_id", "名称": "name"}, inplace=True)
            obj_list = records2objlist(df, OdsAkshareStock)

            # 如果有数据，则del and insert数据库
            try:
                session = get_session()
                for stock in obj_list:
                    session.merge(stock)
                session.commit()

                # 更新统计表
                DsStatTool.log(id=self.DS_ID, end_bar=today(), start_bar="")

                count_of_stock = session.query(sqlalchemy.func.count(
                    OdsAkshareStock.exchange)).one_or_none()
                nums = sqlalchemy.func.count('*').label('c')
                results = session.query(OdsAkshareStock.exchange, nums).group_by(
                    OdsAkshareStock.exchange).all()
                msg = "下载股票{0}支，各交易所股票数量为：{1}".format(
                    count_of_stock[0], results)
                log.debug(msg)
                res = tl.get_success_result(msg=msg)
                return res
            except Exception as err:
                err_msg = "下载Akshare A股股票清单时遇到异常，SQL异常:" + str(err)
                log.error(err_msg)
                session.rollback()
                res = tl.get_failed_result(msg=err_msg)
                return res
            finally:
                session.close()
        except Exception as err:
            err_msg = "下载Akshare A股股票清单时遇到异常，" + str(err)
            log.error(err_msg)
            return tl.get_failed_result(msg=err_msg)


# 网易，股票日线
class AkStockDaily_163:
    """ Akshare 网易，股票日线 """

    def __init__(self) -> None:
        self.DS_ID = "akshare.cnstock_daily_163"
        self.columns_mapping = {
            "日期": "trade_date",
            "股票代码": "symbol",
            "名称": "name",
            "收盘价": "p_close",
            "最高价": "p_high",
            "最低价": "p_low",
            "开盘价": "p_open",
            "前收盘": "pre_close",
            "涨跌额": "p_change",
            "涨跌幅": "pct_change",
            "换手率": "turnover_rat",
            "成交量": "volume_h",
            "成交金额": "volume",
            "总市值": "tmv",
            "流通市值": "cmv"
        }

    # # 按日期下载全部股票日线数据
    # def download_by_date(self, trade_date: str, stock_id: str = None):
    #     # 下载更新
    #     log = get_logger()
    #     if not trade_date:
    #         log.error("交易日期为空，下载终止！")
    #         return {"result": False, "msg": ["交易日期为空"]}

    #     log.debug("下载更新Akshare A股日线数据 [date={0}]".format(trade_date))

    #     # TODO （不包含北交所）

    #     if stock_id:
    #         df = ak.stock_zh_a_hist_163(
    #             start_date=trade_date, end_date=trade_date, symbol=stock_id)
    #     else:
    #         print("all")
    #         # TODO 读取全部股票，并逐一进行查询
    #         df_list = []
    #         all_stock = get_stockid(return_type="pre")
    #         for stock_id in all_stock:
    #             print(stock_id)
    #             df_s = ak.stock_zh_a_hist_163(
    #                 start_date=trade_date, end_date=trade_date, symbol=stock_id)
    #             # TODO 异常处理
    #             # print(df_s)
    #             df_list.append(df_s)
    #         df = pd.concat(df_list)
    #     print(df)
    #     log.debug("Akshare网关获取{0}条数据".format(df.shape[0]))

    #     # # 数据清洗(字段翻译)
    #     # df.rename(columns=self.columns_mapping, inplace=True)
    #     # obj_list = records2objlist(df, OdsAkshareStockDaily_163)
    #     # print(len(obj_list))

    #     # TODO 继续开发

    #     # if len(obj_list) == 0:
    #     #     err_msg = "当日未找到符合条件的数据, date={0}".format(trade_date)
    #     #     log.debug(err_msg)
    #     #     return {"result": False, "msg": [err_msg]}

    #     # # 写入数据库
    #     # try:
    #     #     session = get_session()
    #     #     session.query(OdsAkshareStockDaily_163).filter(OdsAkshareStockDaily_163.trade_date == trade_date).delete()      # 清除表数据
    #     #     session.bulk_save_objects(obj_list)
    #     #     session.commit()

    #     #     # 更新统计表
    #     #     DsStatTool.log(id=self.DS_ID, end_bar=trade_date)

    #     #     log.debug("下载更新完成")
    #     #     return {"result": True, "msg": []}
    #     # except Exception as err:
    #     #     err_msg = "下载Akshare A股股票日线时遇到异常，SQL异常:" + str(err)
    #     #     log.error(err_msg)
    #     #     session.rollback()
    #     #     return {"result": False, "msg": [err_msg]}
    #     # finally:
    #     #     session.close()

    # # 按股票下载全部历史数据
    # def download_by_stock(self, ts_code: str, trade_date: str = None, start_date: str = None, end_date: str = None):
    #     log = get_logger()

    #     log.debug("下载更新Akshare A股日线数据 [id={0}]".format(ts_code))

    #     gw = AkshareGateWay()
    #     if trade_date:
    #         df = gw.call(
    #             gw.api.daily, fields=FIELDS["daily"], ts_code=ts_code, trade_date=trade_date)
    #     elif start_date:
    #         df = gw.call(
    #             gw.api.daily, fields=FIELDS["daily"], ts_code=ts_code, start_date=start_date, end_date=end_date)
    #     else:
    #         df = gw.call(gw.api.daily, fields=FIELDS["daily"], ts_code=ts_code)
    #     log.debug("Akshare网关获取{0}条数据".format(df.shape[0]))

    #     # 数据清洗(字段翻译)
    #     df.rename(columns={"open": "p_open",
    #                        "high": "p_high",
    #                        "low": "p_low",
    #                        "close": "p_close",
    #                        "change": "p_change"}, inplace=True)
    #     obj_list = records2objlist(df, OdsAkshareStockDaily_163)

    #     if len(obj_list) == 0:
    #         err_msg = "当日未找到符合条件的数据, date={0}".format(trade_date)
    #         log.debug(err_msg)
    #         return {"result": False, "msg": [err_msg]}

    #     # 写入数据库
    #     try:
    #         session = get_session()
    #         session.query(OdsAkshareStockDaily_163).filter(
    #             OdsAkshareStockDaily_163.ts_code == ts_code).delete()      # 清除表数据
    #         # TODO 按条件删除
    #         session.bulk_save_objects(obj_list)
    #         session.commit()

    #         # 更新统计表
    #         DsStatTool.log(id=self.DS_ID, end_bar=trade_date)

    #         log.debug("下载更新完成")
    #         return {"result": True, "msg": []}
    #     except Exception as err:
    #         err_msg = "下载Akshare A股股票日线时遇到异常，SQL异常:" + str(err)
    #         log.error(err_msg)
    #         session.rollback()
    #         return {"result": False, "msg": [err_msg]}
    #     finally:
    #         session.close()

    # # 下载全部历史数据
    # def download_all(self, stockid_test: str = None) -> None:
    #     """ 下载全量历史数据

    #     Args:
    #         stockid_test (str, optional): 单元测试用股票id，如600016.SH. Defaults to None.
    #     """
    #     # 按股票清单，逐一股票下载
    #     log = get_logger()

    #     try:
    #         session = get_session()
    #         # 取得股票清单id列表
    #         if stockid_test:
    #             log.info("【单元测试】仅下载测试用股票：{0}".format(stockid_test))
    #             stocks = [(stockid_test, "测试股票名",)]
    #         else:
    #             stocks = session.query(OdsAkshareStockBasic.ts_code, OdsAkshareStockBasic.name).order_by(
    #                 OdsAkshareStockBasic.ts_code.desc()).all()      # 清除表数据
    #         count_of_stocks = len(stocks)
    #         log.info("共计有{0}支股票历史日线数据开始下载，请等待较长时间 ...".format(count_of_stocks))
    #         for idx, stock in enumerate(stocks, start=1):
    #             log.debug(stock)
    #             log.debug("{idx}/{all} {id}:{name}".format(idx=idx,
    #                       all=count_of_stocks, id=stock[0], name=stock[1]))
    #             self.download_by_stock(ts_code=stock[0])

    #         # 统计信息记录
    #         first_bar = session.query(sqlalchemy.func.min(
    #             OdsAkshareStockDaily_163.trade_date)).scalar()
    #         last_bar = session.query(sqlalchemy.func.max(
    #             OdsAkshareStockDaily_163.trade_date)).scalar()
    #         DsStatTool.log(id=self.DS_ID, start_bar=first_bar,
    #                        end_bar=last_bar)

    #         log.debug("全部下载完成！")
    #     except Exception as err:
    #         err_msg = "下载Akshare A股股票历史全量日线时遇到异常，SQL异常:" + str(err)
    #         log.error(err_msg)
    #         session.rollback()
    #     finally:
    #         session.close()


# 新浪，股票日线
class AkStockDaily_Sina:
    # TODO 新浪，股票日线
    pass


# 东方财富，股票日线
class AkStockDaily_EM:
    """ 东方财富，股票日线下载 """

    def __init__(self) -> None:
        self.DS_ID = "akshare.cnstock_daily_em"
        self.columns_mapping = {
            "日期": "trade_date",
            "股票代码": "symbol",
            # "名称": "name",
            "开盘": "p_open",
            "收盘": "p_close",
            "最高": "p_high",
            "最低": "p_low",
            "成交量": "volume_h",
            "成交额": "volume",
            "振幅": "amp",
            "涨跌额": "p_change",
            "涨跌幅": "pct_change",
            "换手率": "turnover_rat",
        }

    # 数据清洗
    def df_clear(self, df: pd.DataFrame, ts_code: str):
        """数据清洗

        Args:
            df (pd.DataFrame): _description_

        Returns:
            _type_: _description_
        """
        if df is None or df.empty:
            return None
        df.rename(columns=self.columns_mapping, inplace=True)
        df["symbol"] = ts_code
        df["trade_date"] = df["trade_date"].apply(d2dbstr)
        # print(df.info())
        return df

    # 按日期进行单日数据下载
    def download_by_date(self, date: str, test_mode: bool = False):
        """按日下载股票数据

        Args:
            date (str): _description_

        Returns:
            _type_: _description_
        """
        if not date:
            err_msg = "交易日期为空，停止下载！"
            return tl.get_failed_result(msg=err_msg)

        log = get_logger()
        log.info("下载Akshare东方财富{d}的A股日线数据".format(d=date))
        dw = AkshareGateWay()
        stocks = fd_api.get_stockid()       # FIXME 指定数据源
        df_list = []
        skip_stock_list = []    # 当日无数据，跳过的股票
        log.debug("准备下载{0}支股票{1}的日线数据".format(len(stocks), date))
        for idx, ts_code in enumerate(stocks, start=1):
            if test_mode and idx > 20:
                log.debug("测试模式启用，下载部分后停止  。。。 ")
                break
            df = ak.stock_zh_a_hist(symbol=dw.tscode_2_symbol(ts_code), period="daily",
                                    start_date=date, end_date=date, adjust="")      # TODO 做复权参数
            # 数据清洗
            if self.df_clear(df, ts_code) is None:
                skip_stock_list.append(ts_code)
                continue
            else:
                # 当日有数据：
                df_list.append(df)
            # 命令行提示
            if idx % len(stocks) == 500:
                log.debug("处理中 ... 已处理 {0}, 共计{1}".format(idx, len(stocks)))
        df = pd.concat(df_list)
        if df is None or df.empty:
            err_msg = "无法读取{0}的东方财富股票日线数据".format(date)
            log.error(err_msg)
            return {"result": False, "msg": [err_msg]}
        obj_list = records2objlist(df, OdsAkshareStockDaily_EM)
        log.debug("从Akshare接口读取{0}条数据".format(len(obj_list)))
        log.debug("另有{0}条股票无数据".format(len(skip_stock_list)))

        # 写入数据库
        try:
            session = get_session()
            # 清除表数据
            del_query = session.query(OdsAkshareStockDaily_EM).filter(
                OdsAkshareStockDaily_EM.trade_date == date)
            del_query.delete()
            session.bulk_save_objects(obj_list)
            session.commit()
            log.debug("更新完成")

            # 更新统计表
            DsStatTool.log(id=self.DS_ID, end_bar=date)

            msg = "按日下载Akshare股票日线数据(日期{0}), 记录数{1}".format(
                date, len(obj_list))
            log.debug(msg)
            return tl.get_success_result(msg=msg)
        except Exception as err:
            err_msg = "下载Akshare A股日线数据（东方财经） 时遇到异常，SQL异常:" + str(err)
            log.error(err_msg)
            session.rollback()
            return tl.get_failed_result(msg=err_msg)
        finally:
            session.close()

    # 按股票下载全部历史数据
    def download_by_stock(self, ts_code: str, start_date: str = "None", end_date: str = tl.today(), log_stat: bool = True):
        """按股票下载全部历史数据

        Args:
            ts_code (str): 股票代码，格式 600016.SH
            start_date (str, optional): yyyyMMdd 取数开始日期（含）. Defaults to None，按单日取数.
            end_date (str, optional): yyyyMMdd 取数结束日期（含）. Defaults to None，按单日取数.
            log_stat (bool, optional): 是否要登记统计信息，默认为True

        Returns:
            _type_: 执行结果, {"result": False, "msg": [""]}
        """
        log = get_logger()

        log.debug("下载更新Akshare A股日线数据（东方财经） [股票代码: {0}]".format(ts_code))

        gw = AkshareGateWay()
        stock_symbol = gw.tscode_2_symbol(
            ts_code)      # 600016.SH格式转为sh600016格式
        if start_date:
            df = ak.stock_zh_a_hist(symbol=stock_symbol, period="daily",
                                    start_date=start_date, end_date=end_date, adjust="")
        else:
            df = ak.stock_zh_a_hist(
                symbol=stock_symbol, period="daily", end_date=end_date, adjust="")
        # 数据清洗:
        df = self.df_clear(df, ts_code=ts_code)
        if df is None:
            err_msg = "Akshare股票日线(东财)，股票代码{0}未获得数据".format(ts_code)
            return tl.get_failed_result(err_msg)
        else:
            obj_list = records2objlist(df, OdsAkshareStockDaily_EM)
        if len(obj_list) == 0:
            err_msg = "当日未找到符合条件的数据，参数：ts_code={0}, start_date={1}, end_date={2}".format(
                ts_code, start_date, end_date)
            log.error(err_msg)
            return tl.get_failed_result(err_msg)

        # 写入数据库
        try:
            session = get_session()
            # 清除表数据
            del_query = session.query(OdsAkshareStockDaily_EM).filter(
                OdsAkshareStockDaily_EM.symbol == ts_code)
            del_query.delete()
            if start_date:
                del_query.filter(
                    OdsAkshareStockDaily_EM.trade_date >= start_date)
            if end_date:
                del_query.filter(
                    OdsAkshareStockDaily_EM.trade_date <= end_date)
            # 插入数据
            session.bulk_save_objects(obj_list)
            session.commit()

            # 更新统计表
            if log_stat:
                if start_date:
                    DsStatTool.log(
                        id=self.DS_ID, start_bar=start_date, end_bar=end_date)
                else:
                    DsStatTool.log(id=self.DS_ID, end_bar=end_date)

            msg = "按股下载Akshare股票日线数据(代码：{0}), 更新记录{1}条".format(
                ts_code, len(obj_list))
            log.debug(msg)
            return tl.get_success_result(msg=msg)
        except Exception as err:
            err_msg = "下载Akshare A股日线数据（东方财经） 时遇到异常，SQL异常:" + str(err)
            log.error(err_msg)
            session.rollback()
            return tl.get_failed_result(err_msg)
        finally:
            session.close()

    # 下载全部历史数据
    def download_all(self, stockid_test: str = None) -> None:
        """ 下载全量历史数据，包括全部日期，全部股票代码

        Args:
            stockid_test (str): 单元测试用股票id，如600016.SH. Defaults to None.
        """
        # 按股票清单，逐一股票下载
        log = get_logger()

        err_msgs = []
        try:
            session = get_session()
            # 取得股票清单id列表
            if stockid_test:
                log.error("【单元测试】仅下载测试用股票：{0}".format(stockid_test))
                stocks = [stockid_test]
            else:
                # 从fdapi读取
                stocks = fd_api.get_stockid()   # FIXME 要进行优化，可指定数据源
            count_of_stocks = len(stocks)
            # print(stocks)
            log.info("共计有{0}支股票历史日线数据开始下载，请等待较长时间 ...".format(count_of_stocks))

            # 逐支股票开始下载
            for idx, stock in enumerate(stocks, start=1):
                try:
                    result = self.download_by_stock(ts_code=stock, log_stat=False)
                    if not result["result"]:
                        err_msg = "{0} 下载失败".format(stock)
                        log.error(err_msg)
                        err_msgs.append(err_msg)
                    else:
                        log.info("{idx}/{all} {id}".format(idx=idx,
                                                           all=count_of_stocks, id=stock))
                        pass
                except Exception as err:
                    err_msgs.append("{0} 下载异常, {1}".format(stock, str(err)))
            log.info("全部下载完成")

            # 统计信息记录
            first_bar = session.query(sqlalchemy.func.min(
                OdsAkshareStockDaily_EM.trade_date)).scalar()
            last_bar = session.query(sqlalchemy.func.max(
                OdsAkshareStockDaily_EM.trade_date)).scalar()
            DsStatTool.log(id=self.DS_ID, start_bar=first_bar,
                           end_bar=last_bar)

            msg = "Akshare 东财 股票日线数据全量下载完毕（{s} - {e}）".format(s=first_bar, e=last_bar)
            if len(err_msgs)>0:
                return tl.get_failed_result(msg=msg, data=err_msgs)
            else:
                return tl.get_success_result(msg=msg)
        except Exception as err:
            err_msg = "下载Akshare A股日线数据（东方财经）历史全量日线时遇到异常，SQL异常:" + str(err)
            log.error(err_msg)
            return tl.get_failed_result(msg=err_msg)
            session.rollback()
        finally:
            session.close()


if __name__ == "__main__":
    tl.TEST_MODE = True
    srv = AkStockDaily_EM()
    res = srv.download_all(stockid_test="600016.SH")
    print(res)

# if __name__ == "__main__":
#     tl.TEST_MODE = True
#     srv = AkCNStockList()
#     res = srv.download()
#     print(res)

# if __name__ == "__main__":
#     # srv = AkStockDaily_163()
#     # res = srv.download_by_date(trade_date="20221209")
#     # print(res)
#     srv = AkStockDaily_EM()
#     # res = srv.download_by_stock(ts_code="600016.SH", start_date="20221209")
#     # print(res)
#     # res = srv.download_all(stockid_test="600016.SH")
#     # print(res)
#     res = srv.download_by_date(date="20221213", test_mode=True)
#     print(res)

# if __name__ == "__main__":
#     tl.TEST_MODE = True
#     srv = AkStockDaily_EM()
#     # res = srv.download_by_date(date="20230719", test_mode=True)
#     res = srv.download_by_stock(ts_code="600016.SH", start_date="20230710")
#     print(res)

# if __name__ == "__main__":
#     srv = AkStockDaily_EM()
#     # res = srv.download_all(stockid_test="688525.SH")
#     res = srv.download_all()
#     print(res)

# if __name__ == "__main__":
#     srv = AkStockDaily_EM()
#     # res = srv.download_all(stockid_test="688525.SH")
#     res = srv.download_by_date(date="20221215", test_mode=True)
#     print(res)
