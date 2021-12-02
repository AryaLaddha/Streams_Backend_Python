from src.auth_helpers import list_dm_update, list_channel_update, create_user_handle, checker
from src.auth_helpers import get_channels, get_dms, secret_code_present, final_handle, get_permission_id
from src.auth_helpers import generateOTP, verify_token_logout, verify_login, handle_present, remove_non_alnum
from src.function_helpers import verify_token, verify_email, get_decoded_token, get_user_store
from src.function_helpers import get_channel_store, get_dm_store
from src.helpers import generate_new_session_id, generate_jwt, decode_jwt, hash
from src.upload_photos_helper import get_default_img_url
from src.error import InputError, AccessError
from src.data_store import data_store

import json
import smtplib

# ----------------------- Implementation ----------------------- #
# ----------------------- Implementation ----------------------- #

def auth_login_v1(email, password):
    """
    Description:
        This function will return true if the user enters
        the correct email and password for logging in

    Arguments:
        Email      - string - This is the email of the user which is unique for everyone.
        Password   - string - This is the password of the user which will help him in logging in.

    Exceptions:
        InputError - Occurs when a person leaves an empty string in any of the fields.
        InputError - Occurs when a persons email or password is a wrong input.

    Return Value:
        Returns { 'auth_user_id' : auth_user_id, 'token': 'An encoded string' } if there are no InputErrors.
    """

    user_details = get_user_store()

    auth_user_id = verify_login(user_details,email,password)
    session_id = generate_new_session_id()

    user_details[auth_user_id - 1]['session_list'].append(session_id)
    username = user_details[auth_user_id - 1]['token']

    return {
        'auth_user_id': auth_user_id,
        'token': generate_jwt(username,session_id),
    }

def auth_register_v1(email, password, name_first, name_last):
    """
    Description:
        This function will register a new user and add its details
        in data_store, which will then be accessible for other functions

    Arguments:
        Email      - string - This is the email of the user which is unique for everyone.
        Password   - string - This is the password of the user which will help him in logging in.
        name_first - string - This is the first name of the user who is registering.
        name_last  - string - This is the last name of the user who is registering.

    Exceptions:
        InputError - Occurs when a person leaves an empty string in any of the fields.
        InputError - Occurs when a persons email is of the wrong format.
        InputError - Occurs when the password or name_first or name_last length is not correct.
        InputError - Occurs when a user is already registered and is registering again.

    Return Value:
        Returns { 'auth_user_id' : auth_user_id, 'token': 'An encoded string' } if there are no InputErrors.
    """

    user_details = get_user_store()

    checker(user_details,email,password,name_first,name_last)

    session_id = generate_new_session_id()

    handle_str = create_user_handle(name_first,name_last)
    handle_str = final_handle(user_details, handle_str)

    auth_user_id = len(user_details) + 1
    permission_id = get_permission_id(auth_user_id)

    user_details.append({
        'token' : str(auth_user_id),
        'auth_user_id' : auth_user_id,
        'email' : email,
        'password' : hash(password),
        'name_first' : name_first,
        'name_last' : name_last,
        'handle_str' : handle_str,
        'profile_img_url': get_default_img_url(auth_user_id),
        'permission_id' : permission_id,
        'session_list':[session_id],
        'is_removed': False
    })

    return {
        'auth_user_id': auth_user_id,
        'token': generate_jwt(str(auth_user_id),session_id),
    }

def auth_logout_v1(token):
    """
    Description:
        This function will log a registered user out of its session which we will
        decode from the token that will be passed to us as a parameter
    Arguments:
        token       - Helps in identiying the user in a secure way and verifying the users
                     session_id
    Exceptions:
        AccessError - When a token passed is not able to verify the registered user.
                      (Meaning the user is not registered or a session_id is invalid)
    Return Value:
        Returns {} if there are no AccessErrors.
    """
    decoded_token = get_decoded_token(token)
    user_details = get_user_store()

    verify_token_logout(decoded_token, user_details)

    return ({})

def auth_passwordreset_request_v1(email): # pragma: no cover
    """
    Description:
        This function will make a password reset request by send a verification email
        to the user
    Arguments:
        email       - To send the email to the user if the user is registered
    Exceptions:
        No Exceptions for privacy reasons
    Return Value:
        Returns {}
    """
    user_details = get_user_store()
    if not verify_email(user_details, email):
        return {}

    initial_object = data_store.get()
    password_reset_user = initial_object['password_reset']

    gmail_user = 'fifteendodo@gmail.com'
    gmail_password = 'f15bdodo123'

    SECRET_CODE = generateOTP()
    while secret_code_present(SECRET_CODE, password_reset_user):
        SECRET_CODE = generateOTP()


    sent_from = gmail_user
    to = [email]
    body = f'Your password reset code is {SECRET_CODE}'

    email_text = f"{body}"

    try:
        smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        smtp_server.ehlo()
        smtp_server.login(gmail_user, gmail_password)
        smtp_server.sendmail(sent_from, to, email_text)
        smtp_server.close()

        flag = 0

        for user in password_reset_user:
            if user['email'] == email:
                flag = 1
                user['secret_code'] = SECRET_CODE
        if flag == 0:
            temp = {'email':email, 'secret_code':SECRET_CODE}
            password_reset_user.append(temp)

    except Exception:
        pass
    return {}

def auth_passwordreset_reset_v1(reset_code, new_password): # pragma: no cover
    """
    Description:
        This function will reset the password of the user
    Arguments:
        reset_code     - In the email sent to the user
        new_password   - The new password of the user
    Exceptions:
        InputError     - When the reset password is wrong
        InputError     - When the new password length is not correct
    Return Value:
        Returns {}
    """
    if len(new_password) < 6:
        raise InputError(description="length of password is not right")
    initial_object = data_store.get()
    password_reset_user = initial_object['password_reset']
    user_details = get_user_store()

    flag = 0

    for user in password_reset_user:
        if int(user['secret_code']) == int(reset_code):
            flag = 1
            email = user['email']
            password_reset_user.remove(user)

    if flag == 0:
        raise InputError(description="Incorrect Reset code")

    for user in user_details:
        if user['email'] == email:
            user['password'] =  hash(new_password)

    return {}

def search_v1(token, query_str):
    """
    Description:
        This function will search in all channels and dms for a string
        or sub string "query_str"
    Arguments:
        token          - Used to identify the person making the request
        query_str      - The new query
    Exceptions:
        AccessError    - If the token is incorrect
    Return Value:
        Returns {'messages': return_value}
    """
    decoded_token = get_decoded_token(token)
    user_details = get_user_store()

    verify_token(decoded_token, user_details)

    dm_details = get_dm_store()
    channel_details = get_channel_store()

    user_id = int(decoded_token['username'])

    channels = get_channels(user_id, channel_details)
    dms = get_dms(user_id, dm_details)

    search_list = []

    search_list = list_channel_update(search_list, query_str, channels)
    search_list = list_dm_update(search_list, query_str, dms)

    return search_list

# ----------------------- Implementation ----------------------- #
# ----------------------- Implementation ----------------------- #
