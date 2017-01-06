# -*- coding: utf-8 -*-
'''此文件定义了若干函数，用于CMS外呼调用'''
import requests
import xmltodict
import json


# 定义全局变量
apiuser = 'webapi'
apipassword = 'C1sco123'
my_headers = {'content-type': "application/x-www-form-urlencoded"}


# 检查系统状态是否OK
def system_status_ok():
    cms_url = 'https://10.74.164.204/api/v1/system/status'
    response = requests.request("GET", cms_url,
                                auth=(apiuser, apipassword), verify=False)
    # 如果返回状态不是2XX，则返回相应的Status Code，否则返回真值
    if not response.status_code // 100 == 2:
        print("Error: Unexpected response {}".format(response))
        return False
    else:
        return True


# 根据callId查找coSpace ID.
def get_coSpace_id(callId):
    # 修改url访问coSpaces
    cms_url ='https://10.74.164.204/api/v1/coSpaces'
    cms_url += '?filter=' + callId
    # 赋值coSpace_id为空
    coSpace_id = None
    response = requests.request("GET", cms_url,
                                auth=(apiuser, apipassword), verify=False)

    # 将返回的xml内容存储到文件
    with open('coSpace.xml', 'w') as f_obj:
        f_obj.write(response.text)
    # 将xml文件转换为字典
    with open('coSpace.xml') as fd:
        doc = xmltodict.parse(fd.read())

    if doc['coSpaces']['@total'] == '0':
        print('The meeting ' + callId + ' is not found.')
        return None
    elif doc['coSpaces']['coSpace']['callId'] == callId:
        coSpace_id = doc['coSpaces']['coSpace']['@id']

    return coSpace_id
    # 如果不做过滤根据callId来查找coSpace的ID
    # for value in doc['coSpaces']['coSpace']:
    #     if value['callId'] == callId:
    #         coSpace_id = value['@id']
    #     else:
    #         continue
    # # 如果找到对应coSpace ID，则返回该值；否则返回None
    # if coSpace_id != '':
    #     return coSpace_id
    # else:
    #     print("Can not find the callId " + callId + '.')
    #     return None


# 根据coSpace_id创建呼叫
def creat_meeting(coSpace_id, header):
    # 修改url访问calls
    cms_url = 'https://10.74.164.204/api/v1/calls'
    payload = 'coSpace=' + coSpace_id
    response = requests.request("POST", cms_url, headers=header, data=payload,
                                auth=(apiuser, apipassword), verify=False)
    if response.status_code // 100 == 2:
        print('Meeting is created... Response：' + str(response.status_code))
    else:
        print('Meeting is not created... Response: ' + str(response.status_code))


# 查找返回的呼叫ID
def get_call_id(coSpace_id):
    # 修改url访问calls
    cms_url = 'https://10.74.164.204/api/v1/calls?coSpacefilter='
    cms_url += coSpace_id
    # 赋值call_id为空
    call_id = None
    response = requests.request("GET", cms_url,
                                auth=(apiuser, apipassword), verify=False)
    if response.status_code == 200:
        # 将返回的xml内容存储到文件
        with open('calls.xml', 'w') as f_obj:
            f_obj.write(response.text)

        # 将xml文件转换为字典
        with open('calls.xml') as fd:
            doc = xmltodict.parse(fd.read())
        if doc['calls']['@total'] == '0':
            print('No active calls in the coSpace ' + coSpace_id)
            call_id = None
        elif doc['calls']['call']['coSpace'] == coSpace_id:
            call_id = doc['calls']['call']['@id']
        else:
            call_id = None
    else:
        print(response.status_code)
    # 如果找到对应Call ID，则返回Call ID，没找到则返回None
    return call_id


# 呼叫参会者
def call_attendee(call_id, header, call_uri):
    # 修改url访问callleg
    cms_url = 'https://10.74.164.204/api/v1/calls/'
    cms_url += call_id + '/callLegs'
    payload = 'remoteParty=' + call_uri
    response = requests.request("POST", cms_url, headers=header, data=payload,
                                auth=(apiuser, apipassword), verify=False)
    if response.status_code == 200:
        print('Calling ' + call_uri + '...')
    else:
        print('Calling failed status: '+ str(response.status_code))


# 查看参会者是否上线
def is_online(call_id, call_uri):
    # 修改url访问calls
    cms_url = 'https://10.74.164.204/api/v1/calls/'
    cms_url += call_id + '/callLegs'
    call_leg_id = ''
    response = requests.request("GET", cms_url,
                                auth=(apiuser, apipassword), verify=False)

    # 将返回的xml内容存储到文件
    with open('current_calls.xml', 'w') as f_obj:
        f_obj.write(response.text)

    # 将xml文件转换为字典
    with open('current_calls.xml') as fd:
        doc = xmltodict.parse(fd.read())

    # 将is_onlie初始值设置为False
    is_online = False
    total_online = doc['callLegs']['@total']
    # 如果在线人数为0，直接结束查找，返回None
    if total_online == '0':
        print("No one is online, end checking.")
        return None
    # 如果只有一个在线，只返回一个字典类型
    elif total_online == '1':
        print('=' * 20)
        print('Checking ' + call_uri + '...')
        if doc['callLegs']['callLeg']['remoteParty'] == call_uri:
            is_online = True
            call_leg_id = doc['callLegs']['callLeg']['@id']
        else:
            is_online = False
    # 如果多人在线，返回一个包含字典的列表，需要遍历该列表
    else:
        print('=' * 20)
        print('Checking ' + call_uri + '...')
        for item in doc['callLegs']['callLeg']:
            if item['remoteParty'] == call_uri:
                is_online = True
                call_leg_id = item['@id']
            else:
                continue
    if is_online:
        print(call_uri + ' is on line.')
        return call_leg_id
    else:
        print(call_uri + ' is not online.')
        return 1


# 生成地址本
def create_addr_book(address_book):
    attendees = []
    promt = 'Please enter the attendee URI in sequence, ' \
            'type \'q\' when complete:'
    while True:
        attendee = input(promt)
        if attendee != 'q':
            attendees.append(attendee)
        else:
            break
    print('\n\tYou\'v input the following:')
    for attendee in attendees:
        print('\t\t' + attendee)
    confirm = input('\nAre these right?y/n -')
    while True:
        if confirm == 'y':
            with open(address_book, 'w') as file_obj:
                json.dump(attendees, file_obj)
                print('Save to ' + address_book)
            break
        elif confirm != 'n':
            print('Invalid input')
        elif confirm == 'n':
            print('Please restart this program.')
            break


# 开始录制会议
def start_record(call_id, header):
    # 修改url访问calls
    cms_url = 'https://10.74.164.204/api/v1/calls/' + call_id
    payload = 'recording=true'
    response = requests.request("PUT", cms_url, headers=header, data=payload,
                                auth=(apiuser, apipassword), verify=False)
    if response.status_code == 200:
        print('The meeting is now recorded.')


# 结束录制会议
def stop_record(call_id, header):
    # 修改url访问calls
    cms_url = 'https://10.74.164.204/api/v1/calls/' + call_id
    payload = 'recording=false'
    response = requests.request("PUT", cms_url, headers=header, data=payload,
                                auth=(apiuser, apipassword), verify=False)
    if response.status_code == 200:
        print('The recording is now stoped.')


# 结束当前会议
def end_meeting(call_id, header):
    # 修改url访问calls
    cms_url = 'https://10.74.164.204/api/v1/calls/' + call_id
    response = requests.request("DELETE", cms_url, headers=header,
                                auth=(apiuser, apipassword), verify=False)
    if response.status_code == 200:
        print('The recording is now stoped.')