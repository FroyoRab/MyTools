# -*- coding: utf-8 -*-
# @Time      :2020/4/9 下午 12:32
# @File      :RunDebug.py
import os
import sys
import re
from time import time


class debugApk:
    def __init__(self,apkPath):
        '''
        给到apk路径，通过aapt2查询包名类名
        可以调用安装apk(已经安装将会跳过)，开调试服务器，杀旧的调试服务器
        设置端口转发，并调试启用app
        :param apkPath:
        '''
        self.__infoList = []
        self.__apkPath = apkPath
        self.__getInfo()
        self.__packageName = self.__getPackageName()
        self.__mainActivity = self.__getMainActivity()
        self.__pointNum = "23456"

    def printInfo(self):
        print("packageName:\t"+self.__packageName)
        print("MainActivity:\t"+self.__mainActivity)
        os.system("pause")

    def setPointNum(self,pointNum):
        self.__pointNum = str(pointNum)

    def __getInfo(self):
        cmd = "aapt2 d badging {}".format(apkPath)
        out = os.popen(cmd)
        out = out.read().split("\n")
        # 将信息分割
        for index, line in enumerate(out):
            out[index] = line.split("\'")

        self.__infoList = out

    def __getPackageName(self):
        return self.__infoList[0][1]

    def __getMainActivity(self):
        for info in self.__infoList:
            if info[0]=="launchable-activity: name=":
                return info[1]

    def installApk(self):
        #判断是否已经安装
        out = os.popen("adb shell pm list packages")
        for package in out.readlines():
            if package.find(self.__packageName)!=-1:
                print("已经安装此apk……")
                return
        print("安装apk……")
        os.system("adb install {}".format(self.__apkPath))

    def openAndroidDbgServer(self,jdb=None):
        print("开启端口:23456")
        timeOld = time()
        #开启jdb调试等待
        if jdb==None:
            os.system("START python -i jdbDebug.py -{}".format(self.__packageName))
        os.system("adb shell su -run ./data/local/tmp/ands -p23456")
        timeNow = time()
        #判断是否地址占用
        if not ((timeNow-timeOld) > 1):
            self.killOldAnds()
            self.openAndroidDbgServer(jdb=1)

    def pushAndroidDbgServer(self):
        #查找文件夹下是否有android_server文件
        for files in os.walk(os.getcwd()):
            for file in files:
                if "android_server" in file:
                    print("上传文件夹下的android_server至/data/local/tmp 并重命名为ands……")
                    os.system("adb push android_server /data/local/tmp/ands")
                    print("设置ands chmod777")
                    os.system("adb shell su -c chmod 777 /data/local/tmp/ands")

    def killOldAnds(self):
        out = os.popen("adb shell ps")
        for package in out.readlines():
            if package.find("./data/local/tmp/ands")!=-1:
                pid = re.search(r"[0-9]+",package).group(0)
                print("端口占用!查找到有ands运行，正在kill pid:"+str(pid))
                os.system("adb shell su -c kill -9 "+str(pid))
                return
        raise RuntimeError("端口占用！未找到ands正在运行！请更换端口")

    def openPointForwarding(self):
        print("端口转发")
        os.system("adb forward tcp:23456 tcp:23456")

    def runApk(self):
        print("dbg方式打开app……")
        os.system("adb shell am start -D -n {}/{}".format(self.__packageName, self.__mainActivity))

if __name__ == '__main__':
    argv = sys.argv
    apkPath = argv[1] if argv.__len__()>1 else input("请拖入调试apk:")
    dbgApk = debugApk(apkPath)
    dbgApk.printInfo()
    point = input("是否使用23456端口调试？(Y or Point):")
    if point != "Y" and point != "" :
        dbgApk.setPointNum(point)
    dbgApk.installApk()
    dbgApk.openPointForwarding()
    dbgApk.runApk()
    dbgApk.pushAndroidDbgServer()
    dbgApk.openAndroidDbgServer()