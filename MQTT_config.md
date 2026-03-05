# 设备-服务端通信

# 实时上报数据
* Topic: $oc/devices/{device_id}/sys/gateway/sub_devices/properties/report
* 数据上报格式:
{

      "comm_state":{ "EM_1": 101, "EM_2": 50, "IOMODEL_1": 100, "IOMODEL_2": 0}, // 设备通讯状态
      "EM_1_Voltage": {"Phase_A": 0.0, "Phase_B": 0.0, "Phase_C": 0.0},               // 表1电压
      "EM_2_Voltage": {"Phase_A": 0.0, "Phase_B": 0.0, "Phase_C": 0.0},               // 表2电压
      "Main_Electrical_Energy": {"Phase_A": 0.0, "Phase_B": 0.0, "Phase_C": 0.0},     // 电柜各相线总电能
      "Main_Power_Factor": {"Phase_A": 0.0, "Phase_B": 0.0, "Phase_C": 0.0},          // 电柜各相线功率因素                                                              
      "Main_Current": {"Phase_A": 0.0, "Phase_B": 0.0, "Phase_C": 0.0},               // 电柜各相线总电流
      "line_1": {"current": 0.0, "electrical_energy": 0.0, "power_factor": 0.0},      //线路1参数
      "line_2": {"current": 0.0, "electrical_energy": 0.0, "power_factor": 0.0},      //线路2参数
      "line_3": {"current": 0.0, "electrical_energy": 0.0, "power_factor": 0.0},      //线路3参数
      "line_4": {"current": 0.0, "electrical_energy": 0.0, "power_factor": 0.0},      //线路4参数
      "line_5": {"current": 0.0, "electrical_energy": 0.0, "power_factor": 0.0},      //线路5参数
      "line_6": {"current": 0.0, "electrical_energy": 0.0, "power_factor": 0.0},      //线路6参数
      "line_7": {"current": 0.0, "electrical_energy": 0.0, "power_factor": 0.0},      //线路7参数
      "line_8": {"current": 0.0, "electrical_energy": 0.0, "power_factor": 0.0},      //线路8参数
      "line_9": {"current": 0.0, "electrical_energy": 0.0, "power_factor": 0.0},      //线路9参数
      "line_10": {"current": 0.0, "electrical_energy": 0.0, "power_factor": 0.0},     //线路10参数
      "line_11": {"current": 0.0, "electrical_energy": 0.0, "power_factor": 0.0},     //线路11参数
      "line_12": {"current": 0.0, "electrical_energy": 0.0, "power_factor": 0.0}     //线路12参数

}
               

## 离线数据

* 服务端发送请求离线消息 topic $oc/devices/{device_id}/user/offline_data
* 设备收到请求消息上报数据消息 topic $oc/devices/{device_id}/user/offline_data_reply
* 服务端数据格式 {"st":1705042800,"et":1705043520}

| 参数 | 类型   | 说明   | 示例         |
|----|------|------|------------|
| st | long | 开始时间 | 1705042800 |
| et | long | 结束时间 | 1705043520 |

* 设备返回数据 {}
    topic： $oc/devices/{device_id}/user/offline_data_reply
    数据结构：{“timestamp":{  "EM_values": "{}, "iomodle_value": "{}"}
           
            "1705042800": {
                            "EM_values": {  "comm_state":{ "EM_1": 101, "EM_2": 50, "IOMODEL_1": 100, "IOMODEL_2": 0}, // 设备通讯状态
                                            "EM_1_Voltage": {"Phase_A": 0.0, "Phase_B": 0.0, "Phase_C": 0.0},               // 表1电压
                                            "EM_2_Voltage": {"Phase_A": 0.0, "Phase_B": 0.0, "Phase_C": 0.0},               // 表2电压
                                
                                            "main_Electrical_energy": {"Phase_A": 0.0, "Phase_B": 0.0, "Phase_C": 0.0},     // 电柜各相线总电能
                                            "main_Power_factor": {"Phase_A": 0.0, "Phase_B": 0.0, "Phase_C": 0.0},          // 电柜各相线功率因素                                                              
                                            "Main_Current": {"Phase_A": 0.0, "Phase_B": 0.0, "Phase_C": 0.0},               // 电柜各相线总电流
                                  
                                            "line_1": {"current": 0.0, "electrical_energy": 0.0, "power_factor": 0.0},      //线路1参数
                                            "line_2": {"current": 0.0, "electrical_energy": 0.0, "power_factor": 0.0},      //线路2参数
                                            "line_3": {"current": 0.0, "electrical_energy": 0.0, "power_factor": 0.0},      //线路3参数
                                            "line_4": {"current": 0.0, "electrical_energy": 0.0, "power_factor": 0.0},      //线路4参数
                                            "line_5": {"current": 0.0, "electrical_energy": 0.0, "power_factor": 0.0},      //线路5参数
                                            "line_6": {"current": 0.0, "electrical_energy": 0.0, "power_factor": 0.0},      //线路6参数
                                            "line_7": {"current": 0.0, "electrical_energy": 0.0, "power_factor": 0.0},      //线路7参数
                                            "line_8": {"current": 0.0, "electrical_energy": 0.0, "power_factor": 0.0},      //线路8参数
                                            "line_9": {"current": 0.0, "electrical_energy": 0.0, "power_factor": 0.0},      //线路9参数
                                            "line_10": {"current": 0.0, "electrical_energy": 0.0, "power_factor": 0.0},     //线路10参数
                                            "line_11": {"current": 0.0, "electrical_energy": 0.0, "power_factor": 0.0},     //线路11参数
                                            "line_12": {"current": 0.0, "electrical_energy": 0.0, "power_factor": 0.0}}     //线路12参数
                            "iomodle_value": "{""ch01":"trun_on"}"
                            },
             


