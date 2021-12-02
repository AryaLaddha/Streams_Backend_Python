from flask import Flask, request
from src.data_store import data_store
from src.error import InputError,AccessError
from src.helpers import decode_jwt
from datetime import datetime, timezone, time
from json import dumps
from datetime import datetime
from time import sleep
import threading
from src.stats_helper import update_user_activity_messages_id
from src.notification_helper import notification_message_send, notification_senddm

MESSAGE_STORAGE = 100

def check_channel(channel_id):
    initial_object = data_store.get()
    channels = initial_object['channels']

    all_id = [channel_data['channel_id'] for channel_data in channels]
    return channel_id in all_id
    # for channel_detail in channels:
    #     if channel_detail['channel_id'] == channel_id:
    #         return channel_detail
    # return None

def check_dm(dm_id):
    initial_object = data_store.get()
    dms = initial_object['dms']

    all_id = [dm_dict['dm_id'] for dm_dict in dms]
    return dm_id in all_id
    # for dm_dict in dms:
    #     if dm_dict['dm_id'] == dm_id:
    #         return True
    # return False

def decode_token(token):
    try:
        decoded_token = decode_jwt(token)
        return decoded_token
    except Exception as error:
        raise AccessError(description="invalid token") from error

def find_id(token):
    initial_object = data_store.get()
    user_data = initial_object['users']

    decoded = decode_token(token)

    for user in user_data:
        if (decoded['username'] == str(user['auth_user_id']) and decoded['session_id'] in user['session_list']):
            if user['is_removed'] == False:
                return user['auth_user_id']
            raise AccessError("User already removed")

def length_message_check(message):
    # if len(message) > 1000:
    #     return true
    # return false
    return len(message) > 1000

def check_user_in_dm(u_id,dm_dict):
    if dm_dict['creator'] == u_id or u_id in dm_dict['u_ids']:
        return True
    return False

def get_wait_time(time_sent):
    time_get = datetime.fromtimestamp(time_sent,tz=timezone.utc)

    now_time = datetime.now(timezone.utc)

    timestamp = datetime.fromtimestamp(time_sent)
    print(f"time get is {time_get} and timestamp {timestamp} and now is {now_time}")
    diff = (time_get - now_time).total_seconds()
    print(f"time diff is {diff}")
    if diff < 0:
        raise InputError("tme_sent is a time in the past")
    return time_get,diff

#   check if time has passed current time
# def check_time(time_sent):
#     curr_time = datetime.now()
#     if time_sent < curr_time:
#         return False
#     return True

def check_user_in_channel(channel_dict, u_id):
    return u_id in channel_dict['all_user_ids']


def create_dm_message_id(u_id,dm_id):
    
    return_list = [str(x) for x in str(dm_id)]

    for a in str(u_id):
        return_list.append(a)
        
    initial_object = data_store.get()
    dms_data = initial_object['dms']
    for dm in dms_data:
        if dm['dm_id'] == dm_id:
            return_list.append(str(len(dm['messages'])+dm['num_message_later']))

    string_return_id = (''.join(return_list))

    return int(string_return_id)


def send_dm_message(token,dm_dict,dm_id,message_id,u_id,message,timestamp,wait_time):
    initial_object = data_store.get()
    # all_dm = [dms for dms in initial_object['dms']]
    # for dm in all_dm:
    #     if dm['dm_id'] == dm_id:
    #         dm_dict = dm


    sleep(wait_time)
    dm_dict['messages'].append({'message_id':message_id,
                        'u_id':u_id,
                        'message':message,
                        'time_created':int(timestamp),
                        'reacts': [
                                {
                                    'react_id': 1,
                                    'u_ids': [],
                                    'is_this_user_reacted': False
                                }
                            ],
                            'is_pinned': False,
                            'is_shared_message':True})

    dm_dict['num_message_later'] -= 1

    notification_senddm(token, dm_id, message)

    data_store.set(initial_object)


def send_channel_message(channel_id,token,channel_dict,initial_object,message_id,u_id,message,timestamp,wait_time):

    sleep(wait_time)
    channel_dict['messages'].append({
        'message_id':message_id,
        'u_id':u_id,
        'message':message,
        'time_created':int(timestamp),
        'reacts': [
                    {
                        'react_id': 1,
                        'u_ids': [],
                        'is_this_user_reacted': False
                    }
                ],
                'is_pinned': False,
                'is_shared_message':True
    })

    channel_dict['num_message_later'] -= 1
    update_user_activity_messages_id(u_id)

    notification_message_send(token, channel_id, message)

    data_store.set(initial_object)


#   --------------------------Main implementation-----------------------

def message_sendlater(token, channel_id, message, time_sent):
    if not check_channel(channel_id):
        raise InputError("Channel_id not exist")

    if length_message_check(message):
        raise InputError("Length of message is too long")
    
    initial_object = data_store.get()
    channels_data = initial_object['channels']
    for channel in channels_data:
        if channel['channel_id'] == channel_id:
            channel_dict = channel

    input_datetime,wait_time = get_wait_time(time_sent)
    timestamp = input_datetime.replace(tzinfo=timezone.utc).timestamp()

    u_id = find_id(token)
    if not check_user_in_channel(channel_dict,u_id):
        raise AccessError("Channel exist but user not in it")
    
    message_id = (channel_id * MESSAGE_STORAGE) + len(channel_dict['messages'])+channel_dict['num_message_later'] + 1

    channel_dict['num_message_later'] += 1
    data_store.set(initial_object)
    
    t2 = threading.Thread(target = send_channel_message,args=[channel_id,token,channel_dict,initial_object,message_id,u_id,message,timestamp,wait_time])
    t2.start()
    return message_id






def dm_sendlater(token, dm_id, message, time_sent):


    if check_dm(dm_id) == False:
        raise InputError("dm_id not exist")

    initial_object = data_store.get()
    dms = initial_object['dms']
    for dm_data in dms:
        if dm_data['dm_id'] == dm_id:
            dm_dict = dm_data

    if length_message_check(message):
        raise InputError("Length of message is too long")


    input_datetime,wait_time = get_wait_time(time_sent)
    timestamp = input_datetime.replace(tzinfo=timezone.utc).timestamp()


    u_id = find_id(token)
    if not check_user_in_dm(u_id,dm_dict):
        raise AccessError("Dm exist but user not in it")


    message_id = create_dm_message_id(u_id,dm_id)

    dm_dict['num_message_later'] += 1
    data_store.set(initial_object)
    t1 = threading.Thread(target = send_dm_message,args=[token,dm_dict,dm_id,message_id,u_id,message,timestamp,wait_time])
    t1.start()


    return message_id

