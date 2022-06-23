#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   dlserver.py
@Time    :   2021/08/13 13:02:12
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   数据下载服务器代码
'''
import time
import gtp.fd.base.base as base
import gtp.fd.common as tl
from gtp.fd.base.mg_dao.server_status import ServerStatus


class DLServer:
    """数据下载服务器
    """

    # 服务器状态常数
    STATUS_STOP = ServerStatus.STATUS_STOP     # 停止
    STATUS_RUNNING = ServerStatus.STATUS_RUNNING  # 运行中
    STATUS_CLOSING = ServerStatus.STATUS_CLOSING  # 停止中

    def __init__(self, set_name: str = None, *args, **kwargs):
        """初始函数

        Args:
            set_name (str, optional): 套件名. Defaults to None，表示执行默认全部步骤.
        """
        # 读取数据下载单元
        cfg_srv = base.ConfigService()
        self.unit_list = cfg_srv.load_by_set(set_name)
        tl.get_logger().debug(
            "完成读取数据单元信息，单元数量={0}".format(len(self.unit_list)))

    def can_start(self) -> bool:
        """检查服务器是否可启动

        如状态不是0停止则不能启动，说明后后台服务正在运行

        Returns:
            boolean: 服务器是否可启动
        """
        ss_dao = ServerStatus()
        try:
            server_status = ss_dao.get()
            if server_status in [DLServer.STATUS_STOP]:
                return True
            else:
                tl.get_logger().debug(
                    "当前服务器状态为{0}，不能重新启动服务".format(server_status))
                return False
        except Exception as err:
            tl.get_logger().error(
                "判断服务器状态时出现异常，默认无服务不允许启动，异常情况 = {0}".format(err))
            return False

    def start(self) -> bool:
        """下载服务启动
        """

        log = tl.get_logger()
        ss_dao = ServerStatus()

        # 打印待执行的步骤名称
        tl.get_logger().info("-"*20)
        tl.get_logger().info("总步骤数量 = {0}".format(len(self.unit_list)))
        for idx, unit in enumerate(self.unit_list):
            tl.get_logger().info(
                '{i}. {name}'.format(i=(idx+1), name=unit.name))
        tl.get_logger().info("-"*20)

        # 检查服务状态是否可启动服务？
        if not self.can_start():
            log.error("服务器启动失败，目前有后台服务运行中")
            return False

        log.info("数据下载服务开始启动")
        self.thead_pool = []    # 线程池

        # 更新server_status数据库表
        ss_dao.start()

        count_unit = len(self.unit_list)
        log.info("数据单元总数 : {0}".format(count_unit))
        for idx, unit in enumerate(self.unit_list):
            self.thead_pool.append(unit)
            unit.start()
            log.info("[{idx}/{count}] 数据单元 {name} 启动".format(idx=idx +
                                                             1, count=count_unit, name=unit.name))
        log.info("线程合计 = {0}".format(len(self.thead_pool)))
        log.info("主线程等待({0}秒) ... ".format(tl.get_server_cfg("server.sleep")))
        time.sleep(int(tl.get_server_cfg("server.sleep")))   # 从配置文件中读取等待时间

        for t in self.thead_pool:
            t.join()
        log.info("数据下载服务关闭！")

        return True

    def shutdown(self) -> bool:
        """关闭数据下载服务

        此处只是发出一个指令，后台收到指令后会逐一等待运行中的下载单元完成，最后才全部关闭
        """
        ss_dao = ServerStatus()
        status_flag = ss_dao.get()
        if status_flag != ServerStatus.STATUS_RUNNING:
            tl.get_logger().error(
                "数据下载服务状态错误，无法关闭（状态码={0}）".format(status_flag))
        ss_dao.shundown()
        tl.get_logger().info("数据下载服务开始关闭，请等待运行中的DataUnit执行完毕")
        return True


if __name__ == "__main__":
    # 服务器启动
    srv = DLServer()
    srv.start()

    # 服务器停止
