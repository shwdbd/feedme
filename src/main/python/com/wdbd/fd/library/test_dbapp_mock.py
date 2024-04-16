#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   test_dbapp_mock.py
@Time    :   2024/04/11 09:25:43
@Author  :   Jeffrey Wang
@Version :   1.0
@Contact :   shwangjj@163.com
@Desc    :   使用Mock测试使用SQLAlchemy的数据库应用程序
'''
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import unittest
from unittest.mock import Mock, patch


# 定义SQLAlchemy模型
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)


# 创建数据库引擎和会话
engine = create_engine('sqlite:///test.db')
Session = sessionmaker(bind=engine)


# 函数：根据ID获取用户信息
def get_user_by_id(session, user_id):
    """ 通过用户ID获取用户信息 """
    user = session.query(User).filter(User.id == user_id).first()
    session.close()
    return user


class TestGetUser(unittest.TestCase):
    """ 单元测试 """

    def test_get_user_by_id(self):
        # 创建一个模拟的session对象
        mock_session = Mock()
        # 创建一个模拟的User对象
        mock_user = Mock(spec=User)
        mock_user.id = 1
        mock_user.name = 'Mock User'

        # 当调用session.query(User).filter(User.id == user_id).first()时，返回模拟的User对象
        mock_session.query.return_value.filter.return_value.first.return_value = mock_user

        # 使用patch装饰器来替换真实的session对象
        with patch('com.wdbd.fd.library.test_dbapp_mock.Session') as mock_session_class:
            mock_session_class.return_value = mock_session

            # 调用get_user_by_id函数, 传入模拟的session对象和用户ID
            user = get_user_by_id(mock_session, 1)

            # 验证返回的用户对象是否正确
            self.assertEqual(user.id, 1)
            self.assertEqual(user.name, 'Mock User')

            # 验证session.close()被调用
            mock_session.close.assert_called_once()


if __name__ == '__main__':
    unittest.main()
