'''
Author: (JP) Jonathan Pan (z5257551) 
Date: 19/10/2021 
Functions for implementation file

This program contains implementation functions for channel_join_v2, 
channel_messages_v2, channel_send_message_v1, channel_edit_message_v1, 
channel_remove_message_v1, and dm_message_v1
'''

import time

from src.function_helpers import get_user_store
from src.data_store import data_store
from src.error import InputError
from src.error import AccessError
import src.helpers

MESSAGE_STORAGE = 100

################# general helper functions ####################

def get_decoded_token(token):
    '''Decodes the user's token
    
    Arguments:
        token ([string])    - User's token 
    
    Exceptions:
        AccessError - Occurs when token is not decodable 

    Return Value:
        Returns decoded_token on successfully decoded user token
    '''

    try:
        decoded_token = src.helpers.decode_jwt(token)
        return decoded_token
    except Exception as error:
        raise AccessError("Invalid token") from error

def check_exist_user(decoded_token, store):
    '''Check if user exists for message operations
    
    Arguments:
        decoded_token ([dictionary])    - Dictionary data in user's decoded token 
        store ([dictionary])    - Dictionary of Stream's stored data 
    
    Exceptions:
        AccessError - Occurs when user's token does not exist or the user was removed 

    Return Value:
        Returns user['auth_user_id'] on successfully recognised user token
    '''

    for user in store['users']:
        if str(user['auth_user_id']) == decoded_token['username'] and decoded_token['session_id'] in user['session_list']:
            if user['is_removed'] is False and user['name_first'] != "Removed" and user['name_last'] != "user":
                return user['auth_user_id']

    raise AccessError("User token does not exist")
    
def check_exist_channel_and_user_in_channel(auth_user_id, channel_id, store):
    '''Check if channel ID exists and also if user is in channel (for channel_messages)
    
    Arguments:
        auth_user_id ([int])    - Integer ID of user
        channel_id ([int])    - Integer ID of channel 
        store ([dictionary])    - Dictionary of Stream's stored data
    
    Exceptions:
        InputError - When no channel has been created yet, or if it doesn't exists
        AccessError - When user is not in channel

    Return Value:
        Returns nothing on successful verification for both channel and user IDs
    '''
    
    if store['channels'] == []:
        raise InputError("Channel ID does not exist")

    no_channel = 0
    no_user = 0

    for channel in store['channels']:
        if channel_id == channel['channel_id']:
            for user in channel['all_user_ids']:
                if user != auth_user_id:
                    no_user += 1
                # else:
                #     break 
                
                if no_user == len(channel['all_user_ids']):
                    raise AccessError("User ID is not in channel")
        else:
            no_channel += 1

        if no_channel == len(store['channels']):
            raise InputError("Channel ID does not exist")
        
################### channel_messages_v2 helper functions ######################

def check_start(auth_user_id, channel_id, start, store):
    '''Check if start is smaller, equaler or greater than total messages
    
    Arguments:
        auth_user_id ([int])    - Integer ID of user
        channel_id ([int])    - Integer ID of channel 
        start ([int])    - Integer of message number the user wants to start getting the message history from
        store ([dictionary])    - Dictionary of Stream's stored data 
    
    Exceptions:
        InputError - When the 
        message number that the user wants to start on doesn't exist 

    Return Value:
        Returns dictionary containing messages, start, and end (message history) on successful implementation of channel_messages
    '''
    
    og_start = start
    target_messages = []

    for channel in store['channels']:
        if channel['channel_id'] == channel_id and start == 0 and len(channel['messages']) == 0:
            pass
        elif channel['channel_id'] == channel_id and start <= len(channel['messages']):
            target = len(channel['messages']) - 1 - start
            
            while start < len(channel['messages']) and start < og_start + 50:
                target_messages.append(channel['messages'][target])
                target -= 1
                start += 1
        elif channel['channel_id'] == channel_id and start > len(channel['messages']):
            raise InputError("Requested index is greater than total amount of messages")

    end = -1

    if start - 50 == og_start:
        end =  og_start + 50

    data_store.set(store)
    
    for message in target_messages:
        for react in message['reacts']:
            for u_id in react['u_ids']:
                if u_id == auth_user_id:
                    react['is_this_user_reacted'] = True
                    break
                else:
                    react['is_this_user_reacted'] = False

    return {
        'messages': target_messages,
        'start': og_start,
        'end': end
    }
    
