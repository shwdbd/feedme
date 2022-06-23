#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   admin.py
@Time    :   2022/03/29 15:07:33
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   后台管理模块 模型对象
'''
from app.extensions import db


class Menu(db.Model):
    """ 菜单项 """
    __tablename__ = 'admin_menu'

    authorityId = db.Column(db.Integer, primary_key=True)    # 菜单唯一编号
    authorityName = db.Column(db.String(20), nullable=False)    # 菜单名
    menuUrl = db.Column(db.String(20), default="/")             # 链接地址
    isMenu = db.Column(db.Integer, name='is_menu', default=0)   # 是否菜单项目，否则是菜单组等非末级菜单
    parentId = db.Column(db.Integer, default=-1)   # 是否菜单项目，否则是菜单组等非末级菜单

    def __init__(self, id, name, url, parent_id, is_menu=1):
        self.authorityId = id
        self.authorityName = name
        self.menuUrl = url
        self.isMenu = is_menu
        self.parentId = parent_id
        self.data = []      # 子节点

    def to_dict(self):
        dict = self.__dict__
        if "_sa_instance_state" in dict:
            del dict["_sa_instance_state"]
        return dict
