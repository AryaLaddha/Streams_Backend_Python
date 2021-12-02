from src.helpers import generate_new_session_id, generate_jwt, decode_jwt
from src.error import InputError, AccessError
from src.data_store import data_store
import math, random
import smtplib
import re
import json

def list_dm_update(search_list, query_str, dms):
    for dm in dms:
        for message in dm['messages']:
            if query_str in message['message']:
                temp = {
                    'message_id':message['message_id'],
                    'u_id':message['u_id'],
                    'message':message['message'],
                    'time_created':message['time_created'],
                    'reacts':message['reacts'],
                    'is_pinned':message['is_pinned']
                }
                search_list.append(temp)
    return search_list

def list_channel_update(search_list, query_str, channels):
    for channel in channels:
        for message in channel['messages']:
            if query_str in message['message']:
                temp = {
                    'message_id':message['message_id'],
                    'u_id':message['u_id'],
                    'message':message['message'],
                    'time_created':message['time_created'],
                    'reacts':message['reacts'],
                    'is_pinned':message['is_pinned']
                }
                search_list.append(temp)
    return search_list

def get_channels(user_id, channel_details):
    channel_list = []
    for channel in channel_details:
        if user_id in channel['all_user_ids']:
            channel_list.append(channel)
    return channel_list

def get_dms(user_id, dm_details):
    dm_list = []
    for dm in dm_details:
        if user_id in dm['u_ids'] or user_id == dm['creator']:
            dm_list.append(dm)
    return dm_list

def secret_code_present(SECRET_CODE, password_reset_user): # pragma: no cover
    for user in password_reset_user:
        if user['secret_code'] == SECRET_CODE:
            return True
    return False

def generateOTP(): # pragma: no cover
    digits = "0123456789"
    OTP = ""

    OTP += digits[math.floor(random.random() * 10)]
    OTP += digits[math.floor(random.random() * 10)]
    OTP += digits[math.floor(random.random() * 10)]
    OTP += digits[math.floor(random.random() * 10)]
    OTP += digits[math.floor(random.random() * 10)]
    OTP += digits[math.floor(random.random() * 10)]
    OTP += digits[math.floor(random.random() * 10)]
    OTP += digits[math.floor(random.random() * 10)]

    return OTP

def verify_token_logout(decoded_token, user_details):
    for user in user_details:
        if user['token'] == decoded_token['username'] and decoded_token['session_id'] in user['session_list']:
            if not user['is_removed']:
                user['session_list'].remove(decoded_token['session_id'])
                return True
    raise AccessError(description="invalid token")

def verify_login(user_details,email,password):
    for i in user_details:
        if i['email'] == email and i['password'] == password and not i['is_removed']:
            return i['auth_user_id']
    raise InputError(description="Email or password incorrect")

def handle_present(user_details,handle_str):
    for i in user_details:
        if i['handle_str'] ==  handle_str and not i['is_removed']:
            return True
    return False

def remove_non_alnum(name_first,name_last):
    n1 = re.sub(r'[\W_]+', '', name_first)
    n2 = re.sub(r'[\W_]+', '', name_last)
    return n1.lower(), n2.lower()

def create_user_handle(name_first,name_last):
    name_first,name_last = remove_non_alnum(name_first,name_last)
    name = name_first + name_last
    if len(name) < 21:
        return name
    return name[0:21]

def final_handle(user_details, handle_str):
    if handle_present(user_details,handle_str):
        i = 0
        handle_str += str(i)
        i += 1
        while handle_present(user_details,handle_str):
            length = len(str(i))
            handle_str = handle_str[0:len(handle_str) - length]
            handle_str += str(i)
            i += 1
    return handle_str

def checker(user_details,email,password,name_first,name_last):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

    if not (1 <= len(name_first) <= 50 and 1 <= len(name_last) <= 50):
        raise InputError(description="Word limit exceeded or empty field entered")

    if not re.fullmatch(regex, email):
        raise InputError(description="Invalid email format")

    for i in user_details:
        if i['email'] == email and i['is_removed'] is False:
            raise InputError(description="User already registered")

    if len(password) < 6:
        raise InputError(description="Length of password not greater than 6")

    return True

def get_permission_id(auth_user_id):
    if auth_user_id == 1:
        return 1
    return 2
