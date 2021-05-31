import requests
import json
import re
import argparse
import sys
import time
from requests.api import head
#防止在控制台输出SSL不安全信息，手动关闭警告
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)\

parser = argparse.ArgumentParser(description="\033[32mThis is a Title\033[0m")
parser.add_argument("-r",help="读取文档中目标并添加")
# parser.add_argument("-s",help="秀一手")
parser.add_argument("-n",help="最大扫描数（默认为3）")
parser.add_argument("-t",help="检测时间（默认为10秒）")

args = parser.parse_args()

max_num = 3
max_time = 10


def title():
    print('\033[34m===============================\033[0m')
    print('\033[35m          欢 迎 使 用\033[0m')
    print('\033[32mr读取url文档，-r test.txt\033[0m')
    print('\033[32mn设置最大扫描数，-r 2 默认为3\033[0m')
    print('\033[32mt设置检测间隔时间，-t 10 默认为10\033[0m')
    print('\033[34m===============================\033[0m')

#获取url列表
def get_target(file):
    try:
        with open(file,"r",encoding="UTF-8") as f:
            content = f.readlines()
        return content
    except Exception as e:
        print("no such file\n")
        sys.exit(0)


#获取目前扫描个数
def get_scanningnum(headers):
    api_url = "https://yourAWVSIP/api/v1/me/stats"
    ret = requests.get(url = api_url,headers = headers,verify=False).text
    ret = json.loads(ret)
    return ret['scans_running_count']


#添加目标
def add_target(target_list,headers):
    count = 1
    id_list = []

    api_url='https://yourAWVSIP/api/v1/targets'
    property_name = input("请输入资产名:\n")
    for each_target in target_list:
        print("目标%d已读取并添加进目标中："%(count)+each_target)
        count=count+1
        data = {
            "address" : each_target,
            "description" : property_name,
            "criticality" : "10"
        }
        data = json.dumps(data)
        ret = requests.post(url = api_url,headers=headers,verify=False,data=data).text
        ret = json.loads(ret)
        print("目标targetID为："+ret['target_id'])
        print("=======================================================")

        id_list.append(ret["target_id"])
    return id_list

#添加扫描
def add_scan(headers,max_num,waiting_time,id_list):
    count = 1
    print("当前最大扫描数为%s"%max_num)
    for i in id_list:

        scanningnum = get_scanningnum(headers)
        while scanningnum >= int(max_num):
            print("当前已到达/超过最大扫描数，服务器顶不住了，请等待%s秒"%waiting_time)
            print("当前正在扫描的数量为：%d"%scanningnum)
            time.sleep(int(waiting_time))
            scanningnum = get_scanningnum(headers)
        
        #此时可添加扫描
        api_url = "https://yourAWVSIP/api/v1/scans"
        data = {
            "target_id":i,
            "profile_id":"11111111-1111-1111-1111-111111111111",
            "schedule":    
                {
                    "disable":False,
                    "start_date":None,
                    "time_sensitive":False
                }
        }
        data = json.dumps(data)
        ret = requests.post(url = api_url,headers = headers,data = data,verify=False).text
        print("已添加扫描第%d个目标"%count)
        count+=1
        time.sleep(3)
    print("添加扫描结束！")

def init():
    file = args.r
    scanningnum = get_scanningnum(headers)
    if(file):
        url_list = get_target(file)
        id_list = add_target(url_list,headers)
        add_scan(headers,max_num,max_time,id_list)
    print("当前正在扫描的数量为：%d"%scanningnum)
    
if __name__=='__main__':
    title()
    id_list = []
    headers = {
        'X-Auth' : 'YOUR AWVS API-KEY',
        'Content-type' : 'application/json'
    }
    if(args.t):max_time = args.t
    if(args.n):max_num = args.n
    init()