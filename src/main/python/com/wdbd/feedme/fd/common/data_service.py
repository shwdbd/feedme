#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   data_service.py
@Time    :   2021/08/13 13:02:33
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   数据下载服务业务逻辑代码
'''
import gtp.fd.base.base as base
import gtp.fd.common as tl
from gtp.fd.base.mg_dao.dataunit_status import DataUnitStatusDAO
import gtp.fd.fdapi as fdapi
import datetime


class DataService:
    """ 数据下载服务 """

    def download_all(self, unit_name: str = None, set_name: str = None, start_date: str = None, rebuild: bool = True, dataunit_configfile: str = None, set_configfile=None) -> bool:
        """下载存量数据

        unit_name和set_name两者必须提供一个

        Args:
            unit_name (str, optional): 数据单元名. Defaults to None，.
            set_name (str, optional): 数据单元集合名. Defaults to None.
            start_date (str, optional): 数据开始日期. Defaults to None.
            rebuild (bool, optional): 是否重建数据环境. Defaults to True.

        Returns:
            bool: 执行结果
        """
        log = tl.get_logger()
        # 获取需要执行的unit清单
        unit_list = self._get_unit(unit_name=unit_name, set_name=set_name,
                                   dataunit_configfile=dataunit_configfile, set_configfile=set_configfile)
        if len(unit_list) == 0:
            log.info("未找到符合条件的数据单元，下载终止")
            return False

        # 打印待执行的步骤名称
        log.info("-"*20)
        log.info("总步骤数量 = {0}".format(len(unit_list)))
        for idx, unit in enumerate(unit_list):
            log.info(
                '{i}. {name}'.format(i=(idx+1), name=unit.name))
        log.info("-"*20)

        # 逐一运行unit
        s_start = datetime.datetime.now()
        count_unit = len(unit_list)
        for idx, unit in enumerate(unit_list):
            start = datetime.datetime.now()
            log.info(
                "[{i}/{c}] {n}开始 ... ".format(i=idx+1, c=count_unit, n=unit.name))
            if unit.config.stored.rebuild:
                res = unit.rebuild()
                if res:
                    log.info("表结构重建完成 ... ")
                else:
                    log.error("表结构重建失败!")
                    break
            if unit.download_all(from_date=start_date):         # 表格初始化、数据下载
                end = datetime.datetime.now()
                log.info(
                    "[{i}/{c}] 执行完成，耗时 = {t}".format(t=(end-start), i=idx+1, c=count_unit))
            else:
                log.error(
                    "[{i}/{c}] 执行错误！".format(i=idx+1, c=count_unit))
                break
        s_end = datetime.datetime.now()
        log.info("全部数据下载完成，总耗时 = {0}".format((s_end-s_start)))

        return True

    def download_bydate(self, unit_name: str = None, set_name: str = None, date: str = None, start_date: str = None, end_date: str = None, dataunit_configfile: str = None, set_configfile=None) -> bool:
        """按日下载数据

        unit_name和set_name两者必须提供一个

        Args:
            unit_name (str, optional): 数据单元名. Defaults to None.
            set_name (str, optional): 数据单元集合名. Defaults to None.
            date (str, optional): 指定日期. Defaults to None.
            start_date (str, optional): 时间段，开始日期（含）. Defaults to None.
            end_date (str, optional): 时间段，结束日期（含）. Defaults to None.

        Returns:
            bool: 执行结果
        """
        log = tl.get_logger()

        # 获取需要执行的unit清单
        unit_list = self._get_unit(unit_name=unit_name, set_name=set_name,
                                   dataunit_configfile=dataunit_configfile, set_configfile=set_configfile)
        if len(unit_list) == 0:
            log.info("未找到符合条件的数据单元，下载终止")
            return False

        # 打印待执行的步骤名称
        log.info("-"*20)
        log.info("总步骤数量 = {0}".format(len(unit_list)))
        for idx, unit in enumerate(unit_list):
            log.info(
                '{i}. {name}'.format(i=(idx+1), name=unit.name))
        log.info("-"*20)

        # 处理按日期段运行的情况
        date_list = self._get_date_list(
            date=date, start_date=start_date, end_date=end_date)
        if len(date_list) == 0:
            log.info("未找到符合条件的日期范围，下载终止")
            return False
        else:
            if date:
                log.info('执行日期范围：{d}'.format(d=date))
            else:
                log.info(
                    '执行日期范围：{d1} - {d2}'.format(d1=start_date, d2=end_date))
        log.info("-"*20)

        # 开始依次执行
        # 如有一个步骤执行错误，则处理中断，并返回False
        for day in date_list:
            start_dt = datetime.datetime.now()
            for idx, unit in enumerate(unit_list):
                u_start = datetime.datetime.now()   # 步骤启动时间
                tl.get_logger().info(
                    '【{i}/{c}】步骤{name}开始执行, 数据日期={d}'.format(d=day, i=(idx+1), c=len(unit_list), name=unit.name))
                res = self.__download_single_unit(day, unit)     # 执行下载
                u_end = datetime.datetime.now()
                tl.get_logger().info('本步耗时：{0}'.format((u_end-u_start)))
                if not res:
                    tl.get_logger().error(
                        '【{i}/{c}】步骤执行失败，全部数据下载终止!'.format(i=(idx+1), c=len(unit_list)))
                    break
                else:
                    tl.get_logger().info(
                        '【{i}/{c}】步骤执行完成'.format(i=(idx+1), c=len(unit_list)))
                    tl.get_logger().info("-"*20)
        end_dt = datetime.datetime.now()
        tl.get_logger().info('总耗时：{0}'.format((end_dt-start_dt)))

        return True

    def _get_date_list(self, date: str = None, start_date: str = None, end_date: str = None) -> list:
        """ 返回符合条件的日期范围 """
        # 单个日期
        if date:
            return [date]

        # 加载日期段:
        date_list = fdapi.get_dates(
            start=start_date, end=end_date, trade_date_only=False)
        return date_list

    def _get_unit(self, unit_name: str = None, set_name: str = None, dataunit_configfile: str = None, set_configfile=None) -> list:
        """ 返回符合条件的数据对象列表 """
        # 如果unit_name，则调用load_unit
        # 如果set_name，则调用load_by_set
        # 其余返回[]
        if not unit_name and not set_name:
            return []
        elif unit_name:
            cs = base.ConfigService(
                config_path=dataunit_configfile, set_file_path=set_configfile)
            unit = cs.load_unit(unit_name)
            if unit:
                return [unit]
            else:
                return []
        else:
            cs = base.ConfigService(
                config_path=dataunit_configfile, set_file_path=set_configfile)
            return cs.load_by_set(set_name)

    def __download_single_unit(self, day: str, unit: base.BaseDataUnit) -> bool:
        """执行单个步骤下载

        包括调用函数，包括记录日志

        Returns:
            bool: 下载结果
        """
        dus = DataUnitStatusDAO()
        dus.new(unit_name=unit.name, date=day)
        res = unit.download_bydate(date=day)
        if res:
            dus.done(unit_name=unit.name, date=day)
        else:
            dus.fail(unit_name=unit.name, date=day)
        return res


if __name__ == "__main__":
    srv = DataService()

    # # download by date
    # res = srv.download_bydate(date="20210814", set_name="UnitAB")
    # print(res)

    # download stored data
    res = srv.download_all(set_name="UnitAB", rebuild=False)
    print(res)
