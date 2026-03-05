
import os
import json
import sys
class Global_Values:
    def __init__(self):
        self.energy_meter_current_values ={}
        self.energy_meter_pt_ratio = {}
        self.colid_state ={}
        self.Sql_procese_data = []
        self.MQTT_Config = {}
        self.view_config = {}
        self.view_load_command = False
        self.system_version  = "1.0.21"

        """ 
        self.MQTT_Config = {"host_name"  :"cn-shanghai",
                        "product_key"    :"k0nkq6hdCVJ",
                        "device_name"     :"wf20231216001",
                        "device_secret"   :"1da4d556235f43c20976658815230e31"} 

        self.MQTT_Config = {"host_name"  :"cn-shanghai",
                        "product_key"    :"k0nkq4tDbMd",
                        "device_name"     :"test",
                        "device_secret"   :'0a1784c0f16a1206c7c39fd58bf46fdb'} """


        self.energy_meter_config_data= {"port"     :'/dev/ttyS3',
                                        "baudrate" : 9600 ,
                                        'bytesize' : 8,
                                        "parity"   : 'N', 
                                        "stopbits" : 1, 
                                        "timeout"  : 0.02,
                                        "energy_metter_quantity": 12,
                                        
                                        "key_name" : ['comm_state','Phase_A_voltage', 'Phase_B_voltage', 'Phase_C_voltage', 
                                                                    'Phase_A_current', 'Phase_B_current', 'Phase_C_current',
                                                    'Phase_A_electrical_energy','Phase_B_electrical_energy','Phase_C_electrical_energy',
                                                    'Phase_A_power_factor',     'Phase_B_power_factor',     'Phase_C_power_factor'] ,

                                        "energy_meter_config": [{"substation_address":1,"data_start_address":112 , "pt_ratio_address":42},
                                                                {"substation_address":1,"data_start_address":214 , "pt_ratio_address":43},
                                                                {"substation_address":1,"data_start_address":316 , "pt_ratio_address":44},
                                                                {"substation_address":1,"data_start_address":418 , "pt_ratio_address":45},
                                                                {"substation_address":1,"data_start_address":520 , "pt_ratio_address":46},
                                                                {"substation_address":1,"data_start_address":622 , "pt_ratio_address":47},
                                                                {"substation_address":1,"data_start_address":756 , "pt_ratio_address":48},
                                                                {"substation_address":1,"data_start_address":858 , "pt_ratio_address":49},
                                                                {"substation_address":2,"data_start_address":112 , "pt_ratio_address":42},
                                                                {"substation_address":2,"data_start_address":214 , "pt_ratio_address":43},
                                                                {"substation_address":2,"data_start_address":316 , "pt_ratio_address":44},
                                                                {"substation_address":2,"data_start_address":418 , "pt_ratio_address":45}] }
                                    
        self.IOmodle_config_data= {"port"      : '/dev/ttyS4',
                                    "baudrate" : 9600 ,
                                    'bytesize' : 8,
                                    "parity"   :'N', 
                                    "stopbits" :1, 
                                    "timeout"  :0.1,

                                    "coil_name_list" :['ch12','ch11','ch10','ch09','ch08','ch07','ch06','ch05','ch04','ch03','ch02','ch01','ch13','ch14',
                                                        'ch15','ch16','ch17','ch18','ch19','ch20','ch21','ch22','ch23','ch24','ch25','ch26','ch27','ch28',
                                                        'ch29','ch30','ch31','ch32',"comm1_state","comm2_state"] }
    

        self.getSn()
    def getSn(self):
        now_dir_path = os.path.dirname(os.path.realpath(sys.argv[0]))

        with open(now_dir_path+'/device_ID.json',encoding='utf-8') as f:
            self.MQTT_Config = json.load(f)
            self.MQTT_Config['system_version'] = self.system_version
        with open(now_dir_path+'/view_config.json',encoding='utf-8') as f:
            self.view_config  = json.load(f)
            self.energy_meter_config_data["energy_metter_quantity"] = self.view_config["energy_metter_quantity"]
            