################# dm_message_v1 helper functions ####################

def check_exist_dm_and_user_in_dm_for_dm_messages(auth_user_id, dm_id, store):
    '''Check if dm ID exists and also if user is in dm (for dm_messages)
    
    Arguments:
        auth_user_id ([int])    - Integer ID of user
        dm_id ([int])    - Integer ID of dm
        store ([dictionary])    - Dictionary of Stream's stored data
    
    Exceptions:
        InputError - When no dm has been created yet, or if it doesn't exists
        AccessError - When user is not in dm

    Return Value:
        Returns nothing on successful verification for both dm and user IDs
    '''
    
    if store['dms'] == []:
        raise InputError("Dm ID does not exist")

    no_dm = 0
    no_user = 0

    for dm in store['dms']:
        
            
        if dm_id == dm['dm_id']:
            if dm['creator'] != auth_user_id:
                no_user += 1
        
            for user in dm['u_ids']:
                if user != auth_user_id:
                    no_user += 1
                # else:
                #     break
                    
                if no_user == len(dm['u_ids']) + 1:
                    raise AccessError("User ID is not in dm")
        else:
            no_dm += 1

        if no_dm == len(store['dms']):
            raise InputError("DM ID does not exist")

def message_history(auth_user_id, og_start, target_messages, start, store):
    '''Returns dictionary containing messages, start, and end (message history)
    
    Arguments:
        auth_user_id ([int])    - Integer ID of user
        og_start ([int])    - Integer of message number the user wants to start getting the message history from
        target_messages ([list])    - Message history requested by the user 
        start ([int])    - Integer of message number of the last message of target_messages
        store ([dictionary])    - Dictionary of Stream's stored data
    
    Exceptions:
        None

    Return Value:
        Returns dictionary containing messages, start, and end (message history) on successful implementation of dm_messages
    '''

    end = -1
    
    if start - 50 == og_start:
        end =  og_start + 50

    data_store.set(store)
    
    for message in target_messages:
        for react in message['reacts']:
            for u_id in react['u_ids']:
                if u_id == auth_user_id:
                    react['is_this_user_reacted'] = True
                    break
                else:
                    react['is_this_user_reacted'] = False

    return {
        'messages': target_messages,
        'start': og_start,
        'end': end
    }


def check_start_dm(auth_user_id, dm_id, start, store):
    '''Check if start is smaller, equaler or greater than total messages
    
    Arguments:
        auth_user_id ([int])    - Integer ID of user
        dm_id ([int])    - Integer ID of dm
        start ([int])    - Integer of message number the user wants to start getting the message history from
        store ([dictionary])    - Dictionary of Stream's stored data 
    
    Exceptions:
        InputError - When the message number that the user wants to start on doesn't exist 

    Return Value:
        Returns essage_history(og_start, target_messages, start, store) on valid message number requeted by user
    '''
    
    og_start = start
    target_messages = []

    for dm in store['dms']:
        if dm['dm_id'] == dm_id and start == 0 and len(dm['messages']) == 0:
            return message_history(auth_user_id, og_start, target_messages, start, store)
        elif dm['dm_id'] == dm_id and start <= len(dm['messages']):
            target = len(dm['messages']) - 1 - start
        
            while start < len(dm['messages']) and start < og_start + 50:
                target_messages.append(dm['messages'][target])
                target -= 1
                start += 1
                
            return message_history(auth_user_id, og_start, target_messages, start, store)
    
    raise InputError("Requested index is greater than total amount of messages")
    
################### channel_join_v2 helper functions ######################

