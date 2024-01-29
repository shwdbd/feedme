#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   config.py
@Time    :   2023/12/29 10:02:37
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   数据运行配置
'''
from abc import ABC, abstractmethod
from com.wdbd.fd.common.tl import get_action_logger


# # 动作组配置对象
# class ActionGroup:
#     """动作组配置对象"""
#     # Action出错后的处理模式
#     CONTINUE = "continue"  # 继续执行
#     BREAK = "break"  # 中断执行

#     def __init__(self) -> None:
#         self.name = ""
#         self.desc = ""
#         self.parameters = {
#             "windows": [],   # 时间窗口
#             "interval_minutes": 30,     # 间隔时间（分钟）
#             "on_err": ActionGroup.CONTINUE  # Action出错后的处理模式，有continue和break两种模式可选择
#         }
#         self.p = self.parameters
#         self.actions = {}   # 动作

#     def set_onerr_mode(self, mode: str) -> None:
#         self.parameters["on_err"] = mode

#     def get_onerr_mode(self) -> list:
#         """ 返回 Action出错后的处理模式 """
#         return self.p["on_err"]

#     def get_interval_minutes(self) -> list:
#         """ 返回 间隔时间（分钟） """
#         return self.p["interval_minutes"]

#     def get_windows(self) -> list:
#         """ 返回Group的时间窗口 """
#         if isinstance(self.p["windows"], list):
#             return self.p["windows"]
#         else:
#             return []

#     def set_interval_minutes(self, t: int) -> None:
#         """ 设置间隔时间（分钟）
#         """
#         self.p["interval_minutes"] = t

#     def set_windows(self, win: list) -> None:
#         """ 设置运行窗口
#         如果为空，则设置None
#         """
#         self.p["windows"] = win

#     def append_action(self, action) -> None:
#         self.actions[action.name] = action
#         # self.actions.append(action)

#     def __str__(self) -> str:
#         return "{n}| Group . Action数量({an})".format(n=self.name, an=len(self.actions))


# # 动作配置对象
# class Action:
#     """动作配置对象"""
#     def __init__(self, group: ActionGroup = None) -> None:
#         self.group = group
#         self.class_url = ""
#         self.name = ""
#         self.desc = ""
#         self.parameters = {
#             "windows": [],
#             "once_on_day": True
#         }
#         self.p = self.parameters

#     def get_package(self):
#         """ 返回类模块的名称 """
#         return self.class_url[: self.class_url.rfind(".")]

#     def get_classname(self):
#         """ 返回类的名称 """
#         return self.class_url.split(".")[-1]

#     def get_group(self):
#         return self.group

#     def get_windows(self) -> list:
#         """ 返回Action的时间窗口 """
#         return self.p["windows"]

#     def get_once_on_day(self) -> list:
#         """ 返回Action的是否一天只执行一次 """
#         return self.p["once_on_day"]

#     def __str__(self) -> str:
#         return "ACTION {n}".format(n=self.name)


# # 抽象数据操作类
# class AbstractAction(ABC):
#     """ 抽象数据操作类 """

#     def __init__(self) -> None:
#         self.parameters = {
#             "windows": [],
#             "once_on_day": True
#         }
#         self.p = self.parameters
#         self.name = None        # Action名
#         # 专用的Action日志器
#         self.log = None

#     def set_action_parameters(self, action_cfg: Action) -> None:
#         # 赋值Action配置参数传入
#         self.name = action_cfg.name
#         self.log = get_action_logger(action_name=self.name)
#         self.parameters = action_cfg.parameters
#         # print(action_cfg.parameters)
#         # print(self.parameters)
#         self.p = self.parameters

#     @abstractmethod
#     def check_environment(self) -> bool:
#         """检查环境，检查当前是否可以进行数据下载

#         通常子类中会检查需要下载的数据是否已准备好
#         Returns:
#             bool: 检查结果
#         """
#         return False

#     @abstractmethod
#     def handle(self) -> bool:
#         """数据处理函数，子类必须实现

#         Returns:
#             bool: 执行结果
#         """
#         pass

#     @abstractmethod
#     def rollback(self) -> bool:
#         """错误发生时，回滚动作函数

#         Returns:
#             bool: 回滚操作执行结果
#         """
#         return True
