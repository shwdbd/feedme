#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   dt_model.py
@Time    :   2024/01/24 14:35:23
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   数据处理 模型
'''
from abc import ABC, abstractmethod
import importlib
from com.wdbd.fd.common.tl import get_action_logger, Result
from loguru import logger
import sys

SERVER_STAUTS_SHUNDOWN = "SHUNDOWN"     # 已关闭

SERVER_STAUTS_OPEN = "OPEN"             # 运行中

SERVER_STAUTS_CLOSING = "CLOSING"       # 关闭中

# Action专用Logger是否被设置
HAS_ACTION_LOGGER = None


# 动作组配置对象
class ActionGroup:
    """动作组配置对象"""

    # Action出错后的处理模式
    CONTINUE = "continue"  # 继续执行
    BREAK = "break"  # 中断执行

    # Group执行状态
    RUNNING = '1'
    SUCCESS = '9'
    FAILED = '4'

    def __init__(self) -> None:
        self.name = ""
        self.desc = ""
        self.parameters = {
            "run_windows": [],   # 时间窗口
            "interval_time": 30,     # 间隔时间（分钟）
            "on_error": ActionGroup.CONTINUE  # Action出错后的处理模式，有continue和break两种模式可选择
        }
        self.p = self.parameters
        self.actions = {}   # 动作

    def set_onerr_mode(self, mode: str) -> None:
        self.parameters["on_error"] = mode

    def get_onerr_mode(self) -> list:
        """ 返回 Action出错后的处理模式 """
        return self.p["on_error"]

    def get_interval_minutes(self) -> list:
        """ 返回 间隔时间（分钟） """
        # return self.p["interval_time"]
        # 判断如果有符号，则先进行转换
        t = self.p["interval_time"]
        if type(t) == str and ("s" in t or "h" in t or "m" in t):
            self.p["interval_time"] = self._convert_2_mintues(t)
        return self.p["interval_time"]

    def _convert_2_mintues(self, t) -> float:
        """ 将 时间字符串 转换成 分钟的数字 """
        if type(t) == str:
            if t[-1:] == 'm':   # 分钟
                return int(t[:-1])
            elif t[-1:] == 'h':     # 小时
                return int(t[:-1])*60
            elif t[-1:] == 's':     # 秒
                return int(t[:-1])/60
            else:
                return self.p["interval_time"]
        else:
            return t

    def get_windows(self) -> list:
        """ 返回Group的时间窗口 """
        if isinstance(self.p["run_windows"], list):
            return self.p["run_windows"]
        else:
            return []

    def set_interval_minutes(self, t: int) -> None:
        """ 设置间隔时间（分钟）
        """
        # 根据传入参数（str）判断，这算成分钟
        if type(t) == str:
            self.p["interval_time"] = self._convert_2_mintues(t)
        elif type(t) == int:
            self.p["interval_time"] = t
        else:
            pass

    def set_windows(self, win: list) -> None:
        """ 设置运行窗口
        如果为空，则设置None
        """
        self.p["run_windows"] = win

    def append_action(self, action) -> None:
        """ 增加Action """
        self.actions[action.name] = action
        # self.actions.append(action)

    def __str__(self) -> str:
        return "{n}| Group . Action数量({an})".format(n=self.name, an=len(self.actions))


# 动作配置对象
class ActionConfig:
    """动作配置对象"""

    # Group执行状态
    RUNNING = '1'
    SUCCESS = '9'
    FAILED = '4'

    def __init__(self, group: ActionGroup = None) -> None:
        self.group = group
        self.class_url = ""
        self.name = ""
        self.desc = ""
        self.parameters = {
            "run_windows": [],
            "daily_once": True
        }
        self.p = self.parameters

    def get_package(self):
        """ 返回类模块的名称，如： com.xxx.yyy """
        return self.class_url[: self.class_url.rfind(".")]

    def get_classname(self):
        """ 返回类的名称，如：MyClass """
        return self.class_url.split(".")[-1]

    def get_group(self):
        """ 返回所属ActionGroup对象 """
        return self.group

    def get_windows(self) -> list:
        """ 返回Action的时间窗口 """
        return self.p["run_windows"]

    def set_windows(self, win) -> list:
        """ 设置Action的时间窗口 """
        self.p["run_windows"] = win

    def get_once_on_day(self) -> list:
        """ 返回Action的是否一天只执行一次 """
        return self.p["daily_once"]

    def set_once_on_day(self, is_once) -> list:
        """ 设置Action的是否一天只执行一次 """
        self.p["daily_once"] = is_once

    def check_classname(self) -> bool:
        """ 检查类名是否有效 """
        try:
            # 实例化Action对象
            module = importlib.import_module(self.get_package())
            getattr(module, self.get_classname())()      # 对象实例化
            return True
        except Exception:
            return False

    def __str__(self) -> str:
        return "ACTION {n}".format(n=self.name)


# 抽象数据操作类
class AbstractAction(ABC):
    """ 抽象数据操作类 """

    def __init__(self) -> None:
        """
        初始化函数，用于初始化类的实例。

        Args:
            无

        Returns:
            None
        """
        self.parameters = {
            "windows": [],
            "once_on_day": True
        }
        self.p = self.parameters
        self.name = None        # Action名
        # 设置专用的Action日志器
        self.init_action_logger(self.name)

    def init_action_logger(self, name):
        """ 初始化Action日志 """
        global HAS_ACTION_LOGGER
        if HAS_ACTION_LOGGER is None:
            logger.remove()
            # 初始化日志配置
            logger.add(sys.stderr, level="DEBUG", format="{time:MM-DD HH:mm:ss} 【{extra[action_name]}】 - {message}", filter=lambda x: "action_name" in x["extra"])
            # 日志文件名不能使用bind的变量，
            logger.add("log\\Action_日志.log", level="INFO", rotation="8:00", format="{time:YYYY-MM-DD HH:mm:ss} 【{extra[action_name]}】 - {message}", filter=lambda x: "action_name" in x["extra"])
            HAS_ACTION_LOGGER = "YES"
        self.log = logger.bind(action_name=self.name)   # 参数绑定

    def set_action_parameters(self, action_cfg: ActionConfig) -> None:
        # 赋值Action配置参数传入
        self.name = action_cfg.name
        self.log = get_action_logger(action_name=self.name)
        self.parameters = action_cfg.parameters
        self.p = self.parameters
        # 再绑定一次logger
        self.log = logger.bind(action_name=self.name)   # 参数绑定

    @abstractmethod
    def check_environment(self) -> Result:
        """检查环境，检查当前是否可以进行数据下载

        通常子类中会检查需要下载的数据是否已准备好
        Returns:
            bool: 检查结果
        """
        return False

    @abstractmethod
    def handle(self) -> Result:
        """数据处理函数，子类必须实现

        Returns:
            bool: 执行结果
        """
        pass

    @abstractmethod
    def rollback(self) -> Result:
        """错误发生时，回滚动作函数

        Returns:
            bool: 回滚操作执行结果
        """
        return True


# if __name__ == "__main__":
#     # 实例化 Action
#     action = AbstractAction()
#     # Action赋值
#     cfg = ActionConfig()
#     action.set_action_parameters(cfg)
