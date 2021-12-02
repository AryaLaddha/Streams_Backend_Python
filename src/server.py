import sys
import signal
from json import dumps
from flask import Flask, request, send_from_directory
from flask_cors import CORS
import requests
from src.error import InputError,AccessError
from src import config
import json
import os
import hashlib
import src.helpers
import psycopg2

from src.other import clear_v1
from src.data_store import data_store
from src.error import InputError,AccessError

from src.function_helpers import get_user_store, get_decoded_token, verify_token
from src.channel_leave_helper import leave_channel_valid, invalid_access
from src.channels_list_helper import get_user_channels, get_all_channels
from src.channel_owner_helper import already_owner, remove_owner, only_owner, global_owner_already_member
from src.channel_owner_helper import valid_channel, valid_user, already_member, is_global_owner
from src.channel_owner_helper import check_token_and_user_details, owner_details, add_owner, unauthorised_user
from src.admin_user import find_id, check_uid_valid, check_global, check_only_global, remove_user, permission_change
from src.channel import message_send_v1, message_edit_v1, message_remove_v1, dm_messages_v1, message_react_v1, message_unreact_v1, message_pin_v1, message_unpin_v1
from src.channel import channel_invite_v2, channel_messages_v2, channel_join_v2, channel_details_v2
from src.dm import dm_create_v1, dm_list_v1, dm_remove_v1, dm_leave_v1, dm_details_v1
from src.user import user_profile_v1, users_all_v1, user_profile_setemail_v1
from src.user import user_profile_sethandle_v1, user_profile_setname_v1
from src.auth import auth_register_v1, auth_login_v1, auth_logout_v1
from src.auth import auth_passwordreset_request_v1, auth_passwordreset_reset_v1, search_v1
from src.channels import channels_create_v1,find_auth_id
from src.senddm import message_send
from src.message_share_helper import message_share
from src.notification_helper import notification_message_send, notification_message_edit_channel, notification_message_edit_dm, send_notification_dm, get_old_message, notification_senddm, react_message_notification
from src.sendlater_helper import dm_sendlater, message_sendlater
from src.standup import standup_active_v1, standup_start_v1, standup_send_v1
from src.stats_helper import get_channels_activity, get_messages_activity, get_dms_activity, update_user_activity_channels, update_user_activity_messages, update_user_activity_dms, update_user_activity_dms_id, update_user_activity_channels_id, get_time, initialise_user_activity_channels, initialise_user_activity_messages, initialise_user_activity_dms, update_activity_for_all_in_dm, update_remove_dm_activity_for_creator, calculate_involvement_rate, initialise_workspace_activity, update_channels_exist, update_dms_exist, update_messages_exist, is_first_user, calculate_workspace_utilisation
from src.upload_photos_helper import save_image, set_image, check_file_type, crop_image_to_size, default_image


def quit_gracefully(*args):
    '''For coverage'''
    exit(0)

def defaultHandler(err):
    response = err.get_response()
    print('response', err, err.get_response())
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = 'application/json'
    return response

APP = Flask(__name__, static_url_path = '/static/')
CORS(APP)

APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, defaultHandler)

#### NO NEED TO MODIFY ABOVE THIS POINT, EXCEPT IMPORTS
'''
This code below will set the data store according to
the previously saved database.json before running the
server
'''
try:
    with open('database.json', 'r') as myfile:
        data = myfile.read()
    initial_object = data_store.get()
    initial_object = json.loads(data)
    data_store.set(initial_object)
except:
    with open('database.json', 'w') as myfile:
        initial_object = data_store.get()
        json.dump(initial_object,myfile)
'''
This is used in the routes I have written below for
register and login. It is used to save the data in the
json file.
'''
def save_users_data():
   initial_object = data_store.get()
   with open('database.json','w') as FILE:
       json.dump(initial_object,FILE)


@APP.route("/notifications/get/v1", methods=['GET'])
def notifications():
    user_details = get_user_store()

    token = request.args.get('token',None)

    decoded_token = get_decoded_token(token)
    verify_token(decoded_token, user_details)

    final_list = []

    notification_list = data_store.get()['notifications']
    for uids in notification_list:
        if str(uids['u_id']) == decoded_token['username']:
            final_list = uids['notified']

    reversed_list = final_list[::-1]

    return dumps({ 'notifications' : reversed_list[0:21] })

@APP.route("/search/v1", methods=['GET'])
def search():
    token = request.args.get('token',None)
    query_str = request.args.get('query_str',None)

    return_value = search_v1(token, query_str)

    save_users_data()

    return dumps({'messages': return_value})

