# -*- coding: utf-8 -*-
# @Time      :2020/5/1 下午 04:04
# @File      :getBeiAn.py
import os

import requests
from PIL import Image
from io import BytesIO
import re

class GetZCode:
    def __init__(self):
        '''
        需要手输验证码的半自动备案信息获取
        '''
        #使用的cookie
        self.cookie = ''
        #第一个验证码的结果
        self.zCode1 = ''
        #第二个验证码的结果
        self.zCode2 = ''
        self.proxies = {"http": "http://127.0.0.1:8080"}
        self.url='http://beian.miit.gov.cn'

        #0name,1domain,2url,3license,4ip,5unitName,6zCode
        self.infoList = ['', '', '', '', '', '', '']
        while True:
            try:
                select = int(input("1.网站名称\n2.网站域名\n3.网站首页地址\n4.备案号\n5.ip地址\n6.主办单位名称\n请选择查询方式：:"))
                if select>0 and select<7:
                    break
            except:pass

        self.infoList[select - 1] = input("请输入查询内容：")


    def getZCode(self,select=0):
        '''
        获得验证码
        :param select:默认为0获得第一个验证码，为1时获得第二个“详细信息”验证码
        :return:
        '''
        headerget = {
            #'X-Forwarded-For': ip,
            'Host': 'beian.miit.gov.cn',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' +
                          'AppleWebKit/537.36 (KHTML, like Gecko)',
            'Accept': '*/*',
            'Referer': r'http://beian.miit.gov.cn/icp/publish/query/icpMemoInfo_showPage.action',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        }
        if select:
            url = self.url+'/getDetailVerifyCode?75'
        else:
            url = self.url+'/getVerifyCode?88'
        print("等待验证码……")
        #req =requests.get(url,headers=headerget,proxies=self.proxies,verify=False)
        req = requests.get(url, headers=headerget)
        self.cookie = req.cookies
        #从io获取图片加载至pil并打开
        self.img = Image.open(BytesIO(req.content))
        self.img.show()
        #获取用户识别的验证码
        if select:
            self.zCode2 = str(input("请输入验证码："))
        else:
            self.zCode1 = str(input("请输入验证码："))

    def checkZCode(self):
        '''
        第一个验证码的验证包发送并判断
        :return:
        '''
        headerget = {
            'Host': 'beian.miit.gov.cn',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' +
                          'AppleWebKit/537.36 (KHTML, like Gecko)',
            'Accept': 'application/json, text/javascript, */*',
            'Referer': r'http://beian.miit.gov.cn/icp/publish/query/icpMemoInfo_showPage.action',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'X-Requested-With':'XMLHttpRequest',
            'Content-Type':'application/x-www-form-urlencoded'
        }

        url = self.url+'/common/validate/validCode.action'
        while True:
            data = "validateValue=" + self.zCode1
            #req = requests.post(
            #    url,
            #    headers=headerget,
            #    proxies=self.proxies,
            #    data=data,
            #    cookies=self.cookie,
            #    verify=False
            #)
            req = requests.post(
                url,
                headers=headerget,
                data=data,
                cookies=self.cookie
            )
            if req.text.find("false")!=-1:
                print("验证码错误")
                self.getZCode()
            elif req.text.find("true")!=-1:
                print("第一个验证码正确……")
                break
            else:
                raise RuntimeError("验证出错"+req.text)



    def getInfo(self):
        '''
        获得信息，并通过获得的备案id号获得详细信息
        :return:
        '''
        headerget = {
            'Host': 'beian.miit.gov.cn',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' +
                          'AppleWebKit/537.36 (KHTML, like Gecko)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Referer': r'http://beian.miit.gov.cn/icp/publish/query/icpMemoInfo_showPage.action',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        #将信息列表最后一个设置为之前获得的验证码
        self.infoList[6]=self.zCode1
        #将信息填充到将要发送的data里
        data = ("siteName={0[0]}&condition=1&siteDomain={0[1]}" +
               "&siteUrl={0[2]}&mainLicense={0[3]}&siteIp={0[4]}"+
               "&unitName={0[5]}&mainUnitNature=-1&certType=-1&mainUnitCertNo="+
               "&verifyCode={0[6]}").format(self.infoList)

        url = self.url + '/icp/publish/query/icpMemoInfo_searchExecute.action'
        #req = requests.post(
        #    url,
        #    headers=headerget,
        #    proxies=self.proxies,
        #    data=self.data,
        #    cookies=self.cookie,
        #    verify=False
        #)
        print("正在获取备案信息……")
        req = requests.post(
            url,
            headers=headerget,
            data=data,
            cookies=self.cookie
        )
        if req.text.find("没有符合条件的记录")!=-1:
            raise RuntimeError("未找到指定信息")
        #使用正则查找备案id号
        res = re.search("doDetail\(\'[0-9]{9,9}\'\)",req.text)
        if not res:
            raise RuntimeError(req.text)
        searchId = res.group(0)[10:-2]
        print("备案id：%s"%searchId)
        #获得详细信息
        self.getZCode(1)
        headerget['Referer'] = r"http://beian.miit.gov.cn/icp/publish/query/icpMemoInfo_searchExecute.action"
        url = self.url + r"/icp/publish/query/icpMemoInfo_login.action"
        res = re.search("siteName=.*&mainUnitCertNo=",data)
        data = 'verifyCode={}&id={}&'.format(self.zCode2,searchId)+res.group(0)+'&bindFlag=0'
        #req = requests.post(
        #    url,
        #    headers=headerget,
        #    proxies=self.proxies,
        #    data=data,
        #    cookies=self.cookie,
        #    verify=False
        #)
        print("正在获取详细信息……建议切到后台……")
        req = requests.post(
            url,
            headers=headerget,
            data=data,
            cookies=self.cookie
        )
        #将获得的详细信息直接存成html然后打开
        fp = open("res.html","wb")
        fp.write(req.content)
        fp.close()
        os.system(r".\res.html")


while True:
    code = GetZCode()
    while True:
        try:
            code.getZCode()
            code.checkZCode()
            code.getInfo()
            break
        except Exception as a :
            print(a)