def check_exist_user_for_channel_join(decoded_token, store):
    '''Check if user ID exists (for channel_join)
    
    Arguments:
        decoded_token ([dictionary])    - Dictionary data in user's decoded token 
        store ([dictionary])    - Dictionary of Stream's stored data 
    
    Exceptions:
        AccessError - Occurs when user's token does not exist or the user was removed 

    Return Value:
        Returns info (dictionary of user details from Stream's stored data) on successfully recognised user token
    '''
    
    global_owner = 0
    email = ''
    name_first = ''
    name_last = ''
    handle_str = ''
    profile_img_url = ''

    for user in store['users']:
        if str(user['auth_user_id']) == decoded_token['username'] and decoded_token['session_id'] in user['session_list']:
            if user['is_removed'] is False and user['name_first'] != "Removed" and user['name_last'] != "user":
                email = user['email']
                name_first = user['name_first']
                name_last = user['name_last']
                handle_str = user['handle_str']
                profile_img_url = user['profile_img_url']

                if user['permission_id'] == 1:
                    global_owner = 1
                    
                info = (user['auth_user_id'], email, name_first, name_last, 
                        handle_str, global_owner, profile_img_url)
                        
                return info

    raise AccessError("User token is not valid")

def check_exist_channel_and_user_in_channel_for_channel_join(auth_user_id, channel_id, store):
    '''Check if channel ID exists and also if user is in channel (for channel_join)
    
    Arguments:
        auth_user_id ([int])    - Integer ID of user
        channel_id ([int])    - Integer ID of channel 
        store ([dictionary])    - Dictionary of Stream's stored data
    
    Exceptions:
        InputError - When no channel has been created yet, or if it doesn't exists
        AccessError - When user is not in channel

    Return Value:
        Returns nothing on successful verification for both channel and user IDs
    '''
    
    if store['channels'] == []:
        raise InputError("Channel ID does not exist")

    no_channel = 0

    for channel in store['channels']:
        if channel_id == channel['channel_id']:
            for user in channel['all_user_ids']:
                if user == auth_user_id:
                    raise InputError("User ID already in channel")
        else:
            no_channel += 1

    if no_channel == len(store['channels']):
        raise InputError("Channel ID does not exist")

def append_all(info, channel):
    '''Append to all_user_ids and all_members
    
    Arguments:
        info ([dictionary])    - Dictionary of user details obtained from Stream's stored data
        channel ([int])    - Dictionary of details of a specific channel
    
    Exceptions:
        None

    Return Value:
        Returns nothing on appending all_user_ids and all_members
    '''
    
    channel['all_user_ids'].append(info[0])
    channel['all_members'].append(
        {
            'u_id' : info[0],
            'email' : info[1],
            'name_first' : info[2],
            'name_last' : info[3],
            'handle_str' : info[4],
            'profile_img_url': info[6]
        }
    )

def public_or_private(info, channel_id, store):
    '''Check if channel is public or private
    
    Arguments:
        info ([dictionary])    - Dictionary of user details obtained from Stream's stored data
        channel_id ([int])    - Integer ID of channel 
        store ([dictionary])    - Dictionary of Stream's stored data
    
    Exceptions:
        AccessError - When channel is private for non-global owners 

    Return Value:
        Returns {} on successful implementation of channel_messages
    '''
    
    for channel in store['channels']:
        if channel['channel_id'] == channel_id and channel['is_public']:
            append_all(info, channel)
        elif channel['channel_id'] == channel_id and not channel['is_public']:
            if info[5] == 1:
                append_all(info, channel)
            else:
                raise AccessError("Channel ID is private")
                
    data_store.set(store)
                
    return {}

################# channel_send_message_v1 helper functions ####################

