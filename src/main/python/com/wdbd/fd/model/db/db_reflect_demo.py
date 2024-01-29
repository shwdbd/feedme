from com.wdbd.fd.model.db import get_engine, metadata
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, mapper, declarative_base
from sqlalchemy.schema import MetaData, Table
from sqlalchemy import text


engine = get_engine()
print(engine.url)
Session = sessionmaker(bind=engine)
session = Session()

# Base = declarative_base()
# metadata = MetaData()
# metadata.reflect(bind=engine)

# Session = sessionmaker(bind=engine)
# session = Session()

t_comm_server = metadata.tables.get("comm_server")
print(type(t_comm_server))

# INSERT INTO
result = session.execute(t_comm_server.insert().values({"status": "WIP", "start_dt": "", "end_dt": ""}))
print(result.rowcount)  # 打印受影响的行数

# # DELETE
# result = session.execute(t_comm_server.delete().where(t_comm_server.c.status == 'o'))
# print(result.rowcount)  # 打印受影响的行数

# # UPDATE
# # # 假设要更新的条件是column1等于'value1'，要将column2更新为'new_value'  
# # condition = table.c.column1 == 'value1'  
# # updated_data = {'column2': 'new_value'}  
# # result = session.execute(table.update().where(condition).values(updated_data))  
# # print(result.rowcount)  # 打印受影响的行数

# # 直接执行SQL语句
# # conn = engine.connect()
# # conn.execute("Delete from comm_server where status='WPS1'")

# session.execute(text("insert into comm_server (status) values ('123')"))

session.commit()

session.close()

