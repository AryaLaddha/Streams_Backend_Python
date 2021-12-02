import hashlib
import jwt

SESSION_TRACKER = 0
SECRET = 'F15B_DODO'

def generate_new_session_id():
    """Generates a new sequential session ID

    Returns:
        number: The next session ID
    """
    global SESSION_TRACKER
    SESSION_TRACKER += 1
    return SESSION_TRACKER


def hash(input_string):
    """Hashes the input string with sha256

    Args:
        input_string ([string]): The input string to hash

    Returns:
        string: The hexidigest of the encoded string
    """
    return hashlib.sha256(input_string.encode()).hexdigest()


def generate_jwt(username, session_id=None):
    """Generates a JWT using the global SECRET

    Args:
        username ([string]): The username
        session_id ([string], optional): The session id, if none is provided will
                                         generate a new one. Defaults to None.

    Returns:
        string: A JWT encoded string
    """
    # if session_id is None:
    #     session_id = generate_new_session_id()
    return jwt.encode({'username': username, 'session_id': session_id}, SECRET, algorithm='HS256')


def decode_jwt(encoded_jwt):
    """Decodes a JWT string into an object of the data

    Args:
        encoded_jwt ([string]): The encoded JWT as a string

    Returns:
        Object: An object storing the body of the JWT encoded string
    """
    return jwt.decode(encoded_jwt, SECRET, algorithms=['HS256'])