@APP.route("/auth/register/v2", methods=['POST'])
def register():
    user_detail = request.get_json()
    user_detail['profile_img_url'] = default_image()
    return_value = auth_register_v1(
        user_detail['email'],
        user_detail['password'],
        user_detail['name_first'],
        user_detail['name_last']
    )

    initialise_user_activity_channels(return_value['token'])
    initialise_user_activity_messages(return_value['token'])
    initialise_user_activity_dms(return_value['token'])
    if is_first_user(return_value['auth_user_id']) == True:
        initialise_workspace_activity()
    save_users_data()

    return dumps({
        'auth_user_id': return_value['auth_user_id'],
        'token': return_value['token'],
    })


@APP.route("/auth/login/v2", methods=['POST'])
def login():
    user_detail = request.get_json()
    return_value = auth_login_v1(
        user_detail['email'],
        src.helpers.hash(user_detail['password']),
    )

    save_users_data()

    return dumps({
        'auth_user_id': return_value['auth_user_id'],
        'token': return_value['token'],
    })

@APP.route("/auth/logout/v1", methods=['POST'])
def logout():
    token = request.get_json()
    return_value = auth_logout_v1(token['token'])

    save_users_data()

    return dumps(return_value)

@APP.route("/auth/passwordreset/request/v1", methods=['POST'])
def reset_request():
    email = request.get_json()

    return_value = auth_passwordreset_request_v1(email['email'])
    save_users_data()

    return dumps(return_value)

@APP.route("/auth/passwordreset/reset/v1", methods=['POST'])
def reset():
    data = request.get_json()

    return_value = auth_passwordreset_reset_v1(data['reset_code'], data['new_password'])

    save_users_data()

    return dumps(return_value)

@APP.route("/users/all/v1", methods=['GET'])
def give_all_users():
    user = request.args.get('token')
    users = users_all_v1(user)

    save_users_data()

    return dumps({"users": users})

@APP.route("/user/profile/v1", methods=['GET'])
def give_user_profile():
    token = request.args.get('token',None)
    u_id = request.args.get('u_id',None)
    #set_default_image(u_id)
    return_value = user_profile_v1(token, int(u_id))

    save_users_data()

    return dumps({'user':return_value})

@APP.route("/user/profile/setname/v1", methods=['PUT'])
def user_setname():
    data = request.get_json()
    return_value = user_profile_setname_v1(data['token'], data['name_first'], data['name_last'])

    save_users_data()

    return dumps(return_value)

@APP.route("/user/profile/setemail/v1", methods=['PUT'])
def user_setemail():
    data = request.get_json()
    return_value = user_profile_setemail_v1(data['token'], data['email'])

    save_users_data()

    return dumps(return_value)

@APP.route("/user/profile/sethandle/v1", methods=['PUT'])
def user_sethandle():
    data = request.get_json()
    return_value = user_profile_sethandle_v1(data['token'], data['handle_str'])

    save_users_data()

    return dumps(return_value)

@APP.route("/channels/create/v2",methods = ['POST'])
def create_channel():
    request_data = request.get_json()
    user_token = request_data['token']

    user_id = find_auth_id(user_token)

    if user_id == None:
        raise AccessError

    return_id = channels_create_v1(
        user_id,
        request_data['name'],
        request_data['is_public']
    )
    update_user_activity_channels(user_token)
    update_channels_exist()
    save_users_data()

    return dumps(return_id)

@APP.route("/channel/messages/v2", methods = ['GET'])
def messages():
    data = request.args.to_dict()

    return_value = channel_messages_v2(
        data['token'], int(data['channel_id']),
        int(data['start'])
    )

    save_users_data()

    return dumps({
        'messages': return_value['messages'],
        'start': return_value['start'],
        'end': return_value['end']
    })

@APP.route("/channel/join/v2", methods = ['POST'])
def join():
    param = request.get_json()

    return_value = channel_join_v2(
        param['token'],
        param['channel_id']
    )
    update_user_activity_channels(param['token'])
    save_users_data()

    return dumps(return_value)

@APP.route("/channel/invite/v2", methods=['POST'])
def channel_invite():
    #This is the route to run channel_invite_v2.
    channel_data = request.get_json()

    channel_invite_v2(
        channel_data['token'],
        channel_data['channel_id'],
        channel_data['u_id']
    )
    update_user_activity_channels_id(channel_data['u_id'])
    save_users_data()

    return dumps({})

