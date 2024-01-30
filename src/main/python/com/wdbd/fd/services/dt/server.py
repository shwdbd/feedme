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
from abc import ABC, abstractmethod
from com.wdbd.fd.common.tl import get_logger, get_config_dir, Result, now
import importlib
from com.wdbd.fd.model.db.db_services import start_dtserver, shundown_server, get_server_status, log_group, log_new_action, log_action
import time
from com.wdbd.fd.model.dt_model import ActionConfig, ActionGroup, SERVER_STAUTS_CLOSING
import datetime


# 接口：数据处理服务器引擎
class DTEngine(ABC):
    """ 接口：数据处理服务器引擎 """

    def __init__(self, groups: list) -> None:
        """引擎初始化

        Args:
            groups (list): 待运行的ActionGroup列表
        """
        super().__init__()
        self.threads = {}       # 线程池
        self.groups = groups    # 传入ActionGroup的list

    @abstractmethod
    def start(self) -> Result:
        """数据服务器启动
        """
        return None

    @abstractmethod
    def shundown(self) -> Result:
        """数据服务器停止
        """
        return None


# 基础服务引擎
class BasicEngine(DTEngine):
    """ 基础服务引擎 """

    def start(self) -> Result:
        """数据服务器启动
        """
        get_logger().info("=" * 20)
        get_logger().info("数据处理服务引擎启动 ... ")
        get_logger().info("动作组(ActionGroup)数量: {0} 组".format(len(self.groups)))
        for idx, group in enumerate(self.groups, start=1):
            get_logger().info("{idx} | 动作组: ({gourp_name})中Action数量: {count} 组".format(idx=idx, gourp_name=group.name, count=len(group.actions)))
        get_logger().info("-" * 20)

        # 登记服务状态
        res = start_dtserver()
        if not res or res.result is False:
            # 服务无法启动
            get_logger().error("服务无法启动！" + str(res.msg))
        else:
            # 服务正常启动
            # 为每一个Group新建一个线程
            for group in self.groups:
                params = {"group": group}
                t = threading.Thread(target=self._start_group_threads, name=group.name, kwargs=params)
                self.threads[group.name] = t  # 注册线程
                t.start()
            get_logger().info("{0}个线程已创建，服务已成功启动！".format(len(self.groups)))
        get_logger().info("=" * 20)

        return None

    # 执行Group线程
    def _start_group_threads(self, group, _test_mode: bool = False):
        """ 执行单个Group进程

        Args:
            group (ActionGroup): 动作组
        """
        # EFFECTS:
        # 1. 检查执行时机，比如是否在执行窗口等
        # 2. 登记 group 日志
        # 3. 依次执行Action，前后登记Action日志
        # 4. 登记 group 日志
        # 5. 检查是否服务关闭？
        # 6. sleep等待时间
        # END

        test_loop_time = 1  # 测试模式下循环次数

        # 日志头
        log = get_logger()
        LOG_G = "【{group_name}】".format(group_name=group.name)

        while (test_loop_time > 0 and True):
            if _test_mode:
                test_loop_time = test_loop_time - 1
        
            # TODO 判断服务器状态，如果是停止中，则退出循环
            server_status = get_server_status()
            if server_status == SERVER_STAUTS_CLOSING:
                # TODO 判断如果是最后一个线程，则更新服务状态，否则继续
                # 退出循环，删除线程池中
                del self.threads[group.name]
                break

            # 开始执行本次处理
            log.info("== {T} == ".format(T=LOG_G) + "-"*20)
            log.info("{T}开始执行".format(T=LOG_G))
            log.info("{T} Actions".format(T=LOG_G))
            # 登记Group日志
            group_log_id = log_group(group=group)
            # 记住并返回group的日志id
            log.info("依次执行{0}个Action".format(len(group.actions)))
            for action_idx, action_name in enumerate(group.actions):
                action = group.actions.get(action_name)
                LOG_A = "【{g}|{a}】".format(g=group.name, a=action.name)
                try:
                    # 实例化Action对象
                    module = importlib.import_module(action.get_package())
                    action_obj = getattr(module, action.get_classname())()      # 对象实例化
                    action_obj.set_action_parameters(action)
                except Exception:
                    log.error("{T} {name} 的实例 {clz} 无法实例化！".format(T=LOG_A, name=action.name, clz=action.class_url))
                    if group.get_onerr_mode() == ActionGroup.BREAK:
                        log.error("Group {name} 执行终止！".format(name=group.name))
                        break
                    else:
                        continue
                # 执行Action
                try:
                    # TODO 登记Action日志
                    # TODO 要加入 Action执行的数据日期
                    action_log_id = log_new_action(action_obj, group_log_id=group_log_id, group_name=group.name)
                    # 检查运行环境
                    res = action_obj.check_environment()
                    if res.result is False:
                        log.error("{T}环境监测结果为失败！原因 = {msg}".format(T=LOG_A, msg=res.msg))
                        log_action(action_log_id=action_log_id, result=False, msg=res.msg)
                        if group.get_onerr_mode() == ActionGroup.BREAK:
                            continue    # 执行下一个Action
                    else:
                        # 判断是否在执行窗口中
                        if ServerUtils.is_in_action_windows(action.get_windows()) is False:
                            log.error("{T}不在可执行的时间窗内内！窗口 = {win} | Now = {now}".format(T=LOG_A, win=action.get_windows(), now=now()))
                        else:
                            # 执行Action动作
                            try:
                                res = action_obj.handle()
                                if res is not None and res.result:
                                    log_action(action_log_id=action_log_id, result=True, msg="")
                                else:
                                    log_action(action_log_id=action_log_id, result=False, msg=res.msg)
                                    if group.get_onerr_mode() == ActionGroup.BREAK:
                                        log.error("{T} 错误，并终止执行后续步骤".format(T=LOG_A))
                                        break
                            except Exception:
                                print('Action执行中出现问题')
                except Exception as err:
                    # FIXME 针对无法实例化的问题，需要进行特殊处理
                    # FIXME 针对执行错误，进行日志登记
                    log_action(action_log_id=action_log_id, result=False, msg=str(err))
                    print('Action运行 occurred', str(err))

            # 线程等待
            log.info("Group {n} 等待{0}分钟".format(group.get_interval_minutes(), n=group.name))
            time.sleep(group.get_interval_minutes() * 60)
            log.info("== {T} == ".format(T=LOG_G) + "-"*20)

            # 登记Group日志(END)
            log_group(group=group, result=True)

        print("{T}Group {n}线程结束".format(T=LOG_G, n=group.name))

    def shundown(self) -> Result:
        """数据服务器停止
        """
        # EFFECTS:
        # 1. 更新 comm_server 数据库表
        # END
        
        res = shundown_server()
        return res
        
        # # TODO Group线程的销毁，应该移动到shundown函数中
        # for t in self.threads:
        #     # print(t.is_alive())
        #     t.join()
        #     print("线程{n} joined ".format(n=t))


