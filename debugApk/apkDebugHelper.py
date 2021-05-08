"""
辅助 apk 调试 , 自动完成部分 adb 命令功能。\n
实际上就是 adb/jdb 命令合集。\n
"""
import atexit
import os
import subprocess
import re
import time
import argparse
try:
    from termcolor import colored
except ImportError:
    def colored(cmd,color=None,attr=None):
        return cmd


# apk未对清单文件增加debug时可以使用以下方式启用全局调试。
#
# # magisk 更改prop(首先安装对应模块):
# adb shell //adb进入命令行模式
# su //切换至超级用户
# magisk resetprop ro.debuggable 1  //设置debuggable
# stop;start; //一定要通过该方式重启
# # 再次重启后将失效
#
# 或者更改/system/system/etc/prop.default 对其中增加 ro.debuggable=1

# 参数设置
parser = argparse.ArgumentParser(f'python {__file__}')
# parser.add_argument('option or apkPath',help='填入设置选项或者APK路径\n如果内容为路径，将直接以debug模式启动apk，并使用android_server等待连接。')
parser.add_argument('-a','--androidServer',const=23946,nargs='?',help='传入androidServer端口,开启androidServer,默认端口为23946。')
parser.add_argument('-j','--jdb',const=8700,nargs='?',help='传入jdb调试端口,链接jdb调试,默认为8700。')
parser.add_argument('-i','--apkInfo',action='store_true',help='获取apk信息,使用-p传入路径')
parser.add_argument('-ia','--installApk',action='store_true',help='覆盖安装apk,使用-p传入路径')
parser.add_argument('-k','--killAndroidServer',nargs='?',help='关闭本程序传入的android_server。')
parser.add_argument('-p','--path',type=str,help='传入路径，用于查询信息或者调试apk')
parser.add_argument('-l','--log',action='store_true',help='打印运行的命令')

# 子程序列表
gSubProcessList = []
LOG = False

def getOutPut(cmd) -> str:
    if LOG:print(colored(f'>> {cmd}','yellow'))
    return subprocess.getoutput(cmd)

def System(cmd:str):
    if LOG:print(colored(f'>> {cmd}','yellow'))
    return os.system(cmd)

def DoPopen(cmd:str):
    if LOG:print(colored(f'>> {cmd}','yellow'))
    res = subprocess.Popen(cmd)
    time.sleep(1)
    return res
    

def killAnds():
    out = getOutPut('adb shell su -c "ps -A | grep ands"').split('\n')
    for oneLine in out:
        try:
            pid = re.search(r"[0-9]+", oneLine).group(0)
        except:
            pid = None
        if pid:
            print(f'关闭正在运行ands,pid:{pid}')
            System(f'adb shell su -c kill -9 {pid}')

def forwardPort(port:int):
    print(f"尝试转发端口{port}……")
    out = getOutPut(f"adb forward tcp:{port} tcp:{port}")
    if out.find('cannot bind')!=-1:
        print(colored(f'端口转发失败！{out}','red',attrs=['bold']))
        raise ConnectionError
    else : print(colored(f"成功转发端口:{out}",'green'))


def openAndroidServer(port:int):
    """
    传入程序同目录下android_server并命名为ands,并启动。
    如果端口占用则会尝试杀掉ps列表中能够找到的ands程序。
    :param port: 端口号
    :return:
    """
    # 测试文件夹下android_server
    with open('android_server','r') as ands:
        ands.close()
    # 上传
    print("上传文件夹下的android_server至/data/local/tmp 并重命名为ands……")
    System("adb push android_server /data/local/tmp/ands")
    print("设置ands chmod777……")
    System("adb shell su -c chmod 777 /data/local/tmp/ands")

    # 启动ands
    print('尝试启动ands……')
    process = DoPopen(f'adb shell su -c "./data/local/tmp/ands -p{port}"')
    if process.poll():
        print('启动错误,查找运行中ands,尝试关闭………')
        # 端口占用,删除已存在的ands
        killAnds()
        # 再次启动ands
        print('再次尝试启动ands……')
        process = DoPopen(f'adb shell su -c "./data/local/tmp/ands -p{port}"')
        if process.poll():
            print(colored('ands开启失败！', 'red', attrs=['bold']))
            raise ChildProcessError

    # 转发端口
    forwardPort(port)
    return process

def openJdb(port:int=8700):
    ps = DoPopen(f"jdb -connect com.sun.jdi.SocketAttach:hostname=127.0.0.1,port={port}")
    if ps.poll():
        print(colored('jdb开启失败！','red',attrs=['bold']))
        raise ChildProcessError
    return ps



def getApkInfo(path:str) -> (str,str):
    """
    获取指定apk信息
    :param path:
    :return: packageName , mainActName
    """
    print('查询apk包名类名……')
    out =getOutPut(f"aapt2 d badging {path}")
    try:
        packageName = re.findall(r"package: name='(.+?)'",out)[0]
        actName = re.findall(r"launchable-activity: name='(.+?)'",out)[0]
    except IndexError:
        print(colored('查找指定APK包名、类名错误！','red',attrs=['bold']))
        raise LookupError
    print(colored(f"packageName:{packageName}\nmainActivity:{actName}",'green',attrs=['bold']))
    return packageName,actName

def installApk(path:str):
    # 尝试打开apk
    with open(path,'r') as apk:
        apk.close()
    # 安装apk
    print("尝试安装apk……")
    out = getOutPut(f"adb install -r -t {path}")
    if out.find('ailed')!=-1:
        print(colored(f'apk安装失败！请自行使用-d或-g参数安装apk！\n{out}','red',attrs=['bold']))
        raise FileExistsError
    else:print(colored(out,'green'))


@atexit.register
def doExit():
    if gSubProcessList:
        for ps in gSubProcessList:
            ps.kill()

if __name__ == '__main__':
    System('adb root')

    args = parser.parse_args()
    if args.log:
        LOG = True

    if args.androidServer: # 安装androidServer并启动
        gSubProcessList.append(openAndroidServer(args.androidServer))

    if args.jdb: # jdb
        gSubProcessList.append(openJdb(args.jdb))

    if args.apkInfo: # apkinfo
        if args.path:
            print(getApkInfo(args.path))
        else: raise parser.error('请使用-p传入apk路径！')

    if args.installApk: # 安装apk
        if args.path:
            installApk(args.path)
        else: raise parser.error('请使用-p传入apk路径！')

    if args.killAndroidServer: #关闭ands
        killAnds()

    if args.path and not args.apkInfo and not args.installApk: # debug模式启动并开启jdb
        # 未指定特殊端口情况下开启服务
        if not args.androidServer:
            gSubProcessList.append(openAndroidServer(23946))

        # debug模式开启apk
        installApk(args.path)
        packageName,actName = getApkInfo(args.path)
        out = getOutPut(f'adb shell am start -D -n {packageName}/{actName}')

        # 等待用户输入
        input = input(colored('使用8700端口开启jdb? y/port >','green'))
        jdbPort = 8700 if (not input or input=='y' or input=='Y') else input
        gSubProcessList.append(openJdb(int(jdbPort)))

    if gSubProcessList:
        for ps in gSubProcessList:
            ps.wait()