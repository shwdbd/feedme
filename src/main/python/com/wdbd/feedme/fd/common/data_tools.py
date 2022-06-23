#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   data_tools.py
@Time    :   2021/08/14 17:14:46
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   数据处理工具
'''
import com.wdbd.feedme.fd.common.common as tl
import gtp.fd.fdapi as fdapi
from gtp.fd.datagateway.tushare_gateway import TushareGateWay
import gtp.fd.tools.mg_utils as mg_utils
import com.wdbd.feedme.fd.common.base as base
from progress.bar import Bar


class GernalDataUnit(base.BaseDataUnit):
    """ 通用数据下载单元类 """

    def __init__(self, name, config):
        super().__init__(name=name, config=config)
        self.data = []        # 数据包

    def load_data(self, date: str = None):
        """加载数据，本函数需要继承

        Args:
            date (str, optional): 日增量数据用，数据日期. Defaults to None.
        """
        self.data = []


class TushareDailyDataUnit(GernalDataUnit):
    """ Tushare每日增量数据下载 """
    # 前提：日期字段名为trade_date

    def __init__(self, name: str, config: base.DataUnitConfig, table_name: str, date_field: str, fields_id: str):
        """初始函数

        Args:
            name (str): 数据单元
            config (base.DataUnitConfig): 配置信息
            table_name (str): 关联的表名
            fields_id (str): 字段表id
            date_field ([type]): 日期字段名
        """
        super().__init__(name=name, config=config)
        self.table_name = table_name
        self.date_field = date_field
        self.gw = TushareGateWay()
        self.fields = self.gw.get_fields(fields_id)
        self.data = []

    def download_all(self, from_date: str = None, to_date: str = None, *args, **kwargs) -> bool:
        """ 存量数据下载 """
        log = tl.get_logger()

        if not to_date:
            to_date = tl.today()
        if not from_date:
            from_date = self.start_date

        try:
            dates = fdapi.get_dates(
                start=from_date, end=to_date, trade_date_only=False)
            bar = Bar('{label}存量数据'.format(label=self.name), max=len(dates))
            for day in dates:
                self.load_data(date=day)    # 从网上获取数据
                if len(self.data) > 0:
                    mg_utils.clear(table_name=self.table_name,
                                   where_dict={self.date_field: day})
                    mg_utils.insert_into_collection(
                        collection_name=self.table_name, data=self.data, clear=False)
                    bar.next()
            bar.finish()

            # 回显下载记录数
            where_sql = {
                "$and": [{"trade_date": {'$gte': from_date}}, {"trade_date": {'$lte': to_date}}]}
            log.info("共下载【{label}】存量数据{d}天{c}条记录".format(d=len(dates), label=self.name, c=mg_utils.count(
                table_name=self.table_name, where_dict=where_sql)))

            return True
        except Exception as err:
            log.error("下载【{label}】存量出现问题, {err}".format(
                label=self.name, err=err))
            return False
        return False

    def download_bydate(self, date: str, *args, **kwargs) -> bool:
        # 日增量数据下载
        log = tl.get_logger()

        # 加载数据
        self.load_data(date)
        # 处理数据为空的情况
        if not self.data or len(self.data) == 0:
            if not fdapi.is_trade_date(date):
                log.info("日期{d}为非交易日，无数据。".format(d=date))
                return True
            else:
                log.error("日期{d}无数据，请核对！".format(d=date))
                return False

        # 更新数据库
        try:
            cx = tl.get_mgconn()
            db = tl.get_mgdb()
            session = cx.start_session()
            session.start_transaction()

            # 删除现有数据
            db[self.table_name].delete_many({self.date_field: date})

            # 插入数据
            db[self.table_name].insert_many(self.data)

            # 查询记录返回
            count = db[self.table_name].count_documents(
                {self.date_field: date})
            log.debug("下载并更新【{label}】信息 {c} 条数据[日期:{d}]".format(
                c=count, label=self.name, d=date))

            # 清空数据
            self.data = []

            return True
        except Exception as err:
            log.error("下载【{label}】日增量数据失败，日期={d}, 错误原因：{err}".format(
                label=self.name, d=date, err=err))
            session.abort_transaction()
            return False
        else:
            session.commit_transaction()
        finally:
            session.end_session()

    def query(self) -> base.UnitQueryResult:
        """ 查询统计结果 """
        return mg_utils.stat_daily(self.table_name, self.date_field)

    def stat(self, mode: str = "ctrl", filepath: str = "stat.log", unitname: str = None, setname: str = None) -> base.DailyUnitStatResult:
        """统计存量金融数据
        """
        # TODO 待实现
        return None


class TushareFixedDataUnit(GernalDataUnit):
    """ 基本表（与日期无关）数据下载单元 """

    def __init__(self, name: str, config: base.DataUnitConfig, table_name: str, fields_id: str):
        """初始函数

        Args:
            name (str): 数据单元
            config (base.DataUnitConfig): 配置信息
            table_name (str): 关联的表名
            fields_id (str): 字段表id
        """
        super().__init__(name=name, config=config)
        self.table_name = table_name
        self.gw = TushareGateWay()
        self.fields = self.gw.get_fields(fields_id)

    def download_all(self, from_date: str = None, to_date: str = None, *args, **kwargs) -> bool:
        """ 存量下载 """
        log = tl.get_logger()

        if not self.data:
            self.load_data()

        # 处理数据为空的情况
        if not self.data or len(self.data) == 0:
            log.error("无法获取【{label}】存量数据，请核对！".format(label=self.name))
            return False

        # 存入数据库
        try:
            res = mg_utils.insert_into_collection(
                collection_name=self.table_name, data=self.data)
            log.info("【{label}】 存量数据下载完毕，记录数={c}".format(c=res, label=self.name))

            return True
        except Exception as err:
            log.error("下载【{label}】存量数据出现问题, {e}".format(e=err, label=self.name))
            return False

    def download_bydate(self, date: str, *args, **kwargs) -> bool:
        """数据下载函数，本方法需要子类中具体实现
        """
        log = tl.get_logger()

        if not self.data:
            self.load_data()

        # 处理数据为空的情况
        if not self.data or len(self.data) == 0:
            log.error("无法获取【{label}】数据，请核对！".format(label=self.name))
            return False

        # 存入数据库
        try:
            # 清除现有数据
            mg_utils.clear(table_name=self.table_name)

            res = mg_utils.insert_into_collection(
                collection_name=self.table_name, data=self.data)
            log.info("【{label}】下载完毕，日期={d}，记录数={c}".format(
                c=res, label=self.name, d=date))

            return True
        except Exception as err:
            log.error("日增量下载【{label}】出现问题, {e}".format(e=err, label=self.name))
            return False

    def query(self, date: str = None, start_date: str = None, end_date: str = None) -> base.UnitQueryResult:
        """ 查询统计结果 """
        return mg_utils.stat_basic(table_name=self.table_name)

    def stat(self, mode: str = "ctrl", filepath: str = "stat.log", unitname: str = None, setname: str = None) -> base.FixedUnitStatResult:
        """统计存量金融数据
        """
        # TODO 待实现
        return None
