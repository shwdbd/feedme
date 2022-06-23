#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   base.py
@Time    :   2021/08/13 12:52:24
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   数据下载服务 基本业务类

Change log：
2021-10-28 新增UnitStatResult、DailyUnitStatResult、FixedUnitStatResult类


'''
import com.wdbd.feedme.fd.common.common as tl
import os
import json
from threading import Thread
import time
import importlib
from gtp.fd.base.mg_dao.server_status import ServerStatus
from gtp.fd.base.mg_dao.dataunit_status import DataUnitStatusDAO
import gtp.fd.fdapi as fdapi
import datetime


class DataUnitStoredConfig:
    """ 存量数据配置 """

    def __init__(self, config):
        self.config = config        # 父配置项目的
        self.rebuild = True         # 是否重建环境


class DataUnitDailyConfig:
    """ 每日增量数据配置 """

    def __init__(self, config):
        self.config = config        # 父配置项目的
        self.windows = [["00:00", "23:59"]]     # 可执行时间
        self.only_run_in_trade_day = False      # 是否仅在交易日运行
        self.only_once_in_day = True            # 是否一日仅运行一次
        self.sleep_time = 5


class DataUnitConfig:
    """数据下载单元，配置信息
    """

    def __init__(self, name):
        self.name = name                    # 单元名
        self.class_path = ""                # 数据单元类路径
        self.package_name = ""
        self.class_name = ""
        # 存量数据配置
        self.stored = DataUnitStoredConfig(self)
        # 每日增量数据配置
        self.daily = DataUnitDailyConfig(self)


class UnitQueryResult:
    """数据状态查询结果
    """

    def __init__(self):
        # 全量表
        self.record_count = 0   # 总记录数
        # 增量表
        self.first_date = ""    # 数据首日
        self.last_date = ""     # 数据末日
        self.total_dates = 0    # 总天数
        self.missing_dates = []     # 缺少的天数
        self.is_trade_date = True   # 是否只查询

    def __str__(self):
        """返回一个对象的描述信息"""
        str = "\n" + "-"*20 + "\n"
        str += "记录数量: {0}".format(self.record_count) + "\n"
        if self.first_date:
            str += "开始结束日期: {0} -- {1}".format(self.first_date, self.last_date) + "\n"
        if self.total_dates:
            str += "总日期天数: {0}".format(self.total_dates) + "\n"
        if self.missing_dates:
            str += "缺失日期: {0}天".format(len(self.missing_dates)) + "\n"
            if len(self.missing_dates) > 10:
                str += "列出最近10日" + "\n"
                for day in self.missing_dates[-10:]:
                    str += "{0}".format(day) + "\n"
            else:
                for day in self.missing_dates:
                    str += "{0}".format(day) + "\n"
        str += "-"*20 + "\n"
        return str


class BaseDataUnit(Thread):
    """数据基础单元
    """

    def __init__(self, name: str, config: DataUnitConfig):
        """构造函数

        Args:
            name (str): 数据单元的名称
        """
        super().__init__()
        self.name = name
        self.config = config

    def run(self, date: str, *args, **kwargs):
        """服务器启动下载

        Args:
            date (str): 下载日期，格式：yyyyMMdd
        """
        log = tl.get_logger()
        ss_dao = ServerStatus()
        dus_dao = DataUnitStatusDAO()

        log.info('步骤进程 {0} 开始执行'.format(self.name))

        # 只要服务状态为运行中就一直执行
        while ss_dao.get() == ServerStatus.STATUS_RUNNING:
            # 运行时间点
            if date is None:    # 使用当前系统时间
                sys_day = tl.today()
                sys_time = tl.now()
            else:
                # 使用参数传入时间
                sys_day = date
                sys_time = date + " 000101"

            # 检查步骤是否可以运行
            if self.ready(sys_time):
                log.info("-"*20)
                log.debug('步骤进程{0} 符合条件，可运行'.format(self.name))
                dus_dao.new(unit_name=self.name, date=sys_day)
                start_dt = datetime.datetime.now()
                r = self.download_bydate(date=sys_day)     # 执行
                if r:
                    dus_dao.done(unit_name=self.name, date=sys_day)
                else:
                    dus_dao.fail(unit_name=self.name, date=sys_day)
                end_dt = datetime.datetime.now()
                tl.get_logger().error(
                        '【步骤{name}】耗时{t}'.format(name=self.name, t=(end_dt-start_dt)))
                log.info("-"*20)
            else:
                log.debug('步骤进程{0} 不符合条件，继续等待'.format(self.name))

            # 判断如果是最后一个进程，且服务器已发出shundown信号，则更新服务器状态为stop
            if not self.check_last_closed_unit():
                log.info("步骤{0}等待 ..{1}秒..".format(self.name, self.config.daily.sleep_time))
                time.sleep(self.config.daily.sleep_time)

        log.info('子进程{0}结束！'.format(self.name))

    def check_last_closed_unit(self) -> bool:
        """
        判断如果是最后一个进程，且服务器已发出shundown信号，则更新服务器状态为stop
        """
        # 如果server状体是closing，则继续
        # 如果本步骤是当前最后一个未关闭（date只有自己仍在RUNING）
        ss_dao = ServerStatus()
        dus_dao = DataUnitStatusDAO()
        if ss_dao.get() == ServerStatus.STATUS_CLOSING and dus_dao.all_unit_finish():
            ss_dao.stop()
            return True
        else:
            return False

    def ready(self, time: str) -> bool:
        """返回当前是否可执行下载

        一般在基础类中实施（根据参数不同），如有特殊需要可在子类中覆写

        一般考虑几个因素：
        1. 服务器状态是否停止
        2. 是否当日已成功运行过（当日只执行一次的Unit）
        3. 是否在可执行窗口时间内（包括时间窗口、交易日因素）

        Args:
            time (str): yyyyMMdd HHmmss格式的时间，表示当前执行时间

        Returns:
            bool: 是否可执行下载
        """
        date = time[:8]
        ss_dao = ServerStatus()
        dus_dao = DataUnitStatusDAO()
        logger = tl.get_logger()

        # 1. 服务器状态是否停止，停止则返回False
        if ss_dao.get() != ServerStatus.STATUS_RUNNING:
            logger.debug("当前服务器状态不是运行状态，所以单元无法运行")
            return False

        # 2. 是否当日已成功运行过（当日只执行一次的Unit），否则返回False
        if self.config.daily.only_once_in_day and dus_dao.has_run(unit_name=self.name, date=date):
            logger.debug("当日已运行，不能再次运行")
            return False

        # 3. 是否在可执行窗口时间内（包括时间窗口、交易日因素），否则返回False
        # 判断交易日因素
        if not fdapi.is_trade_date(date) and self.config.daily.only_run_in_trade_day:
            logger.debug("当日不是交易日，不能运行")
            return False

        # 时间窗口因素
        if not self.__check_time_in_windows(time):
            return False

        return True

    def __check_time_in_windows(self, time: str) -> bool:
        """ 检查指定的时间(HHmmss)是否在时间窗口内 """
        if time is None:
            return True
        time_value = int(time[-6:-2])
        in_win = False
        for win in self.config.daily.windows:
            start = int(win[0].replace(":", ""))
            end = int(win[1].replace(":", ""))
            if time_value >= start and time_value <= end:
                in_win = True
        return in_win

    def download_bydate(self, date: str, *args, **kwargs) -> bool:
        """数据按日下载函数，本方法需要子类中具体实现

        Args:
            date (str): yyyyMMdd格式日期

        Returns:
            bool: 执行结果
        """
        return False

    def rebuild(self) -> bool:
        """ 重建环境 """
        return False

    def download_all(self, from_date: str = None, to_date: str = None, *args, **kwargs) -> bool:
        """存量数据下载函数，本方法需要子类中具体实现

        Args:
            from_date (str, optional): 数据下载开始日期（含）. Defaults to None，表示不指定.
            to_date (str, optional): 数据下载结束日期（含）. Defaults to None，表示不指定.

        Returns:
            bool: 执行结果
        """
        return False

    def query(self, date: str = None, start_date: str = None, end_date: str = None) -> UnitQueryResult:
        """查询下载情况

        Args:
            query_date (str, optional): 指定日期查询. Defaults to None.
            start_date (str, optional): 指定日期范围查询，开始日期. Defaults to None.
            end_date (str, optional): 指定日期范围查询，结束日期. Defaults to None.

        Returns:
            UnitQueryResult: [description]
        """
        return UnitQueryResult()

    def stat(self, mode: str = "ctrl", filepath: str = "stat.log", unitname: str = None, setname: str = None):
        """统计存量金融数据
        本接口函数需要子类继承

        Args:
            mode (str): 统计模式，ctrl表示从记录表中统计，table表示从实际数据表中统计. 默认为ctrl
            filepath (str): 导出文件路径，None表示不导出文件. 默认导出到 stat.log 中.
            unitname (str, optional): 指定单元名统计. 默认None，表示不指定.
            setname (str, optional): 指定单元套件统计. 默认None，表示不指定.

        Returns:
            UnitQueryResult: 统计结果
        """
        return None


class ConfigService:
    """ 配置文件服务 """

    def __init__(self, config_path: str = None, set_file_path: str = None):
        """初始函数

        Args:
            config_file_path (str, optional): 配置文件存放地址. Defaults to None，表示使用默认地址.
        """
        # 配置文件
        if not config_path:
            self.config_file_path = tl.get_server_cfg("dataunit.path")
        else:
            self.config_file_path = config_path
        # 套件配置文件
        if not set_file_path:
            self.set_file_path = tl.get_server_cfg("suite.path")
        else:
            self.set_file_path = set_file_path

    def get(self, unit_name: str) -> DataUnitConfig:
        """根据unit名返回配置内容

        如果读取错误或名称未找到，返回None

        Args:
            unit_name (str): 数据单元名

        Returns:
            DataUnitConfig: 配置信息
        """
        if not os.path.exists(self.config_file_path):
            tl.get_logger().error("数据单元配置文件无法找到！path=" + self.config_file_path)
            return None

        cfg_list = self.get_list()
        for cfg in cfg_list:
            if cfg.name == unit_name:
                return cfg
        return None

    def get_list(self) -> list:
        """根据全部Unit配置清单

        如果读取错误返回空列表

        Returns:
            list: 配置列表
        """
        if not os.path.exists(self.config_file_path):
            tl.get_logger().error("数据单元配置文件无法找到！path=" + self.config_file_path)
            return None

        try:
            unit_list = []
            with open(self.config_file_path, encoding='utf-8') as f:
                json_obj = json.loads(f.read())
                for name in json_obj:
                    obj = self._load(name, json_obj.get(name))
                    if obj:
                        unit_list.append(obj)
        except Exception as err:
            tl.get_logger().error("读取数据单元配置文件时出现格式问题")
            tl.get_logger().error(err)
        finally:
            return unit_list

    def _load(self, name, json) -> DataUnitConfig:
        """根据json字符串（或dict）加载成DataUnit对象

        Args:
            json (dict): 配置项目

        Returns:
            DataUnitConfig: 配置信息
        """
        cfg = DataUnitConfig(name)
        cfg.name = name
        cfg.class_path = json["class_path"]
        cfg.package_name = cfg.class_path[0: cfg.class_path.rfind(".")]
        cfg.class_name = cfg.class_path.split(".")[-1]

        # 存量
        stored_json = json["stored"]
        cfg.stored.rebuild = bool(stored_json["rebuild"])

        # 日增量
        daily_json = json["daily"]
        cfg.daily.windows = daily_json["running_windows"]["hours"]
        cfg.daily.only_run_in_trade_day = daily_json["running_windows"]["only_run_in_trade_day"]
        cfg.daily.only_once_in_day = daily_json["running_windows"]["only_once_in_day"]
        cfg.daily.sleep_time = int(daily_json["sleep_time"])

        return cfg

    def load_unit(self, unit_name: str) -> BaseDataUnit:
        """根据unit名，加载一个数据单元类

        Args:
            unit_name (str): [description]

        Returns:
            BaseDataUnit: [description]
        """
        cfg = self.get(unit_name)
        if cfg is None:
            tl.get_logger().error("无效的Unit名")
            return None
        else:
            try:
                module = importlib.import_module(cfg.package_name)
                cls = getattr(module, cfg.class_name)
                obj = cls(name=unit_name, config=cfg)
                return obj
            except ModuleNotFoundError as mnfe:
                print(cfg.package_name)
                print(cfg.class_name)
                tl.get_logger().error(
                    "加载对象失败，无法识别的类名，{err}".format(err=mnfe))
                return None
            except Exception as err:
                tl.get_logger().error(
                    "加载Unit对象失败，{err}".format(err=err))
                return None
        return None

    def _get_unit_name_by_set(self, set_name) -> list:
        """ 根据set_name返回配置名列表  """
        if not os.path.exists(self.set_file_path):
            tl.get_logger().error("数据套件配置文件无法找到！path=" + self.set_file_path)
            return []

        try:
            with open(self.set_file_path, encoding='utf-8') as f:
                json_obj = json.loads(f.read())
                return json_obj[set_name]
        except Exception as err:
            tl.get_logger().error("读取数据套件文件时出现格式问题")
            tl.get_logger().error(err)

    def _get_all_unit_name(self) -> list:
        """ 返回全部单元的名称 """
        if not os.path.exists(self.config_file_path):
            tl.get_logger().error("数据单元配置文件无法找到！path=" + self.config_file_path)
            return None

        try:
            name_list = []
            with open(self.config_file_path, encoding='utf-8') as f:
                json_obj = json.loads(f.read())
                for name in json_obj:
                    name_list.append(name)
        except Exception as err:
            tl.get_logger().error("读取数据单元配置文件时出现格式问题")
            tl.get_logger().error(err)
        finally:
            return name_list

    def load_by_set(self, set_name: str = None) -> list:
        """按套件加载

        Args:
            set_name (str, optional): [description]. Defaults to None，表示加载全部单元.

        Returns:
            list: [description]
        """
        # 读取套件
        if set_name:
            unit_name_list = self._get_unit_name_by_set(set_name)
        else:
            unit_name_list = self._get_all_unit_name()

        # 逐一加载对象
        unit_list = []
        for name in unit_name_list:
            unit = self.load_unit(unit_name=name)
            if unit:
                unit_list.append(unit)

        return unit_list


class UnitStatResult:
    """数据单元统计结果基类
    """

    def __init__(self, unit: BaseDataUnit):
        self._unit = unit


class DailyUnitStatResult(UnitStatResult):
    """日增型数据单元统计结果类
    """

    def __init__(self, unit: BaseDataUnit):
        super().__init__(unit)
        self.start_date = None      # 数据开始日期
        self.end_date = None        # 数据结束日期
        self.days_count = 0         # 总天数
        self.lack_days_count = 0    # 缺失天数
        self.lack_days = []         # 缺失日期明细
        self.record_count = 0       # 总记录数
        self.last_modifed = None    # 最后更新日期

    def __str__(self):
        """返回一个对象的描述信息"""
        str = ""
        if self._unit:
            str += "\n" + self._unit.name + "\n"
        str += "记录数量: {0}".format(self.record_count) + "\n"
        return str


class FixedUnitStatResult(UnitStatResult):
    """全量型数据单元统计结果类
    """

    def __init__(self, unit: BaseDataUnit):
        super().__init__(unit)
        self.record_count = 0       # 总记录数
        self.last_modifed = None    # 最后更新日期

    def __str__(self):
        """返回一个对象的描述信息"""
        str = ""
        if self._unit:
            str += "\n" + self._unit.name + "\n"
        str += "记录数量: {0}".format(self.record_count) + "\n"
        return str
