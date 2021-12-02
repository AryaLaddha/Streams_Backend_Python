import random
import pytest
from src.error import InputError
from src.error import AccessError
from src.data_store import data_store
import src.helpers

'''
Added functions ################################################
'''
def validate_user_id(auth_user_id):
    # if not isinstance(auth_user_id, int):
    #     return False
    store = data_store.get()
    users = store['users']
    for user in users:
        if user['auth_user_id'] == auth_user_id:
            return True
    return False
'''
Takes in a user_id and outputs the channels that the user is a part of

Arguments: 
    auth_user_id (integer): user_id of the person whose channels list is required
    
Exceptions:
    AccessError: auth_user_id passed is invalid
    
Return Values:
    Returns a dictionary made of list of channels that the user is part of which has
    entries of 'channel_id' and 'name' for each channel that the user is a part of
'''

def channels_list_v1(auth_user_id):
    if not validate_user_id(auth_user_id):
        raise AccessError
    joined_channels = []
    store = data_store.get()
    all_channels = store['channels']
    for channel in all_channels:
        for users in channel['all_user_ids']:
            if auth_user_id == users:
                entry = {'channel_id': channel['channel_id'], 'name': channel['name']}
                joined_channels.append(entry)
    return {'channels':joined_channels}

'''
Provide a list of all channels, including private channels, (and their associated details)

Arguments: 
    auth_user_id (integer): user_id of a registered user.
    
Exceptions:
    AccessError: auth_user_id passed is invalid
    
Return Values:
    Returns a dictionary made of list of all channels with entries like their channel_id
    and 'name' for each channel including private channels.
'''

def channels_listall_v1(auth_user_id):
    if not validate_user_id(auth_user_id):
        raise AccessError
    all_channels_list = []
    store = data_store.get()
    channels_list = store['channels']
    for channel in channels_list:
        entry = {'channel_id': channel['channel_id'], 'name': channel['name']}
        all_channels_list.append(entry)
    return {'channels': all_channels_list}


'''
Added functions ################################################
'''
#   check if the auth_user_id provided is valid and exists
# def auth_user_id_valid(auth_user_id,user_details):
#     for user in user_details:
#         if user['auth_user_id'] == auth_user_id:
#             return True
#     return False

#   check if the name entered has between 1 to 20 characters
def name_length_check(name):
    if len(name) < 1 or len(name)>20:
        return False
    return True

#   function that generates channel_id given the auth_user_id and whether the channel is public or private
def channel_id_generation(auth_user_id, is_public) :
    channel_id = []
    #   Assummptions: if public channel_id starts with 1, if private channel_id starts with 2
    if is_public == True:
        channel_id.append(1)
    else:
        channel_id.append(2)

    channel_id.append(auth_user_id)


    initial_object = data_store.get()
    channel_data = initial_object['channels']

    channel_id.append(len(channel_data))

    channel_id = [str(i) for i in channel_id]
    channel_id = int("".join(channel_id))

    return channel_id


    
#   test is user id exists
def user_detial_obtain(auth_user_id):
    initial_object = data_store.get()
    user_details = initial_object['users']
    user = {
        'u_id' : '',
        'email' : '',
        'name_first' : '',
        'name_last' : '',
        'handle_str' : '',
        'profile_img_url': ''
    }
    # for i in user_details:
    #     if i['auth_user_id'] == auth_user_id:
    #         user['u_id'] = i['auth_user_id']
    #         user['email'] = i['email']
    #         user['name_first'] = i['name_first']
    #         user['name_last'] = i['name_last']
    #         user['handle_str'] = i['handle_str']
    #         return user

    flag = 0
    return_value = {}
    for i in user_details:
        if i['auth_user_id'] == auth_user_id:
            flag = 1
            return_value = i
    if flag == 1:
        return user,return_value

def get_token(token):
    try:
        decoded_token = src.helpers.decode_jwt(token)
        return decoded_token
    except Exception as error:
        raise AccessError(description="invalid token") from error


def find_auth_id(token):
    initial_object = data_store.get()
    user_data = initial_object['users']

    # try:
    #     decoded = src.helpers.decode_jwt(token)
    # except Exception as error:
    #     raise AccessError(descriptionn = "invalid token") from error
    decoded = get_token(token)


    for user in user_data:
        if (decoded['username'] == str(user['auth_user_id']) and decoded['session_id'] in user['session_list']):
            if user['is_removed'] == False:
                return user['auth_user_id']
            else:
                raise AccessError("User already removed")

    return None



def channels_create_v1(auth_user_id, name, is_public):
    """
    Description:
        This function will create a new channel and store its details
        in data_store, which will then be accessible for other function
        This function returns 'channel_id'.

    Arguments:
        auth_user_id  - integer - Id of the creator of the channel
        name          - string  - The name that the user wants for the channel
        is_public     - boolean - "False" for private and "True" for public channel

    Exceptions:
        InputError  - Occurs when the name length is not correct.
        AccessError - Occurs when the auth_user_id is not present in data_store or invalid
        
    Return Value:
        Returns { 'channel_id' : channel_id } (Integer Value) if there are no InputErrors.
    """

    initial_object = data_store.get()
    channel_details = initial_object['channels']



    if name_length_check(name) is False:
        raise InputError

    channel_id = channel_id_generation(auth_user_id,is_public)

    # while channel_id_dup_check(channel_id,channel_details):
    channel_id = channel_id_generation(auth_user_id,is_public)

    channel_dict = {}


    user_dict, return_value = user_detial_obtain(auth_user_id)
    user_dict['u_id'] = return_value['auth_user_id']
    user_dict['email'] = return_value['email']
    user_dict['name_first'] = return_value['name_first']
    user_dict['name_last'] = return_value['name_last']
    user_dict['handle_str'] = return_value['handle_str']
    user_dict['profile_img_url'] = return_value['profile_img_url']


    #user_dict = user_detial_obtain(auth_user_id)
    channel_dict['channel_id'] = channel_id
    channel_dict['name'] = name
    channel_dict['original_user_id'] = auth_user_id
    channel_dict['all_user_ids'] = [auth_user_id]
    channel_dict['is_public'] = is_public
    channel_dict['messages'] = []
    channel_dict['owner_members'] = [user_dict]
    channel_dict['all_members'] = [user_dict]
    channel_dict['is_standup'] = False
    channel_dict['num_message_later'] = 0
    channel_dict['standup'] = {'message_queue': [], 'time_finish' : -1}

    channel_details.append(channel_dict)
    data_store.set(initial_object)

    return {
        'channel_id': channel_id
    }
