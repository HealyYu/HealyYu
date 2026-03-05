import logging
import os
import sys
log_level = os.environ.get('LOG_LEVEL', 'ERROR').upper()
now_dir_path = os.path.dirname(os.path.realpath(sys.argv[0]))

def Logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] [%(filename)s] [%(threadName)s] [line:%(lineno)d] [%(funcName)s] %(message)s')
    # 检查是否有log文件夹,没有就创建
    if os.path.exists(now_dir_path+'/log') == False : os.mkdir(now_dir_path+'/log')
    # if os.path.exists(now_dir_path+'/log') : os.mkdir(now_dir_path+'/log')
    fileHandler = logging.FileHandler(now_dir_path+'/log/device_{}.log'.format(name))  # 如果希望将日志输出到文件，创建FileHandler
    fileHandler.setLevel(log_level)
    fileHandler.setFormatter(formatter)
    handler = logging.StreamHandler()
    handler.setLevel(log_level)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.addHandler(fileHandler)
    return logger
