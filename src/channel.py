'''
 Authors: Sean Huynh, (JP) Jonathan Pan
 Date: 24/10/2021
 Implementation file for channel functions
 
 This program contains part of the implementation functions for UNSW
 Streams
'''
from src.data_store import data_store
from src.error import InputError
from src.error import AccessError
import src.helpers
import src.implementation_helpers as jp
import json


def check_valid_auth(token, users):
    try:
        decode_token = src.helpers.decode_jwt(token)
    except Exception as error:
        raise AccessError(description="invalid token") from error

    valid = False
    auth_id = -1
    for user in users:
        if decode_token['username'] == str(user['auth_user_id']) and decode_token['session_id'] in user['session_list']:
            valid = True
            auth_id = user['auth_user_id']

    if not valid:
        raise AccessError(description='caller does not exist')

    return auth_id

def check_unathorised_member(auth_id, members):
    '''This is to check if the member is not apart of the channel.'''
    unauth_id = False

    for user in members:
        if auth_id == user['u_id']:
            unauth_id = True

    if not unauth_id:
        raise AccessError("unauthorised user")

def get_user_handle(token):
    final_user = ''
    decoded_token = src.helpers.decode_jwt(token)
    for user in data_store.get()['users']:
        if user['token'] == decoded_token['username']:
            final_user = user['handle_str']
    return final_user

def channel_invite_v2(token, channel_id, u_id):
    '''
    channel_invite_v1 will invite a user with u_id to a channel with
    channel_id.
    Once, that happens, their details will be stored in the channels list
    (data_store).

    Arguments:
        auth_user_id (integer) - the user who is inviting another user.
        channel_id (integer) - the channel that the invited user will join.
        u_id (integer) - the user who is being invited.

    Exceptions:
        InputError - Occurs when the channel_id does not refer to a valid
                    channel.
                   - Occurs when the u_id doesn't refer to a valid user.
                   - Occurs when the user with u_id is already in the
                    channel.

        AccessError - Occurs when the auth_user_id doesn't refer to a valid
                      auth_user_id.
                    - Occurs when there is no one that exists in the channel
                    - Occurs when the auth_user_id is not in the
                      channel_details.

    Return Value:
        Returns {} when the auth_user_id, channel_id, and u_id are all
        valid.
    '''
    #This grabs the users and channels from the database.
    store = data_store.get()
    stored_channels = store['channels']
    stored_users = store['users']
    channel_detail = {}

    auth_id = check_valid_auth(token, stored_users)

    #This checks if the inputted channel_id is valid (if it exists).
    for channel in stored_channels:
        if channel_id == channel['channel_id']:
            channel_detail = channel
            break

    #This raises an InputError if there is no channel with the channel_id.
    if len(channel_detail) == 0:
        raise InputError(description="invalid channel_id")

    #This goes through all members in channels and checks if the
    #auth_user_id is in the channel. It also checks if the u_id is already
    #in the channel.
    members = channel_detail['all_members']
    members_id = channel_detail['all_user_ids']

    check_unathorised_member(auth_id, members)

    for user in members:
        if u_id == user['u_id']:
            raise InputError(description="user in channel already")

    invited_user = {}

    #This goes through the users database and gets data from the specified
    #user with u_id.
    for users in stored_users:
        if u_id == users['auth_user_id']:
            invited_user = {
                'u_id': users['auth_user_id'],
                'email': users['email'],
                'name_first': users['name_first'],
                'name_last': users['name_last'],
                'handle_str': users['handle_str'],
                'profile_img_url': users['profile_img_url']
            }

    #This checks if it can't find the user.
    if len(invited_user) == 0:
        raise InputError("invited user does not exist")

    #This appends the invited_user to the channel's database.
    members.append(invited_user)
    members_id.append(invited_user['u_id'])

    ####### Notifications #######

    final_handle = get_user_handle(token)
    notification_dictionary = {
        'channel_id':channel_id,
        'dm_id':-1,
        'notification_message':f"{final_handle} added you to {channel_detail['name']}"
    }
    flag = 0
    notifications = data_store.get()['notifications']
    if notifications == []:
        notifications.append(
            {
                'u_id' : u_id,
                'notified' : [notification_dictionary]
            }
        )
    else:
        for uids in notifications:
            if uids['u_id'] == u_id:
                flag = 1
                uids['notified'].append(notification_dictionary)
        if flag == 0:
            notifications.append(
                {
                    'u_id' : u_id,
                    'notified' : [notification_dictionary]
                }
            )

    ####### Notifications #######

    data_store.set(store)

    return {}

