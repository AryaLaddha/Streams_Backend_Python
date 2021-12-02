from src.function_helpers import get_decoded_token, get_channel_store, get_user_store, get_channel_store, get_dm_store
from src.helpers import decode_jwt
from src.auth_helpers import get_channels, get_dms
from src.data_store import data_store

def get_temp_token(token):
    try:
        decoded_token = decode_jwt(token)
        return decoded_token
    except:
        return False

def check_tag_message_send(message):
    return list(set([word for word in message.split() if word[0] == '@']))

def get_user(handle, username):
    user_details = get_user_store()

    for user in user_details:
        if user['handle_str'] == handle and int(username) != user['auth_user_id']:
            return user

def check_user_in_channel(u_id,channel_id):
    channel_details = get_channel_store()

    for channel in channel_details:
        if channel['channel_id'] == channel_id and u_id in channel['all_user_ids']:
            return True
    return False

def check_user_in_dm(u_id, dm_id):
    dm_details = get_dm_store()

    for dm in dm_details:
        if dm['dm_id'] == dm_id and (u_id in dm['u_ids'] or u_id == int(dm['creator'])):
            return True
    return False

def get_channel_name(channel_id):
    channel_details = get_channel_store()
    channel_name = ""

    for channel in channel_details:
        if channel['channel_id'] == channel_id:
            channel_name = channel['name']
    return channel_name

def get_dm_name(dm_id):
    dm_details = get_dm_store()
    dm_name = ""

    for dm in dm_details:
        if dm['dm_id'] == dm_id:
            dm_name = dm['name']
    return dm_name

def get_user_handle(auth_user_id):
    user_details = get_user_store()
    return_value = ""

    for user in user_details:
        if user['auth_user_id'] == auth_user_id:
            return_value = user['handle_str']
    return return_value

def notification_message_send(token, channel_id, message):
    notifications = data_store.get()['notifications']
    final_list = check_tag_message_send(message)

    if final_list == []:
        return True

    decoded_token = get_decoded_token(token)
    in_channel = []
    for tags in final_list:
        user = get_user(tags[1:], decoded_token['username'])
        if user != None and check_user_in_channel(user['auth_user_id'], channel_id):
            in_channel.append(user)

    notification_dictionary = {
        'channel_id' : channel_id,
        'dm_id' : -1,
        'notification_message' : f"{get_user_handle(int(decoded_token['username']))} tagged you in {get_channel_name(channel_id)}: {message[0:21]}"
    }

    for person in in_channel:
        if notifications == []:
            notifications.append(
                {
                    "u_id" : person['auth_user_id'],
                    "notified" : [notification_dictionary]
                }
            )
        else:
            flag = 0
            for uids in notifications:
                if uids['u_id'] == person['auth_user_id']:
                    flag = 1
                    uids['notified'].append(notification_dictionary)
            if flag == 0:
                notifications.append(
                    {
                        'u_id' : person['auth_user_id'],
                        'notified' : [notification_dictionary]
                    }
                )
    return True

def get_old_message(token, message_id, message):
    if not get_temp_token(token):
        return False

    decoded_token = get_temp_token(token)
    channel_details = get_channel_store()
    dm_details = get_dm_store()

    try:
        int(decoded_token['username'])
    except:
        return False

    channels = get_channels(int(decoded_token['username']), channel_details)
    dms = get_dms(int(decoded_token['username']), dm_details)

    for channel in channels:
        for message in channel['messages']:
            if message['message_id'] == message_id:
                return message["message"], "channel", channel['channel_id']

    for dm in dms:
        for message in dm['messages']:
            if message['message_id'] == message_id:
                return message["message"], "dm", dm['dm_id']

    return False

def notification_message_edit_channel(token,message_id,message,old_messages,channel_id):
    notifications = data_store.get()['notifications']
    decoded_token = get_decoded_token(token)
    new_list = check_tag_message_send(message)

    if new_list == []:
        return True

    old_list = check_tag_message_send(old_messages)
    new_tags = list(set(new_list) - set(old_list))

    if new_tags == []:
        return True

    in_channel = []
    for tags in new_tags:
        user = get_user(tags[1:], decoded_token['username'])
        if user != None and check_user_in_channel(user['auth_user_id'], channel_id):
            in_channel.append(user)

    notification_dictionary = {
        'channel_id' : channel_id,
        'dm_id' : -1,
        'notification_message' : f"{get_user_handle(int(decoded_token['username']))} tagged you in {get_channel_name(channel_id)}: {message[0:21]}"
    }

    for person in in_channel:
        if notifications == []:
            notifications.append(
                {
                    "u_id" : person['auth_user_id'],
                    "notified" : [notification_dictionary]
                }
            )
        else:
            flag = 0
            for uids in notifications:
                if uids['u_id'] == person['auth_user_id']:
                    flag = 1
                    uids['notified'].append(notification_dictionary)
            if flag == 0:
                notifications.append(
                    {
                        'u_id' : person['auth_user_id'],
                        'notified' : [notification_dictionary]
                    }
                )
    return True

