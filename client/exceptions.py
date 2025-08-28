import client
import sys
import logging

log = logging.getLogger(__name__)

class OkException(Exception):
    """Base exception class for OK."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        log.debug('Exception raised: {}'.format(type(self).__name__))
        log.debug('python version: {}'.format(sys.version_info))
        log.debug('okpy version: {}'.format(client.__version__))


class LoadingException(OkException):
    """Exception related to loading assignments."""
    
class SerializeException(LoadingException):
    """Exceptions related to de/serialization."""
    
class ConfigException(OkException):
    """Exceptions related to configuration files."""
    
class ProtocolException(OkException):
    """Exceptions related to protocol errors."""