# from src.channels import channels_create_v1
# from src.config import url
# from json import dumps
# from flask import Flask, request
# from src.data_store import data_store
# from src.error import InputError,AccessError
# from src.server import APP
# from src.helpers import decode_jwt
# #from src.server import save_user_data


# def find_auth_id(token):
#     initial_object = data_store.get()
#     user_details = initial_object['users']
    
#     for i in user_details:
#         if i['auth_user_id'] == decode_jwt(token):
#             return decode_jwt(token)
#     return None



# @APP.route("/channels/create/v2",methods = ['POST'])
# def create_channel():
#     request_data = request.get_json()
#     # print(request_data['token'])
#     user_token = request_data['token']

#     user_id = find_auth_id(user_token)
    
#     if user_id == None:
#         raise AccessError

#     # save_users_data()

#     return_id = channels_create_v1(user_id,request_data['name'],request_data['is_public'])


#     return dumps(return_id)