def check_send_message(auth_user_id, channel_id, message, store):
    '''Check if message is too short or too long, then add into messages
    
    Arguments:
        auth_user_id ([int])    - Interger ID of user 
        channel_id ([int])    - Integer ID of channel 
        message ([string]) - String that the user wants to send 
        store ([dictionary])    - Dictionary of Stream's stored data
    
    Exceptions:
        InputError - When message is below one charatcer or over 1000 characters

    Return Value:
        Returns message_id on successful implementation of channel_send_message
    '''
    if len(message) < 1:
        raise InputError("Message is too short!")
    elif len(message) > 1000:
        raise InputError("Message is too long!")
    
    message_id = ''
    
    for channel in store['channels']:
        if channel['channel_id'] == channel_id:
            message_id = (channel_id * MESSAGE_STORAGE) + len(channel['messages']) + channel['num_message_later'] + 1
            
            channel['messages'].append(
                    {
                        'message_id' : message_id,
                        'u_id' : auth_user_id,
                        'message' : message,
                        'time_created' : int(time.time()),
                        'reacts': [
                            {
                                'react_id': 1,
                                'u_ids': [],
                                'is_this_user_reacted': False
                            }
                        ],
                        'is_pinned': False
                    }
                )

    data_store.set(store)
            
    return message_id
           
## helper functions to edit, remove, react, unreact, pin and unpin a message ##
            
def edit_message(message_id, message, store, delete, info, location):
    '''Once user is authorised and message is valid, edit message
    
    Arguments:
        message_id ([int])    - Interger ID of message
        message ([string]) - String that the user wants to edit original message with 
        store ([dictionary])    - Dictionary of Stream's stored data
        delete ([int])    - Indicates whether the user wants to replace original message with empty string
        info ([dictionary])    - Dictionary of details of the original message
        location ([dictionary])    - Dictionary of the whereabouts (either channel or dm) of the original message
    
    Exceptions:
        None

    Return Value:
        Returns nothing on editing the original message
    '''

    if info['message_id'] == message_id and delete == 1:
        location['messages'].remove(info)
    elif info['message_id'] == message_id:
        info['message'] = message

def check_edit_message(message_id, message, store, location):
    '''Check if new message is too short or too long, and if user and message are in same channel/dm
    
    Arguments:
        message_id ([int])    - Interger ID of message 
        message ([string]) - String that the user wants to edit original message with 
        store ([dictionary])    - Dictionary of Stream's stored data
        location ([string]) - String that indicates whether the message is in a channel/dm
    
    Exceptions:
        InputError - When message is over 1000 characters

    Return Value:
        Returns {} on successful implementation of message_edit
    '''
       
    delete = 0
    
    if len(message) < 1:
        delete = 1
    elif len(message) > 1000:
        raise InputError("Message is too long!") 
    
    # If user and message is in a channel
    if location == "channel":
        for channel in store['channels']:
            for info in channel['messages']:
                edit_message(message_id, message, store, delete, info, channel)
    # If user and message is in a dm
    else:            
        for dm in store['dms']:
            for info in dm['messages']:
                edit_message(message_id, message, store, delete, info, dm)
        
    data_store.set(store)
     
    return {}

def check_remove_message(message_id, store, location):
    '''Check if user and message are in same channel/dm
    
    Arguments:
        message_id ([int])    - Interger ID of message 
        store ([dictionary])    - Dictionary of Stream's stored data
        location ([string]) - String that indicates whether the message is in a channel/dm
    
    Exceptions:
        None

    Return Value:
        Returns {} on successful implementation of message_remove
    '''                   

    # If user and message is in a channel
    if location == "channel":
        for channel in store['channels']:
            for info in channel['messages']:
                if info['message_id'] == message_id:
                    channel['messages'].remove(info)
    # If user and message is in a dm
    else:            
        for dm in store['dms']:
            for info in dm['messages']:
                if info['message_id'] == message_id:
                    dm['messages'].remove(info)
        
    data_store.set(store)
     
    return {}

