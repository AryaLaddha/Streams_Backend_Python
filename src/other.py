from src.data_store import data_store

def clear_v1():
    store = data_store.get()
    store['users'] = []
    store['channels'] = []
    store['dms'] = []
    store['password_reset'] = []
    store['notifications'] = []
    store['workspace_stats'] = []
    data_store.set(store)
