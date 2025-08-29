import logging
import os
import pickle
from client import exceptions as ex

log = logging.getLogger(__name__)

CONFIG_DIRECTORY = os.path.join(os.path.expanduser('~'), '.config', 'ok')
CONFIG_FILE = os.path.join(CONFIG_DIRECTORY, 'config.pkl')

def create_config_directory():
    if not os.path.exists(CONFIG_DIRECTORY):
        os.makedirs(CONFIG_DIRECTORY)
    return CONFIG_DIRECTORY

def get_storage(key):
    """Retrieves information from the storage.

    Args:
        key (str): The key of the information to retrieve.

    Returns:
        str: The value associated with the key, or None if not found.
    """
    with open(CONFIG_FILE, 'rb') as fp:
        storage = pickle.load(fp)

    return storage[key]

def get_all_storage():
    """Retrieves all information from the storage.

    Returns:
        dict: A dictionary containing all key-value pairs in the storage.
    """
    try:
        with open(CONFIG_FILE, "rb") as f:
            storage = pickle.load(f)
    except Exception:
        storage = {}

    return storage

def update_storage(key, info):
    if not info:
        raise ex.ConfigException(info)
    create_config_directory()
    storage = get_all_storage()

    storage[key] = info

    with open(CONFIG_FILE, "wb") as f:
        pickle.dump(storage, f)
        
def get_info_from_input(key):
    retry = True
    times = 0
    while retry:
        retry = False
        times += 1
        value = input(f"Please enter your {key}: ")
        try:
            update_storage(key, value)
        except ex.ConfigException as e:
            print(f'Please enter a valid {key}.')
            log.warning(f'Retry {times}, received input: {e}')
    return value

"""Below are contents originally in storage"""
import ctypes
import shelve # persistance
import hmac # security
from client import exceptions as ex

def set_foreign_function_type(func, restype, argtypes):
    if func.argtypes is None:
        func.argtypes = argtypes
        func.restype = restype

# Platform-specific imports
windll = None
try:
    windll = ctypes.windll
    from ctypes.wintypes import BOOL, BOOLEAN, BYTE, DWORD, HANDLE, LARGE_INTEGER, LPCWSTR, LPWSTR, LPVOID, ULONG, WCHAR
    set_foreign_function_type(windll.ktmw32.CreateTransaction, HANDLE, [LPVOID, LPVOID, DWORD, DWORD, DWORD, DWORD, LPWSTR])
    set_foreign_function_type(windll.ktmw32.CommitTransaction, BOOL, [HANDLE])
    set_foreign_function_type(windll.kernel32.MoveFileTransactedW, BOOL, [LPCWSTR, LPCWSTR, ctypes.WINFUNCTYPE(LARGE_INTEGER, LARGE_INTEGER, LARGE_INTEGER, LARGE_INTEGER, DWORD, DWORD, HANDLE, HANDLE, LPVOID), LPVOID, DWORD, HANDLE])
    set_foreign_function_type(windll.kernel32.CloseHandle, BOOL, [HANDLE])
except (AttributeError, ImportError, OSError): pass

##################
# Secure Storage #
##################

SHELVE_FILE = '.ok_storage'
SECURITY_KEY = 'uMWm4sviPK3LyPzgWYFn'.encode('utf-8')

def mac(value):
    mac = hmac.new(SECURITY_KEY, digestmod='md5')
    mac.update(repr(value).encode('utf-8'))
    return mac.hexdigest()

def contains(root, key):
    key = '{}-{}'.format(root, key)
    with shelve.open(SHELVE_FILE) as db:
        return key in db

def store(root, key, value):
    key = '{}-{}'.format(root, key)
    with shelve.open(SHELVE_FILE) as db:
        db[key] = {'value': value, 'mac': mac(value)}
    return value

def get(root, key, default=None):
    if not contains(root, key):
        return default
    key = '{}-{}'.format(root, key)
    with shelve.open(SHELVE_FILE) as db:
        data = db[key]
        if not hmac.compare_digest(data['mac'], mac(data['value'])):
            raise ex.ProtocolException('{} was tampered.  Reverse changes, or redownload assignment'.format(SHELVE_FILE))
    return data['value']

def replace_transactional(source, destination):
    # Like os.replace, but tries to be actually atomic when possible on Windows.
    if windll:
        error_code = 50  # ERROR_NOT_SUPPORTED
        if windll.ktmw32:
            tx = windll.ktmw32.CreateTransaction(None, None, 0, 0, 0, 0, None)
            if tx != HANDLE(-1).value:
                try: error_code = 0 if windll.kernel32.MoveFileTransactedW(source, destination, windll.kernel32.MoveFileTransactedW.argtypes[2](), None, 0x1 | 0x2, tx) and windll.ktmw32.CommitTransaction(tx) else ctypes.GetLastError()
                finally: windll.kernel32.CloseHandle(tx)
            else: error_code = ctypes.GetLastError()
        if error_code:
            raise ctypes.WinError(error_code)
    else:
        raise NotImplementedError("transactional file systems not supported")