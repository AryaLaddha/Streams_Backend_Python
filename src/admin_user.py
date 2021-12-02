from src.channels import channels_create_v1
from src.config import url
from json import dumps
from flask import Flask, request
from src.data_store import data_store
from src.error import InputError,AccessError
import src.helpers

def check_uid_valid(u_id):
    users = data_store.get()['users']
    existing_ids = [user['auth_user_id'] for user in users]
    return u_id in existing_ids


def check_global(u_id):
    initial_object = data_store.get()
    user_detail = initial_object['users']
    for i in user_detail:
        if u_id == i['auth_user_id']:
            if i['permission_id'] == 1:
                #   global owner
                return True
            return False
    # return False

def check_only_global(u_id):
    initial_object = data_store.get()
    user_detail = initial_object['users']

    for i in user_detail:
        if i['permission_id'] == 1:
            if i['auth_user_id'] != u_id:
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
                return user
            raise AccessError("User already removed")




def remove_user(u_id,user_dict):
    initial_object = data_store.get()
    user_data = initial_object['users']
    dm_data = initial_object['dms']
    channel_data = initial_object['channels']

    for i in user_data:
        if i['auth_user_id'] == u_id:
            if i['is_removed'] == True:
                raise AccessError("User already removed")
            i['name_first'] = "Removed"
            i['name_last'] = "user"
            i['is_removed'] = True
    
    
    for channels in channel_data:
        for owner_detail in channels['owner_members']:
            if owner_detail['u_id'] == u_id:
                channels['owner_members'].remove(owner_detail)
                break
        for user_id in channels['all_user_ids']:
            if u_id == user_id:
                channels['all_user_ids'].remove(u_id)
                break

        for user_detail in channels['all_members']:
            if user_detail['u_id'] == u_id:
                channels['all_members'].remove(user_detail)
                break
        if channels['original_user_id'] == u_id:
            channels['original_user_id'] = -1

        for message_detail in channels['messages']:
            if message_detail['u_id'] == u_id:
                message_detail['message'] = "Removed user"
                break

    for dms in dm_data:
        for dm_detail in dms['messages']:
            if dm_detail['u_id'] == u_id:
                dm_detail['message'] = "Removed user"
                dm_detail['u_id'] = -1
        if dms['creator'] == u_id:
            dms['creator'] = -1
        for ind_id in dms['u_ids']:
            if ind_id == u_id:
                dms['u_ids'].remove(u_id)

    data_store.set(initial_object)

    

def permission_change(u_id,permission_id):
    initial_object = data_store.get()
    user_detail = initial_object['users']

    #   permission id 1 means global owner, 2 means member
    for i in user_detail:
        if i['auth_user_id'] == u_id:
            if i['is_removed'] == True:
                raise AccessError("User has been removed")
            i['permission_id'] = permission_id
            break

    data_store.set(initial_object)
