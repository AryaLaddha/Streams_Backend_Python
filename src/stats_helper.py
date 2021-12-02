from src.data_store import data_store
from src.channels import find_auth_id
import datetime
from datetime import timezone

'''
Returns the number of channel joined by the user with the given token

Arguments:
    token - string - token of the user to report channels_joined
    ...

Return Value:
    channel_joined_count - int - Number of channels joined by the user.
'''
def number_of_channels_joined(token):
    channel_joined_count = 0
    auth_id = find_auth_id(token)
    initial_object = data_store.get()
    channel_details = initial_object['channels']
    for channel in channel_details:
        for user_id in channel['all_user_ids']:
            if auth_id == user_id:
                channel_joined_count += 1
    return channel_joined_count 
    
'''
Returns the number of channel joined by the user with the given auth_id

Arguments:
    auth_id - int - auth_id of the user to report channels_joined
    ...

Return Value:
    channel_joined_count - int - Number of channels joined by the user.
'''
def number_of_channels_joined_id(auth_id):
    channel_joined_count = 0
    initial_object = data_store.get()
    channel_details = initial_object['channels']
    for channel in channel_details:
        for user_id in channel['all_user_ids']:
            if auth_id == user_id:
                channel_joined_count += 1
    return channel_joined_count 
     
     
'''
Returns the number of dms joined by the user with the given token

Arguments:
    token - string - token of the user to report dms_joined
    ...

Return Value:
    dm_joined_count - int - Number of dms joined by the user.
'''  
def number_of_dms_joined(token):
    dm_joined_count = 0
    auth_id = find_auth_id(token)
    initial_object = data_store.get()
    dm_details = initial_object['dms']
    for dm in dm_details:
        for user_id in dm['u_ids']:
            if auth_id == user_id:
                dm_joined_count += 1
    return dm_joined_count

'''
Returns the number of dms created by the user with the given token

Arguments:
    token - string - token of the user to report dms_created
    ...

Return Value:
    dm_created_count - int - Number of dms created by the user.
'''      
def number_of_dms_created(token):
    dm_created_count = 0
    auth_id = find_auth_id(token)
    initial_object = data_store.get()
    dm_details = initial_object['dms']
    for dm in dm_details:
        if auth_id == dm['creator']:
            dm_created_count += 1
    return dm_created_count

'''
Returns the number of dms created by the user with the given auth_id

Arguments:
    auth_id - int - auth_id of the user to report dms_created
    ...

Return Value:
    dm_created_count - int - Number of dms created by the user.
'''     
def number_of_dms_created_id(auth_id):
    dm_created_count = 0
    initial_object = data_store.get()
    dm_details = initial_object['dms']
    for dm in dm_details:
        if auth_id == dm['creator']:
            dm_created_count += 1
    return dm_created_count

'''
Returns the number of dms joined by the user with the given auth_id

Arguments:
    auth_id - int - auth_id of the user to report dms_joined
    ...

Return Value:
    dm_joined_count - int - Number of dms joined by the user.
'''   
def number_of_dms_joined_id(auth_id):
    dm_joined_count = 0
    initial_object = data_store.get()
    dm_details = initial_object['dms']
    for dm in dm_details:
        for user_id in dm['u_ids']:
            if auth_id == user_id:
                dm_joined_count += 1
    return dm_joined_count
    

'''
Returns the total number of channels that exist

Return Value:
    all_channels - int - Total number of channels.
'''   
def total_channels():
    all_channels = 0
    initial_object = data_store.get()
    channel_details = initial_object['channels']
    for channel in channel_details:
        assert channel != None
        all_channels += 1
    return all_channels

'''
Returns the total number of channels that exist

Return Value:
    total_channels_exist - int - Total number of channels that exist at one point.
'''      
def total_channels_exist():
    total_channels_exist = 0
    initial_object = data_store.get()
    channel_details = initial_object['channels']
    for channel in channel_details:
        assert channel != None
        total_channels_exist += 1
    return total_channels_exist

'''
Returns the total number of dms that exist

Return Value:
    total_dms_exist - int - Total number of dms that exist at one point.
''' 
def total_dms_exist():
    total_dms_exist = 0
    initial_object = data_store.get()
    dm_details = initial_object['dms']
    for dm in dm_details:
        assert dm != None
        total_dms_exist += 1
    return total_dms_exist
 
