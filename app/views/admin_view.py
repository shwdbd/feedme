#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   admin_view.py
@Time    :   2022/03/23 22:56:16
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   系统管理模块模块Views

views：

部门维护部分：
Endpoint           Methods    Rule
-----------------  ---------  ------------------------------
admin.dept_index   GET        /admin/dept
admin.dept_list    GET, POST  /admin/dept_query
admin.dept_new     GET, POST  /admin/dept/new
admin.dept_add     GET, POST  /admin/dept/add
admin.dept_detail  GET, POST  /admin/dept/<string:id>
admin.dept_modify  GET, POST  /admin/dept/modify/<string:id>
admin.dept_save    GET, POST  /admin/dept/update/<string:id>
admin.dept_delete  GET, POST  /admin/dept/delete/<string:id>
'''
from flask import (
    Blueprint, render_template, request, jsonify
)
from flask import current_app as app
from app.models.auth import AdminDepartment, AdminUser, InvaidIdException
from sqlalchemy import func
from app.extensions import db
from sqlalchemy import or_
from app.commons.utils.flask_utils import AjaxResponse, query2tabledata
from app.service.ft_mis.hr import create_dept, query_user


# 构建蓝图
bp = Blueprint('admin', __name__, url_prefix='/admin')


# @bp.route('/test_auth')
# @login_required
# def test_auth():
#     return '这个页面需要登录后才能看'


# ===========================================================
# 人员维护部分

# 人员列表
@bp.route('/user')
def user_index():
    """ 返回部门清单页面 """
    return render_template('admin/user.html')


# 人员查询数据
@bp.route('/user_query', methods=('GET', 'POST'))
def user_query():
    """ 返回查询数据 """
    if request.method == 'GET':
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 5))
        # 根据查询字段：
        query_list = []
        q_id = request.args.get('id', default=None)
        if q_id:
            query_list.append(AdminUser.id == q_id)
        q_name = request.args.get('name', default=None)
        if q_name:
            query_list.append(AdminUser.name.like(
                '%{name}%'.format(name=q_name)))
        query_condition = or_(*query_list)  # 查询条件
        app.logger.debug("人员查询：{0}".format(request.args))

    try:
        users = AdminUser.query.filter(query_condition).offset(
            (page - 1) * limit).limit(limit).all()
        data = []
        for obj in users:
            obj.dept_name = obj.get_dept_name()     # 部门名
            obj.status_desc = obj.get_status()
            data.append(obj.to_dict())
        # data = query2tabledata(users)
        if len(query_list) > 0:
            record_count = db.session.query(func.count(
                AdminUser.id).filter(query_condition)).scalar()
        else:
            record_count = db.session.query(
                func.count(AdminUser.id)).scalar()

        # 返回前台数据接口
        json_data = {
            "code": 0,
            "msg": "",
            "count": record_count,
            "data": data
        }
        print(data)
        return jsonify(json_data)
    except Exception as e:
        app.logger.error(str(e))
        return jsonify({"code": "500", "msg": "异常," + str(e), "count": 0, "data": []})


# 人员部门页面
@bp.route('/user/new')
def user_new():
    """返回添加录入页面"""
    return render_template('admin/user_new.html')


# 单用户查看
@bp.route('/user/<string:user_id>', methods=('GET', 'POST'))
def user_detail(user_id: str):
    """ 查询并返回人员对象 """
    user = AdminUser.query.filter(AdminUser.id == user_id).first()
    if user:
        context = {
            'user': user,
        }
        return render_template("/admin/user_detail.html", **context)
    else:
        return "数据读取错误"


# ===========================================================
# 部门维护部分

# 部门列表
@bp.route('/dept')
def dept_index():
    """ 返回部门清单页面 """
    return render_template('admin/dept.html')


# 新建部门页面
@bp.route('/dept/new', methods=('GET', 'POST'))
def dept_new():
    """返回添加录入页面"""
    return render_template('admin/dept_new.html')


# 新建部门动作
@bp.route('/dept/add', methods=('GET', 'POST'))
def dept_add():
    """接受新增请求，执行新增动作并反馈结果
    """
    app.logger.info("新建部门")
    if request.method == 'POST':
        dept_id = request.form.get("id")
        dept_name = request.form.get("name")

        try:
            dept = create_dept(dept_id=dept_id, name=dept_name)
            if dept:
                return jsonify(AjaxResponse(message="添加成功").to_json())
            else:
                return jsonify(AjaxResponse(False, code=AjaxResponse.SERVER_ERROR, message="添加部门失败！").to_json())
        except InvaidIdException as ide:
            return jsonify(AjaxResponse(False, code=AjaxResponse.SERVER_ERROR, message="添加部门失败！" + str(ide)).to_json())

    return jsonify(AjaxResponse(False, code=AjaxResponse.SERVER_ERROR, message="系统错误").to_json())


# 部门查询数据
@bp.route('/dept_query', methods=('GET', 'POST'))
def dept_query():
    """ 返回查询数据 """
    if request.method == 'GET':
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 5))      # TODO 默认的每页显示，要加入到系统参数中
        # TODO 分页参数的引用，要抽象出去
        # 根据查询字段：
        query_list = []
        q_id = request.args.get('id', default=None)
        if q_id:
            query_list.append(AdminDepartment.id == q_id)
        q_name = request.args.get('name', default=None)
        if q_name:
            query_list.append(AdminDepartment.name.like(
                '%{name}%'.format(name=q_name)))
        query_condition = or_(*query_list)  # 查询条件
        app.logger.debug("部门查询：{0}".format(request.args))

    try:
        depts = AdminDepartment.query.filter(query_condition).offset(
            (page - 1) * limit).limit(limit).all()
        data = query2tabledata(depts)
        # TODO 计算count，要抽象出去
        if len(query_list) > 0:
            record_count = db.session.query(func.count(
                AdminDepartment.id).filter(query_condition)).scalar()
        else:
            record_count = db.session.query(
                func.count(AdminDepartment.id)).scalar()

        # 返回前台数据接口
        json_data = {
            "code": 0,
            "msg": "",
            "count": record_count,
            "data": data
        }
        print(data)
        return jsonify(json_data)
    except Exception as e:
        app.logger.error(str(e))
        return jsonify({"code": "500", "msg": "异常," + str(e), "count": 0, "data": []})


# 部门查看
@bp.route('/dept/<string:id>', methods=('GET', 'POST'))
def dept_detail(id):
    """ 查询并返回部门对象 """
    dept = db.session.query(AdminDepartment).filter(AdminDepartment.id == id).first()
    print(dept)
    if dept:
        context = {
            'dept': dept,
        }
        return render_template("/admin/dept_detail.html", **context)
    else:
        return "数据读取错误"


# 部门编辑
@bp.route('/dept/modify/<string:id>', methods=('GET', 'POST'))
def dept_modify(id):
    dept = db.session.query(AdminDepartment).filter(AdminDepartment.id == id).first()
    if dept:
        context = {
            'dept': dept,
        }
        return render_template("/admin/dept_edit.html", **context)
    else:
        return "数据读取错误"


# 部门编辑保存
@bp.route('/dept/update/<string:id>', methods=('GET', 'POST'))
def dept_save(id):
    app.logger.info("保存部门")
    if request.method == 'POST':
        dept = db.session.query(AdminDepartment).filter(AdminDepartment.id == id).first()
        if dept:
            dept.name = request.form.get("name")
            db.session.commit()
            return jsonify(AjaxResponse(message="更新{0}成功".format(dept.name)).to_json())
        else:
            app.logger.error("部门{0}未找到".format(id))
            return jsonify(AjaxResponse(False, code=AjaxResponse.SERVER_ERROR, message="部门{0}未找到".format(id)).to_json())

    return jsonify(AjaxResponse(False, code=AjaxResponse.SERVER_ERROR, message="系统错误").to_json())


# 部门删除
@bp.route('/dept/delete/<string:id>', methods=('GET', 'POST'))
def dept_delete(id):
    """ 接受删除请求，执行并反馈结果 """
    app.logger.info("删除部门")
    if request.method == 'POST':
        dept = db.session.query(AdminDepartment).filter(AdminDepartment.id == id).first()
        if dept:
            db.session.delete(dept)
            db.session.commit()
            return jsonify(AjaxResponse(message="删除{0}成功".format(dept.name)).to_json())

    return jsonify(AjaxResponse(False, code=AjaxResponse.SERVER_ERROR, message="系统错误").to_json())


# ===========================================================
# 公共组件
# 人员选择
@bp.route('/choose_user', methods=('GET', 'POST'))
def choose_user():
    """ 人员选择 """
    if request.method == 'POST':
        name = request.form.get("name")
        oa_id = request.form.get("oa_id")
        users = query_user(name=name, oa_id=oa_id)
        print(users)
        context = {
            'users': users,
            'f_name': name,
            'f_oa_id': oa_id,
        }
        return render_template("/admin/user_picker.html", **context)

    return render_template('/admin/user_picker.html')


# if __name__ == "__main__":
#     from app import app
#     with app.app_context():
#         dept_detail('00')
