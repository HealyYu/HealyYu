
import time
import struct
import json
import modbus_tk
import serial
import modbus_tk.defines as cst
from modbus_tk import modbus_rtu
import sys  # 导入 sys 模块，用于处理命令行参数和退出应用程
from PyQt5.QtCore import QObject, pyqtSignal, QThread, pyqtSignal
from log import Logger
logger = Logger(__name__)

class Energy_meter_interface(QThread):
    logger.debug("模块启动")
    Energy_meter_senddate_signal =pyqtSignal(dict,dict)#电表控制线程
    publish_energy_meter_event_signal = pyqtSignal(dict)
    def __init__(self, config_data):
        super().__init__()
        
        self.energy_meter_config     = config_data
        self.port                    = self.energy_meter_config.get("port")
        self.baudrate                = self.energy_meter_config.get("baudrate")
        self.bytesize                = self.energy_meter_config.get("bytesize")
        self.parity                  = self.energy_meter_config.get("parity")
        self.stopbits                = self.energy_meter_config.get("stopbits")
        self.timeout                 = self.energy_meter_config.get("timeout")
        self.energy_meters_config    = self.energy_meter_config.get("energy_meter_config")
        self.key_name                = self.energy_meter_config.get("key_name")
        self.energy_metter_quantity  = self.energy_meter_config.get("energy_metter_quantity")

        self.substation_addresses    = [d["substation_address"] for d in self.energy_meters_config]
        self.read_data_start_address = [d["data_start_address"] for d in self.energy_meters_config]
        self.pt_ratio_address        = [d["pt_ratio_address"]   for d in self.energy_meters_config]


        self.data_stack = [[0.0 for _ in range(13)] for _ in range(len(self.substation_addresses))]
        self.comm_state = [ 0   for _ in range(len(self.substation_addresses))]
        self.Energy_meters_current_history = []
        self.Energy_meters_values_list  ={"comm_state":{"EM_1":50,"EM_2":50,"IOMODEL_1":50,"IOMODEL_2":50} ,"EM_2_Voltage": {"Phase_A":0.0,"Phase_B":0.0,"Phase_C":0.0}}
        self.initialize_sign = False
        
        # 创建串口连接


    def read_registers(self, index=1):
        float_values = []
        sift_values=[0.0 for _ in range(13)]
        try:
            data = self.master.execute(self.substation_addresses[index], cst.READ_HOLDING_REGISTERS, self.read_data_start_address[index], 76)
            result =list(data)
            for i in range(0, len(result), 2):# 按大端序（big-endian）解析每两个寄存器中的数据为浮点数                
                float_value = struct.unpack('>f', struct.pack('>HH', data[i], data[i + 1]))[0]
                float_values.append(float_value)

            sift_values[1]  = round(float_values[0], 2)
            sift_values[2]  = round(float_values[1], 2)
            sift_values[3]  = round(float_values[2], 2)
            sift_values[4]  = round(float_values[3], 2)
            sift_values[5]  = round(float_values[4], 2)
            sift_values[6]  = round(float_values[5], 2)
            sift_values[7]  = round(float_values[25], 2)
            sift_values[8]  = round(float_values[26], 2)
            sift_values[9]  = round(float_values[27], 2)
            sift_values[10] = round(float_values[8], 2)
            sift_values[11] = round(float_values[9], 2)
            sift_values[12] = round(float_values[10], 2) 
            sift_values[0]  = 0
            self.comm_state[index] = 0              
            self.data_stack[index] =  sift_values
            
        except Exception as e:
                self.comm_state[index] += 1 
                self.data_stack[index][0]= self.comm_state[index]
                if self.comm_state[index] > 100 : 
                    self.comm_state[index] = 100                      
        finally:            
            if self.comm_state[index] == 0 :
                meter_dict = sift_values# 将提取出来的电表数据 转换成字典
            else:
                meter_dict =  self.data_stack[index]# 将提取出来的电表数据 转换成字典             
            return meter_dict 
        
    def read_CT_ratio(self, index=1):
        try:
            PT_data = self.master.execute(self.substation_addresses[index], cst.READ_HOLDING_REGISTERS, self.pt_ratio_address[index], 1)
            return (PT_data[0])
        except Exception as e:
            return(0)
    
    def energy_meter_event_check(self):
        try:           
            current_list = []
            for key,value in self.Energy_meters_values_list.items():
                for key_2, value_2 in value.items():
                    if "current" in key_2:
                        current_list.append(value_2)

            for i  in range(len(current_list) - 1):
                if current_list[i] > self.Energy_meters_current_history[i] * 3 and self.Energy_meters_current_history[i] < 2:
                    string_array = [str(element) for element in self.Energy_meters_current_history]
                    message = dict(zip(string_array,current_list))
                    self.publish_energy_meter_event_signal.emit(message)
                    break
            
            self.Energy_meters_current_history = current_list
        except:
                pass

    def read_EM_CT(self):
        CT_ratio_list = []
        CT_ratio_key  = []
        for i in range(self.energy_metter_quantity ):    
                CT_ratio = self.read_CT_ratio(index=i) #读互感器匝数比
                CT_ratio_list.append(CT_ratio)
                CT_ratio_key.append("EM_" + str(i+1) + "_CT")
        CT_Message = dict(zip(CT_ratio_key, CT_ratio_list))

        if CT_ratio_list[0] != 0:  
            self.initialize_sign = True
        return CT_Message

    def run(self):
        try:
            self.serial = serial.Serial(port        =self.port, 
                                        baudrate    =self.baudrate, 
                                        bytesize    =self.bytesize,
                                        parity      =self.parity, 
                                        stopbits    =self.stopbits, 
                                        timeout     =self.timeout)
            self.master = modbus_rtu.RtuMaster(self.serial)
            self.master.set_timeout(0.04)
        except Exception as e:
            logger.error(e)
        while True :           
            if self.initialize_sign == False :
                self.EM_CT_dir = self.read_EM_CT()

            for i in range(self.energy_metter_quantity ):    
                read_value = self.read_registers(index = i )#读电表数据

                if i== 0 :
                    self.Energy_meters_values_list["comm_state"]["EM_1"]   = read_value[0]
                    voltage = {}
                    voltage["Phase_A"] = read_value[1]
                    voltage["Phase_B"] = read_value[2]
                    voltage["Phase_C"] = read_value[3]                    
                    self.Energy_meters_values_list["EM_1_Voltage"]      = voltage
                    current = {}
                    current["Phase_A"] = read_value[4]
                    current["Phase_B"] = read_value[5]
                    current["Phase_C"] = read_value[6]
                    electrical_energy={}
                    electrical_energy["Phase_A"] = read_value[7]
                    electrical_energy["Phase_B"] = read_value[8]
                    electrical_energy["Phase_C"] = read_value[9]                 
                    power_factor ={}
                    power_factor["Phase_A"] = read_value[10]
                    power_factor["Phase_B"] = read_value[11]
                    power_factor["Phase_C"] = read_value[12]
                    self.Energy_meters_values_list["Main_Current"]              = current
                    self.Energy_meters_values_list["Main_Electrical_Energy"]    = electrical_energy
                    self.Energy_meters_values_list["Main_Power_Factor"]         = power_factor                   
                else:
                    if i== 8 :
                        self.Energy_meters_values_list["comm_state"]["EM_2"]    = read_value[0]
                        voltage = {}
                        voltage["Phase_A"] = read_value[1]
                        voltage["Phase_B"] = read_value[2]
                        voltage["Phase_C"] = read_value[3]                    
                        self.Energy_meters_values_list["EM_2_Voltage"]      = voltage   
                    
                    for j in range(3):
                        line_data = {}
                        line_data["current"]= read_value[4+j]
                        line_data["electrical_energy"] = read_value[7+j]
                        line_data["power_factor"] = read_value[10+j]
                        self.Energy_meters_values_list["line_" + str(3*i+j-2)] = line_data

                time.sleep(0.02)
            
            self.Energy_meter_senddate_signal.emit(self.Energy_meters_values_list,self.EM_CT_dir)
            self.energy_meter_event_check()

            time.sleep(0.02)