@APP.route("/channel/details/v2", methods=['GET'])
def channel_details():
    #This is the route to run channel_details_v2.
    token = request.args.get('token', None)
    channel_id = request.args.get('channel_id', None)
    return_value = channel_details_v2(token, int(channel_id))

    save_users_data()

    return return_value

@APP.route("/message/send/v1", methods = ['POST'])
def send():
    param = request.get_json()

    return_value = message_send_v1(
        param['token'],
        param['channel_id'],
        param['message']
    )
    update_user_activity_messages(param['token'])
    update_messages_exist()

    notification_message_send(
        param['token'],
        param['channel_id'],
        param['message']
    )

    save_users_data()

    return dumps({
        'message_id': return_value
    })

@APP.route("/message/edit/v1", methods = ['PUT'])
def edit():
    param = request.get_json()

    action = ""
    old_messages = ""
    id1 = 0

    flag = 0
    if not get_old_message(
        param['token'],
        param['message_id'],
        param['message']
    ):
        flag = 1
    else:
        old_messages, action, id1 = get_old_message(
            param['token'],
            param['message_id'],
            param['message']
        )

    return_value = message_edit_v1(
        param['token'],
        param['message_id'],
        param['message']
    )

    if flag == 0 and action == "channel":
        notification_message_edit_channel(
            param['token'],
            param['message_id'],
            param['message'],
            old_messages,
            id1
        )
    elif flag == 0 and action == "dm":
        notification_message_edit_dm(
            param['token'],
            param['message_id'],
            param['message'],
            old_messages,
            id1
        )

    save_users_data()

    return dumps(return_value)

@APP.route("/message/remove/v1", methods = ['DELETE'])
def remove():
    param = request.get_json()

    return_value = message_remove_v1(
        param['token'],
        param['message_id']
    )
    update_messages_exist()
    save_users_data()

    return dumps(return_value)

@APP.route("/message/react/v1", methods = ['POST'])
def react():
    param = request.get_json()

    return_value = message_react_v1(
        param['token'],
        param['message_id'],
        param['react_id']
    )

    react_message_notification(
        param['token'],
        param['message_id'],
        param['react_id']
    )

    save_users_data()

    return dumps(return_value)

@APP.route("/message/unreact/v1", methods = ['POST'])
def unreact():
    param = request.get_json()

    return_value = message_unreact_v1(
        param['token'],
        param['message_id'],
        param['react_id']
    )

    save_users_data()

    return dumps(return_value)

@APP.route("/message/pin/v1", methods = ['POST'])
def pin():
    param = request.get_json()

    return_value = message_pin_v1(
        param['token'],
        param['message_id']
    )

    save_users_data()

    return dumps(return_value)

@APP.route("/message/unpin/v1", methods = ['POST'])
def unpin():
    param = request.get_json()

    return_value = message_unpin_v1(
        param['token'],
        param['message_id']
    )

    save_users_data()

    return dumps(return_value)

@APP.route("/dm/messages/v1", methods = ['GET'])
def dm_messages():
    data = request.args.to_dict()

    return_value = dm_messages_v1(
        data['token'],
        int(data['dm_id']),
        int(data['start'])
    )

    save_users_data()

    return dumps({
        'messages': return_value['messages'],
        'start': return_value['start'],
        'end': return_value['end']
    })


@APP.route("/dm/create/v1", methods=['POST'])
def dm_create():
    dm_details = request.get_json()
    return_value = dm_create_v1(dm_details['token'], dm_details['u_ids'])
    update_user_activity_dms(dm_details['token'])
    for u_id in dm_details['u_ids']:
        update_user_activity_dms_id(u_id)
    update_dms_exist()

    send_notification_dm(return_value['dm_id'])

    save_users_data()

    return dumps({'dm_id': return_value['dm_id']})

@APP.route("/dm/list/v1", methods=['GET'])
def dm_list():
    token = request.args.get('token', None)
    return_value = dm_list_v1(token)

    save_users_data()

    return dumps(return_value)

@APP.route("/dm/remove/v1", methods=['DELETE'])
def dm_remove():
    dm_details = request.get_json()
    update_activity_for_all_in_dm(dm_details['dm_id'])
    update_remove_dm_activity_for_creator(dm_details['dm_id'])
    dm_remove_v1(dm_details['token'], dm_details['dm_id'])
    update_dms_exist()
    save_users_data()

    return dumps({})

@APP.route("/dm/leave/v1", methods=['POST'])
def dm_leave():
    dm_details = request.get_json()
    dm_leave_v1(dm_details['token'], dm_details['dm_id'])
    update_user_activity_dms(dm_details['token'])
    save_users_data()

    return dumps({})