def channel_details_v2(token, channel_id):
    '''
    Channel_details will produce the details of a channel, given that the
    channel exists and that the user who calls this function is in the
    channel.
    It should produce the name, the owner, all the members in the channel,
    and if the channel is public or not.

    Arguments:
        auth_user_id (integer) - the user who is inviting another user.
        channel_id (integer) - the channel that the invited user will join.

    Exceptions:
        InputError - Occurs when the channel_id does not refer to a valid
        channel.

        AccessError - Occurs when the auth_user_id doesn't refer to a valid
                      auth_user_id.
                    - Occurs when the auth_user_id is not in the
                      channel_details.

    Return Value:
        Returns {name, owner_members, all_members, is_public} when the
        auth_user_id and channel_id are valid.
    '''

    #Grabs the stored lists of channel_details and user_details.
    store = data_store.get()
    stored_channels = store['channels']
    stored_users = store['users']
    dets = {}
    valid = False
    return_desc = {
        'name' : '',
        'owner_members' : [],
        'all_members' : [],
        'is_public' : ''
    }

    auth_id = check_valid_auth(token, stored_users)

    #This is to check where the channel_id refers to a valid channel.
    for ids in stored_channels:
        if ids['channel_id'] == channel_id:
            dets = ids

    if len(dets) == 0:
        raise InputError(description="invalid channel_id")

    #This goes through the all_members lists
    #and checks if the authorised user is a member of the channel.
    members = dets['all_members']
    for user in members:
        if auth_id == user['u_id']:
            valid = True
            break

    #This is to check if they are not a member of the channel.
    if not valid:
        raise AccessError(description="unauthorised user")

    #grabs the details in the designated channel and returns
    #it.
    print(dets)
    for key in return_desc:
        return_desc[key] = dets[key]

    return return_desc

###############################################################################
################# JP - channel_messages_v2, channel_join_v2, ##################
################# message_send_v1, message_edit_v1           ##################
################# message_remove_v1, dm_message_v1           ##################
################# message_react_v1, message_unreact_v1,      ##################
################# message_pin_v1, message_unpin_v1           ##################
###############################################################################

def initial_check(token, channel_id, dm_id, action, store):
    '''Helper function to check token, channel and user
    
    Arguments:
        token ([str])    - JWT token of user calling the function
        channel_id ([int])    - Integer ID of channel the user calls the function in
        dm_id ([int])    - Integer ID of dm the user calls the function in
        action ([str])    - The function called by the user
        store ([dictionary])    - Dictionary of Stream's stored data
        
    Exceptions:
        None

    Return Value:
        Returns dictionary {info} containing user details or integer {auth_user_id} on successful verification of token, channel ID, and user ID
    '''
    decoded_token = jp.get_decoded_token(token)

    if action == "channel_join_v2":
        info = jp.check_exist_user_for_channel_join(decoded_token, store)
        
        jp.check_exist_channel_and_user_in_channel_for_channel_join(info[0], 
                                                                    channel_id, 
                                                                    store)
                                                        
        return info

    auth_user_id = jp.check_exist_user(decoded_token, store)
                                                   
    if action == "message_send_v1" or action == "channel_messages_v2":
        jp.check_exist_channel_and_user_in_channel(auth_user_id, channel_id, 
                                                   store)
    elif action == "dm_messages_v1":
        jp.check_exist_dm_and_user_in_dm_for_dm_messages(auth_user_id, dm_id, 
                                                         store)
    
    return auth_user_id

###################### main functions #########################
def channel_messages_v2(token, channel_id, start):
    '''channel_messages_v2 main function
    
    Arguments:
        token ([str])    - JWT token of user calling the function
        channel_id ([int])    - Integer ID of channel the user calls the function in
        start ([int])    - Integer of message number the user wants to start getting the message history from
        
    Exceptions:
        None

    Return Value:
        Returns the output of function check_start after initial checks of token, channel ID, user ID are passed
    '''
    
    store = data_store.get()
    
    action = "channel_messages_v2"
    dm_id = None

    auth_user_id = initial_check(token, channel_id, dm_id, action, store)

    return jp.check_start(auth_user_id, channel_id, start, store)
    
def dm_messages_v1(token, dm_id, start):
    '''dm_messages_v1 main function
    
    Arguments:
        token ([str])    - JWT token of user calling the function
        dm_id ([int])    - Integer ID of dm the user calls the function in
        start ([int])    - Integer of message number the user wants to start getting the message history from
        
    Exceptions:
        None

    Return Value:
        Returns the output of function check_start_dm after initial checks of token, channel ID, user ID are passed
    '''
    
    store = data_store.get()
    
    action = "dm_messages_v1"
    channel_id = None
    
    auth_user_id = initial_check(token, channel_id, dm_id, action, store)

    return jp.check_start_dm(auth_user_id, dm_id, start, store)

def channel_join_v2(token, channel_id):
    '''channel_join_v2 main function
    
    Arguments:
        token ([str])    - JWT token of user calling the function
        channel_id ([int])    - Integer ID of channel the user calls the function in
        
    Exceptions:
        None

    Return Value:
        Returns the output of function public_or_private after initial checks of token, channel ID, user ID are passed
    '''
    
    store = data_store.get()
   
    action = "channel_join_v2"
    dm_id = None
    
    info = initial_check(token, channel_id, dm_id, action, store)

    return jp.public_or_private(info, channel_id, store)
    
