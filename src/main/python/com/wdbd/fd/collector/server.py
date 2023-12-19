#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   server.py
@Time    :   2023/12/15 10:59:08
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   FD数据处理服务器相关代码
'''
import os
import json
import threading
import time


# 抽象数据操作类
class AbstractAction:
    """ 抽象数据操作类 """

    def __init__(self) -> None:
        self.parameters = {
            "windows": [],
            "once_on_day": True
        }

    def handle(self) -> bool:
        """数据处理函数，子类必须实现

        Returns:
            bool: 执行结果
        """
        pass

    def rollback(self) -> bool:
        """错误发生时，回滚动作函数

        Returns:
            bool: 回滚操作执行结果
        """
        return True


# 动作组配置对象
class ActionGroup:
    """动作组配置对象"""

    def __init__(self) -> None:
        self.name = ""
        self.desc = ""
        self.parameters = {
            "windows": []   # 时间窗口
        }
        self.p = self.parameters
        self.actions = {}   # 动作

    def get_windows(self) -> list:
        """ 返回Group的时间窗口 """
        if isinstance(self.p["windows"], list):
            return self.p["windows"]
        else:
            return []

    def set_windows(self, win: list) -> None:
        """ 设置运行窗口
        如果为空，则设置None
        """
        self.p["windows"] = win

    def append_action(self, action) -> None:
        self.actions[action.name] = action
        # self.actions.append(action)

    def __str__(self) -> str:
        return "{n}| Group . Action({an})".format(n=self.name, an=len(self.actions))


# 动作配置对象
class Action:
    """动作配置对象"""
    def __init__(self, group: ActionGroup = None) -> None:
        self.group = group
        self.name = ""
        self.desc = ""
        self.parameters = {
            "windows": [],
            "once_on_day": True
        }
        self.p = self.parameters

    def get_group(self):
        return self.group

    def get_windows(self) -> list:
        """ 返回Action的时间窗口 """
        return self.p["windows"]

    def get_once_on_day(self) -> list:
        """ 返回Action的是否一天只执行一次 """
        return self.p["once_on_day"]

    def __str__(self) -> str:
        return "ACTION {n}".format(n=self.name)


class DTServer:
    """服务器相关功能"""

    def open_action_group(self, group: ActionGroup) -> bool:
        print("Group {n} 开始运行 ... ")
        time.sleep(10)
        return False
        

    def start(self, group_id: list = None, group_obj: list = None, group_file_path: list = None) -> None:
        """数据下载服务器启动

        需要启动的动作组可以通过三种方式配置：
        1. 读取数据库配置，使用group_id参数，其中id使用数据库中存放的group_id；
        2. 外部配置传入，使用group_obj参数，提供json配置的列表；
        3. 通过读取配置文件方式，使用 group_file_path 参数。提供 \\group_config目录下的配置文件名列表

        Args:
            group_id (list, optional): 读取数据库模式，组id的列表. Defaults to None，表示不采用这种模式.
            group_obj (list, optional): 外部传入模式，json配置的列表. Defaults to None，表示不采用这种模式.
            group_file_path (list, optional): 配置文件模式。提供 \group_config目录下的配置文件名列表. Defaults to None，表示不采用这种模式.
        """
        if group_obj:
            action_groups = group_obj
        # FIXME 如果三个参数都么有提供，则报错
        
        
        # TODO 待实现
        print("Server running ... ")

        # TODO 登记服务状态
        
        # TODO 判断服务是否能启动（如已在启动中，则无法再启动）
        
        # 为每一个Group新建一个线程
        threads = []    # 线程的集合
        for group in action_groups:
            t = threading.Thread(target=self.open_action_group, args=(action_groups), name=group.name)
            threads.append(t)
            t.start()

        for t in threads:
            # print(t.is_alive())
            t.join()
            print("线程{n} joined ".format(n=t))


    def _in_time_windows(self, time_windows: list, _now_time: str = None) -> bool:
        """判断当前时间是否在时间窗口内

        Args:
            time_windows (list): _description_
            _now_time (str, optional): _description_. Defaults to None.

        Returns:
            bool: _description_
        """
        # TODO 待实现
        return False

    def _load_group_define_file(self, file_path: str) -> ActionGroup:
        """读取 动作组 配置文件

        如果出错，则不抛出异常，返回None

        Args:
            file_path (str): 相对路径，或绝对路径

        Returns:
            ActionGroup: 加载得到的动作组对象
        """
        if not os.path.exists(file_path):
            # 当前目录下的group_config目录
            DEFAULT_CONFIG_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "group_config")
            file_path = os.path.join(DEFAULT_CONFIG_DIR, file_path)

        # 文件不存在，直接返回None
        if not os.path.exists(file_path):
            return None

        with open(file_path, encoding='utf-8') as f:
            try:
                jason_data = json.loads(f.read())
                # 组装ActionGroup
                group = ActionGroup()
                group.name = jason_data.get("name")
                group.desc = jason_data.get("desc")
                group.set_windows(jason_data.get("run_windows"))
                # 组装Actions
                for action_name in jason_data["actions"]:
                    action_tag = jason_data["actions"][action_name]
                    action = Action(group=group)
                    action.name = action_name
                    for tag in action_tag:
                        if tag.lower() == 'desc':
                            action.desc = action_tag.get("desc")
                        elif tag.lower() == 'run_windows':
                            action.p["windows"] = action_tag.get("run_windows")
                        elif tag.lower() == 'daily_once':
                            action.p["once_on_day"] = bool(action_tag.get("daily_once"))
                        else:
                            action.p[tag] = action_tag.get(tag)
                    group.append_action(action)
                return group
            except Exception as err:
                print('Something went wrong, ', str(err))   # FIXME 改为日志输出
                return None


if __name__ == "__main__":
    # # 读取ActionGroup配置文件
    # ser = DTServer()
    # res = ser._load_group_define_file("开发测试用.json")
    # print(res)
    # print(res.p)
    # print(res.parameters)
    # # for act in res.actions:
    # #     print(act)
    
    # 启动服务
    ser = DTServer()
    res = ser.start(group_obj=[ser._load_group_define_file("开发测试用.json")])
    print(res)
