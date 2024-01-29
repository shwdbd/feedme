import logging


class DispatchingFormatter:

    def __init__(self, formatters, default_formatter):
        """初始化

        Args:
            formatters (_type_): 日志名与日志格式的对照
            default_formatter (_type_): 默认日志格式
        """
        self._formatters = formatters
        self._default_formatter = default_formatter

    def format(self, record):
        """ 继承函数 """
        # print(record)
        formatter = self._formatters.get(record.name, self._default_formatter)
        return formatter.format(record)


handler = logging.StreamHandler()
handler.setFormatter(DispatchingFormatter({
    'base.foo': logging.Formatter('FOO: %(message)s'),
    'base.bar': logging.Formatter('BAR: %(message)s'),
    'group': logging.Formatter('GROUP: %(message)s %(name)s'),
    'action': logging.Formatter('ACTION: %(message)s %(name)s'),
},
    logging.Formatter('%(message)s'),
))
logging.getLogger().addHandler(handler)


group_log = logging.getLogger('group')
group_action = logging.getLogger('action')


logging.getLogger('base.foo').error('Log from foo')
logging.getLogger('base.bar').error('Log from bar')
logging.getLogger('base.baz').error('Log from baz')

group_log.error("xxxxx")
group_action.error("111111")
group_log.error("yyyyy")
group_action.error("222222")