# 服务器工具类
class ServerUtils:
    """ 工具类 """

    @staticmethod
    def load_group(group_context: dict) -> ActionGroup:
        """ 根据配置项，解析返回一个ActionGroup对象 """
        # 组装ActionGroup
        if not group_context or type(group_context) is not dict:
            return None

        group = ActionGroup()
        group.name = group_context.get("name")
        group.desc = group_context.get("desc")
        # Group rules 规则
        for rule_name in group_context.get("rules"):
            group.parameters[rule_name] = group_context.get("rules").get(rule_name)

        # 组装Actions
        for action_name in group_context["actions"]:
            action_tag = group_context["actions"][action_name]

            action = ActionConfig(group=group)
            action.name = action_name
            action.class_url = action_tag.get("class")
            # 检查class是否有效
            if action.check_classname() is False:
                get_logger().error("Action {name} 的类{c}无法正确识别！，配置文件读取错误".format(name=action.name, c=action.class_url))
                return None
            # Group rules 规则
            for rule_name in group_context.get("rules"):
                action.parameters[rule_name] = group_context.get("rules").get(rule_name)
            group.append_action(action)

        return group

    @staticmethod
    def load_config_file(file_path: str = None) -> list:
        """ 读取单一解析配置文件

        Args:
            file_path (str): _description_

        Returns:
            ActionGroup: _description_
        """
        if file_path is None or not os.path.exists(file_path):
            DEFAULT_CONFIG_DIR = os.path.join(get_config_dir(), "DEFAULT_ACTION_GROUP.json")
            get_logger().info("默认配置文件: " + DEFAULT_CONFIG_DIR)
            file_path = DEFAULT_CONFIG_DIR
            # src\main\config\DEFAULT_ACTION_GROUP.json

        # 文件不存在，直接返回None
        if os.path.exists(file_path) is False:
            get_logger().error("ActionGroup配置文件未能找到")
            return None

        with open(file_path, encoding='utf-8') as f:
            try:
                jason_data = json.loads(f.read())
                result = []     # 返回值
                for group_name in jason_data.keys():
                    group = ServerUtils.load_group(jason_data.get(group_name))
                    if group:
                        result.append(group)
                    else:
                        get_logger().error("配置文件读取失败！")
                        return None
                return result
            except Exception as err:
                get_logger().error('读取ActionGroup定义文件失败, {err}, file : {f} '.format(err=str(err), f=file_path))
                return None

    # 判断时间是否在窗口内
    @staticmethod
    def is_in_action_windows(windows: list, _test_time: str = None) -> bool:
        """判断当前时间是否在Action的运行窗口内

        Args:
            windows (list): 时间窗口
            _test_time (str, optional): 测试用时间窗口. Defaults to None.

        Returns:
            bool: 判断结果
        """
        if windows is None or len(windows) == 0:
            return True

        if _test_time is None:
            TIME_VIEW_FORMAT = "%H%M"
            t = datetime.datetime.now().strftime(TIME_VIEW_FORMAT)
            t = now()
        else:
            t = _test_time
        for win_item in windows:
            # ["0900", "103000"]
            print(win_item)
            if t > win_item[0] and t < win_item[1]:
                return True
        return False


class DTServer:
    """服务器"""

    @staticmethod
    def getConfigFileEngine(file_name: str = None) -> DTEngine:
        """ 根据配置文件组建数据引擎

        如果发生问题，则返回None

        Args:
            file_name (str or list): 文件名或文件名的列表，类似：akshare_daily.json

        Returns:
            DTEngine: 生成的引擎
        """
        # TODO 补充实现的文档
        gorups = []
        if type(file_name) == list:
            for f in file_name:
                gorups.append(ServerUtils.load_config_file(f))
        else:
            res = ServerUtils.load_config_file(file_name)
            if res is None:
                get_logger().error("读取ActionGroup配置文件失败，引擎启动终止! ")
                return None
            else:
                gorups = res
        return BasicEngine(groups=gorups)

    @staticmethod
    def shundown():
        """ 关闭服务器 """
        res = shundown_server()
        get_logger().info("服务器已关闭")
        return res

    # def _in_time_windows(self, time_windows: list, _now_time: str = None) -> bool:
    #     """判断当前时间是否在时间窗口内

    #     Args:
    #         time_windows (list): _description_
    #         _now_time (str, optional): _description_. Defaults to None.

    #     Returns:
    #         bool: _description_
    #     """
    #     # TODO 待实现
    #     return False