'''
Returns the total number of messages that exist

Return Value:
    total_messages_exist - int - Total number of dms that exist at one point.
'''     
def total_messages_exist():
    total_messages_exist = 0
    initial_object = data_store.get()
    channel_details = initial_object['channels']
    for channel in channel_details:
        for message in channel['messages']:
            assert message != None
            total_messages_exist += 1
    return total_messages_exist

'''
Returns the total number of dms that exist for a particular user

Arguments:
    token - string - token of the user whose total dms we need to returned
    
Return Value:
    total_dms - int - Total number of dms that the given user has joined
'''    
def total_dms(token):
    total_dms = 0
    initial_object = data_store.get()
    dm_details = initial_object['dms']
    for dm in dm_details:
        assert dm != None
        total_dms += 1
    return total_dms

'''
Returns the total number of messages that exist for a particular user

Arguments:
    token - string - token of the user whose total dms we need to returned
    
Return Value:
    total_messages - int - Total number of messages that the given user has sent
'''    
def total_messages(token):
    total_messages = 0
    initial_object = data_store.get()
    channel_details = initial_object['channels']
    for channel in channel_details:
        for message in channel['messages']:
            assert message != None
            total_messages += 1
    return total_messages
    
'''
Returns the involvement rate of the user given by the token

Arguments:
    token - string - token of the user whose total dms we need to returned
    
Return Value:
    involvement_rate - float - Involvement rate of the user
'''      
def calculate_involvement_rate(token):
    numerator = number_of_channels_joined(token) + get_current_messages_count(token) + number_of_dms_created(token) + number_of_dms_joined(token)
    denominator = total_dms(token) + total_messages(token) + total_channels()
    if denominator == 0:
        return 0
    involvement_rate = numerator/denominator
    if involvement_rate > 1:
        involvement_rate = 1
    return round(involvement_rate, 3)
    
'''
Returns the total number of users of Streams

Arguments:
    token - string - token of an authorised user
    
Return Value:
    total_users - int - Total number of users
'''       
def calculate_total_users(token):
    total_users = 0
    initial_object = data_store.get()
    user_details = initial_object['users']
    for user in user_details:
        assert user != None
        total_users += 1
    return total_users
    
'''
Returns the number of users that have joined atleast one channel or dm

Return Value:
    total_users - int - Number of users that have joined atleast one channel or dm
'''         
def calculate_joined_atleast_one_channel_or_dm():
    total_users = 0
    initial_object = data_store.get()
    user_details = initial_object['users']
    for user in user_details:
        auth_id = user['auth_user_id']
        if number_of_channels_joined_id(auth_id) > 0 or number_of_dms_joined_id(auth_id) > 0:
            total_users += 1
    return total_users    
    
'''
Returns the workspace utilisation of streams

Arguments:
    token - string - token of authorised user

Return Value:
    workspace utlisation - float
'''     
def calculate_workspace_utilisation(token):
    return calculate_joined_atleast_one_channel_or_dm()/calculate_total_users(token)
    
'''
Returns the current time (UTC Timezone)

Return Value:
    timestamp - int - timstamp for current time
'''     
def get_time():
    dt = datetime.datetime.now()
    timestamp = (dt.replace(tzinfo=timezone.utc).timestamp())  
    return round(timestamp)  
    
'''
When called appends the channels_joined entry for that particular user

Arguments:
    token - string - token of the user whose activity we want to update

'''     
def update_user_activity_channels(token):
    auth_id = find_auth_id(token)
    initial_object = data_store.get()    
    user_details = initial_object['users']
    for user in user_details:
        if user['auth_user_id'] == auth_id:
            new_activity = {'num_channels_joined': number_of_channels_joined(token), 'time_stamp': get_time()}
            user['channels_joined'].append(new_activity)
            data_store.set(initial_object)

'''
When called appends the channels_joined entry for that particular user

Arguments:
    auth_id - int - auth_id of the user whose activity we want to update

'''  
def update_user_activity_channels_id(auth_id):
    initial_object = data_store.get()    
    user_details = initial_object['users']
    for user in user_details:
        if user['auth_user_id'] == auth_id:
            new_activity = {'num_channels_joined': number_of_channels_joined_id(auth_id), 'time_stamp': get_time()}
            user['channels_joined'].append(new_activity)
            data_store.set(initial_object)
            
