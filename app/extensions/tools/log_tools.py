
import logging.config


# =============================================
# 日志
# 使用方式：log.info('xxxx')
def get_logger():
    """返回日志记录器
    """
    config_file_path = r'config/log.cfg'

    logging.config.fileConfig(config_file_path)
    return logging.getLogger('ftmis')


logger = get_logger()


if __name__ == "__main__":
    logger.info("This is info")