def react_message(auth_user_id, react_id, react_action, info):
    '''User reacts or unreacts to message
    
    Arguments:
        auth_user_id ([int])    - Integer ID of user 
        react_id ([int])    - Interger ID of react the user wants to react with
        react_action ([str])    - Indicates whether the user wants to "react" or "unreact" 
        info ([dictionary])    - Dictionary of the message to react on
    
    Exceptions:
        InputError - When user already reacted to the message, unreact to an unreacted message, or invalid react_id

    Return Value:
        Returns to previous function when successfully react or unreact
    '''

    for react in info['reacts']:
        if react['react_id'] == react_id:
            for u_id in react['u_ids']:
                if u_id == auth_user_id and react_action == 'react':
                    raise InputError("User already have this react to this message")
                elif u_id == auth_user_id and react_action == 'unreact':
                    if len(react['u_ids']) == 1:
                        react['is_this_user_reacted'] = False
                        
                    react['u_ids'].remove(u_id)  
                    
                    return
                     
            if react_action == 'unreact':
                raise InputError("User had not had this react to this message yet")
            else:
                react['u_ids'].append(auth_user_id)  
                
                return        

    raise InputError("React ID is not valid") 
    
def check_react_message(auth_user_id, message_id, react_id, react_action, store, 
                        location):
    '''Find whether the message to react on is in a channel or dm
    
    Arguments:
        auth_user_id ([int])    - Interger ID of user 
        message_id ([int])    - Interger ID of message 
        react_id ([int])    - Interger ID of react the user wants to react with
        react_action ([str])    - Indicates whether the user wants to "react" or "unreact" 
        store ([dictionary])    - Dictionary of Stream's stored data
        location ([string]) - String that indicates whether the message is in a channel/dm
    
    Exceptions:
        None

    Return Value:
        Returns {} on successful implementation of message_react
    '''

    # If user and message is in a channel
    if location == "channel":
        for channel in store['channels']:
            for info in channel['messages']:
                if info['message_id'] == message_id:
                    react_message(auth_user_id, react_id, react_action, info)
    # If user and message is in a dm
    else:            
        for dm in store['dms']:
            for info in dm['messages']:
                if info['message_id'] == message_id:
                    react_message(auth_user_id, react_id, react_action, info)
        
    data_store.set(store)
     
    return {}                 

def check_pin_message(message_id, pin_action, store, location):
    '''Find whether the message to pin or unpin is in a channel or dm, then perform the action
    
    Arguments:
        message_id ([int])    - Interger ID of message 
        pin_action ([str])    - Indicates whether the user wants to "pin" or "unpin" 
        store ([dictionary])    - Dictionary of Stream's stored data
        location ([string]) - String that indicates whether the message is in a channel/dm
    
    Exceptions:
        InputError - When user already pinned to the message, or unpin an unpinned message

    Return Value:
        Returns {} on successful implementation of message_pin
    '''

    # If user and message is in a channel
    if location == "channel":
        for channel in store['channels']:
            for info in channel['messages']:
                if info['message_id'] == message_id and info['is_pinned'] == False and pin_action == 'pin':
                    info['is_pinned'] = True
                    
                    data_store.set(store)
     
                    return {}
                elif info['message_id'] == message_id and info['is_pinned'] == True and pin_action == 'unpin':
                    info['is_pinned'] = False
                    
                    data_store.set(store)
     
                    return {}

    # If user and message is in a dm
    else:            
        for dm in store['dms']:
            for info in dm['messages']:
                if info['message_id'] == message_id and info['is_pinned'] == False and pin_action == 'pin':
                    info['is_pinned'] = True
                    
                    data_store.set(store)
     
                    return {}
                elif info['message_id'] == message_id and info['is_pinned'] == True and pin_action == 'unpin':
                    info['is_pinned'] = False
                    
                    data_store.set(store)
     
                    return {}
        
    raise InputError('User is either pinning a pinned message or unpinning an unpinned messages')
    
