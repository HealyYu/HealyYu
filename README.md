# 工控机程序

# 依赖

    查看 requirements.txt 文件
    额外的依赖  pyqt5

# 开发运行

    运行环境为 python 3.7.3 64位 其他也行, 不要求 各版本安装pyqt5 不一样

# 开发运行方法

    python test.py

# 编译

    编译前请先安装 pyinstaller
    编译命令 pyinstaller -F test.py
    编译后会在 dist 文件夹下生成 test.exe 文件

# 运行

    运行前请先将 test.exe 放入到工控机的任意目录下
    运行 test.exe 即可
# device_ID.josn 文件说明

    "host_name": 已无用
    "product_ID": 设备ID前缀
    "device_name": 设备名称
    "device_secret": 设备密匙
    "system_version": 程序版本号 无用
    "huawei_iot_server_uri": iot 服务器地址
    开发环境 : 66cdb864d3.st1.iotda-device.cn-east-3.myhuaweicloud.com
    线上环境 : bfc3622fc3.st1.iotda-coaps.cn-east-3.myhuaweicloud.com
# 线路规则
  UI 的 objectName 定义
  0 为 1 线路

  line_0_name 线路名称
  line_0_used 用电量
  line_0_e 电流
  line_0_v 电压
  line_0_state 线路状态
  line_0_state_text 线路状态文字
  
  total_a_v A相总电压
  total_a_e A相总电流
  total_a_used A相总电流
  total_b_v B相总电压
  total_b_e B相总电流
  total_b_used B相总电流
  total_c_v C相总电压
  total_c_e C相总电流
  total_c_used C相总电流

  device_id 设备ID
  site 场地
  sys_version 软件版本
  config_name   配置名称
  line_nums 回路数量
  tab_0 切换按钮

# 注意事项
