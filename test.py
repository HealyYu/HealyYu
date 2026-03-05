# 开发第一个基于PyQt5的桌面应用

import sys
import copy
import json
import ast
import os
import re
from datetime import datetime, timedelta
from config import Global_Values
from PyQt5.QtWidgets import QApplication,QMainWindow,QVBoxLayout,QHBoxLayout
from PyQt5.QtCore import QObject, pyqtSignal, QThread,QTimer,QFile, QTextStream,QIODevice
from PyQt5 import QtGui
from ui.mainwindow_ui import*
from Energy_meters_manger import Energy_meter_interface
from IO_Modle_manger import ModbusRTUDevice
from Sqlite_Manger import Sqlmanger
from huawei_mqtt_Manger import Mqtt_manger
from power_btn_ui import QPowerButton
import random
from log import Logger
logger = Logger(__name__)
class MyMainWindow(QMainWindow,Ui_MainWindow):  # 继承 QMainWindow 类和 Ui_MainWindow 界面类

    def __init__(self):
        super().__init__()  # 初始化父类       
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint|QtCore.Qt.WindowStaysOnTopHint) #隐藏标题栏
        # self.setWindowFlags(QtCore.Qt.FramelessWindowHint) #隐藏标题栏
        # self.setWindowFlag() #隐藏标题栏
        #  Qt::FramelessWindowHint |Qt::WindowStaysOnTopHint|
        #self.setWindowFlags(QtCore.Qt.CustomizeWindowHint)#开放放大缩小功能
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)#背景透明
        self.Background_apps()#背景线程组（服务端线程组合）调用
        self.line_nums = Global_Values.view_config['line_nums']
        self.cycle_time = QTimer(self) #主线程定时任务计时器
        self.cycle_time.timeout.connect(self.cycle_tasks)#连接任务函数
        self.cycle_time.start(3000)#设置定时任务周期2000MS
        self.insert_sql_timer = QTimer(self) #定时备份数据库
        self.insert_sql_timer.timeout.connect(self.insert_Sql_task)
        self.insert_sql_timer.start(60000)
        self.updata_lable_timer = QTimer(self)
        self.updata_lable_timer.timeout.connect(self.updata_lable_task) #更新电表电压电流值
        self.updata_lable_timer.start(1000)
        self.diff_line_state_timer = QTimer(self)
        self.diff_line_state_timer.timeout.connect(self.diff_line_state)
        self.diff_line_state_timer.start(500)
        
        # 创建主垂直布局
        main_layout = self.ui.page_2.row
        # 绑定page-2,push事件
        total_buttons = self.line_nums
        buttons_list = [ ]
        for i in range(total_buttons):
            button = QPowerButton(i)
            button.setFixedSize(160,234)
            buttons_list.append(button)
            
            # 判断是否有线路名称,没有的花隐藏掉,不然后续更新会报错
            if self.is_hidden(Global_Values.view_config['line_{}_name'.format(i)]):
                # buttons_list[i].setVisible(False)
                # 设置透明度的值，0.0到1.0，最小值0是透明，1是不透明
                op = QtWidgets.QGraphicsOpacityEffect()
                op.setOpacity(0)
                buttons_list[i].setGraphicsEffect(op)
                # continue
        # 动态创建水平布局并添加按钮
        for i in range((total_buttons // 6) + (total_buttons % 6 > 0)):
            # 每行创建一个新的水平布局
            hbox = QHBoxLayout()
            # 将当前行的6个按钮添加到水平布局中
            for _ in range(min(6, total_buttons - (i * 6))):
                hbox.addWidget(buttons_list[i * 6 + _])
                # hbox.setGeometry(100, 100, 200, 50) 
            
            # 将当前行的水平布局添加到主垂直布局中
            main_layout.addLayout(hbox)
        
        for i in range(total_buttons): 
            setattr(self.ui.page_2,buttons_list[i].objectName(),buttons_list[i])
            if self.is_hidden(Global_Values.view_config['line_{}_name'.format(i)] ):continue
            buttons_list[i].clicked.connect(lambda i=i: self.change_light_state("ch0{}".format (i+1)) if i <10 else self.change_light_state("ch{}".format (i+1)))        
                

        # tab事件绑定
        for i in range(0,3): 
            ev = getattr(self.ui,"tab_{}_box".format(i))
            ev_icon = getattr(self.ui,"tab_{}".format(i))
            ev.clicked.connect(lambda i=i : self.change_tab_index(i))
            ev_icon.clicked.connect(lambda _,i=i : self.change_tab_index(i))
        
        self.ui.page_2.setStyleSheet(readQssFile())
        device_id = Global_Values.MQTT_Config["device_name"].split('_')
        self.ui.device_id.setText(device_id[1])
        self.ui.page_3.device_id.setText(device_id[1])
        self.ui.page_3.sys_version.setText(Global_Values.system_version)
        self.ui.page_3.site.setText(Global_Values.view_config['device_name'])
        self.ui.page_3.line_nums.setText(str(self.line_nums))
        self.ui.page_3.config_name.setText(Global_Values.view_config['config_name'])
        self.show()
        
    # 切换tab事件
    def change_tab_index(self,index):
        qss = readQssFile()
        self.ui.stackedWidget.setCurrentIndex(index)
        for i in range(0,3) :
            ev_icon = getattr(self.ui, 'tab_{}'.format(i))
            ev_name = getattr(self.ui, 'tab_{}_name'.format(i))
            ev_line = getattr(self.ui, 'tab_{}_line'.format(i))
            if index == i:
                ev_icon.setProperty('class', "tab_box_icon_action")
                ev_name.setProperty('class', "tab_box_name_action")
                ev_line.setProperty('class', "tab_box_line")
            else :
                ev_icon.setProperty('class', "tab_box_icon")
                ev_name.setProperty('class', "tab_box_name")
                ev_line.setProperty('class', "")
            ev_name.setStyleSheet(qss)
            ev_line.setStyleSheet(qss)
            ev_icon.setStyleSheet(qss)


        
    def Background_apps(self):#服务端线程组合
        global Global_Values
        Global_Values = Global_Values() #全局数据块

        self.energy_meter_interface = Energy_meter_interface( Global_Values.energy_meter_config_data) #创建Modbus_RTU通讯实体类                                                          
        self.energy_meter_interface.start()
        self.energy_meter_interface.Energy_meter_senddate_signal.connect(self.receive_energy_meters_data)#电表控制线程通讯
        self.energy_meter_interface.publish_energy_meter_event_signal.connect(self.publish_energy_meter_event)

        self.IOmodle_interface = ModbusRTUDevice( Global_Values.IOmodle_config_data)
        self.IOmodle_interface.start()
        self.IOmodle_interface.IOmodle_cycle_send_signal.connect(self.IOmodle_senddata_to_Global_Values) 
        self.IOmodle_interface.IOmodle_backup_states_sign.connect(self.IOmodle_send_history_data)
        

        self.sqlite_manger = Sqlmanger()
        self.sqlite_manger.start()
        self.sqlite_manger.send_data_to_global.connect(self.sql_send_data_to_Global)#周期性操作数据库
        self.sqlite_manger.send_offline_data_to_mqtt.connect(self.sql_send_data_to_mqtt)

        
        self.mqtt_manger =Mqtt_manger(Global_Values.MQTT_Config)
        self.mqtt_manger.start()
        self.mqtt_manger.control_IOmodle_sign.connect( self. mqtt_control_coil)
        self.mqtt_manger.select_offline_data_sign.connect(self.mqtt_select_offile_data)
        self.mqtt_manger.updata_view_sign.connect(self.mqtt_updata_view_config)
        self.mqtt_manger.select_switch_status_sign.connect(self.mqtt_select_switch_status)

    def receive_energy_meters_data(self, data1,data2):#电表数据反馈至全局变量
        # _data2 = {'EM_1_CT': -random.randint(0, 100), 'EM_2_CT': random.randint(0, 100), 'EM_3_CT': random.randint(0, 100), 'EM_4_CT': random.randint(0, 100), 'EM_5_CT': random.randint(0, 100)}
        # _data1 = self.renge_data()
        # print("data1", _data1)
        # print("data2", _data2)
        Global_Values.energy_meter_current_values = data1
        Global_Values.energy_meter_pt_ratio       = data2

    def publish_energy_meter_event(self,data): #电表事件反馈至MQTT服务器
        self.mqtt_manger.pulish_energy_meter_event_sign.emit(data)
        
    def IOmodle_senddata_to_Global_Values(self,data1):#IO模块状态反馈至全局变量
        Global_Values.colid_state =data1
        
    def IOmodle_send_history_data(self,data): #IO模块操作记录
        self.mqtt_manger.publish_coil_operate_sign.emit(data)
        self.sqlite_manger.uperdate_operate_history.emit(data)  

    def mqtt_select_offile_data(self,start_time,end_time):  #MQTT服务器查询离线数据  
        self.sqlite_manger.Mqtt_select_Sql_sign.emit(start_time,end_time)

    def mqtt_control_coil(self,params):#MQTT发布命令
        self.IOmodle_interface.IOmodle_receive_command_from_mqtt_sign.emit(params)
        
    def mqtt_select_switch_status(self,params):#查询全局变量表中的IOstaus
        self.mqtt_manger.pulish_switch_status_sign.emit(Global_Values.colid_state )

    def mqtt_updata_view_config(self,params):#MQTT更新视图
        with open('view_config.json',encoding='utf-8') as f:
            Global_Values.view_config  = json.load(f)
            Global_Values.energy_meter_config_data["energy_metter_quantity"] = Global_Values.view_config["energy_metter_quantity"]

    def sql_send_data_to_mqtt(self,data):  # SQL数据库向MQTT 服务器发送离线数据     
        self.mqtt_manger.publish_offline_sign.emit(data)
    def sql_send_data_to_Global(self,data):#sql数据库最新记录镜像到全局变量
        Global_Values.Sql_procese_data = list(data)
    def cycle_tasks(self): #主线程定时任务30秒 
        self.sqlite_manger.cycle_operaate_sql_sign.emit() #发起周期性查询    

    def insert_Sql_task(self): #主线程60秒任务插入SQL存储一条数据  ,向MQTT服务器发送一条镜像在SQL的数据
        # print('energy_meter_current_values======',Global_Values.energy_meter_current_values,)
        # print('colid_state======',Global_Values.colid_state)
        self.sqlite_manger.sql_insert_sign.emit(Global_Values.energy_meter_current_values,Global_Values.colid_state) #从全局数据块向数据库管理线程写入数据
        self.mqtt_manger.cycle_publish_sign.emit(Global_Values.energy_meter_current_values,Global_Values.colid_state) 
    
    # 更新线路状态
    def diff_line_state(self):
        current_state = Global_Values.colid_state
        # print('当前全局线路状态',current_state)
        list = ['线路关闭',"线路通畅","线路断开"]
        dict = ("off","open","close")
        # print(power_btn)
        for i in range(self.line_nums):
            # if self.is_hidden(Global_Values.view_config['line_{}_name'.format(i)]):continue
            power_btn = getattr(self.ui.page_2,'QPowerButton_{}'.format(i))
            # 当前状态
            # text = power_btn.line_state.text()
            # print(text)
            # 全局状态
            g_state = current_state['ch{}'.format("0"+str(i+1) if i<9 else str(i+1))]
            # print("全局",g_state, '数组:g_state',list[g_state],)
            # 判断状态是否一致
            # if list[g_state] != text :
            power_btn.changeStyles(dict[g_state])
            
    # 线路状态切换
    def change_light_state(self, key_name):
        
        current_state = Global_Values.colid_state[key_name]
        new_state = not bool(current_state)
        operate_code = {key_name: new_state}
        # print(current_state,new_state,operate_code,index)
        # box.setStyleSheet()
        self.IOmodle_interface.IOmodle_receive_command_from_mainwindow_sign.emit(operate_code)

    def updata_lable_task(self):#更新电表电压电流值
        try:
            if "line_1" in Global_Values.energy_meter_current_values:
                #print("更新电表电压电流值")
                page2 = getattr(self.ui,"page_{}".format(2))
                page1 = getattr(self.ui,"page_{}".format(1))
                for i in range(self.line_nums):
                    # if self.is_hidden(Global_Values.view_config['line_{}_name'.format(i)]):continue
                    
                    getattr(page2,'QPowerButton_{}'.format(i)).line_name.setText(Global_Values.view_config["line_{}_name".format(i)])
                    getattr(page1,'line_{}_name'.format(i)).setText(Global_Values.view_config["line_{}_name".format(i)])

                # count_electrical_energy = Global_Values.energy_meter_current_values["line_1"]['electrical_energy'] + Global_Values.energy_meter_current_values["line_2"]['electrical_energy'] +Global_Values.energy_meter_current_values["line_3"]['electrical_energy'] 
                # self.ui.page_1.label_4.setText('总用电量 : '+str(count_electrical_energy))
                self.ui.page_1.total_a_v.setText(str(Global_Values.energy_meter_current_values["EM_1_Voltage"]['Phase_A'])+"V")
                self.ui.page_1.total_b_v.setText(str(Global_Values.energy_meter_current_values["EM_1_Voltage"]['Phase_B'])+"V")
                self.ui.page_1.total_c_v.setText(str(Global_Values.energy_meter_current_values["EM_1_Voltage"]['Phase_C'])+"V")

                self.ui.page_1.total_a_e.setText(str(Global_Values.energy_meter_current_values["Main_Current" ]["Phase_A"])+"A")
                self.ui.page_1.total_b_e.setText(str(Global_Values.energy_meter_current_values["Main_Current" ]["Phase_B"])+"A")
                self.ui.page_1.total_c_e.setText(str(Global_Values.energy_meter_current_values["Main_Current" ]["Phase_C"])+"A")

                self.ui.page_1.total_a_used.setText(str(Global_Values.energy_meter_current_values["Main_Electrical_Energy"]["Phase_A"])+"Kw.h")
                self.ui.page_1.total_b_used.setText(str(Global_Values.energy_meter_current_values["Main_Electrical_Energy"]["Phase_B"])+"Kw.h")
                self.ui.page_1.total_c_used.setText(str(Global_Values.energy_meter_current_values["Main_Electrical_Energy"]["Phase_C"])+"Kw.h")

                for i in range(0,12):
                    getattr(self.ui.page_1,"line_{}_used".format(i)).setText("{}Kw.h".format(Global_Values.energy_meter_current_values['line_{}'.format(i+1)]['electrical_energy']) )  
                    getattr(self.ui.page_1,"line_{}_e".format(i)).setText("{}A".format(Global_Values.energy_meter_current_values['line_{}'.format(i+1)]['current']) ) 
                        
        except Exception as e:
            logger.error("更新电表电压电流值失败:{}".format(e))
            pass
    def is_hidden(self,s:str):
        white_list  = [r'安防']
        pattern = re.compile("|".join(white_list))
        pattern.search(s)
        # print('正则匹配',pattern.search(s))
        return pattern.search(s)
def readQssFile():
    # 获取当前执行文件所在目录
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS  # 对于 PyInstaller 打包后的单文件或单个目录模式
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))  # 对于未打包的开发环境

    file = QFile(os.path.join(base_path, 'ui/main.qss'))
    # print('====================file')
    # print(file)
    if not file.open(QIODevice.ReadOnly | QIODevice.Text):
        logger.error("Failed to open the file")
    else:
        try:
            stream = QTextStream(file)
            # 使用文本流读取或写入数据...
            content = stream.readAll()
            # 处理 content...
            return content
        finally:
            file.close()  # 确保文件最终会被关闭

if __name__ == '__main__':
    logger.debug('======程序启动======')
    app = QApplication(sys.argv)  # 在 QApplication 方法中使用，创建应用程序对象
    myWin = MyMainWindow()  # 实例化 MyMainWindow 类，创建主窗口

    qssStyles = readQssFile()
    # print('=============================qssStyles')
    # print(qssStyles)
    app.setStyleSheet(qssStyles)
    sys.exit(app.exec_())  # 结束进程，退出程序
