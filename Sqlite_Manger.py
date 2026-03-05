
import os
import sqlite3
from datetime import datetime
import json
import time
from log import Logger
logger = Logger(__name__)


from PyQt5.QtCore import QObject, pyqtSignal, QThread, pyqtSignal,QTimer


class Sqlmanger(QThread):  
   

    sql_insert_sign             = pyqtSignal(dict,dict)
    send_data_to_global         = pyqtSignal(tuple)
    send_offline_data_to_mqtt   = pyqtSignal(dict)
    cycle_operaate_sql_sign     = pyqtSignal()
    Mqtt_select_Sql_sign        = pyqtSignal(int,int)
    uperdate_operate_history    =pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.sql_insert_sign.connect(self.SQL_insert_data) 
        self.cycle_operaate_sql_sign.connect(self.cycle_operaate_SQL)
        self.Mqtt_select_Sql_sign.connect(self.mqtt_select_data)
        self.uperdate_operate_history.connect(self.uperdate_coil_operate_history)

        self.SQL_max_records = 4500
        self.coil_operate_history = {}
        #self.db_path = 'D:\\meter_sql\\example.db'  #数据库路径
        self.db_path = 'example.db' 
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.create_table()
    
        #self.cycle_updata_sign.connect(self.receive_values)  # 将定时器的超时信号连接到更新UI的槽函数

    def uperdate_coil_operate_history(self,data):
        self.coil_operate_history.update(data) 


    def create_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS data 
                               (time_ID INTEGER PRIMARY KEY, 
                                timestamp TEXT,
                                energy_meter_value TEXT, 
                                iomodle_value TEXT     
                                
                                 )''')
        self.conn.commit()
    
    def SQL_insert_data(self,data1,data2):         
        this_time               =  datetime.now()
        timestamp_minutes       = int(this_time .timestamp()) //60    # 将时间转换为时间戳（精确到秒）
        self.this_time_str      = this_time .strftime("%Y-%m-%d %H:%M")
        self.this_times_tamp    = timestamp_minutes * 60 

        energy_meter_data     = data1

        energy_meter_data["comm_state"]["IOMODEL_1"] = data2["comm1_state"]
        energy_meter_data["comm_state"]["IOMODEL_2"] = data2["comm2_state"]

        self.energy_meter_value = json.dumps(energy_meter_data)
 
        self.iomodle_value      = json.dumps(self.coil_operate_history)

        values_to_insert = (self.this_times_tamp,  self.this_time_str  , self.energy_meter_value,  self.iomodle_value )
        insert_query = '''INSERT INTO data (time_ID ,timestamp, energy_meter_value , iomodle_value ) VALUES (?, ?, ?, ?)'''
 
        try:
            self.cursor.execute(insert_query, values_to_insert)
            self.conn.commit()
        except Exception as e:# 在发生异常时返回一个错误值 
            logger.error("数据库写入失败:{}".format(e))   
        finally:
            self.coil_operate_history = {}   

    def cycle_operaate_SQL(self):
        try:
            self.cursor.execute("SELECT COUNT(*) FROM data")
            count= self.cursor.fetchone()[0]
            if  (count is not None ) and  count >= self.SQL_max_records:     
                self.cursor.execute("SELECT MIN(time_ID) FROM data")
                earliest_timestamp = self.cursor.fetchone()[0]
                self.cursor.execute("DELETE FROM data WHERE time_ID = ?", (earliest_timestamp,))# 删除最早时间戳对应的记录
                self.conn.commit()# 提交更改并关闭连接
        except Exception as e :
            logger.error("SQL删除历史数据错误:{}".format(e))

        try:
            self.cursor.execute("SELECT MAX(time_ID) FROM data")
            latest_timestamp = self.cursor.fetchone()[0]
            self.cursor.execute("SELECT * FROM data WHERE time_ID = ?", (latest_timestamp,))# 查询最新记录
            latest_record = self.cursor.fetchone()
            self.send_data_to_global.emit(latest_record)
        except Exception as e :
            latest_record =[0,'','',''] 
            #logger.error("SQL查询最新数据错误",e)
      
    def mqtt_select_data (self,start_time,end_time):
        try:
            self.cursor.execute("SELECT * FROM data WHERE time_ID BETWEEN ? AND ?", (start_time, end_time))
            records_within_time_range = self.cursor.fetchall()
            message = list(records_within_time_range)
            time_stamp =[]
            value_list =[]
            for i in range(len(message)):
                time_stamp.append(str(message[i][0]))
                values = {"EM_values":message[i][2],"iomodle_value":message[i][3]}
                value_list.append(values)

            data_dir = dict(zip(time_stamp,value_list))  
            
            data_json = json.dumps(data_dir) 
            # print(type(data_json))
            # print(data_json)

            self.send_offline_data_to_mqtt.emit(data_dir)        
        except Exception as e :
            logger.error("采集离线数据错误:{}".format(e))
        # records_within_time_range 中包含了在指定时间范围内的记录数据,e


    def close_connection(self):
        self.cursor.close()
        self.conn.close()

          






    
























