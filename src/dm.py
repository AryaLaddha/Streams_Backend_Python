import json
from src.helpers import decode_jwt
from src.data_store import data_store
from src.error import InputError
from src.error import AccessError

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

def dm_create_v1(token, u_ids):
    '''
    Dm_create will create a new dm with the caller as the creator of the dm.
    The members of the dm will be in the u_ids.

    Arguments:
        token (string) - An encryption that contains the caller/creator of the dm.
                       It contains the id of caller and session id.
        u_ids (list of ints) - The users that the dm is directed to.

    Exceptions:
        InputError - Occurs when any u_id in u_ids does not refer to a valid user.

        AccessError - Occurs when the token doesn't decode.
                    - Occurs when the token does not refer to an existant user.


    Return Value:
        Returns {dm_id} when the token and u_ids are all valid.
    '''
    store = data_store.get()
    users = store['users']
    dms = store['dms']
    valid = 0
    dm_id = {}
    dm = {}
    names = []
    auth_id = check_valid_auth(token, users)

    #This goes through the users database and obtains the handle_str for all
    #The users in u_ids.
    for u_id in u_ids:
        for user in users:
            if u_id == user['auth_user_id']:
                valid += 1
                names.append(user['handle_str'])

            if u_id == auth_id:
                raise AccessError(description = 'U_ids contains caller')

    #This checks if all the u_ids in the u_ids list are valid.
    if valid != len(u_ids):
        raise InputError(description = 'One or more u_ids are invalid')

    #This grabs the handle_str of the caller.
    for user in users:
        if auth_id == user['auth_user_id']:
            names.append(user['handle_str'])

    #This inititalises the dm.
    names.sort()
    name_string = ', '.join(names)
    dm_id['dm_id'] = len(dms) + 1
    dm['dm_id'] = dm_id['dm_id']
    dm['u_ids'] = u_ids
    dm['name'] = name_string
    dm['messages'] = []
    dm['creator'] = auth_id
    dm['num_message_later'] = 0
    dms.append(dm)
    data_store.set(store)

    return dm_id
 
def dm_list_v1(token):
    '''
    Dm_list will provide the caller all then dms that they are a member of.
    Arguments:
        token (string) - An encryption that contains the caller/creator of the dm.
                       It contains the id of caller and session id.

    Exceptions:
        InputError - Occurs when any u_id in u_ids does not refer to a valid user.

        AccessError - Occurs when the token doesn't decode.
                    - Occurs when the token does not refer to an existant user.

    Return Value:
        Returns {dms} when the token is valid.
    '''
    store = data_store.get()
    dms = store['dms']
    users = store['users']
    user_dms = []
    temp_dm = {}

    #This checks if the token is valid.
    auth_id = check_valid_auth(token, users)

    #This goes through the dms_data and gets the id of dm and gets the dm data
    #from the dms the user is apart of.
    for dm in dms:
        temp_dm = {}
        if auth_id == dm['creator']:
            temp_dm['dm_id'] = dm['dm_id']
            temp_dm['name'] = dm['name']
            user_dms.append(temp_dm)

        temp_dm = {}
        for user in dm['u_ids']:
            if auth_id == user:
                temp_dm['dm_id'] = dm['dm_id']
                temp_dm['name'] = dm['name']
                user_dms.append(temp_dm)

    return {'dms': user_dms}

def dm_remove_v1(token, dm_id):
    '''
    Dm_remove will remove a dm from the dm_database. This can only be done by the creator.
    Arguments:
        token (string) - An encryption that contains the caller/creator of the dm.
                         It contains the id of caller and session id.
        dm_id (integer) - An id for the dm.

    Exceptions:
        InputError - Occurs when any u_id in u_ids does not refer to a valid user.

        AccessError - Occurs when the token doesn't decode.
                    - Occurs when the token does not refer to an existant user.
                    - Occurs when the caller of th function is not the creator.

    Return Value:
        Returns {} when the token and dm_id is valid.
    '''
    store = data_store.get()
    dms = store['dms']
    users = store['users']
    auth_id = check_valid_auth(token, users)
    valid = False

    #This goes through the dm_database and finds the dm, then it checks if
    #the caller is the creator of the dm. If so, then it is deleted.
    for dm in dms:
        if dm['dm_id'] == dm_id:
            valid = True

            if dm['creator'] == auth_id:
                dms.remove(dm)

            else:
                raise AccessError(description = "user is not creator of DM.")

    if not valid:
        raise InputError(description = "DM is invalid.")

    data_store.set(store)
 
    return {}
    
