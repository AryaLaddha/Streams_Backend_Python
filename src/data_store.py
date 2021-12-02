'''
data_store.py

This contains a definition for a Datastore class which you should use to store your data.
You don't need to understand how it works at this point, just how to use it :)

The data_store variable is global, meaning that so long as you import it into any
python file in src, you can access its contents.

Example usage:

    from data_store import data_store

    store = data_store.get()
    print(store) # Prints { 'names': ['Nick', 'Emily', 'Hayden', 'Rob'] }

    names = store['names']

    names.remove('Rob')
    names.append('Jake')
    names.sort()

    print(store) # Prints { 'names': ['Emily', 'Hayden', 'Jake', 'Nick'] }
    data_store.set(store)
'''

## YOU SHOULD MODIFY THIS OBJECT BELOW
initial_object = {
    'notifications' : [
        # {
        #     'u_id' : '',
        #     'notified' : [
        #     {channel_id:'', 'dm_id':'', 'notification_message':''},
        #     {channel_id:'', 'dm_id':'', 'notification_message':''},
        #     ...
        #     ]
        # },
        # {
        #     'u_id' : '',
        #     'notified' : [
        #     {channel_id:'', 'dm_id':'', 'notification_message':''},
        #     {channel_id:'', 'dm_id':'', 'notification_message':''},
        #     ...
        #     ]
        # }
    ],
    'password_reset':[
        #     emails that need resetting
    ],
    'users': [
        # {
        #     'auth_user_id': '',
        #     'name_first' : '',
        #     'name_last':'',
        #     'email':'',
        #     'password':'',
        #     'handle_str':'',
        #     'permission_id':''
        #     ‘session_list’:[]
        #     ‘number_of_messages_sent’: []
        #     ‘user_activity_channels’: []
        #     ‘user_activity_dms’: []
        # }
    ],
 'channels': [
        # {
        #     'channel_id': '',
        #     'name' : '',
        #     'owner_members':[{
        #         'u_id' : '',
        #         'email' : '',
        #         'name_first' : '',
        #         'name_last' : '',
        #         'handle_str' : ''
        #     }],
        #     'all_members':[{
        #         'u_id' : '',
        #         'email' : '',
        #         'name_first' : '',
        #         'name_last' : '',
        #         'handle_str' : ''
        #     }],
        #     'all_user_ids' : [],
        #     'original_user_id' : [],
        #     'is_public':'',
        #     'messages':[{
        #         'message_id': '',
        #         'u_id': '',
        #         'message': '',
        #         'time_created': ''
        #         'react_id': ''
        #         'time_created': ''
        #         ‘is_share_message’:
        #     }]
        #	   ‘is_standup’: ‘’,
        #     ‘standup’ : {
        # 	      ‘message_queue’ : ‘’,
        #        ‘time_finish’ : ‘’
        #	    },
        # 	‘num_message_later’:
        # }
    ],
    'dms' : [
       #{
        #      ‘dm_id’: ‘’,
        #      ‘u_ids’: [],
        #      ‘name’: []
        #      'messages':[{
        #            'message_id': '',
        #             'u_id': '',
        #             'message': '',
        #             'time_created': '',
        #             'reacts': '',
        #             'is_pinned': ''
        #         ‘is_share_message’:
        #     }]
        #       'creator':''
      # num_message_later:
      ],
    'workspace_stats': [

      ]
    }





## YOU SHOULD MODIFY THIS OBJECT ABOVE

class Datastore:
    def __init__(self):
        self.__store = initial_object

    def get(self):
        return self.__store

    def set(self, store):
        if not isinstance(store, dict):
            raise TypeError('store must be of type dictionary')
        self.__store = store

print('Loading Datastore...')

global data_store
data_store = Datastore()
