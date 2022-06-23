#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   admin_srv.py
@Time    :   2022/04/01 09:22:56
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   Admin组件业务逻辑
'''
from app.extensions import db
from app.models.admin import Menu


def get_menu_dict() -> list:
    """ 返回Admin左侧目录数据列表 """
    # TODO 单元测试
    res = []
    root_nodes = db.session.query(Menu).filter(Menu.parentId == -1).all()
    # print(root_node)
    for root_node in root_nodes:
        # 加载子目录
        sub_nodes = db.session.query(Menu).filter(Menu.parentId == root_node.authorityId).all()
        sub_data = []
        for node in sub_nodes:
            sub_data.append(node.to_dict())
        root_node.data = sub_data
        res.append(root_node.to_dict())

    return res


# if __name__ == "__main__":

#     from app import app
#     with app.app_context():
#         d = get_menu_dict()
#         print(d)
