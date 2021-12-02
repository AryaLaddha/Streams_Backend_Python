from src.data_store import data_store
from src.channels import find_auth_id
from src.channel_owner_helper import already_member, valid_channel

'''Removes a member from the channel

Arguments:
    token(string) - User token 
    channel_id_check(int) - Channel ID to leave 
    ...

Return Value:
    Removes user from the channel is token and channel_id is valid'''

def channel_leave_member(token, channel_id_check):
    user_id_check = find_auth_id(token)
    initial_object = data_store.get()
    channel_details = initial_object['channels']
    for channel in channel_details:
        if channel_id_check == channel['channel_id']:
            for member in channel['all_members']:
                if user_id_check == member['u_id']:
                    channel['all_members'].remove(member)
            for user_id in channel['all_user_ids']:
                if user_id_check == user_id:
                    channel['all_user_ids'].remove(user_id)
    data_store.set(initial_object)
    
'''Removes an owner from the channel

Arguments:
    token(string) - User token 
    channel_id_check(int) - Channel ID to leave 
    ...

Return Value:
    Removes user from the channel is token and channel_id is valid'''
def channel_leave_owner(token, channel_id_check):
    user_id_check = find_auth_id(token)
    initial_object = data_store.get()
    channel_details = initial_object['channels']
    for channel in channel_details:
        if channel_id_check == channel['channel_id']:
            for owner in channel['owner_members']:
                if user_id_check == owner['u_id']:
                    channel['owner_members'].remove(owner)
            for user_id in channel['all_user_ids']:
                if user_id_check == user_id:
                    channel['all_user_ids'].remove(user_id)
            if user_id_check == channel['original_user_id']:
                channel['original_user_id'] = -1
    data_store.set(initial_object)

'''Checks if channel is valid and if user is the owner of the channel

Arguments:
    token(string) - User token 
    channel_id_check(int) - Channel ID to leave 
    ...

Return Value:
    Removes user from the channel is token and channel_id is valid'''    
def leave_channel_valid(token, channel_id_check):
    user_id_check = find_auth_id(token)
    initial_object = data_store.get()
    channel_details = initial_object['channels']
    for channel in channel_details:
        if channel_id_check == channel['channel_id']:
            for owner in channel['owner_members']:
                if user_id_check == owner['u_id']:
                    channel_leave_owner(token, channel_id_check)
                    break
            channel_leave_member(token, channel_id_check)
        

'''Checks if user is a member of the channel

Arguments:
    token(string) - User token 
    channel_id_check(int) - Channel ID to leave 
    ...

Return Value:
    True : User is a member of the channel
    False: If user is not member of the channel''' 
def invalid_access(token, channel_id_check):
    user_id_check = find_auth_id(token)
    if already_member(user_id_check, channel_id_check) == False:
        return True
    return False
        
        
        
