

from PyQt5.QtCore import QObject, pyqtSignal, QThread, pyqtSignal,QTimer
import sys
import time
from datetime import datetime
import json
import os
from iot_device_sdk_python.client.client_conf import ClientConf
from iot_device_sdk_python.client.connect_auth_info import ConnectAuthInfo
from iot_device_sdk_python.client.request.device_message import DeviceMessage
from iot_device_sdk_python.client.request.service_property import ServiceProperty
from iot_device_sdk_python.transport.raw_message import RawMessage
from iot_device_sdk_python.transport.raw_message_listener import RawMessageListener
from iot_device_sdk_python.client.listener.default_publish_action_listener import DefaultPublishActionListener
from iot_device_sdk_python.iot_device import IotDevice, OTAService
from huawei_ota import OTASampleListener
from log import Logger
logger = Logger(__name__)

import queue
now_dir_path = os.path.dirname(os.path.realpath(sys.argv[0]))


class MyMessageListener(RawMessageListener):

    def __init__(self, q):
        self._q:queue.Queue = q

    def on_message_received(self, message: RawMessage):
        logger.debug("收到订阅消息")
        self._q.put(message)


class Mqtt_manger(QThread ):
    cycle_publish_sign              = pyqtSignal(dict,dict)
    publish_coil_operate_sign       = pyqtSignal(dict)
    publish_offline_sign            = pyqtSignal(dict)
    pulish_energy_meter_event_sign  = pyqtSignal(dict)
    control_IOmodle_sign            = pyqtSignal(dict)
    select_offline_data_sign        = pyqtSignal(int,int)
    updata_view_sign                = pyqtSignal(bool)
    select_switch_status_sign       = pyqtSignal(bool)    
    pulish_switch_status_sign       = pyqtSignal(dict)   
    
    def __init__(self,config):
        super().__init__() 
        self.logger = logger 
        self.cycle_publish_sign.connect(self.updata_attribute_value)
        self.publish_coil_operate_sign.connect(self.publish_coil_operate_state)
        self.publish_offline_sign.connect(self.sql_send_data_to_mqtt)
        self.pulish_energy_meter_event_sign.connect(self.pulish_energy_meter_event)
        self.pulish_switch_status_sign.connect(self.pulish_switch_status)

        self.receive_attribute_enabled  = False 
        self.mqtt_server_online         = False 
        self.mqtt_subscribe_sign        = False
        self.command_id                 =""
        self.system_version         = config['system_version']   
        self.server_uri             = config['huawei_iot_server_uri']
        self.port                   = 8883
        self.iot_cert_file_path     = now_dir_path + "/resources/GlobalSignRSAOVSSLCA2018.crt.pem"

        self.connect_auth_info               = ConnectAuthInfo()
        self.connect_auth_info.server_uri    = self.server_uri
        self.connect_auth_info.port          = self.port
        self.connect_auth_info.id            = config.get("device_name")
        self.connect_auth_info.secret        = config.get("device_secret")
        self.connect_auth_info.iot_cert_path = self.iot_cert_file_path
        self.connect_auth_info.bs_mode       = ConnectAuthInfo.BS_MODE_DIRECT_CONNECT
        self._q = queue.Queue()
        self.listen = MyMessageListener(self._q)
    def sql_send_data_to_mqtt(self,data):  # SQL数据库向MQTT 服务器发送离线数据
        try:
            my_topic = "$oc/devices/"+self.connect_auth_info.id  +"/user/offline_data_reply"
            self.device.get_client().publish_raw_message(RawMessage(my_topic, json.dumps( data)))
            logger.debug("发送离线数据成功")
        except Exception as e:
            logger.error("发送离线数据失败:{}".format(e))

    def publish_coil_operate_state(self,data):
        try:
            message_list = {}
            if self.command_id != "":
                message_list["id"] = self.command_id
            message_list["state"] = data
            my_topic = "$oc/devices/"+self.connect_auth_info.id  +"/user/switch_reply"
            self.device.get_client().publish_raw_message(RawMessage(my_topic, json.dumps(message_list)))
            self.command_id = ""
            logger.debug("发送操作回执成功")
        except Exception as e:
            logger.error("发送操作回执失败:{}".format(e))
            
    def pulish_switch_status(self,data):
        try:
            my_topic = "$oc/devices/"+self.connect_auth_info.id  +"/user/switch_status_reply"
            self.device.get_client().publish_raw_message(RawMessage(my_topic, json.dumps( data)))
            logger.debug("发送全部IO状态成功")
        except Exception as e:
            logger.error("发送全部IO状态失败:{}".format(e))       
        

    def pulish_energy_meter_event(self,data):
        try:
            my_topic = "$oc/devices/"+self.connect_auth_info.id  +"/user/energy_meter_event"
            self.device.get_client().publish_raw_message(RawMessage(my_topic, json.dumps( data)))
            logger.debug("发送电表异常数据成功")
        except Exception as e:
            logger.error("发送电表异常数据失败:{}".format(e))

    def updata_attribute_value(self,data1,data2):
        try: 
            self.logger.info("begin report message")
            send_message = data1
            send_message["comm_state"]["IOMODEL_1"] = data2["comm1_state"]
            send_message["comm_state"]["IOMODEL_2"] = data2["comm2_state"]
            service_property = ServiceProperty()
            service_property.service_id = 'line_data'
            service_property.properties = send_message
            services = [service_property]
            self.device.get_client().report_properties(services, DefaultPublishActionListener())
            logger.debug("更新数据成功")
        except Exception as e:
            logger.error("更新数据出错:{}".format(e))
    

    def run(self):
        self.client_conf    = ClientConf(self.connect_auth_info)
        self.device         = IotDevice(self.client_conf)
        # self.ota            = OTASampleListener(self.client_conf,self.system_version)          
        ota_service: OTAService = self.device.get_ota_service()
        ota_service_listener = OTASampleListener(ota_service,self.system_version)
        ota_service.set_ota_listener(ota_service_listener)
        # self.device.get_client().set_ota_listener(self.ota)              
        if self.device.connect() != 0:
            self.logger.error("init failed")
            return
        #self.device.get_client().set_raw_device_msg_listener(RawDeviceMsgListener())
        my_topic = "$oc/devices/"+self.connect_auth_info.id  +"/user/offline_data"
        self.device.get_client().subscribe_topic(my_topic, 1, self.listen)
        my_topic = "$oc/devices/"+self.connect_auth_info.id  +"/user/config"
        self.device.get_client().subscribe_topic(my_topic, 1, self.listen)        
        my_topic = "$oc/devices/"+self.connect_auth_info.id  +"/user/switch"
        self.device.get_client().subscribe_topic(my_topic, 1, self.listen)  
        my_topic = "$oc/devices/"+self.connect_auth_info.id  +"/user/switch_status"
        self.device.get_client().subscribe_topic(my_topic, 1, self.listen)  

        while True:
            
            subscribe_message = self._q.get()
            try:
                topic = subscribe_message.topic
                topic_name = topic.split('/')[-1]      
                message_str = subscribe_message.payload.decode('utf-8')
                message_list = json.loads(message_str)
                message = message_list["content"]
                order_ID = message_list["id"]

                if topic_name == "offline_data"  :     
                    start_time  = message["st"]
                    end_time    = message["et"]          
                    self.select_offline_data_sign.emit(start_time,end_time)
                elif topic_name == "config":
                    with open(now_dir_path+'/view_config.json', 'r', encoding='utf-8') as file:
                        config_data = json.load(file)  # 加载原始配置数据
                    
                    for key, value in message.items():
                        config_data[key] = value  # 更新对应键的数值

                    with open(now_dir_path+'/view_config.json', 'w', encoding='utf-8') as file:
                        json.dump(config_data, file,ensure_ascii=False ,indent=4)  # 将更新后的数据写回文件
                        self.updata_view_sign.emit(True)
                elif topic_name == "switch":
                    logger.debug("收到开关指令",message)
                    logger.debug(type(message))
                    this_time              = int( datetime.now().timestamp())
                    if message.get("timestamp") >= this_time - 5 :
                        self.control_IOmodle_sign.emit(message.get("switch"))
                        self.command_id = order_ID
                        logger.debug(self.command_id)
                elif topic_name == "switch_status":
                    self.select_switch_status_sign.emit(True)

            except Exception as e:
                logger.error("数据解析出错:{}".format(e))


