from src.data_store import data_store
from src.error import InputError
from src.error import AccessError
import src.helpers
import re

# ----------------------- Implementation ----------------------- #
# ----------------------- Implementation ----------------------- #

def users_all_v1(token):
    """
    Description:
        This function will return all the users and it details accept the users
        who have been removed

    Arguments:
        token      - string - This is the unique for each user and helps us in identification

    Exceptions:
        AccessError - Occurs when a token is invalid or a token cannot be decoded
        
    Return Value:
        Returns { 'users' } if there are no AccessErrors
    """

    initial_object = data_store.get()
    user_details = initial_object['users']

    decoded_token = get_decoded_token(token)
    verify_token(decoded_token, user_details)

    final_users_list = []
    
    for user in user_details:
        if user['is_removed'] is False:
            final_users_list.append({
                'u_id': user['auth_user_id'],
                'email': user['email'],
                'name_first': user['name_first'],
                'name_last': user['name_last'],
                'handle_str': user['handle_str'],
                'profile_img_url': user['profile_img_url']
                })
    return final_users_list

def user_profile_v1(token, u_id):
    """
    Description:
        This function will return user whose details have been passed in the parameter

    Arguments:
        token   - string  - This is the unique for each user and helps us in identification
        u_id    - integer - This also help in identifying the user, in a less secure way

    Exceptions:
        AccessError - Occurs when a token is invalid or a token cannot be decoded
        InputError  - u_id does not refer to a valid user
        
    Return Value:
        Returns { 'user' } if there are no AccessErrors or InputErrors
    """

    initial_object = data_store.get()
    user_details = initial_object['users']

    decoded_token = get_decoded_token(token)
    verify_token(decoded_token, user_details)

    user = check_details(u_id, user_details, decoded_token)
    return({
        'u_id': user['auth_user_id'],
        'email': user['email'],
        'name_first': user['name_first'],
        'name_last': user['name_last'],
        'handle_str': user['handle_str'],
        'profile_img_url': user['profile_img_url']
        })

def user_profile_setname_v1(token, name_first, name_last):
    """
    Description:
        This function will change the name_first and last of the user whose token is passed

    Arguments:
        token       - string - This is the unique for each user and helps us in identification
        name_first  - string - The new first name of the user
        name_last   - string - The new last name of the user

    Exceptions:
        AccessError - Occurs when a token is invalid or a token cannot be decoded
        InputError  - length of name_first is not between 1 and 50 characters inclusive
        InputError  - length of name_last is not between 1 and 50 characters inclusive
        
    Return Value:
        Returns {  } if there are no AccessErrors or InputErrors
    """

    initial_object = data_store.get()
    user_details = initial_object['users']
    channel_details = initial_object['channels']

    decoded_token = get_decoded_token(token)
    verify_token(decoded_token, user_details)

    check_length_name(name_first,name_last)

    update_names(decoded_token, user_details, name_first, name_last)
    update_names_channel(decoded_token, channel_details, name_first, name_last)

    data_store.set(initial_object)

    return({})

def user_profile_setemail_v1(token, email):
    """
    Description:
        This function will change the email of the user whose token is passed

    Arguments:
        token  - string - This is the unique for each user and helps us in identification
        email  - string - The new email of the user

    Exceptions:
        AccessError - Occurs when a token is invalid or a token cannot be decoded
        InputError  - email entered is not a valid email
        InputError  - email address is already being used by another user
        
    Return Value:
        Returns {  } if there are no AccessErrors or InputErrors
    """

    initial_object = data_store.get()
    user_details = initial_object['users']
    channel_details = initial_object['channels']

    decoded_token = get_decoded_token(token)
    verify_token(decoded_token, user_details)

    check_email(email)

    update_email(decoded_token, user_details, email)
    update_email_channel(decoded_token, channel_details, email)

    data_store.set(initial_object)

    return({})

def user_profile_sethandle_v1(token, handle_str):
    """
    Description:
        This function will change the handle of the user whose token is passed

    Arguments:
        token       - string - This is the unique for each user and helps us in identification
        handle_str  - string - The new email of the user

    Exceptions:
        AccessError - Occurs when a token is invalid or a token cannot be decoded
        InputError  - length of handle_str is not between 3 and 20 characters inclusive
        InputError  - handle_str contains characters that are not alphanumeric
        InputError  - the handle is already used by another user
        
    Return Value:
        Returns {  } if there are no AccessErrors or InputErrors
    """

    initial_object = data_store.get()
    user_details = initial_object['users']
    channel_details = initial_object['channels']
    dm_details = initial_object['dms']

    decoded_token = get_decoded_token(token)
    verify_token(decoded_token, user_details)

    check_length_handle(handle_str)
    check_handle_type(handle_str)
    check_handle_in_use(user_details, handle_str)

    old_handle = get_old_handle(decoded_token, user_details)

    update_handle(decoded_token, user_details, handle_str)
    update_handle_channel(decoded_token, channel_details, handle_str)
    update_handle_dm(dm_details, handle_str, old_handle)

    data_store.set(initial_object)

    return ({})

