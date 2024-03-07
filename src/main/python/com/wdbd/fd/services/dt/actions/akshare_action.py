#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   akshare_action.py
@Time    :   2024/03/06 15:27:20
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   Akshare 数据源处理
'''
from com.wdbd.fd.model.dt_model import AbstractAction
from com.wdbd.fd.common.tl import Result
from com.wdbd.fd.services.gateway.ak_gateway import get_ak_gateway, DataException
import akshare as ak
from com.wdbd.fd.model.db import get_engine, table_objects_pool as DB_POOL
from sqlalchemy.orm import sessionmaker
import com.wdbd.fd.common.tl as tl
from sqlalchemy.exc import SQLAlchemyError as SQLAlchemyError


# 市场总貌|上海证券交易所
class Ak_SSE_Summary(AbstractAction):
    """
    市场总貌|上海证券交易所

    DOC: https://lxhcvhnie6k.feishu.cn/docx/DrErdGaWBodRRIxFMVYcTB0rnBf#M6zmdZRMJotFngx9DTOcPCnrnhf
    """

    def __init__(self) -> None:
        self.name = "市场总貌、上海证券交易所"
        self.gw = get_ak_gateway()  # 数据网关
        super().__init__()

    def check_environment(self) -> bool:
        """检查环境，检查当前是否可以进行数据下载

        通常子类中会检查需要下载的数据是否已准备好
        Returns:
            bool: 检查结果
        """
        return Result()

    def handle(self) -> bool:
        """数据处理函数，子类必须实现

        Returns:
            bool: 执行结果
        """
        # TEST 待测试
        # 用于单独运行时候
        if self.log is None:
            self.log = tl.get_action_logger(action_name=self.name)

        self.log.info("下载 市场总貌|上海证券交易所")
        try:
            engine = get_engine()
            Session = sessionmaker(bind=engine)
            session = Session()

            # 获取数据
            df = self.gw.call(callback=ak.stock_sse_summary)
            if df.empty:    # 如果返回为空
                return Result()
            # 数据清洗
            df = df.set_index('项目')
            df = df.T
            df = df.reset_index()   # 将索引列变为第一列
            # 修改列名，与db中一致
            new_column_names = {'index': 'market',
                                '流通股本': 'ltgb',
                                '总市值': 'zsz',
                                '总市值': 'zsz',
                                '平均市盈率': 'pjsyl',
                                '上市公司': 'ssgs',
                                '上市股票': 'ssgp',
                                '流通市值': 'tlsz',
                                '总股本': 'zgb',
                                }
            df = df.rename(columns=new_column_names)
            trade_date = df['报告时间'][0]  # 报告日期
            df["trade_date"] = trade_date
            df.drop('报告时间', axis=1, inplace=True)
            # print(df)

            # 删除现有的数据
            t_ods_akshare_stock_sse_summary = DB_POOL.get("ods_akshare_stock_sse_summary")
            session.query(t_ods_akshare_stock_sse_summary).filter(t_ods_akshare_stock_sse_summary.c.trade_date == trade_date).delete()
            session.commit()

            # 写入数据库
            df.to_sql(name='ods_akshare_stock_sse_summary', con=engine, if_exists='append', index=False)

            self.log.info("市场总貌|上海证券交易所 ({0}) 更新完成".format(trade_date))

            return Result()
        except DataException as dwe:
            msg = "Akshare获取数据异常，" + str(dwe)
            self.log.error(msg)
            return tl.Result(result=False, msg=msg)
        except SQLAlchemyError as sqle:
            msg = "SQL异常" + str(sqle)
            self.log.error(msg)
            return tl.Result(result=False, msg=msg)
        finally:
            session.close()

    def rollback(self) -> bool:
        """错误发生时，回滚动作函数

        Returns:
            bool: 回滚操作执行结果
        """
        return Result()


# 交易日历
class Ak_Stock_Cal(AbstractAction):
    """
    交易日历

    DOC: https://lxhcvhnie6k.feishu.cn/docx/DrErdGaWBodRRIxFMVYcTB0rnBf#part-I36ndQh0Fo3d4sxyUvCcZeg2nxc
    """

    def __init__(self) -> None:
        self.name = "交易日历"
        self.gw = get_ak_gateway()  # 数据网关
        self.DOWNLOAD_ALL = False    # 全量参数
        super().__init__()

    def check_environment(self) -> bool:
        """检查环境，检查当前是否可以进行数据下载

        通常子类中会检查需要下载的数据是否已准备好
        Returns:
            bool: 检查结果
        """
        return Result()

    def _get_year_to_down(self):
        # 判断到底更新哪一年的数据
        year_to_down = None   # 拟下载的数据年份
        today = tl.today()
        year = today[:4]
        month = today[4:6]

        if int(month) in [11, 12]:
            year_to_down = str(int(year) + 1)   # 下一年
        else:
            year_to_down = year     # 今年
        # print("year_to_down = " + year_to_down)
        return year_to_down

    def handle(self) -> bool:
        """数据处理函数，子类必须实现

        Returns:
            bool: 执行结果
        """
        # TEST 待测试
        # 用于单独运行时候
        if self.log is None:
            # self.log = tl.get_action_logger(action_name=self.name)
            self.log = tl.get_logger()

        self.log.info("下载 股票交易日历")
        try:
            engine = get_engine()
            Session = sessionmaker(bind=engine)
            session = Session()

            year_to_down = self._get_year_to_down()
            self.log.info("更新数据年份：" + year_to_down)

            # 取得全量数据
            df = self.gw.call(callback=ak.tool_trade_date_hist_sina)
            if df.empty:    # 如果返回为空
                return Result(result=False, msg="数据返回为空！")
            # 过滤符合条件的df数据
            if self.DOWNLOAD_ALL:
                # 全量下载，现删除现有数据
                t_cal = DB_POOL.get("ods_akshare_tool_trade_date_hist_sina")
                session.query(t_cal).delete()
                session.commit()
            elif year_to_down is not None:
                # 过滤后只剩余特定年饭的数据
                self.log.debug("只更新{0}年数据".format(year_to_down))
                start_dt = "{0}-01-01".format(year_to_down)
                end_dt = "{0}-12-31".format(year_to_down)
                t_cal = DB_POOL.get("ods_akshare_tool_trade_date_hist_sina")
                session.query(t_cal).filter(t_cal.c.trade_date >= start_dt).filter(t_cal.c.trade_date <= end_dt).delete()
                session.commit()
                df = df.astype({'trade_date': str})
                df = df[(df['trade_date'] >= start_dt) & (df['trade_date'] <= end_dt)]
            else:
                # 不更新本地数据
                df = None

            # 写入数据库
            if df is not None:
                df.to_sql(name='ods_akshare_tool_trade_date_hist_sina', con=engine, if_exists='append', index=False)
            self.log.info("下载交易日历{0}条数据数据".format(df.shape[0]))

            return Result()
        except DataException as dwe:
            msg = "Akshare获取数据异常，" + str(dwe)
            self.log.error(msg)
            return tl.Result(result=False, msg=msg)
        except SQLAlchemyError as sqle:
            msg = "SQL异常" + str(sqle)
            self.log.error(msg)
            return tl.Result(result=False, msg=msg)
        finally:
            session.close()

    def rollback(self) -> bool:
        """错误发生时，回滚动作函数

        Returns:
            bool: 回滚操作执行结果
        """
        return Result()


if __name__ == "__main__":
    # # ENVIRONMENT = ""
    # # 
    # action = Ak_SSE_Summary()
    # res = action.handle()
    # print(res.result)

    # # tl.get_action_logger("ABC").info("Action日志")

    # 下载股票交易日历
    action = Ak_Stock_Cal()
    res = action.handle()
    print(res.result)