def check(auth_user_id, message_id, message, react_id, react_action, pin_action, store):
    '''Check if user is authorised to edit, remove, react, unreact, pin, or unpin a message
    
    Arguments:
        auth_user_id ([int])    - Interger ID of user 
        message_id ([int])    - Interger ID of message 
        message ([string]) - String that the user wants to edit original message with 
        react_id ([int])    - Interger ID of react the user wants to react with
        react_action ([str])    - Indicates whether the user wants to "react" or "unreact" 
        pin_action ([str])    - Indicates whether the user wants to "pin" or "unpin" 
        store ([dictionary])    - Dictionary of Stream's stored data
    
    Exceptions:
        AccessError - When user is in the same channel/dm as the message but not authorised to perform the action
        InputError - When message is not in user's authorised channels and dms

    Return Value:
        Returns the repsective functions of message_remove, message_edit, message_react, message_unreact, message_pin, and message_unpin
    '''
    
    global_owner = 0
    
    # Check if user is a global owner
    for user in store['users']:
        if user['auth_user_id'] == auth_user_id and user['permission_id'] == 1:
            global_owner = 1
            break
    
    unauthorised_action = 0
    
    # Check in channel first
    for channel in store['channels']:
        owner_member = 0
        member = 0
        og_sender = 0
        message_in = 0
        
        for user in channel['owner_members']:
            if user['u_id'] == auth_user_id:
                owner_member = 1
                break 

        for user in channel['all_user_ids']:
            if user == auth_user_id and global_owner == 1:
                owner_member = 1
                member = 1
                break
            elif user == auth_user_id:
                member = 1
                break

        for info in channel['messages']:
            if info['message_id'] == message_id and info['u_id'] == auth_user_id:
                og_sender = 1
                message_in = 1
                break
            elif info['message_id'] == message_id:
                message_in = 1
                break

        if member == 1 and message_in == 1:
            remove_and_edit_permission = 0
            pin_permission = 0

            if owner_member == 1:
                remove_and_edit_permission = 1
                pin_permission = 1
            elif og_sender == 1:
                remove_and_edit_permission = 1
                
            location = "channel"
                   
            if remove_and_edit_permission == 1 and message == None and react_id == None and react_action == None and pin_action == None:
                return check_remove_message(message_id, store, location)
            elif remove_and_edit_permission == 1 and react_id == None and react_action == None and pin_action == None:                                
                return check_edit_message(message_id, message, store, location)
            elif react_action != None and message == None and pin_action == None:
                return check_react_message(auth_user_id, message_id, react_id, 
                                           react_action, store, location) 
            elif pin_permission == 1 and message == None and react_id == None and react_action == None:
                return check_pin_message(message_id, pin_action, store, 
                                         location)                                     
            else:
                unauthorised_action = 1
                            
    # If not in channel, check in DM            
    for dm in store['dms']:
        owner_member = 0
        member = 0
        og_sender = 0
        message_in = 0
        
        if dm['creator'] == auth_user_id:
            owner_member = 1
            member = 1

        for user in dm['u_ids']:
            if user == auth_user_id:
                member = 1
                break          

        for info in dm['messages']:
            if info['message_id'] == message_id and info['u_id'] == auth_user_id:
                og_sender = 1
                message_in = 1
                break
            elif info['message_id'] == message_id:
                message_in = 1
                break
                
        if member == 1 and message_in == 1:
            remove_and_edit_permission = 0
            pin_permission = 0

            if owner_member == 1:
                remove_and_edit_permission = 1
                pin_permission = 1
            elif og_sender == 1:
                remove_and_edit_permission = 1
                
            location = "dm"
                   
            if remove_and_edit_permission == 1 and message == None and react_id == None and react_action == None and pin_action == None:
                return check_remove_message(message_id, store, location)
            elif remove_and_edit_permission == 1 and react_id == None and react_action == None and pin_action == None:                                
                return check_edit_message(message_id, message, store, location)
            elif react_action != None and message == None and pin_action == None:
                return check_react_message(auth_user_id, message_id, react_id, 
                                           react_action, store, location) 
            elif pin_permission == 1 and message == None and react_id == None and react_action == None:
                return check_pin_message(message_id, pin_action, store, 
                                         location)      
            else:
                unauthorised_action = 1                                                              
    
    if unauthorised_action == 1:
        raise AccessError("User unauthorised to take action on message")
    else:
        raise InputError("Message not in user's authorised channels or dms")

