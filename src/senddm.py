from src.config import url
from json import dumps
from flask import Flask, request
from src.data_store import data_store
from src.error import InputError,AccessError
import src.helpers
import random
from datetime import datetime, timezone
import time


def check_dm_id(dm_id):
    initial_object = data_store.get()
    dm_details = initial_object['dms']

    for dm_specific in dm_details:
        if dm_id == dm_specific['dm_id']:
            return True
    return False


def message_length_check(message):
    if len(message) < 1 or len(message) > 1000:
        return False
    return True



def decode_token(token):


    try:
        decoded_token = src.helpers.decode_jwt(token)
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
            else:
                raise AccessError("User already removed")



def auth_user_in_dm(authorised_id,dm_dict):
    if authorised_id == dm_dict['creator']:
        return True

    if authorised_id in dm_dict['u_ids']:
        return True
    return False

def create_message_id(u_id,dm_id):
    
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





def message_send(token,dm_id,message):
    if not message_length_check(message):
        raise InputError('Message length not in range')
    
    if check_dm_id(dm_id) == False:
        raise InputError("dm_id not refer to specific dm")

    initial_object = data_store.get()
    dm_details = initial_object['dms']
    
    for dictionary in dm_details:
        if dictionary['dm_id'] == dm_id:
            dm_dict = dictionary

    user_id = find_id(token)
    # if user_id == None:
    #     raise AccessError(f"token None {token} and returned {user_id}")

    if check_dm_id(dm_id) and auth_user_in_dm(user_id,dm_dict) == False:
        raise AccessError("dm_id valid but authorisation not in dm")

    # if check_if_removed(user_id) == True:
    #     raise AccessError("User already removed")

    message_id = create_message_id(user_id,dm_id)
    # while check_dup_message_id(message_id):
    #     message_id = create_message_id(user_id,dm_id)

    # curr_time = datetime.now()
    # timestamp = curr_time.replace(tzinfo=timezone.utc).timestamp()

    dm_dict['messages'].append({'message_id':message_id,
                                'u_id':user_id,
                                'message':message,
                                'time_created':int(time.time()),
                                'reacts': [
                                    {
                                        'react_id': 1,
                                        'u_ids': [],
                                        'is_this_user_reacted': False
                                    }
                                ],
                                'is_pinned': False,
                                'is_shared_message':True})


    data_store.set(initial_object)

    return message_id