def message_send_v1(token, channel_id, message):
    '''channel_send_message_v1 main function
    
    Arguments:
        token ([str])    - JWT token of user calling the function
        channel_id ([int])    - Integer ID of channel the user calls the function in
        message ([str])    - The message the user wants to send in a channel
        
    Exceptions:
        None

    Return Value:
        Returns the output of function check_send_message after initial checks of token, channel ID, user ID are passed
    '''
    
    store = data_store.get()
    
    action = "message_send_v1"
    dm_id = None
    
    auth_user_id = initial_check(token, channel_id, dm_id, action, store)
    
    return jp.check_send_message(auth_user_id, channel_id, message, store)

def message_edit_v1(token, message_id, message):
    '''message_edit_v1 main function
    
    Arguments:
        token ([str])    - JWT token of user calling the function
        message_id ([int])    - Integer ID of message the user wants to edit
        message ([str])    - The message the user wants to replace with
        
    Exceptions:
        None

    Return Value:
        Returns the output of function check after initial checks of token, channel ID, user ID are passed
    '''

    store = data_store.get()
    
    action = None
    channel_id = None
    dm_id = None 
    
    auth_user_id = initial_check(token, channel_id, dm_id, action, store)
 
    react_id = None
    react_action = None
    pin_action = None
    
    return jp.check(auth_user_id, message_id, message, react_id, react_action, 
                    pin_action, store)

def message_remove_v1(token, message_id):
    '''message_remove_v1 main function
    
    Arguments:
        token ([str])    - JWT token of user calling the function
        message_id ([int])    - Integer ID of message the user wants to edit
        
    Exceptions:
        None

    Return Value:
        Returns the output of function check after initial checks of token, channel ID, user ID are passed
    '''

    store = data_store.get()
    
    action = None
    channel_id = None
    dm_id = None  
    
    auth_user_id = initial_check(token, channel_id, dm_id, action, store)
    
    message = None
    react_id = None
    react_action = None
    pin_action = None
    
    return jp.check(auth_user_id, message_id, message, react_id, react_action, 
                    pin_action, store)
    
def message_react_v1(token, message_id, react_id):
    '''message_react_v1 main function
    
    Arguments:
        token ([str])    - JWT token of user calling the function
        message_id ([int])    - Integer ID of message the user wants to edit
        react_id ([int])    - The ID of the react the user wants to react with
        
    Exceptions:
        None

    Return Value:
        Returns the output of function check after initial checks of token, channel ID, user ID are passed
    '''
    
    store = data_store.get()
    
    action = None
    channel_id = None
    dm_id = None  
    
    auth_user_id = initial_check(token, channel_id, dm_id, action, store)
    
    message = None
    react_action = 'react'
    pin_action = None
    
    return jp.check(auth_user_id, message_id, message, react_id, react_action,
                    pin_action, store)
    
def message_unreact_v1(token, message_id, react_id):
    '''message_unreact_v1 main function
    
    Arguments:
        token ([str])    - JWT token of user calling the function
        message_id ([int])    - Integer ID of message the user wants to edit
        react_id ([int])    - The ID of the react the user wants to unreact with
        
    Exceptions:
        None

    Return Value:
        Returns the output of function check after initial checks of token, channel ID, user ID are passed
    '''
    
    store = data_store.get()
    
    action = None
    channel_id = None
    dm_id = None  
    
    auth_user_id = initial_check(token, channel_id, dm_id, action, store)
    
    message = None
    react_action = 'unreact'
    pin_action = None 
    
    return jp.check(auth_user_id, message_id, message, react_id, react_action,
                    pin_action, store)
   
def message_pin_v1(token, message_id):
    '''message_pin_v1 main function
    
    Arguments:
        token ([str])    - JWT token of user calling the function
        message_id ([int])    - Integer ID of message the user wants to edit
        
    Exceptions:
        None

    Return Value:
        Returns the output of function check after initial checks of token, channel ID, user ID are passed
    '''
    
    store = data_store.get()
    
    action = None
    channel_id = None
    dm_id = None  
    
    auth_user_id = initial_check(token, channel_id, dm_id, action, store)
    
    message = None
    react_id = None
    react_action = None
    pin_action = 'pin'
    
    return jp.check(auth_user_id, message_id, message, react_id, react_action,
                    pin_action, store)
    
def message_unpin_v1(token, message_id):
    '''message_unpin_v1 main function
    
    Arguments:
        token ([str])    - JWT token of user calling the function
        message_id ([int])    - Integer ID of message the user wants to edit
        
    Exceptions:
        None

    Return Value:
        Returns the output of function check after initial checks of token, channel ID, user ID are passed
    '''
    
    store = data_store.get()
    
    action = None
    channel_id = None
    dm_id = None  
    
    auth_user_id = initial_check(token, channel_id, dm_id, action, store)
    
    message = None
    react_id = None
    react_action = None
    pin_action = 'unpin'
    
    return jp.check(auth_user_id, message_id, message, react_id, react_action,
                    pin_action, store)