| 参数 | 类型   | 说明   | 示例         
|----|------|------|------------|
| st | long | 开始时间 | 1705042800 |
| et | long | 结束时间 | 1705043520 |

## 在线控制开关

* 服务端发送控制开关消息 topic $oc/devices/{device_id}/user/switch
* 设备收到请求消息上报数据消息 topic $oc/devices/{device_id}/user/switch_reply
* 服务端数据格式 {"timestamp":1705042800,"switch":{"ch01":1}}

| 参数        | 类型      | 说明                                            | 示例         |
|-----------|---------|-----------------------------------------------|------------|
| timestamp | long    | 时间                                            | 1705042800 |
| switch    | json结构体 | 开关路数作key<br/> 执行动作作value。范围: <br/>1-开<br/>0-关 | {"ch01":1} |
 云端下发消息案例："message_id":"******", "timestamp":1705042800,"switch":{"ch01":1}
 设备端消息回执云端案例："message_id":"******", "switch":{"ch01":"trun_on"}
 设备端消息回执本地操作案例："switch"{"ch01":"trun_on"}




* 设备返回数据 {}

| 参数 | 类型   | 说明   | 示例         |
|----|------|------|------------|
| st | long | 开始时间 | 1705042800 |
| et | long | 结束时间 | 1705043520 |

## 配置属性下发
* 服务端发送配置属性 topic $oc/devices/{device_id}/user/config
    消息案例：{ "line_0_name": "空调",
    "line_1_name": "消防电路",
    "line_2_name": "安防闸机",
    "line_3_name": "大厅灯光",
    "line_4_name": "门厅照明",
    "line_5_name": "招牌霓虹灯",
    "line_6_name": "A区插座",
    "line_7_name": "B区插座",
    "line_8_name": "C区插座",
    "line_9_name": "充电桩A",
    "line_10_name": "充电桩B",
    "line_11_name": "充电桩C",
    "line_12_name": "充电桩A",
    "line_13_name": "充电桩B",
    "line_14_name": "充电桩C",
    "line_15_name": "充电桩A",
    "line_16_name": "充电桩B",
    "line_17_name": "充电桩C",
    "line_18_name": "充电桩A",
    "line_19_name": "充电桩B",
    "line_20_name": "充电桩C",
    "line_21_name": "充电桩A",
    "line_22_name": "充电桩B",
    "line_23_name": "充电桩C",

    "energy_metter_quantity": 5,


    "line_0_swicth": "None",  
    "line_1_swicth": "None",  
    "line_2_swicth": "None",   
    "line_3_swicth": "ch01",  
    "line_4_swicth": "ch02",
    "line_5_swicth": "ch03",  
    "line_6_swicth": "ch04",
    "line_7_swicth": "ch05",  
    "line_8_swicth": "ch06",
    "line_9_swicth": "ch07",  
    "line_10_swicth": "ch08",
    "line_11_swicth": "ch09",  
    "line_12_swicth": "ch010",
    "line_13_swicth": "ch011",  
    "line_14_swicth": "ch012",
    "line_15_swicth": "None",   
    "line_16_swicth": "None",  
    "line_17_swicth": "None",   
    "line_18_swicth": "None",  
    "line_19_swicth": "None",  
    "line_20_swicth": "None",  
    "line_21_swicth": "None",  
    "line_22_swicth": "None",  
    "line_23_swicth": "None",  

    "line_0_alarm_current": 20,
    "line_1_alarm_current": 20,
    "line_2_alarm_current": 20,
    "line_3_alarm_current": 20,  
    "line_4_alarm_current": 20,
    "line_5_alarm_current": 20,  
    "line_6_alarm_current": 20,
    "line_7_alarm_current": 20,  
    "line_8_alarm_current": 20,
    "line_9_alarm_current": 20,  
    "line_10_alarm_current": 20,
    "line_11_alarm_current": 20,  
    "line_12_alarm_current": 20,
    "line_13_alarm_current": 20,  
    "line_14_alarm_current": 20,
    "line_15_alarm_current": 20,  
    "line_16_alarm_current": 20,
    "line_17_alarm_current": 20,  
    "line_18_alarm_current": 20,
    "line_19_alarm_current": 20,  
    "line_20_alarm_current": 20,
    "line_21_alarm_current": 20,  
    "line_22_alarm_current": 20,
    "line_23_alarm_current": 20

}
消息内容可以只发其中一条键值对，也可以发多条键值对
* 服务端数据格式 {}