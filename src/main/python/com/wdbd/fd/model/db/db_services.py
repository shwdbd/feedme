#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   db_services.py
@Time    :   2024/01/25 11:16:03
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   数据库操作涉及服务
'''
from com.wdbd.fd.model.db import get_engine, table_objects_pool as DB_POOL
from com.wdbd.fd.model.dt_model import SERVER_STAUTS_OPEN, SERVER_STAUTS_CLOSING, ActionGroup, ActionConfig
from sqlalchemy.orm import sessionmaker
from sqlalchemy import or_, and_
import com.wdbd.fd.common.tl as tl


# 启动并登记服务器状态
def start_dtserver() -> tl.Result:
    """启动服务

    先判断是否可以启动，如果已有服务正在运行，则返回False结果

    Returns:
        tl.Result: 执行结果
    """
    # TEST 需要单元测试
    try:
        engine = get_engine()
        Session = sessionmaker(bind=engine)
        session = Session()

        t_comm_server = DB_POOL.get("comm_server")

        # 判断是否有服务正在运行
        count_of_runningserver = session.query(t_comm_server).filter(or_(
            t_comm_server.c.status == SERVER_STAUTS_OPEN, t_comm_server.c.status == SERVER_STAUTS_CLOSING)).count()
        if count_of_runningserver > 0:
            # 有服务正在运行，返回False
            return tl.Result(result=False, msg="当前有服务正在运行，无法新启动新服务")
        else:
            # 可以登记新服务
            session.execute(t_comm_server.insert().values(
                {"status": SERVER_STAUTS_OPEN, "start_dt": tl.now(), "end_dt": ""}))
            session.commit()
            return tl.Result(result=True)
    except Exception as sqle:
        msg = "登记新服务日志时出现异常。" + str(sqle)
        tl.get_logger().error(msg)
        return tl.Result(result=False, msg=msg)
    finally:
        session.close()


# 发起服务终止指令
def shundown_server() -> tl.Result:
    """ 发起服务终止指令 """
    # 如果当前没有服务在OPEN状态，终止
    # 将当前活动服务状态设置为CLOSING
    # END
    # TEST 单元测试

    try:
        engine = get_engine()
        Session = sessionmaker(bind=engine)
        session = Session()

        t_comm_server = DB_POOL.get("comm_server")

        condition = (t_comm_server.c.status == SERVER_STAUTS_OPEN)
        updated_data = {'status': SERVER_STAUTS_CLOSING, "end_dt": tl.now()}
        session.execute(t_comm_server.update().where(
            condition).values(updated_data))

        session.commit()
        return tl.Result(result=True)
    except Exception as sqle:
        msg = "关闭新服务时遇到问题。" + str(sqle)
        tl.get_logger().error(msg)
        return tl.Result(result=False, msg=msg)
    finally:
        session.close()


# 返回当前服务器状态
def get_server_status() -> str:
    """ 返回当前服务器状态 """
    # TEST 单元测试

    try:
        engine = get_engine()
        Session = sessionmaker(bind=engine)
        session = Session()

        t_comm_server = DB_POOL.get("comm_server")
        res = session.query(t_comm_server.c.status).order_by(
            t_comm_server.c.start_dt.desc()).first()
        return res[0]
    except Exception as sqle:
        msg = "关闭新服务时遇到问题。" + str(sqle)
        tl.get_logger().error(msg)
        return None
    finally:
        session.close()


# 登记ActionGroup日志
def log_group(group: ActionGroup, result: bool = None, msg: str = None):
    """
    登记ActionGroup日志
    result = None，则表示新的Group日志
    """
    # EFFECTS:
    # 1. 如果这个group有日志，则将result和msg更新
    # 如果没有则新建一条
    # END
    try:
        engine = get_engine()
        Session = sessionmaker(bind=engine)
        session = Session()

        t_group = DB_POOL.get("comm_action_group_log")

        rs_group = session.query(t_group).with_entities(t_group.c.id).filter(and_(
            t_group.c.group_name == group.name, t_group.c.status == ActionGroup.RUNNING))
        if rs_group.count() > 0:
            # 有正在运行的Group
            condition = (t_group.c.id == rs_group[0].id)
            if result:
                updated_data = {'status': ActionGroup.SUCCESS,
                                "end_dt": tl.now(), "msg": msg}
            else:
                updated_data = {'status': ActionGroup.FAILED,
                                "end_dt": tl.now(), "msg": msg}
            session.execute(t_group.update().where(
                condition).values(updated_data))
            session.commit()
        else:
            # 无记录，新增
            str_actions = ", ".join(group.actions)  # 拼接Action信息字符串

            data = {"group_name": group.name, "status": ActionGroup.RUNNING,
                    "start_dt": tl.now(), "end_dt": "", "msg": "", "actions": str_actions}
            session.execute(t_group.insert().values(data))
            session.commit()
            # 返回自增id
            new_log = session.query(t_group).with_entities(t_group.c.id).filter(and_(
                t_group.c.group_name == group.name, t_group.c.status == ActionGroup.RUNNING)).first()
            return new_log.id
    except Exception as sqle:
        msg = "登记ActionGroup日志时遇到问题。" + str(sqle)
        tl.get_logger().error(msg)
    finally:
        session.close()


# 新登记Action操作日志
def log_new_action(action: ActionConfig, group_log_id: int, group_name: str, date_dt: str = None) -> int:
    """ 新登记Action操作日志 """
    try:
        engine = get_engine()
        Session = sessionmaker(bind=engine)
        session = Session()

        t_action_log = DB_POOL.get("comm_actions_log")

        # 新增记录
        data = {"group_name": group_name,
                "action_id": action.name,
                "status": ActionConfig.RUNNING,
                "start_dt": tl.now(),
                "end_dt": "",
                "msg": "",
                "date_dt": date_dt,
                "group_log_id": group_log_id
                }
        session.execute(t_action_log.insert().values(data))
        session.commit()
        # 返回自增id
        new_log = session.query(t_action_log).with_entities(t_action_log.c.id).filter(and_(
            t_action_log.c.group_name == group_name, t_action_log.c.action_id == action.name, t_action_log.c.status == ActionConfig.RUNNING)).order_by(t_action_log.c.id.desc()).first()
        return new_log.id
    except Exception as sqle:
        msg = "登记Action日志时遇到问题。" + str(sqle)
        tl.get_logger().error(msg)
        return None
    finally:
        session.close()


# 新登记Action操作日志
def log_action(action_log_id: str, result: bool, msg: str = None) -> int:
    """ 登记Action操作日志 """
    try:
        engine = get_engine()
        Session = sessionmaker(bind=engine)
        session = Session()

        t_action_log = DB_POOL.get("comm_actions_log")

        condition = (t_action_log.c.id == action_log_id)
        if result:
            updated_data = {'status': ActionConfig.SUCCESS,
                            "end_dt": tl.now(), "msg": msg}
        else:
            updated_data = {'status': ActionConfig.FAILED,
                            "end_dt": tl.now(), "msg": msg}
        print(result)
        session.execute(t_action_log.update().where(
            condition).values(updated_data))
        session.commit()
    except Exception as sqle:
        msg = "登记Action日志时遇到问题。" + str(sqle)
        tl.get_logger().error(msg)
        return None
    finally:
        session.close()


# if __name__ == "__main__":
#     action_A = ActionConfig()
#     action_A.name = "动作A"
#     action_A.class_url = "com.wdbd.fd.services.dt.actions.test_actions.DemoActionA"
#     action_A.set_windows([])
#     action_A.set_once_on_day(True)
#     id = log_new_action(action_A, group_log_id=11, group_name="新组")
#     print(id)


# if __name__ == "__main__":
#     res = start_dtserver()
#     print(res)

# if __name__ == "__main__":
#     engine = get_engine()

#     print(engine.url)

#     # # print(TABLE_POOL.get("comm_server"))
#     # t_comm_server = TABLE_POOL.get("comm_server")
#     # # 执行查询
#     # Session = sessionmaker(bind=engine)
#     # session = Session()
#     # # 全表查询
#     # rows = session.query(t_comm_server).all()
#     # print(rows)

#     # rows = session.query(t_comm_server).all()
#     # print(rows)
#     # session.close()
