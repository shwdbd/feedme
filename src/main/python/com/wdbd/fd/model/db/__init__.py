from sqlalchemy import create_engine, MetaData, Table
from com.wdbd.fd.common.tl import get_cfg, get_logger
from sqlalchemy.ext.declarative import declarative_base


# 表集合
tables = [
    "employee",
    "comm_server",
    "comm_action_group",
    "comm_actions",
    "comm_action_group_log",
    "comm_actions_log",
    "ods_akshare_stock_sse_summary",
    "ods_akshare_tool_trade_date_hist_sina",
    "ods_akshare_stock_list",
    "ods_akshare_stock_info_sh_name_code",
    "ods_akshare_stock_info_sz_name_code",
    "ods_akshare_stock_info_bj_name_code",
]

# 表对象池
table_objects_pool = {}


Base = declarative_base()
metadata = MetaData()


def _init_tables(engine, output_level: int = 0):
    """ 初始化数据库表对象池

    Args:
        engine (_type_): _description_
        output_level (int, optional): 输出日志级别，0表示不输出，1表示输出全部初始化的表对象. Defaults to 0.
    """
    # output_level = 1 则输出实例化的表清单

    if len(table_objects_pool) > 0:
        return
    else:
        # 使用反射机制，获得表对象引用
        get_logger().debug("开始初始化数据库表对象:")
        metadata_obj = MetaData()
        metadata_obj.reflect(bind=engine)    # 获得元数据
        table_count = 0
        for t_name in tables:
            # print(t_name)
            if metadata_obj.tables.get(t_name) is not None:
                # table_objects_pool[t_name] = metadata_obj.tables[t_name]
                table_objects_pool[t_name] = Table(
                    t_name, metadata_obj, autoload=True, autoload_with=engine)  # 创建表对象
                # print(type(table_objects_pool[t_name]))
                table_count += 1
                if output_level >= 1:
                    get_logger().info("{i}. 表 {tn} ".format(
                        tn=t_name, i=table_count))
        get_logger().debug(
            "数据库表对象初始化 ... 完毕 (池中表数量: {0})".format(len(table_objects_pool)))


# 取得数据库连接
def get_engine():
    db_url = "mysql+pymysql://{user}:{pwd}@{host}:{port}/{db}".format(user=get_cfg(section="db", key="user"), pwd=get_cfg(
        section="db", key="password"), host=get_cfg(section="db", key="host"), db=get_cfg(section="db", key="db_name"), port=get_cfg(section="db", key="port"))
    engine = create_engine(db_url)
    if not engine:
        get_logger().error("连接失败！")
        raise Exception("数据库连接失败！")
    # 数据库连接成功
    _init_tables(engine=engine, output_level=0)
    metadata.reflect(bind=engine)
    return engine
