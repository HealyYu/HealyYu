

import modbus_tk
import serial
import modbus_tk.defines as cst
from modbus_tk import modbus_rtu
import time
import struct
import json
from PyQt5.QtCore import QObject, pyqtSignal, QThread, pyqtSignal
from log import Logger
logger = Logger(__name__)


class ModbusRTUDevice(QThread):
    IOmodle_backup_states_sign        = pyqtSignal(dict)
    IOmodle_cycle_send_signal         = pyqtSignal(dict)
    IOmodle_receive_command_from_mainwindow_sign = pyqtSignal(dict)
    IOmodle_receive_command_from_mqtt_sign       = pyqtSignal(dict)
    
    def __init__(self, config_data):
        super().__init__()  
        self.IOmodle_receive_command_from_mainwindow_sign.connect(self.IOmodle_operate_code)
        self.IOmodle_receive_command_from_mqtt_sign.connect(self.IOmodle_operate_code)

        self.port            = config_data.get("port")
        self.baudrate        = config_data.get("baudrate")
        self.bytesize        = config_data.get("bytesize")
        self.parity          = config_data.get("parity")
        self.stopbits        = config_data.get("stopbits")
        self.timeout         = config_data.get("timeout")
        self.coil_name_list  = config_data.get("coil_name_list")
        
        self.coil_stack         = [[0 for _ in range(16)] for _ in range(2)]
        self.actual_comm_state  = [0,0]
        self.actual_coil_states = [ 0  for _ in range(32)]
        self.coil_operate_code  = [ 0  for _ in range(32)]
        self.first_can          = 2
        
    def read_coil_state(self, index,station_address,value_point_address,number_of_registers):
        try:
            data = self.master.execute(station_address, cst.READ_COILS, value_point_address, number_of_registers)
            self.actual_comm_state[index] = 0              
            self.coil_stack [index] =  list(data)     
        except Exception as e:
            self.actual_comm_state[index ] += 1 
            if self.actual_comm_state[index] > 100 : 
                self.actual_comm_state[index] = 100              
        finally:  
            return self.coil_stack [index]
            
        

    def write_command(self, station_address,value_point_address,order):
        try:
            self.master.execute(station_address, cst.WRITE_SINGLE_COIL, value_point_address, output_value = order)
        except Exception as e:
            pass
            #logger.error(f"写入数据时出错: {e}")

    def check_dict_key(self,dictionary, key):
        if key in dictionary:
            if dictionary[key] is True:
                return 2
            elif dictionary[key] is False:
                return 1
            elif dictionary[key] is 1:
                return 2
            elif dictionary[key] is 0:
                return 1



        return None  # 如果键不存在或者键值不是布尔类型，返回None或者你认为合适的默认值
    def IOmodle_operate_code(self,data):
        logger.info("收到命令:{}".format(data))
        for i in range(32):   
                order = self.check_dict_key(data, self.coil_name_list[i])
                if   order == 1:
                    self.coil_operate_code[i] = 1
                elif order == 2:
                    self.coil_operate_code[i] = 2


    def run(self):
        try:
            self.serial = serial.Serial(port=self.port, baudrate=self.baudrate, bytesize=self.bytesize , parity=self.parity , stopbits=self.stopbits, timeout=self.timeout)
            self.master = modbus_rtu.RtuMaster(self.serial)
            self.master.set_timeout(self.timeout)
        except Exception as e:
            logger.error(e)


        while True :
            #读操作码并执行modbus写线圈操作
            for i in range(32):       
                if self.coil_operate_code[i] == 2 :
                    operate_code = 1
                else:
                    operate_code = 0
                
                if self.coil_operate_code[i] != 0 :
                    if i <= 15 :
                        self.write_command (station_address = 1,value_point_address = i,   order = operate_code )
                    elif i > 15 and i>32 : 
                        self.write_command(station_address = 2,value_point_address = i, order = operate_code )
            #读线圈状态
            bool_array_L = self.read_coil_state(index =0,station_address = 1,value_point_address = 0, number_of_registers = 16)
            bool_array_H =[ 0 for _ in range(16)]
            #bool_array_H = self.read_coil_state(index =1,station_address = 2,value_point_address = 0, number_of_registers = 16)
            self.actual_coil_states = bool_array_L + bool_array_H 
            
            #清理完成操作过程的操作码
            operate_history= {}
            for i in range(32): 
                if self.coil_operate_code[i] == 1  and  self.actual_coil_states[i] == 0 :
                    self.coil_operate_code[i] = 0 
                    operate_history[self.coil_name_list[i]] = 0

                if self.coil_operate_code[i] ==2  and  self.actual_coil_states[i] == 1 :
                    self.coil_operate_code[i] = 0  
                    operate_history[self.coil_name_list[i]] = 1
            
            if operate_history!= {} and self.first_can > 6:
                self.IOmodle_backup_states_sign.emit(operate_history)

            #整合状态合并成字典，发送给主线程
            IOmodle_state =  self.actual_coil_states + self.actual_comm_state 
            meter_dict = dict(zip(self.coil_name_list, IOmodle_state))
            self.IOmodle_cycle_send_signal.emit(meter_dict)
            
            if self.first_can <= 6 : #上电初始化继电器状态与实际值状态
                for i in range(len(bool_array_L)) :
                
                    if bool_array_L[i] == 0:
                        self.coil_operate_code[i] = 1
                    elif bool_array_L[i] == 1:
                        self.coil_operate_code[i] = 2
                self.first_can += 1
                logger.info("初始化完成")
                
            # logger.info("时间",self.first_can)
            time.sleep(0.1)






