# -*- coding: utf-8 -*-
import requests
import time
import json
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from cmslib import *
import sys

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
attendees = []
meet_num = ''

# with open('meet.json', 'r') as file_obj:
#     meet_info = json.load(file_obj)
#
# cms_url = meet_info['cms_url']
# apiuser = meet_info['apiuser']
# apipassword = meet_info['apipassword']
# attendees = meet_info['attendees']

if len(sys.argv)<3:
    meet_num = '8002'
    address_book = 'addr_book.json'
    print('''\nUsage: python3 cms_outbound.py [meet number] [address book].
    The default meet number is 8002.
    The default address book is addr_book.json\n''')
else:
    meet_num = sys.argv[1]
    address_book = sys.argv[2]

try:
    with open(address_book, 'r') as f_obj:
        attendees = json.load(f_obj)

    print('The following attendees will be invited:')
    for attendee in attendees:
        print('\t' + attendee)

# 如果文件不存在
except FileNotFoundError:
    msg = "Sorry, the file " + address_book + " does not exist.\n"
    msg += 'Will now create the address book: ' + address_book
    print(msg)
    create_addr_book(address_book)
    with open(address_book, 'r') as f_obj:
        attendees = json.load(f_obj)


if system_status_ok():
    print('\n' + '=' * 10 + 'starting now' + '=' * 10 + '\n')
    coSpace_id = get_coSpace_id(meet_num)
    # coSpace_id = '513df603-97f9-44af-94cc-c1158b02e801'
    creat_meeting(coSpace_id, my_headers)
    if coSpace_id != None:
        the_call_id = get_call_id(coSpace_id)
    else:
        print("coSpace is not Null.")
        sys.exit()

    if the_call_id == None:
        print('Meeting is not been created.')
    else:
        for attendee in attendees:
            call_attendee(the_call_id, my_headers, attendee)
            time.sleep(0.3)

        print("Please wait 5 seconds to check the status.")
        i = 1
        while i < 6:
            print('.' * 10 + str(i) + '.' * 10)
            time.sleep(1)
            i += 1

        for attendee in attendees:
            call_leg_id = is_online(the_call_id, attendee)
            if call_leg_id == None:
                break
            elif call_leg_id == 1:
                continue
            else:
                print(call_leg_id)

    # start_record(the_call_id, my_headers)