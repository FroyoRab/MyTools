from getInfo import getInfo
import xlsxwriter
import requests
import traceback

try:
    if __name__ == '__main__':
            info = getInfo()
            saveName = input("请输入结果数据文件名(不要填写尾缀名):")
            savePath = "\\".join(info.pathList[0].split("\\")[0:-1])+"\\"+saveName+".xlsx"
            newExl = xlsxwriter.Workbook(savePath)
            sheet1 = newExl.add_worksheet()
            #添加列标题
            sheet1.write_row("A1",["月份"]+info.exlNameList)
            #添加行标题
            sheet1.write_column("A2",["留存人数","工作量50-100h人数","工作量100-150h人数","工作量大于150h人数"])
            #添加sheet1数据
            sheet1.write_row("B2",info.differenceList)
            sheet1.write_row("B3",info.count50List)
            sheet1.write_row("B4",info.count100List)
            sheet1.write_row("B5",info.count150List)
            #添加名单
            for index,name in enumerate(info.exlNameList):
                sheetNew = newExl.add_worksheet(name)
                #添加列标题
                sheetNew.write_row("A1", ["工作量50-100h人数", "工作量100-150h人数", "工作量大于150h人数"])
                #添加数据
                sheetNew.write_column("A2", info.time50List[index])
                sheetNew.write_column("B2", info.time100List[index])
                sheetNew.write_column("C2", info.time150List[index])

            #添加图表
            #创建一个线图
            picLine = newExl.add_chart({'type': 'line'})
            picLine.add_series({#留存率
                'name':'=Sheet1!$A$2',
                'categories':'=Sheet1!$C$1:$E$1',
                'values':'=Sheet1!$C$2:$E$2'
            })
            picLine.add_series({#50
                'name':'=Sheet1!$A$3',
                'categories':'=Sheet1!$C$1:$E$1',
                'values':'=Sheet1!$C$3:$E$3'
            })
            picLine.add_series({#100
                'name':'=Sheet1!$A$4',
                'categories':'=Sheet1!$C$1:$E$1',
                'values':'=Sheet1!$C$4:$E$4'
            })
            picLine.add_series({#150
                'name':'=Sheet1!$A$5',
                'categories':'=Sheet1!$C$1:$E$1',
                'values':'=Sheet1!$C$5:$E$5'
            })
            picLine.set_title({'name':info.exlNameList[0]+"-"+info.exlNameList[-1]+"统计折线图"})
            picLine.set_x_axis({'name':'月份'})
            picLine.set_y_axis({'name':'人数(人)'})

            picLine.set_style(3)
            sheet1.insert_chart("A10",picLine)
            newExl.close()

except Exception as err:
    requests.get(url=r"https://sc.ftqq.com/[KEY].send?text=%s"%err +\
                 "&desp=%s"%traceback.format_exc())
    print("已经发送错误给我了,我看到了会来找你的，如果着急可以直接微信我")





