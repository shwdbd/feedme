#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   CNStock.py
@Time    :   2022/07/06 10:27:46
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   中国A股参数
'''
import backtrader as bt


class CommInfoPro(bt.CommInfoBase):
    """ A股手续费 """

    params = (
        ('stamp_duty', 0.001),  # 印花税率
        ('stamp_duty_fe', 1),   # 最低印花税
        ('commission', 0.001),  # 佣金率
        ('commission_fee', 5),  # 最低佣金费
        ('stocklike', True),    # 股票
        ('commtype', bt.CommInfoBase.COMM_PERC),    # 按比例收
    )

    def _getcommission(self, size, price, pseudoexec):
        '''
        如果size大于0，表示买入
        如果size小于0，标识卖出
        If size is greater than 0, this indicates a long / buying of shares.
        If size is less than 0, it idicates a short / selling of shares.
        '''
        if size > 0:  # 买入，不考虑印花税
            return max(size * price * self.p.commission, self.p.commission_fee)
        elif size < 0:  # 卖出，考虑印花税
            return max(size * price * (self.p.stamp_duty + self.p.commission), self.p.stamp_duty_fe)
        else:
            return 0  # just in case for some reason the size is 0.
