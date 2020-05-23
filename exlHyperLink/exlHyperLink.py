import xlrd
import xlsxwriter
import re
import requests
import traceback

class getInfo:
    def __init__(self):
        self.cityNameList = []
        self.cityList = []
        self.regionNameList=["华中", "华东", "华南", "华北", "西南"]
        # 0中  1东  2南  4北  5西南
        self.regionList=[[],[],[],[],[],]
        print("+"+"="*105+"+",end="\n\n")
        print("请确保信息表sheet1中\t|第一列为区域\t|第二列为门店名称\t|第三列为店铺地址\t|第四列为时薪\t|")
        print("\t\t例:\t|华北\t\t|包头华联友谊店\t\t|重庆市渝北区新南路36号\t|22\t\t|",end="\n\n")
        print("保存至的文件名需要包含.xlsx的尾缀  例:new.xlsx  也可以直接回车使用默认文件名")
        print("制作的表格将保存在 \"原表\" 路径下,如为输入文件名，默认为new.xlsx",end="\n\n")
        print("+"+"="*105+"+",end="\n\n")
        temp = input("制作的表格保存时的文件名:")
        newName = "new.xlsx" if temp=="" else  temp
        exlPath = input("拖入sheet1为内容的信息表：")
        exlBook = xlrd.open_workbook(exlPath)
        newExlPath = "\\".join(exlPath.split("\\")[0:-1])+"\\"+newName
        self.newExl = xlsxwriter.Workbook(newExlPath)
        self.exlSheet = exlBook.sheet_by_index(0)

        print("获取所有信息……",end="")
        self.storeNameList = self.exlSheet.col_values(1)[1:]
        self.originRegionList = self.exlSheet.col_values(0)[1:]
        self.addressList = self.exlSheet.col_values(2)[1:]
        self.salaryList = self.exlSheet.col_values(3)[1:]
        print("√")
        # 创建超链接格式：
        self.linkFormat = self.newExl.add_format({"underline":True,"font_color":"blue"})
        self.linkFormat.set_center_across()

        self.fillingList()
        self.createHomePage()
        self.createRegionSheet()
        self.createCitySheet()

        #print("创建区域列表……",end="")
        #for region in self.regions:
        #    self.newExl.add_worksheet(region)
        #print("√")
        print("正在保存……")
        while True:
            try:
                self.newExl.close()
                break
            except xlsxwriter.exceptions.FileCreateError:
                input("请!!关闭!!保存文件后 在此回车 ")
        print("保存完成√")

    def fillingList(self):
        print("构造列表……")
        for index,address in enumerate(self.addressList):
            res = re.search(".{2,5}?(自治区|自治州|省|市)",address)
            if res is None:
                print("此地址未找到省市区:"+address)
                res = re.search(".{2,5}?(自治区|自治州|省|市)",input("请手动输入省市(以\"省/市/自治区/自治州\"为结尾):"))
            if res:
                # 添加门店到城市列表
                try:
                    self.cityList[self.cityNameList.index(res.group(0))].append(self.storeNameList[index])
                except ValueError:
                    self.cityList.append([])
                    self.cityNameList.append(res.group(0))
                    self.cityList[self.cityNameList.index(res.group(0))].append(self.storeNameList[index])
                # 添加城市到区域列表
                try:
                    # 判断列表内是否有此城市
                    self.regionList[self.regionNameList.index(self.originRegionList[index][0:2])].index(res.group(0))
                    # index报ValueError表示无此城市，则添加
                except ValueError:
                    self.regionList[self.regionNameList.index(self.originRegionList[index][0:2])].append(res.group(0))
            else:
                raise RuntimeError("此地址未找到省市区并且输入识别失败:"+address)
        print("构造列表完成√")

    def createRegionSheet(self):
            print("添加区域sheet……",end="")
            for index,citys in enumerate(self.regionList):
                sheet = self.newExl.add_worksheet(self.regionNameList[index])
                # 插入区域列表
                # sheet.write_column("A1",citys)
                # 构造超链接，地址，时薪列表
                hyperLinkList = []
                for city in citys:
                    hyperLinkList.append("=HYPERLINK(\"#{}!{}\",\"{}\")".format(city,"A1",city))
                #插入超链接
                sheet.write_column("A1",hyperLinkList,self.linkFormat)
                # 插入返回
                sheet.write("D1", "=HYPERLINK(\"#{}!{}\",\"{}\")".format("首页", "A1", "返回首页"),self.linkFormat)
            print("√")

    def createCitySheet(self):
        print("添加城市sheet……",end="")
        for index,stores in enumerate(self.cityList):
            sheet = self.newExl.add_worksheet(self.cityNameList[index])
            # 插入标题
            sheet.write_row("A1",["门店名称","门店地址","时薪"])
            # 居中格式
            centerFormat = self.newExl.add_format()
            centerFormat.set_center_across()
            # 设置列宽
            sheet.set_column("A:A",20,centerFormat)
            sheet.set_column("B:B",50,centerFormat)
            sheet.set_column("C:C",5,centerFormat)
            # 插入门店列表
            sheet.write_column("A2",stores)
            # 插入返回
            region = ""
            #print("城市名称:"+self.cityNameList[index])
            for inIndex,citys in enumerate(self.regionList):
                try:
                    citys.index(self.cityNameList[index])
                    region = self.regionNameList[inIndex]
                    #print("找到的区域名称:" + region)
                    break
                except ValueError : pass
                    #print("%d中未找到……"%inIndex)
            sheet.write("D2", "=HYPERLINK(\"#{}!{}\",\"{}\")".format(region, "A1", "返回"),self.linkFormat)
            # 插入地址及时薪
            addresses = []
            salaries = []
            for store in stores:
                where = self.storeNameList.index(store)
                addresses.append(self.addressList[where])
                salaries.append(self.salaryList[where])
            # 插入地址及时薪
            sheet.write_column("B2", addresses)
            sheet.write_column("C2", salaries)

        print("√")

    def createHomePage(self):
        sheet = self.newExl.add_worksheet("首页")
        regionLink = []
        for region in self.regionNameList:
            regionLink.append("=HYPERLINK(\"#{}!{}\",\"{}\")".format(region,"A1",region))
        sheet.write_column("A1",regionLink,self.linkFormat)
try:
    info = getInfo()
except Exception as err:
    requests.get(url=r"https://sc.ftqq.com/[key].send?text=%s&desp=%s"%("方丽娜的exlHyperlink报错啦",traceback.format_exc()))


