# 代码调用窗口
from com.wdbd.fd.services.dt.server import DTServer, ServerUtils
from com.wdbd.fd.model.db.db_services import start_dtserver, shundown_server, get_server_status, log_group
from com.wdbd.fd.services.dt.server import BasicEngine
from com.wdbd.fd.model.dt_model import ActionGroup, AbstractAction, ActionConfig


def run_test_group():
    # 测试单个线程
    engine = BasicEngine(groups=[])
    group = ActionGroup()
    group.name = "测试组AB"
    group.set_interval_minutes("5s")
    # 模拟新线程
    engine.threads[group.name] = "s"
    # 加载Action
    action_A = ActionConfig()
    action_A.name = "动作A"
    action_A.class_url = "com.wdbd.fd.services.dt.actions.test_actions.DemoActionA"
    action_A.set_windows([])
    action_A.set_once_on_day(True)
    group.append_action(action_A)
    action_B = ActionConfig()
    action_B.name = "动作B"
    action_B.class_url = "com.wdbd.fd.services.dt.actions.test_actions.DemoActionB"
    action_B.set_windows([])
    action_B.set_once_on_day(True)
    group.append_action(action_B)
    print("测试参数准备完毕！")

    # 执行
    engine._start_group_threads(group=group)


if __name__ == "__main__":

    # # 测试启动单个Group
    # run_test_group()
    
    # 记录Group日志
    group = ActionGroup()
    group.name = "测试组AB"
    group.set_interval_minutes("5s")
    # 加载Action
    action_A = ActionConfig()
    action_A.name = "动作A"
    action_A.class_url = "com.wdbd.fd.services.dt.actions.test_actions.DemoActionA"
    action_A.set_windows([])
    action_A.set_once_on_day(True)
    group.append_action(action_A)
    action_B = ActionConfig()
    action_B.name = "动作B"
    action_B.class_url = "com.wdbd.fd.services.dt.actions.test_actions.DemoActionB"
    action_B.set_windows([])
    action_B.set_once_on_day(True)
    group.append_action(action_B)
    print("测试参数准备完毕！")
    # log_group(group=group)
    log_group(group=group, result=False, msg="xxxyyy")

    # # 启动服务
    # engine = DTServer.getConfigFileEngine()
    # if engine:
    #     engine.start()
    #     # 关闭服务器
    #     DTServer.shundown()
    # else:
    #     print("服务引擎启动失败!")

    # # 查询当前服务状态
    # res = get_server_status()
    # print(res)

    # # 登记新服务
    # res = start_dtserver()
    # print(res)
    
    # # 关闭服务
    # res = shundown_server()
    # print(res)

    # # 从配置文件读取ActionGroup数组
    # file_path = "C:/github/shwdbd/feedme/src/test/python/com/wdbd/fd/test/services/demo_config.json"
    # groups = ServerUtils.load_config_file(file_path)
    # print("结果: " + str(groups))
    # group = groups[0]
    # print(group.get_onerr_mode())
    # print(group.get_interval_minutes())
    # print(group.get_windows())
    # # -----------
    # action = group.actions["Tushare_A股清单"]
    # print("Action: " + str(action))
    # print("action.: " + str(action.get_windows()))
    # print("action.: " + str(action.get_once_on_day()))
