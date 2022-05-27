# MyTools

## 1. GetGpsFromAmap.py
通过高德api接口，搜索关键字返回结果。

**使用前请先填写自己的高德apiKey于 `GetGpsFromAmap/__init__/__apiKey` 位置**

- 结果内容包括：

  - 地点类型
  - 地点地址
  - 地点名称
  - 省
  - 市
  - 区
  - 经纬度
  - 其他(暂时觉得用不到)

  > 构造对象后可以使用`getAnswer`搜索并获得答案，
  > `getAddress`等获得细答案的函数必须使用在`setInfo`或者`getAnswer`后使用，否则没有答案。



## 2. DebugApk
获取root手机后的自动化debug流程，包括上传文件夹下的调试服务器，并以root方式启动
端口转发，debug模式启动apk

> 可以接收“发送到”的参数，所以可以打包了放sendto文件夹下

- 执行流程：
  - 通过命令行参数，或者拖入获得apk路径
  - 使用aapt2查询包名类名
  - 获取debug服务器需要开启的端口
  - 安装debugapk,将查询手机已存在包名列表，如果已经存在将跳过
  - 开启端口转发
  - debug模式启动apk
  - 新开窗口准备执行jdb指令
  - 上传android_server至/data/local/tmp
  - 启动./data/local/tmp下的以ands命名的android_server在设定的端口号上
  - 如果被直接返回(例如端口占用情况)将查找是否有已经在运行的ands并杀死后重启
  
 > 使用的是一大堆cmd命令、adb命令，获取返回值以后通过字符串操作来获得android的信息……
 > 技术含量很低，大佬轻喷
  
  **程序需要adb shell能进su**

  
## 3.GetExlFromMikeCRM.py
从http://sv.mikecrm.com/ 下载收到的反馈表单，需要 用户名，密码，表单id。
> 密码有两个，可以通过抓包得到.推荐使用utool的抓包插件，最方便了
> 表单id为**表单反馈页面的url结尾的id号**
> 不要太频繁了，当心自己的ip被mike限流

 - 使用流程
    ```python
    from GetExlFromMikeCRM import GetExl
    exl_path = GetExl("表单id").get_filename()
    #exl_path就是下载下来的新表单路径
    ```
**警告！！！**
**要注意有个函数为__del_oldFile() 会删除路径下所有以`.xls`结尾的文件。**

**可以在def__download_exl()函数内注释掉self.__del_oldFile()这一行**


## 4. moguding_sign.py
蘑菇丁app的每天自动签到。
**需要我写的另一个高德地图的文件一起使用**
- 使用方法
  ```python
  import moguding_sign
  moguding_sign.mgd_sign().set_accountInfo(account,password,address,city)
  mgd.run()
  #之后可以重复使用set_accountInfo()后调用run()不需要重复创建类对象
  ```
  自己觉得备注写的蛮全的了_(:_」∠)_ 不写其他的了