@APP.route("/dm/details/v1", methods=['GET'])
def dm_details():
    token = request.args.get('token', None)
    dm_id = request.args.get('dm_id', None)
    return_value = dm_details_v1(token, int(dm_id))

    save_users_data()

    return dumps(return_value)

@APP.route("/channel/addowner/v1", methods = ['POST'])
def add_channel_owner():
    data = request.get_json()
    token_value = data['token']
    channel_to_addowner_id = data['channel_id']
    user_id = data['u_id']

    check_token_and_user_details(token_value)

    if unauthorised_user(token_value, channel_to_addowner_id) == True and is_global_owner(token_value) == False:
        raise AccessError(description = "Not a channel owner")
    if not valid_channel(channel_to_addowner_id):
        raise InputError(description = "Invalid channel")
    if not valid_user(user_id):
        raise InputError(description = "Invalid user")
    if is_global_owner(token_value) == True and global_owner_already_member(token_value, channel_to_addowner_id) == False:
        raise AccessError(description = "Global owner not a member of the channel")
    if not already_member(user_id, channel_to_addowner_id):
        raise InputError(description = "Not a member of the channel")
    if already_owner(user_id, channel_to_addowner_id):
        raise InputError(description = "Already an owner")
    add_owner(user_id, channel_to_addowner_id)

    save_users_data()

    return dumps({})

@APP.route("/channel/removeowner/v1", methods = ['POST'])
def remove_channel_owner():
    data = request.get_json()
    token = data['token']
    channel_to_removeowner_id = data['channel_id']
    user_id = data['u_id']

    check_token_and_user_details(token)

    if unauthorised_user(token, channel_to_removeowner_id) and is_global_owner(token) == False:
        raise AccessError(description = "Not a channel owner or global owner")
    if not valid_channel(channel_to_removeowner_id):
        raise InputError(description = "Invalid channel")
    if not valid_user(user_id):
        raise InputError(description = "Invalid user")
    if is_global_owner(token) == True and global_owner_already_member(token, channel_to_removeowner_id) == False:
        raise AccessError(description = "Global owner not a member of the channel to remove owner")
    if not already_owner(user_id, channel_to_removeowner_id):
        raise InputError(description = "Not an owner")
    if only_owner(channel_to_removeowner_id):
        raise InputError(description = "Cannot remove sole owner")

    remove_owner(user_id, channel_to_removeowner_id)

    save_users_data()

    return dumps({})

@APP.route("/channel/leave/v1", methods = ['POST'])
def leave_channel():
    data = request.get_json()
    token = data['token']
    channel_to_leave_id = data['channel_id']

    check_token_and_user_details(token)

    if not valid_channel(channel_to_leave_id):
        raise InputError(description = "Invalid channel")
    if invalid_access(token, channel_to_leave_id):
        raise AccessError(description = "Not a member of the channel")

    leave_channel_valid(token, channel_to_leave_id)
    update_user_activity_channels(token)
    save_users_data()

    return dumps({})

@APP.route("/channels/list/v2", methods = ['GET'])
def list_channels():
    user_token = request.args.get('token')
    check_token_and_user_details(user_token)
    user_channels = get_user_channels(user_token)

    save_users_data()

    return dumps(user_channels)

@APP.route("/channels/listall/v2", methods = ['GET'])
def listall_channels():
    user_token = request.args.get('token')
    check_token_and_user_details(user_token)
    all_channels = get_all_channels(user_token)

    save_users_data()

    return dumps(all_channels)


@APP.route('/message/senddm/v1',methods = ["POST"])
def senddm():
    requests_data =request.get_json()

    token = requests_data['token']
    dm_id = requests_data['dm_id']
    message = requests_data['message']

    message_id = message_send(token,dm_id,message)

    save_users_data()

    notification_senddm(token, dm_id, message)

    return dumps({'message_id':message_id})


#   ADMIN user part is in now
@APP.route('/admin/user/remove/v1',methods = ['DELETE'])
def user_remove_admin():
    request_data = request.get_json()
    user_token = request_data['token']
    u_id = request_data['u_id']

    user_dict = find_id(user_token)
    if user_dict == None:
        raise AccessError("TOken cannot be found")
    authorised_user_id = user_dict['auth_user_id']

    if check_uid_valid(u_id) == False:
        raise InputError("Id not valid")
    if check_global(authorised_user_id) == False:
        raise AccessError("Authorisation not global")

    if check_only_global(u_id):
        raise InputError("Only gobal uid")

    remove_user(u_id,user_dict)

    save_users_data()

    return dumps({})


