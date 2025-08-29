from client import exceptions as ex
from client.sources.ok_test import concept
from client.sources.ok_test import models
from client.sources.common  import importing
import copy
import logging
import os

from client.utils import encryption

log = logging.getLogger(__name__)

SUITES = {
    'concept': concept.ConceptSuite
}

def load(file, parameter, assign):
    """Loads an OK-style test from a specified filepath.

    PARAMETERS:
    file -- str; a filepath to a Python module containing OK-style
            tests.

    RETURNS:
    Test
    """
    filename, ext = os.path.splitext(file)
    if not os.path.isfile(file) or ext != '.py':
        log.info('Cannot import {} as an OK test'.format(file))
        raise ex.LoadingException('Cannot import {} as an OK test'.format(file))

    try:
        test = importing.load_module(file).test
        test = copy.deepcopy(test)
    except Exception as e:
        raise ex.LoadingException('Error importing file {}: {}'.format(file, str(e)))

    name = os.path.basename(filename)
    try:
        return {name: models.OkTest(file, SUITES, assign.endpoint, assign, assign.cmd_args.verbose, **test)}
    except ex.SerializeException as e:
        raise ex.LoadingException('Cannot load OK test {}: {}'.format(file, e))
