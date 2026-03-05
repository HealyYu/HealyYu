import os
import json
from PyQt5.QtCore import QObject, pyqtSignal, QThread, pyqtSignal,QTimer
import sys
from linkkit import linkkit
import threading
import traceback
import inspect
import time
import logging
import os
import shutil
import time
import stat
from log import Logger
logger = Logger(__name__)
# 当前文件路径
# now_dir_path = os.path.dirname(os.path.realpath(sys.executable))
now_dir_path = os.path.dirname(os.path.realpath(sys.argv[0]))




class Mqtt_manger(QThread):
    cycle_publish_sign       = pyqtSignal(dict,dict)
    publish_coil_state_sign  = pyqtSignal(dict)    
    publish_offline_sign     = pyqtSignal(list)  
    control_IOmodle_sign     = pyqtSignal(dict)
    select_offline_data_sign = pyqtSignal(dict)
    updata_view_sign         = pyqtSignal(bool)
    __log_format = '%(asctime)s-%(process)d-%(thread)d - %(name)s:%(module)s:%(funcName)s - %(levelname)s - %(message)s'
    logging.basicConfig(format=__log_format)
    def __init__(self,config):
        super().__init__()  
        self.cycle_publish_sign.connect(self.updata_attribute_value)
        self.publish_coil_state_sign.connect(self.updata_coil_state)
        self.publish_offline_sign.connect(self.sql_send_data_to_mqtt)
        self.receive_attribute_enabled = False 
        self.mqtt_server_online = False 
        self.mqtt_subscribe_sign = False
        self.system_version = config['system_version']
        # 更新文件路径
        self.new_dir_path = os.path.join(now_dir_path, "update")
        # 老文件路径
        self.old_dir_path = os.path.join(now_dir_path, "old")
        self.file_name = '/test'
        self.__linkkit = linkkit.LinkKit(host_name      ="cn-shanghai",
                    product_key     =config["product_key"],
                    device_name     =config["device_name"],
                    device_secret   =config["device_secret"])
        self.config = config
        logger.info(config)
        self.__linkkit = linkkit.LinkKit(host_name      = self.config.get("host_name"),
                                         product_key     =self.config.get("product_key"),
                                        device_name     =self.config.get("device_name"),
                                        device_secret   =self.config.get("device_secret"))
        # self.__linkkit.enable_logger(logging.DEBUG)
        #self.__linkkit.thing_setup("tsl.json")
        self.__linkkit.thing_setup()  

        
        self.__linkkit.on_connect                   = self.on_connect
        self.__linkkit.on_disconnect                = self.on_disconnect
        self.__linkkit.on_topic_message             = self.on_topic_message
        self.__linkkit.on_subscribe_topic           = self.on_subscribe_topic
      
        self.__linkkit.on_publish_topic             = self.on_publish_topic
        self.__linkkit.on_thing_enable              = self.on_thing_enable
        self.__linkkit.on_thing_disable             = self.on_thing_disable
        self.__linkkit.on_thing_event_post          = self.on_thing_event_post
        self.__linkkit.on_thing_prop_post           = self.on_thing_prop_post
        self.__linkkit.on_thing_prop_changed        = self.on_thing_prop_changed
        self.__linkkit.on_thing_call_service        = self.on_thing_call_service
        self.__linkkit.on_thing_raw_data_post       = self.on_thing_raw_data_post
        self.__linkkit.on_thing_raw_data_arrived    = self.on_thing_raw_data_arrived
        self.__linkkit.on_ota_message_arrived       = self.on_ota_message_arrived
        
        self.__linkkit.connect_async()
        self.__linkkit.start_worker_loop()
        
        #self.__linkkit.config_mqtt(endpoint="iot-060a9lbb.mqtt.iothub.aliyuncs.com")
        #self.__linkkit.config_device_info("Eth|03ACDEFF0032|Eth|03ACDEFF0031")
        #self.__linkkit.config_mqtt(port=1883, protocol="MQTTv311", transport="TCP",secure="TLS")
       


    def on_connect(self, session_flag, rc, userdata):
        self.mqtt_server_online = True
        rc, mid = self.__linkkit.subscribe_topic(self.__linkkit.to_full_topic("user/offline_data")) 
        logger.info("on_connect",rc, mid )
        rc, mid = self.__linkkit.query_ota_firmware(module=self.system_version)
        pass
        # logger.info('获取云端设备固件信息',rc, mid )

    def on_disconnect(self, rc, userdata):
       self.mqtt_server_online = False

    def on_topic_message(self, topic, payload, qos, userdata):
        topic_name = topic.split('/')[-1]
        try:
            if topic_name == "offline_data":
                message = json.loads(payload)
                start_time  = message["st"]
                end_time    = message["et"]
                self.select_offline_data_sign.emit(start_time,end_time)
            elif topic_name == "config":
                with open(now_dir_path+'/view_config.json', 'r', encoding='utf-8') as file:
                    config_data = json.load(file)  # 加载原始配置数据

                new_value = json.loads(payload)          
                for key, value in new_value.items():
                    config_data[key] = value  # 更新对应键的数值

                with open(now_dir_path+'/view_config.json', 'w', encoding='utf-8') as file:
                    json.dump(config_data, file,ensure_ascii=False ,indent=4)  # 将更新后的数据写回文件
                self.updata_view_sign.emit(True)

        except Exception as e:
            logger.error(e)
                    

        

    def on_subscribe_topic(self, mid, granted_qos, userdata):
        logger.info("订阅消息成功 mid:%d, granted_qos:%s" %
              (mid, str(','.join('%s' % it for it in granted_qos))))
        self.mqtt_subscribe_sign = True
        


    def on_publish_topic(self, mid, userdata):
        logger.info("on_publish_topic mid:%d" % mid)

    def on_thing_prop_changed(self, params, userdata):  #修改属性命令
        self.control_IOmodle_sign.emit(params)

    def on_thing_enable(self, userdata):
        self.receive_attribute_enabled = True

    def on_thing_disable(self, userdata):
         self.receive_attribute_enabled = False

    def on_thing_event_post(self, event, request_id, code, data, message, userdata):
        logger.info("on_thing_event_post event:%s,request id:%s, code:%d, data:%s, message:%s" %
              (event, request_id, code, str(data), message))

    def on_thing_prop_post(self, request_id, code, data, message,userdata):
        logger.info("on_thing_prop_post request id:%s, code:%d, data:%s message:%s" %
              (request_id, code, str(data), message))

    def on_thing_raw_data_arrived(self, payload, userdata):
        logger.info("on_thing_raw_data_arrived:%s" % str(payload))

    def on_thing_raw_data_post(self, payload, userdata):
        logger.info("on_thing_raw_data_post: %s" % str(payload))

    def on_thing_call_service(self, identifier, request_id, params, userdata):
        logger.info("远程控制开关 identifier:%s, request id:%s, params:%s" %
              (identifier, request_id, params))
       

    def updata_attribute_value(self, electrical_energy,coild_Relays):

        try:
            logger.info("60秒标志周期完成")
            params = electrical_energy
            dict2 = coild_Relays
            #params.update(dict2)  # 将 dict2 合并到 dict1       
            if self.receive_attribute_enabled:
                self.__linkkit.thing_post_property(params) 
        except  Exception as e:
            logger.error('发布物模型数据失败，错误',e)
           

    def updata_coil_state(self, params):

        self.__linkkit.thing_post_property(params)
       
    def sql_send_data_to_mqtt(self,data):  # SQL数据库向MQTT 服务器发送离线数据
        try:
            self.__linkkit.publish_topic(self.__linkkit.to_full_topic("user/offline_data_reply"), json.dumps(data))
        except Exception as e:
            logger.error(e)
    def on_ota_message_arrived(self,ota_notice_type, version, size, url, sign_method, sign, module, extra):
        # ota_notice_type 为0，表示没有服务端没有部署ota任务；为1，表示云端下推的ota任务；为2，表示设备端自己主动向服务端查询ota任务
        logger.info('---------------------update---------------',version)
        # 版本检查
        try:
            state = self.compare_versions(version)
        except Exception as e:
            logger.error(e)
        if state == -1:
            logger.info('new-version:',version,"now-version",self.system_version)
        else:
            self.__linkkit.ota_report_version(module, self.system_version)
            pass
        
        if ota_notice_type > 0:
            # TODO: 用户判断版本号，决定是否要升级，以及何时升级
            # TODO: 如果固件的大下载耗时长，建议用户在这里起一个线程来处理，从而不阻塞整体链路。在这种情况下，如果用户在短时间内多次收到OTA消息
            #  （比如用户短期内多次主动请求OTA固件,或者收到平台主动推送的同时又自己主动请求固件），那么用户需要做好多线程之间的并发处理逻辑，
            #  避免多个线程同时写同一个文件
            logger.info("on_ota_message version:" + version + " size:" + str(size) + " url:" + url + " sign_method:" + sign_method)
            logger.info("on_ota_message sign:" + sign + " module:" + module + " extra:" + extra)
            # TODO: 修改firmware_path变量，将固件存储到需要用户自定义的路径
            # logger.info('222222222222222222222222222')
            try:
                if not os.path.exists(self.new_dir_path): os.makedirs(self.new_dir_path)
                ret = self.__linkkit.download_ota_firmware(url, self.new_dir_path+self.file_name, sign_method, sign)
            except Exception as e:
                logger.error(e)
            logger.info("333333333333333333333")
            
            if self.__linkkit.ErrorCode.SUCCESS == ret:
                # TODO: 用户部署新的固件，并上报新固件的版本号，确认升级完成
                #  
                logger.info("report version")
                # 当前版本文件备份
                try:
                    if not os.path.exists(self.old_dir_path): os.makedirs(self.old_dir_path)
                    # 等待备份文件
                    self.wait_for_copy(self.copy_file)
                    # 等待更新文件
                    self.wait_for_copy(self.update_file)
                    
                    # 系统重启
                    time.sleep(5)
                    # 获取当前解释器路径
                    p = sys.executable
                    # time.sleep(3)
                    # 启动新程序(解释器路径, 当前程序)
                    os.execl(p, p, *sys.argv)
                    # 关闭当前程序
                    sys.exit()
                    # 重启不成功 
                except Exception as e:
                    logger.error('更新失败', e)
                    try:
                        self.wait_for_copy(self.reload_app)
                        logger.error('复原成功')
                    except Exception as e:
                        logger.error('复原失败',e)    
                pass
            else:
                logger.error("download error code %x" % ret.value)
        else:
            logger.error("no firmware ")
    
        
    # 备份文件
    def copy_file(self):
        try:
            if os.path.exists(self.old_dir_path+self.file_name) :shutil.os.remove(self.old_dir_path+self.file_name)
            fd = shutil.copyfile(now_dir_path+self.file_name,self.old_dir_path+self.file_name) 
            logger.info('备份:copy_file',fd)
        except Exception as e:
            logger.error('备份er:',e)
    # 更新文件
    def update_file(self):
        try:
            if os.path.exists(now_dir_path+self.file_name) :shutil.os.remove(now_dir_path+self.file_name)
            fd = shutil.copyfile(self.new_dir_path+self.file_name,now_dir_path+self.file_name)
            os.chmod(fd,stat.S_IRWXU)
            logger.info('更新:update_fiel',fd)
        except Exception as e:
            logger.error('更新er:',e)
    # 还原文件
    def reload_app(self):
        try:
            shutil.os.remove(now_dir_path+self.file_name)
            fd = shutil.copyfile(self.old_dir_path+self.file_name,now_dir_path+self.file_name)
            logger.info('还原:reload_app',fd)
        except Exception as e:
            logger.error('还原er:',e) 
    # 同步处理文件函数
    def wait_for_copy(self,function):
        # 等待复制函数结束
        thread = threading.Thread(target=function)
        thread.start()
        thread.join()
    def compare_versions(self,version):
        # 当前系统版本
        v1 = list(map(int, self.system_version.split(".")))
        # 线上版本
        v2 = list(map(int, version.split(".")))
        logger.info('new-version:',v2,"now-version",v1)
        if v1 > v2:
            return 1
        elif v1 < v2:
            return -1
        else:
            return 0

    def run(self):
        while True:
            if self.mqtt_server_online  :
                logger.info("系统在线","mqtt server online")
            else:
                logger.error("系统离线","mqtt server offline")

            if self.mqtt_subscribe_sign:
                logger.info("系统订阅成功","mqtt subscribe success")
            else:
                logger.error("系统订阅失败","mqtt subscribe fail")
            time.sleep(180)











