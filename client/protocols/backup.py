from client import exceptions
from client.protocols.common import models
import client
import datetime
import logging
import time
import os
import sys
import pickle

log = logging.getLogger(__name__)

from client.utils.printer import print_warning, print_success, print_error
from client.utils.output import DisableLog

class BackupProtocol(models.Protocol):
    """Without online requests. It is a simplified version of backup"""
    BACKUP_FILE = ".ok_messages"

    def run(self, messages):
        """Record the unlock messages and history

        Args:
            messages (_type_): _description_
        """
        if not self.args.unlock:
            return 
        
        message_list = self.load_messages()


        self.dump_messages(message_list + [messages], messages['email'].strip().split('@')[0] + self.BACKUP_FILE)
        print()

    @classmethod
    def load_messages(cls, file=BACKUP_FILE):
        message_list = []
        try:
            with open(file, 'rb') as fp:
                message_list = pickle.load(fp)
            log.info('Loaded %d backed up messages from %s',
                     len(message_list), file)
        except (IOError, EOFError) as e:
            log.info('Error reading from ' + file + \
                     ', assume nothing backed up')
        return message_list


    @classmethod
    def dump_messages(cls, message_list, file=BACKUP_FILE):
        with open(file, 'wb') as f:
            log.info('Save %d unsent messages to %s', len(message_list),
                     file)

            pickle.dump(message_list, f)
            os.fsync(f)

protocol = BackupProtocol
