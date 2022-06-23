#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   server_status.py
@Time    :   2021/04/19 10:55:24
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   表server_status的服务接口
'''
import gtp.fd.common as tl


class ServerStatus:
    """server_status 表操作
    """

    # 服务器状态常数
    STATUS_STOP = 0     # 停止
    STATUS_RUNNING = 1  # 运行中
    STATUS_CLOSING = 2  # 停止中

    def get(self) -> int:
        """返回服务器状态

        Returns:
            int: 服务器状态代码
        """
        try:
            db = tl.get_mgdb()

            server_status = db.server_status.find_one()
            if not server_status:
                server_status = db["server_status"]
                server_status.insert_one(
                    {"status": ServerStatus.STATUS_STOP, "start_time": "", "end_time": ""})
                return ServerStatus.STATUS_STOP
            else:
                return server_status["status"]
        except Exception as err:
            tl.get_logger().error(
                "判断服务器状态时出现异常，异常情况 = {0}".format(err))
            return None

    def update(self, status, start_time=None, end_time=None):
        """ 表内容更新 """
        cx = tl.get_mgconn()
        db = tl.get_mgdb()
        session = cx.start_session()
        session.start_transaction()
        try:
            data = {"status": status}
            if start_time:
                data["start_time"] = start_time
            if end_time:
                data["end_time"] = end_time
            db.server_status.update_one({}, {"$set": data})
        except Exception as err:
            tl.get_logger().error("SQL ERR: " + str(err))
            session.abort_transaction()
        else:
            session.commit_transaction()
        finally:
            session.end_session()

    def start(self):
        # 设置服务状态为 启动
        self.update(status=ServerStatus.STATUS_RUNNING, start_time=tl.now())

    def shundown(self):
        # 设置服务状态为 关闭中
        self.update(status=ServerStatus.STATUS_CLOSING)

    def stop(self):
        # 设置服务状态为 关闭
        self.update(status=ServerStatus.STATUS_STOP, end_time=tl.now())


# if __name__ == "__main__":
#     srv = ServerStatus()
#     # print(type(srv.get()))
#     # print(srv.get())
#     # srv.start()
#     # print(srv.get())
#     print(srv.shundown())
