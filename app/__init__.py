from flask import Flask, redirect, url_for
from flask_login import login_required
from .views import auth_view, admin_view
from app.views.ft_mis import belongs_view
from app.views.demo import file_upload
from .extensions import init_flask_login
from flask_sqlalchemy import SQLAlchemy
from .extensions import init_plugs
from .extensions.init_scripts import init_command


def create_app(test_config=None):
    # 创建Web应用

    app = Flask(__name__, instance_relative_config=True)
    # 加载配置文件
    app.config.from_object("app.config.settings")

    # 注册插件
    init_plugs(app)

    # 注册脚本
    init_command(app)

    # 注册权限机制
    init_flask_login.init_login_manager(app)

    # 添加Blueprint
    app.register_blueprint(auth_view.bp)
    app.register_blueprint(admin_view.bp)
    app.register_blueprint(belongs_view.bp)
    # 示例用bp
    app.register_blueprint(file_upload.bp)

    # 全局views
    @app.route('/hello')
    def hello():
        return 'Hello, World! Flask Ftmis App'

    @app.route('/')
    @login_required
    def index():
        """ 首页 """
        return redirect(url_for("auth.login"))

    return app


app = create_app()

# 注册数据库
db = SQLAlchemy()   # 数据库对象
db.init_app(app)
