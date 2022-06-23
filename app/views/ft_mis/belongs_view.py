#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   belongs_view.py
@Time    :   2022/04/10 13:41:01
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   业务归属Views
'''
from flask import (
    Blueprint, render_template, request, jsonify, redirect
)
from flask import current_app as app
from app.models.ft_mis.dws_model import BelongRequestForm, BelongRequestFormItem
from app.service.ft_mis.belongs import new_form, add_form_item
from app.service.ft_mis.dws_service import get_cust, get_acct, get_loan
from sqlalchemy import and_
from app.extensions import db
from sqlalchemy import func, desc
from app.commons.utils.flask_utils import AjaxResponse, query2tabledata
from flask_login import current_user
"""
# 1. 提交审批 form_submit
# 2. 审批 form_appv
# 3. 归属执行

"""

# 构建蓝图
bp = Blueprint('belongs', __name__, url_prefix='/ftmis/belongs')


# 申请单列表页面
@bp.route('/form_list')
def form_list():
    """ 返回申请单列表页面 """
    return render_template('ft_mis/form_list.html')


# 查询申请单
@bp.route('/forms_query', methods=('GET', 'POST'))
def forms_query():
    """ 返回查询数据 """
    # 查询条件：status状态，applicant_id申请人
    if request.method == 'GET':
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 10))
        # 根据查询字段：
        query_list = []
        q_status = request.args.get('status', default=None)
        if q_status:
            query_list.append(BelongRequestForm.q_status == q_status)
        q_applicant_id = request.args.get('applicant_id', default=None)
        if q_applicant_id:
            query_list.append(BelongRequestForm.applicant_id == q_applicant_id)
        query_condition = and_(*query_list)  # 查询条件
        # app.logger.debug("人员查询：{0}".format(request.args))

    try:
        obj_lst = BelongRequestForm.query.filter(query_condition).offset(
            (page - 1) * limit).limit(limit).all()
        data = []
        for obj in obj_lst:
            data.append(obj.to_dict())
        # data = query2tabledata(users)
        if len(query_list) > 0:
            record_count = db.session.query(func.count(
                BelongRequestForm.form_id).filter(query_condition)).scalar()
        else:
            record_count = db.session.query(
                func.count(BelongRequestForm.form_id)).scalar()

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


# 新建申请单
@bp.route('/create_form', methods=('GET', 'POST'))
def new_belong_form():
    """ 新建申请单 """
    form_id = new_form(user_id=current_user.id)
    return redirect("/ftmis/belongs/belong_form/{0}".format(form_id))


# 新增条目
@bp.route('/item_add/<string:form_id>', methods=('GET', 'POST'))
def item_add(form_id: str):
    """ 返回申请单查询页面 """
    context = {
        'form_id': form_id,
    }
    return render_template("/ft_mis/item_add.html", **context)


# 申请单查看
@bp.route('/belong_form/<string:id>', methods=('GET', 'POST'))
def belong_form_detail(id):
    """ 查询并返回申请单对象 """
    form = db.session.query(BelongRequestForm).filter(BelongRequestForm.form_id == id).first()
    if form:
        context = {
            'form': form,
        }
        return render_template("/ft_mis/belong_form.html", **context)
    else:
        return "数据读取错误"


class BelongRequestFormItem_Display:
    """ 归属条目，页面展示用对象 """

    def __init__(self, item: BelongRequestFormItem):
        # self.item = item
        self.id = item.id
        self.type = item.get_type_name()
        self.bizno = item.biz_no
        self.cust_name = item.cust_name
        self.belong_str = item.belong_str()

    def to_dict(self):
        dict = self.__dict__
        if "_sa_instance_state" in dict:
            del dict["_sa_instance_state"]
        return dict


# 条目查询数据
@bp.route('/item_query/<string:form_id>', methods=('GET', 'POST'))
def item_query(form_id: str):
    """ 返回查询数据 """
    try:
        items = BelongRequestFormItem.query.filter(BelongRequestFormItem.form_id == form_id).order_by(desc(BelongRequestFormItem.biz_no)).all()
        items_display = []
        for i in items:
            d = BelongRequestFormItem_Display(i)
            items_display.append(d)
        data = query2tabledata(items_display)

        # 返回前台数据接口
        json_data = {
            "code": 0,
            "msg": "",
            "count": len(items),
            "data": data
        }
        return jsonify(json_data)
    except Exception as e:
        app.logger.error(str(e))
        return jsonify({"code": "500", "msg": "异常," + str(e), "count": 0, "data": []})


# 条目删除
@bp.route('/item_delete/<string:item_id>', methods=('GET', 'POST'))
def item_delete(item_id: int):
    """ 删除条目 """
    if request.method == 'POST':
        item = db.session.query(BelongRequestFormItem).filter(BelongRequestFormItem.id == item_id).first()
        if item:
            db.session.delete(item)
            db.session.commit()
            return jsonify(AjaxResponse(message="删除{0}成功").to_json())

    return jsonify(AjaxResponse(False, code=AjaxResponse.SERVER_ERROR, message="系统错误").to_json())


# 新增条目动作
@bp.route('/add_item', methods=('GET', 'POST'))
def belong_add_item():
    """新增条目动作
    """
    if request.method == 'POST':
        f_form_id = request.form.get("form_id")
        f_type = request.form.get("type")
        f_biz_id = request.form.get("biz_no")

        belongs = []
        dept_id_1 = request.form.get("dept_id_1")
        if dept_id_1:
            be_item = {}
            be_item["dept_id"] = request.form.get("dept_id_1")
            be_item["user_id"] = request.form.get("user_id_1")
            be_item["per"] = request.form.get("per_1")
            belongs.append(be_item)
        if request.form.get("dept_id_2"):
            be_item = {}
            be_item["dept_id"] = request.form.get("dept_id_2")
            be_item["user_id"] = request.form.get("user_id_2")
            be_item["per"] = request.form.get("per_2")
            belongs.append(be_item)
        if request.form.get("dept_id_3"):
            be_item = {}
            be_item["dept_id"] = request.form.get("dept_id_3")
            be_item["user_id"] = request.form.get("user_id_3")
            be_item["per"] = request.form.get("per_3")
            belongs.append(be_item)
        if request.form.get("dept_id_4"):
            be_item = {}
            be_item["dept_id"] = request.form.get("dept_id_4")
            be_item["user_id"] = request.form.get("user_id_4")
            be_item["per"] = request.form.get("per_4")
            belongs.append(be_item)
        if request.form.get("dept_id_5"):
            be_item = {}
            be_item["dept_id"] = request.form.get("dept_id_5")
            be_item["user_id"] = request.form.get("user_id_5")
            be_item["per"] = request.form.get("per_5")
            belongs.append(be_item)
        print(request.form)
        print(belongs)

        try:
            item = add_form_item(form_id=f_form_id, type=f_type, biz_id=f_biz_id, belongs=belongs)
            if item:
                return jsonify(AjaxResponse(message="添加成功").to_json())
            else:
                return jsonify(AjaxResponse(False, code=AjaxResponse.SERVER_ERROR, message="添加失败！").to_json())
        except Exception as ide:
            return jsonify(AjaxResponse(False, code=AjaxResponse.SERVER_ERROR, message="添加失败！" + str(ide)).to_json())


# 根据业务编号，查询户名
@bp.route('/query_cust_name', methods=('GET', 'POST'))
def query_cust_name():
    if request.method == 'POST':
        f_type = request.form.get("type")
        f_bizno = request.form.get("biz_no")
        cust_id = None
        print(request.form)
        if f_type == 'cust':
            biz = get_cust(f_bizno)
            if biz:
                cust_id = biz.id
        elif f_type == 'acct':
            biz = get_acct(f_bizno)
            if biz:
                cust_id = biz.customer_id
        elif f_type == 'loan':
            biz = get_loan(f_bizno)
            if biz:
                cust_id = biz.customer_id
        else:
            return jsonify(AjaxResponse(False, code=AjaxResponse.SERVER_ERROR, message="错误的业务类型").to_json())

        if biz:
            data = {
                "cust_id": cust_id,
                "cust_name": biz.name
            }
            return jsonify(AjaxResponse(message="", data=data).to_json())
        else:
            return jsonify(AjaxResponse(False, code=AjaxResponse.SERVER_ERROR, message="查无此户").to_json())
