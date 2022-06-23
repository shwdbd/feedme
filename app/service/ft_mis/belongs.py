#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   belongs.py
@Time    :   2022/04/01 21:56:28
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   业务归属 业务逻辑处理
'''
# from app import app
from tkinter import END
from app.extensions import db
from sqlalchemy import desc
import datetime
from app.models.ft_mis.dws_model import CustomerBelong, BelongRequestForm, BelongRequestFormItem
from app.models.auth import AdminUser
from app.service.ft_mis.hr import query_dept_name, query_user_name, get_dept_public_user
from app.service.ft_mis.dws_service import get_cust, get_acct, get_loan


# 查询客户归属
def query_cust_belong(cust_id: str) -> CustomerBelong:
    """ 查询客户归属 """
    # TODO 待测试
    cb = CustomerBelong.query.filter(CustomerBelong.cust_id == cust_id).first()
    return cb


# 查询存款归属
def query_deposit_belong(acct_id: str) -> list:
    """ 查询存款账号归属 """
    # TODO 待实现
    return None


# 查询贷款归属
def query_loan_belong(loan_id: str) -> list:
    """ 查询借据号归属 """
    # TODO 待实现
    return None


# --------------------------------------
# 申请单操作

# 新建申请单
def new_form(user_id: str) -> str:
    """新建归属申报单

    Args:
        user_id (str): 申报人id

    Returns:
        str: 生成的申报单编号
    """
    # 数据库中新建一条记录，生成一个单号
    # END

    # 1. 找到当日最后的记录，生成序号
    today = datetime.datetime.now().strftime('%Y%m%d')
    form = BelongRequestForm.query.filter(
        BelongRequestForm.form_id.like('GS-{d}-%'.format(d=today))).order_by(BelongRequestForm.form_id.desc()).first()
    if form:
        form_no = '{0:0>5}'.format(int(form.form_id[-5:])+1)
    else:
        form_no = "00001"
    # print(form_no)
    # 2. 生成新的序号
    form_id = 'GS-{d}-{no}'.format(d=today, no=form_no)
    # 3. 新建对象
    form = BelongRequestForm()
    form.form_id = form_id
    form.status = BelongRequestForm.STAUS_DRAFT
    form.applicant_id = user_id
    user = db.session.query(AdminUser).filter(AdminUser.id == user_id).first()
    if user:
        form.applicant_name = user.name       # 姓名
    form.applicant_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%m:%S')
    db.session.add(form)
    db.session.commit()

    return form.form_id


# 添加客户归属变更申请
def _add_cust_change_item(form_id, type: int, biz_id: str, belongs: dict) -> int:
    """ 客户归属调整申请项目 """
    # 客户号不存在
    cust = get_cust(biz_id)
    if cust is None:
        raise Exception("添加错误，{id}查无此客户".format(id=biz_id))
    # 客户已有归属
    if query_cust_belong(cust_id=biz_id) is not None:
        raise Exception("客户已有归属，不能申请调整")
    item = BelongRequestFormItem()
    item.form_id = form_id        # 申请单编号
    # 类型，客户号cust,存款账号acct，贷款借据号loan
    item.type = BelongRequestFormItem.TYPE_CUST
    item.status = BelongRequestFormItem.STAUS_WAIT           # 状态
    item.biz_no = biz_id                                     # 业务编号
    # 检查客户情况
    item.cust_name = cust.name                               # 户名
    # === 1 ====
    if len(belongs) >= 1:
        bl_item = belongs[0]
        item.dept_id_1 = bl_item["dept_id"]                         # 归属部门编号（仅客户号归属有效）
        item.dept_name_1 = query_dept_name(item.dept_id_1)          # 归属部门名称（仅客户号归属有效）
        if bl_item["user_id"]:
            item.user_id_1 = bl_item["user_id"]                     # 归属人编号
            item.user_name_1 = query_user_name(item.user_id_1)      # 归属人姓名
        else:
            # 如果不指定用户，则归属到部门公共
            u_id, u_name = get_dept_public_user(item.dept_id_1)
            item.user_id_1 = u_id
            item.user_name_1 = u_name
        item.per_1 = int(bl_item.get("per", "100"))                  # 归属人归属比例
    # === 2 ====
    if len(belongs) >= 2:
        bl_item = belongs[1]
        item.dept_id_2 = bl_item["dept_id"]                         # 归属部门编号（仅客户号归属有效）
        item.dept_name_2 = query_dept_name(item.dept_id_2)          # 归属部门名称（仅客户号归属有效）
        if bl_item["user_id"]:
            item.user_id_2 = bl_item["user_id"]                     # 归属人编号
            item.user_name_2 = query_user_name(item.user_id_2)      # 归属人姓名
        else:
            # 如果不指定用户，则归属到部门公共
            u_id, u_name = get_dept_public_user(item.dept_id_2)
            item.user_id_2 = u_id
            item.user_name_2 = u_name
        item.per_2 = int(bl_item.get("per", "100"))                  # 归属人归属比例
    # === 3 ====
    if len(belongs) >= 3:
        bl_item = belongs[2]
        item.dept_id_3 = bl_item["dept_id"]                         # 归属部门编号（仅客户号归属有效）
        item.dept_name_3 = query_dept_name(item.dept_id_3)          # 归属部门名称（仅客户号归属有效）
        if bl_item["user_id"]:
            item.user_id_3 = bl_item["user_id"]                     # 归属人编号
            item.user_name_3 = query_user_name(item.user_id_3)      # 归属人姓名
        else:
            # 如果不指定用户，则归属到部门公共
            u_id, u_name = get_dept_public_user(item.dept_id_3)
            item.user_id_3 = u_id
            item.user_name_3 = u_name
        item.per_3 = int(bl_item.get("per", "100"))                  # 归属人归属比例
    # === 4 ====
    if len(belongs) >= 4:
        bl_item = belongs[3]
        item.dept_id_4 = bl_item["dept_id"]                         # 归属部门编号（仅客户号归属有效）
        item.dept_name_4 = query_dept_name(item.dept_id_4)          # 归属部门名称（仅客户号归属有效）
        if bl_item["user_id"]:
            item.user_id_4 = bl_item["user_id"]                     # 归属人编号
            item.user_name_4 = query_user_name(item.user_id_4)      # 归属人姓名
        else:
            # 如果不指定用户，则归属到部门公共
            u_id, u_name = get_dept_public_user(item.dept_id_4)
            item.user_id_4 = u_id
            item.user_name_4 = u_name
        item.per_4 = int(bl_item.get("per", "100"))                  # 归属人归属比例
    # === 5 ====
    if len(belongs) >= 5:
        bl_item = belongs[4]
        item.dept_id_5 = bl_item["dept_id"]                         # 归属部门编号（仅客户号归属有效）
        item.dept_name_5 = query_dept_name(item.dept_id_5)          # 归属部门名称（仅客户号归属有效）
        if bl_item["user_id"]:
            item.user_id_5 = bl_item["user_id"]                     # 归属人编号
            item.user_name_5 = query_user_name(item.user_id_5)      # 归属人姓名
        else:
            # 如果不指定用户，则归属到部门公共
            u_id, u_name = get_dept_public_user(item.dept_id_5)
            item.user_id_5 = u_id
            item.user_name_5 = u_name
        item.per_5 = int(bl_item.get("per", "100"))                  # 归属人归属比例

    db.session.add(item)
    db.session.commit()
    return item.id


# 添加存款账号归属变更申请
def _add_deposit_acct_change_item(form_id, type: int, biz_id: str, belongs: dict) -> int:
    # 抛出异常情况：
    # 1. 账号不存在
    # 2. 归属比例总和不等于100
    # 3. 员工不存在
    # 客户号不存在

    # 检查账户有效性
    acct = get_acct(biz_id)
    if acct is None:
        raise Exception("添加错误，{id}查无此存款账户".format(id=biz_id))
    item = BelongRequestFormItem()
    item.form_id = form_id        # 申请单编号
    item.type = BelongRequestFormItem.TYPE_ACCT
    item.status = BelongRequestFormItem.STAUS_WAIT           # 状态
    item.biz_no = biz_id                                     # 业务编号
    cust = get_cust(acct.customer_id)
    if cust:
        item.cust_name = cust.name
    # 检查分成比例是否为100
    total_per = 0
    for bi in belongs:
        total_per += bi["per"]
    if total_per != 100:
        raise Exception("添加错误, 总分成比例不是100%，而是{0}".format(total_per))
    # 添加归属分成明细
    for idx, bi in enumerate(belongs):
        dept_id = bi["dept_id"]
        user_id = bi["user_id"]
        per = int(bi.get("per", "100"))
        if (idx+1) == 1:
            item.dept_id_1 = dept_id
            item.user_id_1 = user_id
            item.per_1 = per
            item.dept_name_1 = query_dept_name(dept_id)
            item.user_name_1 = query_user_name(user_id)
            if item.dept_name_1 is None:
                raise Exception("添加失败, 无效部门id {0}".format(item.dept_id_1))
            if item.user_name_1 is None:
                raise Exception("添加失败, 无效用户id {0}".format(item.user_id_1))
        elif (idx+1) == 2:
            item.dept_id_2 = dept_id
            item.user_id_2 = user_id
            item.per_2 = per
            item.dept_name_2 = query_dept_name(dept_id)
            item.user_name_2 = query_user_name(user_id)
            if item.dept_name_2 is None:
                raise Exception("添加失败, 无效部门id {0}".format(item.dept_id_2))
            if item.user_name_2 is None:
                raise Exception("添加失败, 无效用户id {0}".format(item.user_id_2))
        elif (idx+1) == 3:
            item.dept_id_3 = dept_id
            item.user_id_3 = user_id
            item.per_3 = per
            item.dept_name_3 = query_dept_name(dept_id)
            item.user_name_3 = query_user_name(user_id)
            if item.dept_name_3 is None:
                raise Exception("添加失败, 无效部门id {0}".format(item.dept_id_3))
            if item.user_name_3 is None:
                raise Exception("添加失败, 无效用户id {0}".format(item.user_id_3))
        elif (idx+1) == 4:
            item.dept_id_4 = dept_id
            item.user_id_4 = user_id
            item.per_4 = per
            item.dept_name_4 = query_dept_name(dept_id)
            item.user_name_4 = query_user_name(user_id)
            if item.dept_name_4 is None:
                raise Exception("添加失败, 无效部门id {0}".format(item.dept_id_4))
            if item.user_name_4 is None:
                raise Exception("添加失败, 无效用户id {0}".format(item.user_id_4))
        elif (idx+1) == 5:
            item.dept_id_5 = dept_id
            item.user_id_5 = user_id
            item.per_5 = per
            item.dept_name_5 = query_dept_name(dept_id)
            item.user_name_5 = query_user_name(user_id)
            if item.dept_name_5 is None:
                raise Exception("添加失败, 无效部门id {0}".format(item.dept_id_5))
            if item.user_name_5 is None:
                raise Exception("添加失败, 无效用户id {0}".format(item.user_id_5))

    db.session.add(item)
    db.session.commit()

    return item.id


# 添加贷款归属变更申请
def _add_loan_change_item(form_id, type: int, biz_id: str, belongs: dict) -> int:
    # TODO 待实现
    # 检查账户有效性
    loan = get_loan(biz_id)
    if loan is None:
        raise Exception("添加错误，{id}查无此存款借据号".format(id=biz_id))
    item = BelongRequestFormItem()
    item.form_id = form_id        # 申请单编号
    item.type = BelongRequestFormItem.TYPE_LOAN
    item.status = BelongRequestFormItem.STAUS_WAIT           # 状态
    item.biz_no = biz_id                                     # 业务编号
    cust = get_cust(loan.customer_id)
    if cust:
        item.cust_name = cust.name
    # 检查分成比例是否为100
    total_per = 0
    for bi in belongs:
        total_per += bi["per"]
    if total_per != 100:
        raise Exception("添加错误, 总分成比例不是100%，而是{0}".format(total_per))
    # 添加归属分成明细
    for idx, bi in enumerate(belongs):
        dept_id = bi["dept_id"]
        user_id = bi["user_id"]
        per = int(bi.get("per", "100"))
        if (idx+1) == 1:
            item.dept_id_1 = dept_id
            item.user_id_1 = user_id
            item.per_1 = per
            item.dept_name_1 = query_dept_name(dept_id)
            item.user_name_1 = query_user_name(user_id)
            if item.dept_name_1 is None:
                raise Exception("添加失败, 无效部门id {0}".format(item.dept_id_1))
            if item.user_name_1 is None:
                raise Exception("添加失败, 无效用户id {0}".format(item.user_id_1))
        elif (idx+1) == 2:
            item.dept_id_2 = dept_id
            item.user_id_2 = user_id
            item.per_2 = per
            item.dept_name_2 = query_dept_name(dept_id)
            item.user_name_2 = query_user_name(user_id)
            if item.dept_name_2 is None:
                raise Exception("添加失败, 无效部门id {0}".format(item.dept_id_2))
            if item.user_name_2 is None:
                raise Exception("添加失败, 无效用户id {0}".format(item.user_id_2))
        elif (idx+1) == 3:
            item.dept_id_3 = dept_id
            item.user_id_3 = user_id
            item.per_3 = per
            item.dept_name_3 = query_dept_name(dept_id)
            item.user_name_3 = query_user_name(user_id)
            if item.dept_name_3 is None:
                raise Exception("添加失败, 无效部门id {0}".format(item.dept_id_3))
            if item.user_name_3 is None:
                raise Exception("添加失败, 无效用户id {0}".format(item.user_id_3))
        elif (idx+1) == 4:
            item.dept_id_4 = dept_id
            item.user_id_4 = user_id
            item.per_4 = per
            item.dept_name_4 = query_dept_name(dept_id)
            item.user_name_4 = query_user_name(user_id)
            if item.dept_name_4 is None:
                raise Exception("添加失败, 无效部门id {0}".format(item.dept_id_4))
            if item.user_name_4 is None:
                raise Exception("添加失败, 无效用户id {0}".format(item.user_id_4))
        elif (idx+1) == 5:
            item.dept_id_5 = dept_id
            item.user_id_5 = user_id
            item.per_5 = per
            item.dept_name_5 = query_dept_name(dept_id)
            item.user_name_5 = query_user_name(user_id)
            if item.dept_name_5 is None:
                raise Exception("添加失败, 无效部门id {0}".format(item.dept_id_5))
            if item.user_name_5 is None:
                raise Exception("添加失败, 无效用户id {0}".format(item.user_id_5))

    db.session.add(item)
    db.session.commit()

    return item.id


# 添加申请表项目
def add_form_item(form_id, type: int, biz_id: str, belongs: dict) -> int:
    """添加归属申报单条目

    Args:
        form_id (_type_): 申报单编号
        type (int): 业务类型，客户号或账号或借据号
        biz_id (str): 业务编号
        belongs (dict): 归属情况，如[{"dept_id": "00", "user_id": "zhangsan", "per": 100}]

    Returns:
        int: 生成的流水号
    """
    if type == BelongRequestFormItem.TYPE_CUST:
        return _add_cust_change_item(form_id, type, biz_id, belongs)
    elif type == BelongRequestFormItem.TYPE_ACCT:
        return _add_deposit_acct_change_item(form_id, type, biz_id, belongs)
    elif type == BelongRequestFormItem.TYPE_LOAN:
        return _add_loan_change_item(form_id, type, biz_id, belongs)
    else:
        return -1


# 提交部门审批
def form_submit(form_id: str, lead_id: str = None):
    """归属申报单 提交部门负责人审批

    Args:
        form_id (str): 单号
        lead_id (str, optional): 部门负责人账号. 默认为None，表示根据系统权限执行.

    Returns:
        bool: 执行结果，Ture, 错我原因
    """
    form = BelongRequestForm.query.filter(BelongRequestForm.form_id == form_id).first()
    if not form:
        return False, "单号{0}不存在".format(form_id)

    # TODO 待实现
    # TODO 待测试
    return False


def form_appv(form_id: str, appved: bool, approval_note: str = "") -> bool:
    """部门负责人审批表单

    Args:
        form_id (str): 单号
        appved (bool): 审批结果，是否同意
        approval_note (str, optional): 意见. Defaults to "".

    Returns:
        bool: 执行结果
    """
    # TODO 待实现
    # TODO 待测试
    return False


# 根据form_id查询归属条目
def get_items_by_formid(form_id):
    """ 取得全部的条目（按业务编号排序）"""
    # TODO 承接，作为前台查询的一个后台服务使用
    items = BelongRequestFormItem.query.filter(BelongRequestFormItem.form_id == form_id).order_by(desc(BelongRequestFormItem.biz_no)).all()
    return items


# --------------------------------------
# 业务归属调整
def belong_form_action(form_id: str) -> bool:
    """ 执行申请单 """
    # 1. 判断单号是否存在，状态是否是可执行
    # 2. 倒序执行各个Item
    # 3. 更新form的状态
    # END
    # TODO 待实现
    # TODO 待测试
    return False


def belong_item_action(item: BelongRequestFormItem):
    """执行归属申请的调整

    1. 写入归属日志
    2. 更新归属表

    Args:
        item (BelongRequestFormItem): 执行任务

    Returns:
        bool, str: 归属结果，消息
    """
    # 根据不同类型，执行不同的归属调整，并记录变更日志

    # 客户号调整：
    # 1. 客户号必须存在，客户号必须是没有归属、归属到分行未落下
    # 2. 记录归属日志
    # 3. 更新客户号归属表
    # 4. 更新Item状态
    # END

    # 账号调整：
    # 1. 账号必须存在，账号必须是没有归属、归属到分行未落下
    # 2. 账号分成必须100%
    # 3. 记录归属日志
    # 4. 更新客户号归属表
    # 5. 更新Item状态
    # END
    
    # 账号调整：
    # 1. 账号必须存在，账号必须是没有归属、归属到分行未落下
    # 2. 账号分成必须100%
    # 3. 记录归属日志
    # 4. 更新客户号归属表
    # 5. 更新Item状态
    # END
    

    # TODO 待实现
    # TODO 待测试
    return False, "归属错误"


# if __name__ == "__main__":
#     with app.app_context():
#         # res = add_form_item(form_id="123", type=BelongRequestFormItem.TYPE_CUST,
#         #                     biz_id="12345", belongs=[{"dept_id": "00", "user_id": ""}])
#         res = add_form_item(form_id="12345", type=BelongRequestFormItem.TYPE_ACCT, biz_id="A00001", belongs=[
#                                     {"dept_id": "01", "user_id": 'zhangsan', "per": 60}, {"dept_id": "01", "user_id": 'user_1', "per": 40}])
#         print(res)
