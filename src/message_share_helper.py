from flask import Flask, request
from src.data_store import data_store
from src.error import InputError,AccessError
from src.helpers import decode_jwt
from datetime import datetime, timezone
from json import dumps


# def check_uid_valid(u_id):
#     initial_object = data_store.get()
#     user_detail = initial_object['users']
#     for i in user_detail:
#         if u_id == i['auth_user_id']:
#             return True
#     return False

def get_channel(channel_id):
    initial_object = data_store.get()
    channel_details = initial_object['channels']
    for i in channel_details:
        if channel_id == i['channel_id']:
            return i
    return None

def get_dm(dm_id):
    initial_object = data_store.get()
    dm_details = initial_object['dms']
    for i in dm_details:
        if dm_id == i['dm_id']:
            return i
    return None   

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

def valid_message_check(og_message_id,u_id):
    initial_object = data_store.get()
    channels_data = initial_object['channels']
    dm_data = initial_object['dms']


    for channels in channels_data:
        if u_id in channels['all_user_ids']:
            #   user in this channel
            for m in channels['messages']:
                if og_message_id == m['message_id']:
                    return m

    for dms in dm_data:
        if u_id in dms['u_ids'] or u_id == dms['creator']:
            for m in dms['messages']:
                if og_message_id == m['message_id']:
                    return m
    return None


def length_check(message):
    if len(message) > 1000:
        return False
    return True

def user_joined_dm_check(dm,u_id):

    if u_id in dm['u_ids'] or u_id == dm['creator']:
            return True
    return False

def user_joined_channel_check(channel,u_id):
    if u_id in channel['all_user_ids']:
        return True
    return False


def new_message_id_generate(old_message_id,id,message_dict,dict):
    x = [str(i) for i in str(old_message_id)]
    x.append(str(0))

    y = [str(i) for i in str(id)]
    y.append(str(len(message_dict)+dict['num_message_later']))

    return_x = str(''.join(x))
    return_y = str(''.join(y))
    return_id = return_x+return_y
    return int(return_id)


# ---------------------ADD REACT ID
def share_message_to_channel(message_dict,channel_dict,message,u_id):
    curr_time = datetime.now()
    timestamp = curr_time.replace(tzinfo=timezone.utc).timestamp()

    initial_object = data_store.get()


    old_message = message_dict['message']
    new_message_id = new_message_id_generate(message_dict['message_id'],channel_dict['channel_id'],message_dict,channel_dict)
    # new_message = old_message + ' '
    # new_message = new_message + '/n'+message
    new_message = message + "\n"+"\n" + old_message
    new_message_dict = {
        'message_id':new_message_id,
        'u_id':u_id,
        'message':new_message,
        'time_created':int(timestamp),
        'reacts': [
                {
                    'react_id': 1,
                    'u_ids': [],
                    'is_this_user_reacted': False
                }
            ],
        'is_pinned': False,
        'is_share_message':True
    }
    

    channel_dict['messages'].append(new_message_dict)
    data_store.set(initial_object)
    return new_message_id

def share_message_to_dm(message_dict,dm_dict,message,u_id):
    curr_time = datetime.now()
    timestamp = curr_time.replace(tzinfo=timezone.utc).timestamp()

    initial_object = data_store.get()
    # dm_data = initial_object['dms']
    # for i in dm_data:
    #     if i['dm_id'] == dm['dm_id']:
    #         dm_dict = i

    old_message = message_dict['message']
    new_message_id = new_message_id_generate(message_dict['message_id'],dm_dict['dm_id'],message_dict,dm_dict)
    new_message = old_message + ' '
    new_message = new_message + message
    new_message_dict = {
        'message_id':123,
        'u_id':u_id,
        'message':new_message,
        'time_created':int(timestamp),
        'reacts': [
            {
                'react_id': 1,
                'u_ids': [],
                'is_this_user_reacted': False
            }
        ],
        'is_pinned': False,
        'is_share_message':True,
    }
    

    dm_dict['messages'].append(new_message_dict)
    data_store.set(initial_object)
    return new_message_id



def check_if_removed(message_dict):
    send_user_id = message_dict['u_id']
    initial_object = data_store.get()
    user_data = initial_object['users']

    for user in user_data:
        if send_user_id == user['auth_user_id']:
            if user['is_removed'] == True:
                raise AccessError("User sendding this message already removed")


def message_share(token, og_message_id, message, channel_id, dm_id):
    u_id = find_id(token)
    dm = get_dm(dm_id)
    channel = get_channel(channel_id)
    message_dict = valid_message_check(og_message_id,u_id)

    if dm is None and channel is None:
        raise InputError("Both channel and dm id are invalid")
    
    if channel_id != -1 and dm_id != -1:
        raise InputError("Neither channel id and dm_id are -1")


    if message_dict is None:
        raise InputError("Message id not exist in that channel or dm")
    if not length_check(message):
        raise InputError("Length of message is too long")

    if channel_id == -1 and dm_id != -1:
        if not user_joined_dm_check(dm,u_id):
            raise AccessError("Not in dm")
    if  channel_id != -1 and dm_id == -1:
        if not user_joined_channel_check(channel,u_id):
            raise AccessError("Not in channel")
    
    if channel_id == -1 and dm_id != -1:
        #   sharing message in dm
        check_if_removed(message_dict)
        shared_id = share_message_to_dm(message_dict,dm,message,u_id)
 
    if channel_id != -1 and dm_id == -1:
        #   sharing message in channel
        check_if_removed(message_dict)
        shared_id = share_message_to_channel(message_dict,channel,message,u_id)
    

    return {'shared_message_id':shared_id}





