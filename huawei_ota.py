# -*- encoding: utf-8 -*-

# Copyright (c) 2020-2023 Huawei Cloud Computing Technology Co., Ltd. All rights reserved.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""
OTA sample,用来演示如何实现设备升级（此例子不再使用）
使用方法:用户在平台上创建升级任务后,修改main函数里设备参数后启动本例,即可看到设备收到升级通知,并下载升级包进行升级,
并上报升级结果。在平台上可以看到升级结果
"""

import os
import sys
import requests
import stat
import threading
import time 
from iot_device_sdk_python.ota.ota_listener import OTAListener
from iot_device_sdk_python.ota.ota_service import OTAService
from iot_device_sdk_python.ota.ota_package_info import OTAPackageInfo
from iot_device_sdk_python.ota.ota_package_info_v2 import OTAPackageInfoV2
from iot_device_sdk_python.utils.iot_util import sha256_hash_from_file
from typing import Union
import shutil
now_dir_path = os.path.dirname(os.path.realpath(sys.argv[0]))

from log import Logger



class OTASampleListener(OTAListener):
    """
    一个实现OTA监听器的例子
    """
    logger = Logger(__name__)
    def __init__(self, ota_service: OTAService,system_version:str):
        self.fw_version = system_version  # 自行修改为实际值 固件版本
        self.sw_version = "v1.0.0"  # 自行修改为实际值 软件版本
        self.ota_service = ota_service
        self.file_name = '/test'
        # 更新文件路径
        self.new_dir_path = os.path.join(now_dir_path, "update")
        # 老文件路径
        self.old_dir_path = os.path.join(now_dir_path, "old")
        # logger.debug('new_dir_path',self.new_dir_path ,"old_dir_path",self.old_dir_path, 'self.file_name',self.file_name,)
    def on_query_version(self):
        """
        接收查询版本通知
        """
        self.logger.info(self.fw_version)
        print('OTASampleListener on_query_version=========================',self.fw_version)
        self.ota_service.report_version(self.fw_version, self.sw_version)

    def on_receive_package_info(self, pkg: Union[OTAPackageInfo, OTAPackageInfoV2]):
        """
        接收新版本通知
        :param pkg:     新版本包信息
        """
        if self.pre_check(pkg) != 0:
            self.logger.error("pre_check failed")
            return
        # 下载包并升级
        self.download_package(pkg)

    def pre_check(self, pkg: Union[OTAPackageInfo, OTAPackageInfoV2]):
        """
        对新版本包信息进行检查
        :param pkg:     新版本包信息
        :return:    如果允许升级，返回0；返回非0表示不允许升级
        """
        # TODO 对版本号、剩余空间、剩余电量、信号质量等进行检查、如果不允许升级，上报OTAService中定义的错误码或者自定义错误码，返回-1
        if self.fw_version == pkg.version:
            self.logger.error("system version is same as new version")
            self.ota_service.report_ota_status(self.ota_service.OTA_CODE_SUCCESS, pkg.version, 100,
                                           "upgrade success")
            return -1
        return 0

    def on_upgrade_success(self, pkg: Union[OTAPackageInfo, OTAPackageInfoV2], sign: str):
        self.logger.info("download package success")
        # 校验下载的升级包
        if self.check_package(pkg, sign) != 0:
            return
         # 上报升级成功，注意版本号要携带更新后的版本号，否则平台会认为升级失败
        self.ota_service.report_ota_status(self.ota_service.OTA_CODE_SUCCESS, pkg.version, 100,
                                           "download package success")
        # return
        # 安装升级包
        if self.install_package() != 0:
            return
        # 上报升级成功，注意版本号要携带更新后的版本号，否则平台会认为升级失败
        # self.ota_service.report_ota_status(self.ota_service.OTA_CODE_SUCCESS, pkg.version, 100,
        #                                    "upgrade success")
    
        self.logger.info("ota upgrade ok==================")

    def on_success(self):
        self.logger.debug('======,{},{},{}'.format('升级成功','======','开始重启'))
        time.sleep(3)
        # 系统重启
        # 获取当前解释器路径
        p = sys.executable
        self.logger.debug('app_path:{}'.format(p))
        print(*sys.argv)
        os.execl(p, p, *sys.argv)
        time.sleep(3)
        # 启动新程序(解释器路径, 当前程序)
        sys.exit(0)
    
    def on_upgrade_failure(self):
        self.logger.error("download package failed")
        self.ota_service.report_ota_status(self.ota_service.OTA_CODE_INSTALL_FAIL, self.fw_version, 0,
                                           "download package failed")
    

    def check_package(self, pkg: Union[OTAPackageInfo, OTAPackageInfoV2], sign: str):
        """
        校验升级包
        :param pkg:     新版本包信息
        :param sign:    str
        :return:    0表示校验成功；非0表示校验失败
        """
        if isinstance(pkg, OTAPackageInfo) and sign != pkg.sign:
            self.logger.error(
                "check package fail: current file sha256 %s , target file sha256 %s" % (sign, pkg.sign))
            return -1
        # TODO 增加其他校验
        return 0

    def install_package(self):
        """
        安装升级包，需要用户实现
        :return:    0表示安装成功；非0表示安装失败
        """
        # TODO 安装升级包，用户实现
        
        try:
            if not os.path.exists(self.old_dir_path): os.makedirs(self.old_dir_path)
            # 等待备份文件
            self.wait_for_copy(self.copy_file)
            # 等待更新文件
            self.wait_for_copy(self.update_file)
            # 关闭当前程序
            self.logger.debug('重启成功')
            return 0
            # logger.error('重启失败',e)
            # 重启不成功 
        except Exception as e:
            self.logger.error('更新失败,{}'.format(e))
            try:
                self.wait_for_copy(self.reload_app)
                self.logger.debug('复原成功')
            except Exception as e:
                self.logger.error('复原失败,{}'.format(e))   
        return 0

    def download_package(self, pkg: Union[OTAPackageInfo, OTAPackageInfoV2]):
        """
        下载包，这里的例子是下载一个txt文件
        # TODO 下载升级包
        """
        path = self.new_dir_path
        if not os.path.exists(path):  # 看是否有该文件夹，没有则创建文件夹
            os.makedirs(path)

        headers = {}
        if isinstance(pkg, OTAPackageInfo):
            headers = {"Authorization": "Bearer " + pkg.access_token}

        response = requests.get(pkg.url, headers=headers, verify=False, stream=True)

        chunk_size = 1024  # 每次下载的数据大小
        try:
            if response.status_code == 200:
                # 下载文件总大小
                content_size = int(response.headers["content-length"])

                filepath = path + self.file_name
                size = 0
                with open(filepath, 'wb') as file:  # 显示进度条
                    for data in response.iter_content(chunk_size=chunk_size):
                        # if(content_size / size ):
                        self.logger.debug("下载进度:{}".format(size))
                        file.write(data)
                        size += len(data)
            
                
                if size == content_size:
                    file_sha256_hash: str = sha256_hash_from_file(filepath)
                    self.logger.debug('=====下载成功+====')
                    self.on_upgrade_success(pkg, file_sha256_hash)
                    self.logger.debug('=====更新成功=====')
                    self.on_success()
        except Exception as e:
            self.on_upgrade_failure()
            self.logger.error('下载失败{}'.format(e))
            raise e
     # 备份文件
    def copy_file(self):
        try:
            if os.path.exists(self.old_dir_path+self.file_name) :shutil.os.remove(os.path.join(self.old_dir_path+self.file_name))
            fd = shutil.copyfile(now_dir_path+self.file_name,self.old_dir_path+self.file_name) 
            self.logger.debug('备份:copy_file %s' % (fd))
        except Exception as e:
            self.logger.error('备份er: %s' % (e))
    # 更新文件
    def update_file(self):
        try:
            if os.path.exists(now_dir_path+self.file_name) :shutil.os.remove(now_dir_path+self.file_name)
            fd = shutil.copyfile(self.new_dir_path+self.file_name,now_dir_path+self.file_name)
            self.logger.debug('更新:update_fiel,{}'.format(fd))
            os.chmod(fd,stat.S_IRWXU)
        except Exception as e:
            self.wait_for_copy(self.reload_app)

            self.logger.error('更新er:{}'.format(e))
    # 还原文件
    def reload_app(self):
        try:
            shutil.os.remove(now_dir_path+self.file_name)
            fd = shutil.copyfile(self.old_dir_path+self.file_name,now_dir_path+self.file_name)
            self.logger.debug('还原:reload_app{}'.format(fd))
        except Exception as e:
            self.logger.error('还原er:{}'.format(e)) 
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
        self.logger.debug('new-version:,{},{},{}'.format(v2,"now-version",v1))
        if v1 > v2:
            return 1
        elif v1 < v2:
            return -1
        else:
            return 0

# def run():
#     server_uri = "iot-mqtts.cn-north-4.myhuaweicloud.com"
#     port = 8883
#     device_id = "< Your DeviceId >"
#     secret = "< Your Device Secret >"
#     iot_ca_cert_path = "./resources/GlobalSignRSAOVSSLCA2018.crt.pem"

#     connect_auth_info = ConnectAuthInfo()
#     connect_auth_info.server_uri = server_uri
#     connect_auth_info.port = port
#     connect_auth_info.id = device_id
#     connect_auth_info.secret = secret
#     connect_auth_info.iot_cert_path = iot_ca_cert_path
#     connect_auth_info.bs_mode = ConnectAuthInfo.BS_MODE_DIRECT_CONNECT

#     client_conf = ClientConf(connect_auth_info)

#     device = IotDevice(client_conf)

#     """ OTA监听器设置 """
#     ota_service: OTAService = device.get_ota_service()
#     ota_service_listener = OTASampleListener(ota_service)
#     ota_service.set_ota_listener(ota_service_listener)

#     if device.connect() != 0:
#         return

#     while True:
#         time.sleep(5)


# if __name__ == "__main__":
#     run()