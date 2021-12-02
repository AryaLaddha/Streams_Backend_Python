import json
import functools
import threading
import time
from datetime import datetime
from src.helpers import decode_jwt
from src.data_store import data_store
from src.error import InputError
from src.error import AccessError

MESSAGE_STORAGE = 100

def check_valid_auth(token, users):
    #This is to check if the token can be decoded and if the token holds
    #any data.

    #This is to check if the token can be decoded.
    try:
        decode_token = decode_jwt(token)
    except Exception as error:
        raise AccessError(description="invalid token") from error

    #This is to check if the token has a non-existant caller.
    valid = False
    auth_id = -1
    for user in users:
        if decode_token['username'] == str(user['auth_user_id']) and decode_token['session_id'] in user['session_list']:
            valid = True
            auth_id = user['auth_user_id']

    if not valid:
        raise AccessError(description='caller does not exist')

    return auth_id

def check_valid_channel_and_user(channels, auth_id, channel_id):
    #This function checks if the given channel_id is valid, as well as check if the
    #user is a member of the channel.

    valid_channel = False
    valid_auth_user = False

    #This goes through the channels database to check whether the channel_id is valid.
    for channel in channels:
        if channel_id == channel['channel_id']:
            valid_channel = True
            channel_details = channel

    if not valid_channel:
        raise InputError(description="invalid channel id")

    #This goes through the members in the channel and checks whether the user is a member
    #of the channel.
    for members in channel_details['all_members']:
        if auth_id == members['u_id']:
            valid_auth_user = True

    if not valid_auth_user:
        raise AccessError(description="caller not a member of the channel")

    return channel_details

def standup_active_v1(token, channel_id):
    '''
    Standup_active shows if there is a standup that is currently active in a channel.
    
    Arguments:
        token (string) - An encryption that contains the caller/creator of the dm.
                         It contains the id of caller and session id.
        channel_id (integer) - An id for the channel.

    Exceptions:
        InputError - Occurs when the channel_id doesn't refer to a vald channel.

        AccessError - Occurs when the token doesn't decode.
                    - Occurs when the token does not refer to an existant user.
                    - Occurs when the caller of th function is not the creator.

    Return Value:
        Returns {'is_active' : '', 'time_finish' : ''} when the arguments are valid.
    '''

    activity = {}
    store = data_store.get()
    users = store['users']
    channels = store['channels']
    auth_id = check_valid_auth(token, users)
    
    #This checks if the channel_id is valid and if the user is a member of the channel.
    channel_details = check_valid_channel_and_user(channels, auth_id, channel_id)

    #This checks if there is a standup that is active in the channel.
    if channel_details['is_standup']:
        activity['is_active'] = True
        activity['time_finish'] = channel_details['standup']['time_finish']

    else:
        activity['is_active'] = False
        activity['time_finish'] = None

    return activity

def standup_send_v1(token, channel_id, message):
    '''
    Standup_send will store a message that was sent during the standup and will store it
    in the message queue.
    
    Arguments:
        token (string) - An encryption that contains the caller/creator of the dm.
                         It contains the id of caller and session id.
        channel_id (integer) - An id for the channel.
        
        message (string) - A string that is being sent.

    Exceptions:
        InputError - Occurs when the channel_id doesn't refer to a vald channel.
                   - Occurs when the message is over 1000 characters long.
                   - Occurs when a standup is not currently active.

        AccessError - Occurs when the token doesn't decode.
                    - Occurs when the token does not refer to an existant user.
                    - Occurs when the caller of th function is not the creator.

    Return Value:
        Returns {} when the arguments are valid.
    '''

    store = data_store.get()
    users = store['users']
    channels = store['channels']
    auth_id = check_valid_auth(token, users)

    #This checks if the channel_id is valid and if the user is a member of the channel.
    channel_details = check_valid_channel_and_user(channels, auth_id, channel_id)

    #This grabs the handle string of the user
    for members in channel_details['all_members']:
        if auth_id == members['u_id']:
            name = members['handle_str']

    #This checks if the message is over 1000 characters.
    if len(message) > 1000:
        raise InputError(description="message is over 1000 characters")

    #This checks if the standup is not currently running.
    if not channel_details['is_standup']:
        raise InputError(description="standup is not running currently")

    standup = channel_details['standup']

    #This adds the message into a message queue.
    if len(standup['message_queue']) == 0:
        standup['message_queue'] = name + ": " + message

    else:
        standup['message_queue'] = standup['message_queue'] + "\n" + name + ": " + message

    standup['is_sent'] = True
    data_store.set(store)

    return {}

def check_send_standup(auth_id, channel_details):
    #This checks if there were any messages sent during the standup. If there was, then
    #the message queue will be sent.

    store = data_store.get()
    messages = channel_details['messages']
    standup =  channel_details['standup']
    message_id = (channel_details['channel_id'] * MESSAGE_STORAGE) + len(messages) + channel_details['num_message_later'] + 1

    #This checks if any messages were sent during the standup. If so, it will send the
    #message queue.
    if standup['is_sent']:
        messages.append(
            {
                'message_id' : message_id,
                'u_id' : auth_id,
                'message' : channel_details['standup']['message_queue'],
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

    #This stops the standup.
    channel_details['is_standup'] = False
    data_store.set(store)

    return

def standup_start_v1(token, channel_id, length):
    '''
    Standup_start will create a standup for a given length in a channel, in which all
    messages sent during the standup will be stored into a message queue. Once the standup
    is over, the message queue will be sent under the user who created the standup.
    
    Arguments:
        token (string) - An encryption that contains the caller/creator of the dm.
                         It contains the id of caller and session id.
        channel_id (integer) - An id for the channel.
        
        length (integer) - An integer that determines how long the standup will last for.

    Exceptions:
        InputError - Occurs when the channel_id doesn't refer to a vald channel.
                   - Occurs when the length is a negative number.
                   - Occurs when a standup is currently active.

        AccessError - Occurs when the token doesn't decode.
                    - Occurs when the token does not refer to an existant user.
                    - Occurs when the caller of th function is not the creator.

    Return Value:
        Returns {'time_finish' : ''} when the arguments are valid.
    '''
    
    store = data_store.get()
    users = store['users']
    channels = store['channels']
    auth_id = check_valid_auth(token, users)
    time_finish = {}
    
    #This checks if the channel_id is valid and if the user is a member of the channel.
    channel_details = check_valid_channel_and_user(channels, auth_id, channel_id)

    #This checks if the length of the standup is negative.
    if length < 0:
        raise InputError(description="length is a negative number")

    #This checks if a standup is already running.
    if channel_details['is_standup']:
        raise InputError(description="standup is already active")

    else:
        channel_details['is_standup'] = True

    #This gets the current unix timestamp.
    time_start = int(time.time())
    time_finish['time_finish'] = time_start + length

    standup = channel_details['standup']
    standup['time_finish'] = time_finish['time_finish']
    standup['message_queue'] = ''
    standup['is_sent'] = False

    #This sets a timer to check whether a message has been sent during the standup.
    #If so, then it will be stored into a message queue and be sent once the standup is
    #over.
    t = threading.Timer(
        length, 
        check_send_standup, 
        args=(auth_id, channel_details), 
        kwargs=None
    )

    t.start()

    data_store.set(store)

    return time_finish