def dm_leave_v1(token, dm_id):
    '''
    Dm_leave will remove a specific user from the dm.
    Arguments:
        token (string) - An encryption that contains the caller/creator of the dm.
                         It contains the id of caller and session id.
        dm_id (integer) - An id for the dm.

    Exceptions:
        InputError - Occurs when the dm_id doesn't refer to a vald dm.

        AccessError - Occurs when the token doesn't decode.
                    - Occurs when the token does not refer to an existant user.
                    - Occurs when the caller of th function is not the creator.

    Return Value:
        Returns {} when the token and dm_id is valid.
    '''
    store = data_store.get()
    users = store['users']
    dms = store['dms']
    auth_id = check_valid_auth(token, users)

    #This goes through the dm database and finds the specified dm.
    valid = False
    for dm in dms:
        if dm['dm_id'] == dm_id:
            valid = True
            dm_details = dm

    if not valid:
        raise InputError(description="invalid dm")

    #This removes the caller from said database.
    valid_user = False
    for user in dm_details['u_ids']:
        if user == auth_id:
            valid_user = True
            dm_details['u_ids'].remove(user)

    if auth_id == dm_details['creator']:
        dm_details['creator'] = -1
        valid_user = True

    if not valid_user:
        raise AccessError(description="user is an unauthorised member")
    
    data_store.set(store)

    return {}

def dm_details_v1(token, dm_id):
    '''
    Dm_details will provide the basic details of a specified dm.
    Arguments:
        token (string) - An encryption that contains the caller/creator of the dm.
                         It contains the id of caller and session id.
        dm_id (integer) - An id for the dm.

    Exceptions:
        InputError - Occurs when the dm_id doesn't refer to a vald dm.

        AccessError - Occurs when the token doesn't decode.
                    - Occurs when the token does not refer to an existant user.
                    - Occurs when the caller of th function is not the creator.

    Return Value:
        Returns {'name': '', 'members': []} when the token and dm_id is valid.
    '''
    store = data_store.get()
    users = store['users']
    dms = store['dms']
    auth_id = check_valid_auth(token, users)
    valid = False
    dm_details = {}
    user_details = {}
    return_value = {
        'name': [],
        'members': []
    }

    #Goes through the database and checks if the dm is valid.
    for dm in dms:
        if dm['dm_id'] == dm_id:
            valid = True
            dm_details = dm

    if not valid:
        raise InputError(description="invalid dm_id")

    #This checks if the caller is in the dm.
    valid_user = False
    for user in dm_details['u_ids']:
        if auth_id == user:
            valid_user = True

    if auth_id == dm_details['creator']:
        valid_user = True

    if not valid_user:
        raise AccessError(description="unauthorised user")

    #This grabs the information from everyone in the dm.
    for dm_user_id in dm_details['u_ids']:
        user_details = {}
        for user in users:
            user_details = {}
            if dm_user_id == user['auth_user_id']:
                user_details['u_id'] = user['auth_user_id']
                user_details['email'] = user['email']
                user_details['name_first'] = user['name_first']
                user_details['name_last'] = user['name_last']
                user_details['handle_str'] = user['handle_str']
                user_details['profile_img_url'] = user['profile_img_url']

            elif dm_details['creator'] == user['auth_user_id']:
                user_details['u_id'] = user['auth_user_id']
                user_details['email'] = user['email']
                user_details['name_first'] = user['name_first']
                user_details['name_last'] = user['name_last']
                user_details['handle_str'] = user['handle_str']
                user_details['profile_img_url'] = user['profile_img_url']

            if user_details not in return_value['members'] and user_details != {}:
                return_value['members'].append(user_details)

    return_value['name'] = dm_details['name']
    return return_value
