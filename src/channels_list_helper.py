from src.data_store import data_store
from src.channels import find_auth_id
from src.channels import channels_list_v1, channels_listall_v1

'''Lists all channels that the user is a part of given a valid token

Arguments:
    Token(string): User token that we want the list of channels for 
    ...

Return Value:
    Dictionary containing a list of all channels that the user is a part of'''   
def get_user_channels(token):
    user_id = find_auth_id(token)
    return channels_list_v1(user_id)

'''Lists all channels public or private that have been created

Arguments:
    Token(string): User token 
    ...

Return Value:
    Dictionary containing a list of all channels '''    
def get_all_channels(token):
    user_id = find_auth_id(token)
    return channels_listall_v1(user_id)