'''
When called appends the dms_joined entry for that particular user

Arguments:
    token - string - token of the user whose activity we want to update

'''  
def update_user_activity_dms(token):
    auth_id = find_auth_id(token)
    initial_object = data_store.get()    
    user_details = initial_object['users']
    for user in user_details:
        if auth_id == user['auth_user_id']:
            new_activity = {'num_dms_joined': number_of_dms_joined(token) + number_of_dms_created(token), 'time_stamp': get_time()}
            user['dms_joined'].append(new_activity)
            data_store.set(initial_object)

'''
When called appends the dms_joined entry for that particular user

Arguments:
    auth_id - int - auth_id of the user whose activity we want to update

'''  
def update_user_activity_dms_id(auth_id):
    initial_object = data_store.get()    
    user_details = initial_object['users']
    for user in user_details:
        if auth_id == user['auth_user_id']:
            new_activity = {'num_dms_joined': number_of_dms_joined_id(auth_id) + number_of_dms_created_id(auth_id), 'time_stamp': get_time()}
            user['dms_joined'].append(new_activity)
            data_store.set(initial_object)

'''
When called appends the num_messages_sent entry for that particular user

Arguments:
    token - string - token of the user whose activity we want to update

'''  
def update_user_activity_messages(token):
    auth_id = find_auth_id(token)
    initial_object = data_store.get()    
    user_details = initial_object['users']
    for user in user_details:
        if auth_id == user['auth_user_id']:
            new_activity = {'num_messages_sent': user['num_messages_sent'] + 1, 'time_stamp': get_time()}
            user['messages_sent'].append(new_activity)
            user['num_messages_sent'] += 1
            data_store.set(initial_object)

'''
When called appends the num_messages_sent entry for that particular user

Arguments:
    auth_id - int - auth_id of the user whose activity we want to update

'''              
def update_user_activity_messages_id(auth_id):
    initial_object = data_store.get()    
    user_details = initial_object['users']
    for user in user_details:
        if auth_id == user['auth_user_id']:
            new_activity = {'num_messages_sent': user['num_messages_sent'] + 1, 'time_stamp': get_time()}
            user['messages_sent'].append(new_activity)
            user['num_messages_sent'] += 1
            data_store.set(initial_object)

'''
Get the entire channels activity for a user

Arguments:
    token - string - token of the user whose activity we want to update

Returns:
    user['channels_joined'] - List - List of dictionaries with each entry an updated activity 
'''     
def get_channels_activity(token):
    auth_id = find_auth_id(token)
    initial_object = data_store.get()
    user_details = initial_object['users']
    for user in user_details:
        if auth_id == user['auth_user_id']:
            return user['channels_joined']


'''
Get the entire dms activity for a user

Arguments:
    token - string - token of the user whose activity we want to update

Returns:
    user['dms_joined'] - List - List of dictionaries with each entry an updated activity 
'''               
def get_dms_activity(token):
    auth_id = find_auth_id(token)
    initial_object = data_store.get()
    user_details = initial_object['users']
    for user in user_details:
        if auth_id == user['auth_user_id']:
            return user['dms_joined']

'''
Get the entire messages activity for a user

Arguments:
    token - string - token of the user whose activity we want to update

Returns:
    user['messages_sent'] - List - List of dictionaries with each entry an updated activity 
'''               
def get_messages_activity(token):
    auth_id = find_auth_id(token)
    initial_object = data_store.get()
    user_details = initial_object['users']
    for user in user_details:
        if auth_id == user['auth_user_id']:
            return user['messages_sent']

'''
Initialises the user activity for channels joined

Arguments:
    token - string - token of the user whose activity we want to update

'''    
def initialise_user_activity_channels(token):
    initial_object = data_store.get()
    auth_id = find_auth_id(token)
    user_detail = initial_object['users']
    for user in user_detail:
        if auth_id == user['auth_user_id']:
            user['channels_joined'] = []
            user['channels_joined'].append({'num_channels_joined': 0, 'time_stamp': get_time()})
            data_store.set(initial_object)

'''
Initialises the user activity for messages sent

Arguments:
    token - string - token of the user whose activity we want to update

'''    
def initialise_user_activity_messages(token):
    initial_object = data_store.get()
    auth_id = find_auth_id(token)
    user_detail = initial_object['users']
    for user in user_detail:
        if auth_id == user['auth_user_id']:
            user['messages_sent'] = []
            user['messages_sent'].append({'num_messages_sent': 0, 'time_stamp': get_time()})
            user['num_messages_sent'] = 0
            data_store.set(initial_object)

