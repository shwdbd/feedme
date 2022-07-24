#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   file_upload.py
@Time    :   2022/07/21 13:04:25
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   文件上传示例程序
'''
from flask import (
    Blueprint, render_template, request
)

# 构建蓝图
bp = Blueprint('demo_file_upload', __name__, url_prefix='/demo/file_upload/')


# 单文件上传页
@bp.route('/file_upload')
def file_upload():
    """ 返回 单文件上传页 """
    return render_template('demo/file_upload.html')


# 单文件上传动作
@bp.route('/file_upload_action/', methods=['GET', 'POST'])
def file_upload_action():
    """ 返回 单文件上传动作 """
    # 接收表单数据：
    v1 = request.form.get('v1')
    print("v1 = {0}".format(v1))
    # 接受文件上传数据
    f = request.files.get("file")       # 获取前端传来的文件
    print("file = {0}".format(f))
    # f.save('C:\\temp\\{0}'.format(f.filename))       # 将文件保存下来
    print("上传、另存为 ok")
    # 返回值
    return {
        "code": 0, "msg": "上传成功", "data": {
            "v1": v1
        }
    }


# 多文件上传页
@bp.route('/file_multi_upload')
def file_multi_upload():
    """ 返回 多文件上传页 """
    return render_template('demo/file_multi_upload.html')


# 多文件上传动作
@bp.route('/file_multi_upload_action/', methods=['GET', 'POST'])
def file_multi_upload_action():
    """ 返回 多文件上传动作 """
    # 提两次POST请求，需要分开处理

    # 接收表单数据：
    # v1 = request.form.get('v1')
    # print("v1 = {0}".format(v1))
    # 接受文件上传数据
    f = request.files.get("file")       # 获取前端传来的文件
    print("file = {0}".format(f))
    # f.save('C:\\temp\\{0}'.format(f.filename))       # 将文件保存下来
    print("上传、另存为 ok")
    # 返回值
    return {
        "code": 0, "msg": "上传成功", "data": {
            # "v1": v1
        }
    }