@APP.route('/admin/userpermission/change/v1',methods = ['POST'])
def user_permission_change():
    request_data = request.get_json()

    user_token = request_data['token']
    permission_id = request_data['permission_id']
    u_id = request_data['u_id']

    if permission_id != 1 and permission_id != 2:
        raise InputError(description = "Permission Id issue")

    user_dict = find_id(user_token)
    if user_dict == None:
        raise AccessError("User token incorrect")

    authorised_user_id = user_dict['auth_user_id']

    if check_uid_valid(u_id) == False:
        raise InputError("u_id not valid")
    if check_only_global(authorised_user_id) and permission_id == 2:
        raise InputError("only gloabl and permission is to demote it")

    if check_global(authorised_user_id) == False:
        raise AccessError("authorised not global")

    permission_change(u_id,permission_id)

    save_users_data()

    return dumps({})

@APP.route("/message/share/v1",methods = ["POST"])
def share_message():
    request_data = request.get_json()
    token = request_data['token']
    og_message_id = request_data['og_message_id']
    message = request_data['message']
    channel_id = request_data['channel_id']
    dm_id = request_data['dm_id']
    message_share_id = message_share(token, og_message_id, message, channel_id, dm_id)
    update_user_activity_messages(token)
    return dumps(message_share_id)


@APP.route('/message/sendlater/v1',methods = ['POST'])
def channel_message_send_later():
    request_data = request.get_json()
    token = request_data['token']
    channel_id = request_data['channel_id']
    message = request_data['message']
    time_sent = request_data['time_sent']

    message_id = message_sendlater(token, channel_id, message, time_sent)
    return dumps({'message_id':message_id})

@APP.route('/message/sendlaterdm/v1',methods = ["POST"])
def dm_message_send_later():
    request_data = request.get_json()
    token = request_data['token']
    dm_id = request_data['dm_id']
    message = request_data['message']
    time_sent = request_data['time_sent']

    message_id = dm_sendlater(token, dm_id, message, time_sent)
    return dumps({'message_id':message_id})


@APP.route('/standup/start/v1', methods=['POST'])
def standup_start():
    data = request.get_json()
    return_value = standup_start_v1(data['token'], data['channel_id'], data['length'])

    save_users_data()

    return dumps(return_value)

@APP.route('/standup/active/v1', methods=['GET'])
def standup_active():
    token = request.args.get('token', None)
    channel_id = request.args.get('channel_id', None)
    return_value = standup_active_v1(token, int(channel_id))

    save_users_data()

    return dumps(return_value)

@APP.route('/standup/send/v1', methods=['POST'])
def standup_send():
    data = request.get_json()
    standup_send_v1(data['token'], data['channel_id'], data['message'])

    save_users_data()

    return dumps({})

@APP.route("/clear/v1", methods=['DELETE'])
def clear():
    clear_v1()

    save_users_data()

    return dumps({})

@APP.route("/user/stats/v1", methods = ['GET'])
def get_stats():
    user_token = request.args.get('token')
    check_token_and_user_details(user_token)
    save_users_data()
    return dumps({'user_stats': {'channels_joined': get_channels_activity(user_token), 'messages_sent': get_messages_activity(user_token), 'dms_joined': get_dms_activity(user_token), 'involvement_rate':calculate_involvement_rate(user_token)}})

@APP.route("/users/stats/v1", methods = ['GET'])
def get_workspace_stats():
    user_token = request.args.get('token')
    check_token_and_user_details(user_token)
    data_store.get()['workspace_stats'][0]['utilization_rate'] = round(calculate_workspace_utilisation(user_token), 3)
    save_users_data()
    return dumps({'workspace_stats': data_store.get()['workspace_stats'][0]})


@APP.route("/user/profile/uploadphoto/v1", methods = ['POST'])
def profile_photo():
    data = request.get_json()
    check_token_and_user_details(data['token'])
    auth_id = find_auth_id(data['token'])
    save_image(data['img_url'], auth_id)
    check_file_type(f'src/static/{auth_id}.jpg')
    crop_image_to_size(f'src/static/{auth_id}.jpg', data['x_start'], data['y_start'], data['x_end'], data['y_end'])
    image_url = config.url + f'static/{auth_id}.jpg'
    set_image(image_url, auth_id)
    save_users_data()
    return dumps({})

@APP.route('/static/<path:path>')
def send_js(path):
    return send_from_directory('', path)
#### NO NEED TO MODIFY BELOW THIS POINT

if __name__ == "__main__":
    signal.signal(signal.SIGINT, quit_gracefully) # For coverage
    APP.run(port=config.port) # Do not edit this port