# ----------------------- Implementation ----------------------- #
# ----------------------- Implementation ----------------------- #


def get_decoded_token(token):
    try:
        decoded_token = src.helpers.decode_jwt(token)
        return decoded_token
    except Exception as error:
        raise AccessError(description="invalid token") from error

def verify_token(decoded_token, user_details):
    for user in user_details:
        if user['token'] == decoded_token['username'] and decoded_token['session_id'] in user['session_list']:
            if user['is_removed'] is False:
                return True
    raise AccessError(description="invalid token")

def check_details(u_id, user_details, decoded_token):
    for user in user_details:
        if user['auth_user_id'] == u_id:
            return user
    raise InputError(description="u_id is not a valid user")

def update_names(decoded_token, user_details, name_first, name_last):
    for user in user_details:
        if(decoded_token['username'] == user['token'] and decoded_token['session_id'] in user['session_list']):
            user['name_first'] = name_first
            user['name_last'] = name_last
    return {}

def update_names_channel(decoded_token, channel_details, name_first, name_last):
    for channel in channel_details:
        for user1 in channel['owner_members']:
            if str(user1['u_id']) == decoded_token['username']:
                user1['name_first'] = name_first
                user1['name_last'] = name_last
        for user1 in channel['all_members']:
            if str(user1['u_id']) == decoded_token['username']:
                user1['name_first'] = name_first
                user1['name_last'] = name_last

def update_email(decoded_token, user_details, email):
    for user in user_details:
        if user['email'] == email and user['is_removed'] is False:
            raise InputError(description="Email already registered")
    for user in user_details:
        if(decoded_token['username'] == user['token'] and decoded_token['session_id'] in user['session_list']):
            user['email'] = email
    return {}

def update_email_channel(decoded_token, channel_details, email):
    for channel in channel_details:
        for user1 in channel['owner_members']:
            if str(user1['u_id']) == decoded_token['username']:
                user1['email'] = email
        for user1 in channel['all_members']:
            if str(user1['u_id']) == decoded_token['username']:
                user1['email'] = email

def check_handle_in_use(user_details, handle_str):
    for user in user_details:
        if user['is_removed'] is False and user['handle_str'] == handle_str:
            raise InputError(description="handle already in use")

def update_handle(decoded_token, user_details, handle_str):
    for user in user_details:
        if(decoded_token['username'] == user['token'] and decoded_token['session_id'] in user['session_list']):
            user['handle_str'] = handle_str
    return {}

def update_handle_channel(decoded_token, channel_details, handle_str):
    for channel in channel_details:
        for user1 in channel['owner_members']:
            if str(user1['u_id']) == decoded_token['username']:
                user1['handle_str'] = handle_str
        for user1 in channel['all_members']:
            if str(user1['u_id']) == decoded_token['username']:
                user1['handle_str'] = handle_str

def get_old_handle(decoded_token, user_details):
    old_handle = ""
    for user in user_details:
        if user['token'] == decoded_token['username']:
            old_handle = user['handle_str']
    return old_handle

def update_handle_dm(dm_details, handle_str, old_handle):
    for dm in dm_details:
        handles_list = dm['name'].split(', ')
        if old_handle in handles_list:
            index = handles_list.index(old_handle)
            handles_list[index] = handle_str
            handles_list.sort()
            name_string = ', '.join(handles_list)
            dm['name'] = name_string

def check_email(email):
    """
    This function will check the format of the email
    of the person registering
    """

    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if re.fullmatch(regex, email):
        return True
    raise InputError(description="Invalid email format")

def check_length_name(name_first,name_last):
    """
    This function will check if the password length is
    (>= 1) and (<= 50) when the user is registering
    """

    if 1 <= len(name_first) <= 50 and 1 <= len(name_last) <= 50:
        return True
    raise InputError(description="Word limit exceeded or empty field entered")

def check_length_handle(handle_str):
    """
    This function will check if the password length is
    (>= 3) and (<= 20) when the user is registering
    """
    if 3 <= len(handle_str) <= 20:
        return True
    raise InputError(description="Word limit exceeded or is less than required")

def check_handle_type(handle_str):
    if handle_str.isalnum():
        return True
    raise InputError(description="Not alpha numeric")
