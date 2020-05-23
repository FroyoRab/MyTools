import xlrd


class getInfo:
    """
    1.按顺序获得两个表格
    --2.获得输入表格及插入sheet
    3.获得表格1中sheet2的名字(第二列)和工时(第九列)
    4.返回工作时长在50-100的名字列表
    5.返回工作时长在100-150的名字列表
    6.返回工作时长在150以上的名字列表
    7.返回两张表中相同名字的个数
    """

    def __init__(self):

        count = int(input("请输入需要统计的表格数量："))
        self.pathList = []
        for a in range(count):
            self.pathList.append(input("请拖入第%d张表:"%(a+1)))

        self.exlNameList = []
        for path in self.pathList:
            self.exlNameList.append(path.split("\\")[-1].split(".")[0])

        self.bookList = []
        for path in self.pathList:
            self.bookList.append(xlrd.open_workbook(path))

        self.__sheetList = []
        for book in self.bookList:
            self.__sheetList.append(book.sheet_by_index(1))

        self.nameListList = []
        self.timeListList = []
        for sheet in self.__sheetList:
            self.nameListList.append(self.__delFUKSpace(sheet.col_values(1)[2:]))#去除开头大标题和列标题
            self.timeListList.append(self.__delFUKSpace(sheet.col_values(8)[2:-1]))#去除结尾总计

        self.__getDifference()
        self.__getWorkingTimeList()
        #print()

    def __delFUKSpace(self, oneList:list):
        return [i for i in oneList if i != '']

    def __getDifference(self):
        """
        获得重复个数
        :return: list 返回重复率list
        """
        print("获得重复个数……",end="")
        self.differenceList = []
        self.differenceList.append(0)
        for index,nameList in enumerate(self.nameListList):
            try:
                allName = nameList+self.nameListList[index + 1]
            except IndexError:
                break
            total = len(allName)
            difference = total - len(set(allName))
            self.differenceList.append(difference)
            print("……",end="")
        print(self.differenceList)



    def __getWorkingTimeList(self):
        """
        返回工作时长在100-150的名字列表
        which_sheet=0第一张工作表
                   =1第二张工作表
        :return: list
        """
        print("获得工时名单……",end="")
        self.time50List = []
        self.time100List = []
        self.time150List = []
        self.count50List = []
        self.count100List = []
        self.count150List = []
        for index_t,timeList in enumerate(self.timeListList):
            temp50List = []
            temp100List = []
            temp150List = []
            count50 = 0
            count100 = 0
            count150 = 0
            for index,value in enumerate(timeList):
                if 50 <= int(value) < 100:
                    temp50List.append(self.nameListList[index_t][index])
                    count50+=1
                elif 100 <= int(value) < 150:
                    temp100List.append(self.nameListList[index_t][index])
                    count100+=1
                elif int(value) > 150:
                    temp150List.append(self.nameListList[index_t][index])
                    count150+=1
            print("……",end="")
            self.time50List.append(temp50List)
            self.time100List.append(temp100List)
            self.time150List.append(temp150List)
            self.count50List.append(count50)
            self.count100List.append(count100)
            self.count150List.append(count150)

        print("√")

