#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   dataunit_status.py
@Time    :   2021/04/19 19:46:56
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   表 dataunit_status 的服务接口
'''
import gtp.fd.common as tl
import pymongo


class DataUnitStatus:
    """ 对照dataunit_status表 """

    RUNNING = 1         # 运行中
    DONE = 9            # 完成
    FAILED = 4          # 失败

    def __init__(self):
        self.unit_name = ""
        self.date = ""
        self.bid = 1
        self.start_time = ""
        self.end_time = ""
        self.status = ""
        self.note = ""


class DataUnitStatusDAO:

    # INIT = 0            # 未开始
    RUNNING = 1         # 运行中
    DONE = 9            # 完成
    FAILED = 4          # 失败

    def get(self, unit_name: str, date: str, bid: int = None) -> int:
        """ 取得当前的步骤状态（返回最新一次的记录） """
        # FIXME bid参数没有起到作用
        try:
            db = tl.get_mgdb()

            sql = {"$and": [{"unit_id": unit_name}, {"date": date}]}
            if bid is not None:
                sql["$and"].append({"bid": bid})
            if db.dataunit_status.count_documents(sql) == 0:
                return None
            else:
                records = db.dataunit_status.find(
                    sql).sort([("bid", pymongo.DESCENDING)]).limit(1)
                for doc in records:
                    return doc["status"]
        except Exception as err:
            tl.get_logger().error(
                "判断数据下载单元状态时出现异常，异常情况 = {0}".format(err))
            return None

    def _next_bid(self, unit_name, date):
        try:
            db = tl.get_mgdb()

            where_sql = {"$and": [{"unit_id": unit_name}, {"date": date}]}
            records = db.dataunit_status.aggregate([{"$match": where_sql},
                                                    {"$group": {
                                                        "_id": None, "max": {"$max": "$bid"}
                                                    }
            }
            ])
            for doc in records:
                return int(doc["max"]) + 1
            return 1
        except Exception as err:
            tl.get_logger().error(
                "异常情况 = {0}".format(err))
            return 1

    def new(self, unit_name: str, date: str):
        """ 新登记 """
        cx = tl.get_mgconn()
        db = tl.get_mgdb()
        session = cx.start_session()
        session.start_transaction()
        try:
            bid = self._next_bid(unit_name, date)
            data = {
                "unit_id": unit_name, "date": date,
                "bid": bid, "start_time": tl.today(), "end_time": "", "status": DataUnitStatus.RUNNING, "note": ""
            }
            db.dataunit_status.insert_one(data)
        except Exception as err:
            tl.get_logger().error("SQL ERR: " + str(err))
            session.abort_transaction()
        else:
            session.commit_transaction()
        finally:
            session.end_session()

    def done(self, unit_name: str, date: str) -> bool:
        """ 新登记 """
        # RUNNING->DONE
        return self.__change_status(unit_name, date, DataUnitStatus.DONE)

    def __change_status(self, unit_name: str, date: str, new_status: int) -> bool:
        db = tl.get_mgdb()
        # 找到最新的bid
        sql = {"$and": [{"unit_id": unit_name}, {"date": date}]}
        record = db["dataunit_status"].find(sql).sort([("bid", pymongo.DESCENDING)]).limit(1)
        bid = record.next()["bid"]
        # 更新状态
        where_sql = {"$and": [{"unit_id": unit_name}, {"date": date}, {"bid": bid}]}
        set_sql = {"status": new_status, "end_time": tl.now()}
        db["dataunit_status"].update_one(where_sql, {"$set": set_sql})
        return True

    def fail(self, unit_name: str, date: str) -> bool:
        """ 新登记 """
        # RUNNING->FAILED
        return self.__change_status(unit_name, date, DataUnitStatus.FAILED)

    def has_run(self, unit_name: str, date: str):
        # 查询当日unit是否运行过（执行成功）

        db = tl.get_mgdb()
        sql = {"$and": [{"unit_id": unit_name}, {
            "date": date}, {"status": DataUnitStatus.DONE}]}
        result = db.dataunit_status.count_documents(sql)
        if result > 0:
            return True
        else:
            return False

    def all_unit_finish(self):
        """ 检查是否所有的步骤都运行结束了 """
        db = tl.get_mgdb()

        sql = {"$and": [{"status": DataUnitStatus.RUNNING}]}
        if db.dataunit_status.count_documents(sql) == 0:
            return True
        else:
            return False
