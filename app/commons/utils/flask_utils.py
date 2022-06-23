#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   flask_utils.py
@Time    :   2022/03/26 12:17:25
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   Flask 工具包
'''


class AjaxResponse:
    """ Ajax响应头 """

    SUCCESS_CODE = 200
    SERVER_ERROR = 500

    def __init__(self, success: bool = True, code: int = SUCCESS_CODE, message: str = "", data: dict = None):
        self.success = success
        self.code = code
        self.message = message
        self.data = data

    def to_json(self):
        return {
            "success": self.success,
            "code": self.code,
            "message": self.message,
            "data": self.data
        }


def query2tabledata(query_objs):
    """ 将sqlachemy查询结果转成Layui数据表格所需要的data格式, list of dict """
    # [{'name': '公共', 'id': '00'}, {'name': '11', 'id': '11'}]
    data = []
    for obj in query_objs:
        data.append(obj.to_dict())
    return data