'''
Initialises the user activity for dms joined

Arguments:
    token - string - token of the user whose activity we want to update

'''    
def initialise_user_activity_dms(token):
    initial_object = data_store.get()
    auth_id = find_auth_id(token)
    user_detail = initial_object['users']
    for user in user_detail:
        if auth_id == user['auth_user_id']:
            user['dms_joined'] = []
            user['dms_joined'].append({'num_dms_joined': 0, 'time_stamp': get_time()})
            data_store.set(initial_object)

'''
Update the activity for everyone in a dm with the given dm_id

Arguments:
    dm_id - int - id of the dm

'''        
def update_activity_for_all_in_dm(dm_id):
    initial_object = data_store.get()
    dms = initial_object['dms']
    users = initial_object['users']
    for dm in dms:
        if dm['dm_id'] == dm_id:
            for u_id in dm['u_ids']:
                new_activity = {'num_dms_joined': number_of_dms_joined_id(u_id) - 1 + number_of_dms_created_id(u_id), 'time_stamp': get_time()}
                for user in users:
                    if u_id == user['auth_user_id']:
                        user['dms_joined'].append(new_activity)
                        data_store.set(initial_object)

'''
Update the activity for everyone in a dm with the given dm_id

Arguments:
    dm_id - int - id of the dm

'''   
def update_remove_dm_activity_for_creator(dm_id):
    initial_object = data_store.get()
    dms = initial_object['dms']
    users = initial_object['users']
    for dm in dms:
        if dm['dm_id'] == dm_id:
            u_id = dm['creator']
            new_activity = {'num_dms_joined': number_of_dms_joined_id(u_id) + number_of_dms_created_id(u_id) - 1, 'time_stamp': get_time()}
            for user in users:
                if u_id == user['auth_user_id']:
                    user['dms_joined'].append(new_activity)
                    data_store.set(initial_object)
                    

'''
Get the number of messages sent by the suer that currently exist

Arguments:
    token - string - token of the user whose activity we want to update

Returns:
    user['num_messages_sent'] - int - Number of messages sent
'''      
def get_current_messages_count(token):
    auth_id = find_auth_id(token)
    initial_object = data_store.get()    
    user_details = initial_object['users']
    for user in user_details:
        if auth_id == user['auth_user_id']:
            return user['num_messages_sent']
    
'''
Initialises the workspace activity to store workspace stats in it.
'''    
def initialise_workspace_activity():
    initial_object = data_store.get()
    workspace = initial_object['workspace_stats']
    initialised_dictionary = {}
    initialised_dictionary['channels_exist'] = []
    initialised_dictionary['channels_exist'].append({'num_channels_exist': 0, 'time_stamp': get_time()})
    initialised_dictionary['dms_exist'] = []
    initialised_dictionary['dms_exist'].append({'num_dms_exist': 0, 'time_stamp': get_time()})
    initialised_dictionary['messages_exist'] = []
    initialised_dictionary['messages_exist'].append({'num_messages_exist': 0, 'time_stamp': get_time()})
    initialised_dictionary['utilization_rate'] = 0
    workspace.append(initialised_dictionary)
    data_store.set(initial_object) 

'''
Update the number of channels that exist

'''   
def update_channels_exist():
    initial_object = data_store.get()    
    workspace_stats = initial_object['workspace_stats']
    new_activity_channels = {'num_channels_exist': total_channels_exist(), 'time_stamp': get_time()}
    workspace_stats[0]['channels_exist'].append(new_activity_channels)
    data_store.set(initial_object)   

'''
Update the number of dms that exist

'''       
def update_dms_exist():
    initial_object = data_store.get()    
    workspace_stats = initial_object['workspace_stats']
    new_activity = {'num_dms_exist': total_dms_exist(), 'time_stamp': get_time()}
    workspace_stats[0]['dms_exist'].append(new_activity)
    data_store.set(initial_object)   

'''
Update the number of messages that exist

'''      
def update_messages_exist():
    initial_object = data_store.get()    
    workspace_stats = initial_object['workspace_stats']
    new_activity = {'num_messages_exist': total_messages_exist(), 'time_stamp': get_time()}
    workspace_stats[0]['messages_exist'].append(new_activity)
    data_store.set(initial_object) 

'''
Checks if the given user is the first user to register

Returns:
    True - Boolean - If the user if the first to register
    False - Boolean - If the user is not the first one to register
'''    
def is_first_user(auth_id):
    if auth_id == 1:
        return True
    return False
     