def notification_message_edit_dm(token,message_id,message,old_messages,dm_id):
    notifications = data_store.get()['notifications']
    decoded_token = get_decoded_token(token)
    new_list = check_tag_message_send(message)

    if new_list == []:
        return True

    old_list = check_tag_message_send(old_messages)
    new_tags = list(set(new_list) - set(old_list))

    if new_tags == []:
        return True

    in_dm = []
    for tags in new_tags:
        user = get_user(tags[1:], decoded_token['username'])
        if user != None and check_user_in_dm(user['auth_user_id'], dm_id):
            in_dm.append(user)

    notification_dictionary = {
        'channel_id' : -1,
        'dm_id' : dm_id,
        'notification_message' : f"{get_user_handle(int(decoded_token['username']))} tagged you in {get_dm_name(dm_id)}: {message[0:21]}"
    }

    for person in in_dm:
        flag = 0
        for uids in notifications:
            if uids['u_id'] == person['auth_user_id']:
                flag = 1
                uids['notified'].append(notification_dictionary)
        if flag == 0:
            notifications.append(
                {
                    'u_id' : person['auth_user_id'],
                    'notified' : [notification_dictionary]
                }
            )
    return True

def send_notification_dm(dm_id):
    notifications = data_store.get()['notifications']
    dm_details = get_dm_store()

    in_dm = []

    for dm in dm_details:
        if dm['dm_id'] == dm_id:
            in_dm = dm['u_ids']

    notification_dictionary = {
        'channel_id' : -1,
        'dm_id' : dm_id,
        'notification_message' : f"{get_user_handle(int(dm['creator']))} added you to {get_dm_name(dm_id)}"
    }

    for person in in_dm:
        if notifications == []:
            notifications.append(
                {
                    "u_id" : person,
                    "notified" : [notification_dictionary]
                }
            )
        else:
            flag = 0
            for uids in notifications:
                if uids['u_id'] == person:
                    flag = 1
                    uids['notified'].append(notification_dictionary)
            if flag == 0:
                notifications.append(
                    {
                        'u_id' : person,
                        'notified' : [notification_dictionary]
                    }
                )
    return True

def notification_senddm(token, dm_id, message):
    notifications = data_store.get()['notifications']
    final_list = check_tag_message_send(message)

    if final_list == []:
        return True

    decoded_token = get_decoded_token(token)
    in_dm = []
    for tags in final_list:
        user = get_user(tags[1:], decoded_token['username'])
        if user != None and check_user_in_dm(user['auth_user_id'], dm_id):
            in_dm.append(user)

    notification_dictionary = {
        'channel_id' : -1,
        'dm_id' : dm_id,
        'notification_message' : f"{get_user_handle(int(decoded_token['username']))} tagged you in {get_dm_name(dm_id)}: {message[0:21]}"
    }

    for person in in_dm:
        flag = 0
        for uids in notifications:
            if uids['u_id'] == person['auth_user_id']:
                flag = 1
                uids['notified'].append(notification_dictionary)
        if flag == 0:
            notifications.append(
                {
                    'u_id' : person['auth_user_id'],
                    'notified' : [notification_dictionary]
                }
            )
    return True

def react_message_notification(token, message_id, react_id):
    notifications = data_store.get()['notifications']
    decoded_token = get_decoded_token(token)

    channel_details = get_channel_store()
    dm_details = get_dm_store()

    channels = get_channels(int(decoded_token['username']), channel_details)
    dms = get_dms(int(decoded_token['username']), dm_details)

    u_id = None
    channel_dm_id = None
    action = None

    flag = 0
    for channel in channels:
        for message in channel['messages']:
            if message['message_id'] == message_id:
                if int(decoded_token['username']) != message['u_id']:
                    flag = 1
                    action, u_id, channel_dm_id = "channel", message['u_id'], channel['channel_id']
                else:
                    return True

    if flag == 0:
        for dm in dms:
            for message in dm['messages']:
                if message['message_id'] == message_id:
                    if int(decoded_token['username']) != message['u_id']:
                        action, u_id, channel_dm_id = "dm", message['u_id'], dm['dm_id']
                    else:
                        return True

    if action == "channel":
        notification_dictionary = {
            'channel_id' : channel_dm_id,
            'dm_id' : -1,
            'notification_message' : f"{get_user_handle(int(decoded_token['username']))} reacted to your message in {get_channel_name(channel_dm_id)}"
        }
    else:
        notification_dictionary = {
            'channel_id' : -1,
            'dm_id' : channel_dm_id,
            'notification_message' : f"{get_user_handle(int(decoded_token['username']))} reacted to your message in {get_dm_name(channel_dm_id)}"
        }

    if notifications == []:
        notifications.append(
            {
                "u_id" : u_id,
                "notified" : [notification_dictionary]
            }
        )
    else:
        flag = 0
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
