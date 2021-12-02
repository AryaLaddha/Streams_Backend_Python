from src.data_store import data_store
from src.user import get_decoded_token, check_details, verify_token
from src.channels import find_auth_id
from src.admin_user import check_global

'''Checks if channel is valid and exists

Arguments:
    channel_id_check(int) - Channel ID to check 
    ...

Return Value:
    True: If channel is valid and exists
    False: If channel is invalid''' 
def valid_channel(channel_id_check):
    initial_object = data_store.get()
    channel_details = initial_object['channels']
    
    for channel in channel_details:
        if channel_id_check == channel['channel_id']:
            return True
    return False
    
'''Checks if user is valid and exists

Arguments:
    user_id_check(int) - User ID to check 
    ...

Return Value:
    True: If user is valid and exists
    False: If user is invalid'''     
def valid_user(user_id_check):
    initial_object = data_store.get()
    all_users = initial_object['users']
    
    for user in all_users:
        if user_id_check == user['auth_user_id']:
            return True
    return False
    
'''Checks if user is a member of the channel

Arguments:
    user_id_check(int) - User ID to check
    channel_id_check(int) - Channel ID to check  
    ...

Return Value:
    True: If user is a member
    False: If user is not a member'''     
def already_member(user_id_check, channel_id_check):
    initial_object = data_store.get()
    channel_details = initial_object['channels']
    
    for channel in channel_details:
        if channel_id_check == channel['channel_id']:
            for user_id in channel['all_user_ids']:
                if user_id_check == user_id:
                    return True
    return False
            
'''Checks if user is an owner of the channel

Arguments:
    user_id_check(int) - User ID to check
    channel_id_check(int) - Channel ID to check 
    ...

Return Value:
    True: If user is an owner of the channel
    False: If user is not an owner'''  
def already_owner(user_id_check, channel_id_check):  
    initial_object = data_store.get()
    channel_details = initial_object['channels']
    
    for channel in channel_details:
        if channel_id_check == channel['channel_id']:
            for owners in channel['owner_members']:
                if user_id_check == owners['u_id']:
                    return True
    return False

'''Checks if the token is valid and if the user is valid

Arguments:
    token(string): Token for the user
    ...

Return Value:
    Calls functions which can raise errors in case an invalid argument is provided. '''           
def check_token_and_user_details(token):
    initial_object = data_store.get()
    user_details = initial_object['users']
    decoded_token = get_decoded_token(token)
    verify_token(decoded_token, user_details)
    
'''Checks if user is the owner of the channel and if the channel is valid

Arguments:
    user_id_check(int) - User ID to check
    channel_id_check(int) - Channel ID to check 
    ...

Return Value:
    True: If user is an owner of the channel and if the channel is valid
    False: If user is not an owner or if the channel is invalid''' 
def unauthorised_user(token, channel_id_check):
    user_id = find_auth_id(token)
    if not already_owner(user_id, channel_id_check):
        if valid_channel(channel_id_check):
            return True
    return False

'''Returns the details of the owner

Arguments:
    user_id_check(int) - User ID to check
    ...

Return Value:
    new_owner_details (Dictionary): Contains data of the owner'''
def owner_details(user_id_check):
    initial_object = data_store.get()
    all_users = initial_object['users']
    for user in all_users:
        if user_id_check == user['auth_user_id']:
            new_owner_details = {'u_id': user['auth_user_id'], 'email': user['email'], 'name_first': user['name_first'], 'name_last': user['name_last'], 'handle_str': user['handle_str']}
    return new_owner_details

'''Adds owner to the channel given by the channel id if the user and the channel is valid

Arguments:
    user_id_check(int) - User ID to check
    channel_id_check(int) - Channel ID to check
    ...

Return Value:
    Adds user as the owner of the channel'''   
def add_owner(user_id_check, channel_id_check):
    initial_object = data_store.get()
    channel_details = initial_object['channels']
    for channel in channel_details:
        if channel_id_check == channel['channel_id']:
            channel['owner_members'].append(owner_details(user_id_check))
    data_store.set(initial_object)

'''Removes owner of the channel given by the channel id if the user and the channel is valid

Arguments:
    user_id_check(int) - User ID to check
    channel_id_check(int) - Channel ID to check
    ...

Return Value:
    Removes the owner of the channel if the channel is valid and the user is valid'''   
def remove_owner(user_id_check, channel_id_check):
    initial_object = data_store.get()
    channel_details = initial_object['channels']
    for channel in channel_details:
        if channel_id_check == channel['channel_id']:
            if user_id_check == channel['original_user_id']:
                channel['original_user_id'] = -1
            for owner in channel['owner_members']:
                if user_id_check == owner['u_id']:
                    channel['owner_members'].remove(owner)
    data_store.set(initial_object)

'''Checks if the channel only has 1 owner

Arguments:
    channel_id_check(int) - Channel ID to check
    ...

Return Value:
    True: If the channel has one owner only
    False: If the channel has more than one owners.'''   
def only_owner(channel_id_check):
    initial_object = data_store.get()
    channel_details = initial_object['channels']
    for channel in channel_details:
        if channel_id_check == channel['channel_id']:
            if len(channel['owner_members']) == 1:
                return True
            return False
            
def is_global_owner(token):
    user_id = find_auth_id(token)
    return check_global(user_id)
    
def global_owner_already_member(token, channel_id_check):
    auth_id = find_auth_id(token)
    return already_member(auth_id, channel_id_check)




             
