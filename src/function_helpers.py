from src.helpers import generate_new_session_id, generate_jwt, decode_jwt
from src.auth_helpers import get_channels, get_dms
from src.error import InputError, AccessError
from src.data_store import data_store
import math, random
import smtplib
import re
import json

def verify_token(decoded_token, user_details):
    for user in user_details:
        if user['token'] == decoded_token['username'] and decoded_token['session_id'] in user['session_list']:
            if not user['is_removed']:
                return True
    raise AccessError(description="invalid token")

def verify_email(user_details, email): # pragma: no cover
    for user in user_details:
        if user['email'] == email and user['session_list'] == []:
            if not user['is_removed']:
                return True
    return False

def get_decoded_token(token):
    try:
        decoded_token = decode_jwt(token)
        return decoded_token
    except Exception as error:
        raise AccessError(description="invalid token") from error

def get_user_store():
    initial_object = data_store.get()
    return initial_object['users']

def get_channel_store():
    initial_object = data_store.get()
    return initial_object['channels']

def get_dm_store():
    initial_object = data_store.get()
    return initial_object['dms']
