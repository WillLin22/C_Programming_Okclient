import uuid

import client
from client import exceptions as ex
from client.sources.common import core
from client.utils.storage import *
from client.utils import format
import collections
import glob
import importlib
import json
import logging
import os


log = logging.getLogger(__name__)

CONFIG_EXTENSION = '*.ok'

def load_assignment(filepath=None, cmd_args=None):
    config = _get_config(filepath)
    if not isinstance(config, dict):
        raise ex.LoadingException('Config should be a dictionary')
    if cmd_args is None:
        cmd_args = Settings()
    return Assignment(cmd_args, **config)


def _get_config(config):
    if config is None:
        configs = glob.glob(CONFIG_EXTENSION)
        if len(configs) > 1:
            raise ex.LoadingException('\n'.join([
                'Multiple .ok files found:',
                '    ' + ' '.join(configs),
                "Please specify a particular assignment's config file with",
                '    python3 ok --config <config file>'
            ]))
        elif not configs:
            raise ex.LoadingException('No .ok configuration file found')
        config = configs[0]
    elif not os.path.isfile(config):
        raise ex.LoadingException(
                'Could not find config file: {}'.format(config))

    try:
        with open(config, 'r') as f:
            result = json.load(f, object_pairs_hook=collections.OrderedDict)
    except IOError:
        raise ex.LoadingException('Error loading config: {}'.format(config))
    except ValueError:
        raise ex.LoadingException(
            '{0} is a malformed .ok configuration file. '
            'Please re-download {0}.'.format(config))
    else:
        log.info('Loaded config from {}'.format(config))
        return result
    
    
class Settings:
    """Command-line arguments that are set programmatically instead of by
    parsing the command line.
    """
    def __init__(self, **kwargs):
        from client.ok import parse_input
        self.args = parse_input([])
        self.update(**kwargs)

    def __getattr__(self, attr):
        return getattr(self.args, attr)

    def update(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self.args, k, v)

    def __repr__(self):
        cls = type(self).__name__
        return "{0}({1})".format(cls, vars(self.args))



class Assignment(core.Serializable):
    name = core.String()
    endpoint = core.String(optional=True, default='') # currently not used
    tests = core.Dict(keys=str, values=str, ordered=True)
    default_tests = core.List(type=str, optional=True)
    protocols = core.List(type=str, optional=True)

    ############
    # Internal #
    ############

    _TESTS_PACKAGE = 'client.sources'
    _PROTOCOL_PACKAGE = 'client.protocols'

    _PROTOCOLS = [
        "lock",
        "unlock"
    ]
    def __init__(self, args, **fields):
        self.cmd_args = args
        self.test_map = collections.OrderedDict()
        self.protocol_map = collections.OrderedDict()
        
    def get_student_email(self):
        """Attempts to get the student's email. Returns the email. If None, an error will be given and exception will be raised"""

        log.info("Attempting to get student email")
        
        try:
            user_email = get_storage()
        except Exception as e:
            user_email = get_email()
        return user_email

    def post_instantiation(self):
        self._print_header()
        self._load_tests()
        self._load_protocols()
        self.specified_tests = self._resolve_specified_tests(
            self.cmd_args.question)

    def is_empty_init(self, path):
        if os.path.basename(path) != '__init__.py':
            return False

        with open(path) as f:
            contents = f.read()

        return contents.strip() == ""
        
    def _resolve_specified_tests(self, questions, all_tests=False):
        """For each of the questions specified on the command line,
        find the test corresponding that question.

        Questions are preserved in the order that they are specified on the
        command line. If no questions are specified, use the entire set of
        tests.
        """
        if not questions and not all_tests \
                and self.default_tests != core.NoValue \
                and len(self.default_tests) > 0:
            log.info('Using default tests (no questions specified): '
                     '{}'.format(self.default_tests))
            bad_tests = sorted(test for test in self.default_tests if test not in self.test_map)
            if bad_tests:
                error_message = ("Required question(s) missing: {}. "
                    "This often is the result of accidentally deleting the question's doctests or the entire function.")
                raise ex.LoadingException(error_message.format(", ".join(bad_tests)))
            return [self.test_map[test] for test in self.default_tests]
        elif not questions:
            log.info('Using all tests (no questions specified and no default tests)')
            return list(self.test_map.values())
        elif not self.test_map:
            log.info('No tests loaded')
            return []

        specified_tests = []
        for question in questions:
            if question not in self.test_map:
                raise ex.InvalidTestInQuestionListException(list(self.test_map), question)

            log.info('Adding {} to specified tests'.format(question))
            if question not in specified_tests:
                specified_tests.append(self.test_map[question])
        return specified_tests

    def _print_header(self):
        if getattr(self.cmd_args, 'autobackup_actual_run_sync', False):
            return
        format.print_line('=')
        print('Assignment: {}'.format(self.name))
        print('OK, version {}'.format(client.__version__))
        format.print_line('=')
        print()

    def _load_tests(self):
        """Loads all tests specified by test_map."""
        log.info('Loading tests')
        for file_pattern, sources in self.tests.items():
            for source in sources.split(","):
                # Separate filepath and parameter
                if ':' in file_pattern:
                    file_pattern, parameter = file_pattern.split(':', 1)
                else:
                    parameter = ''

                for file in sorted(glob.glob(file_pattern)):
                    if self.is_empty_init(file):
                        continue
                    try:
                        module = importlib.import_module(self._TESTS_PACKAGE + '.' + source)
                    except ImportError:
                        raise ex.LoadingException('Invalid test source: {}'.format(source))

                    test_name = file
                    if parameter:
                        test_name += ':' + parameter

                    self.test_map.update(module.load(file, parameter, self))

                    log.info('Loaded {}'.format(test_name))
    def dump_tests(self):
        """Dumps all tests, as determined by their .dump() method.

        PARAMETERS:
        tests -- dict; file -> Test. Each Test object has a .dump method
                 that takes a filename and serializes the test object.
        """
        log.info('Dumping tests')
        for test in self.test_map.values():
            try:
                test.dump()
            except ex.SerializeException as e:
                log.warning('Unable to dump {}: {}'.format(test.name, str(e)))
            else:
                log.info('Dumped {}'.format(test.name))
        
    def _load_protocols(self):
        log.info('Loading protocols')
        for proto in self._PROTOCOLS:
            module = importlib.import_module(self._PROTOCOL_PACKAGE + '.' + proto)
            self.protocol_map[proto] = module.protocol(self.cmd_args, self)
            log.info('Loaded protocol "{}"'.format(proto))
