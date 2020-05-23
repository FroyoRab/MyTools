# -*- coding: utf-8 -*-
# @Time      :2020/4/10 下午 03:33
# @File      :jdbDebug.py
import os

usePoint = "8700"
point = input("是否使用8700作为jdb调试端口？(Y or Point):")
if point!="Y" and point!="":
    usePoint = point
os.system("jdb -connect com.sun.jdi.SocketAttach:hostname=127.0.0.1,port="+str(usePoint))

