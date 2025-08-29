import argparse
import logging
import os
import sys
import client
from client import assignment
from client.common import messages
from datetime import datetime
from client import exceptions as ex
from client.utils.printer import print_error
LOGGING_FORMAT = '%(asctime)s | %(levelname)s | %(filename)s:%(lineno)d | %(message)s'
logging.basicConfig(format=LOGGING_FORMAT)
log = logging.getLogger('client')   # Get top-level logger

CLIENT_ROOT = os.path.dirname(client.__file__)


def parse_input(command_input=None):
    """Parses command line input.
    
    """
    parser = argparse.ArgumentParser(
        prog='python3 ok',
        description=__doc__,
        usage='%(prog)s [--help] [options]',
        formatter_class=argparse.RawDescriptionHelpFormatter)
    
    testing = parser.add_argument_group('running tests')
    testing.add_argument('-q', '--question', type=str, action='append',
                        help="run tests for a specific question")
    testing.add_argument('-u', '--unlock', action='store_true',
                        help="unlock tests interactively")
    testing.add_argument('-v', '--verbose', action='store_true',
                        help="show all tests (not just passing tests) up to failing line (if any)")
    
    # Debug information
    debug = parser.add_argument_group('ok developer debugging options')
    debug.add_argument('--version', action='store_true',
                        help="print the version number and exit")
    debug.add_argument('--tests', action='store_true',
                        help="display a list of all available tests")
    debug.add_argument('--debug', action='store_true',
                        help="show debugging output")

    # Grading
    grading = parser.add_argument_group('grading options')
    grading.add_argument('--lock', action='store_true',
                        help="lock the tests in a directory")
    grading.add_argument('--score', action='store_true', default=False, 
                        help="score the assignment")
    grading.add_argument('--score-out', type=str,
                        nargs='?', const=None, default=None,
                        help="write scores to a file. Stdout if none")
    grading.add_argument('--config', type=str,
                        help="use a specific configuration file")
    grading.add_argument('--reconfigure-user', action='store_true',
                         help="reconfigure user settings")

    return parser.parse_args(command_input)

def main():
    """Run all relevant aspects of ok.py."""
    args = parse_input()
    log.setLevel(logging.DEBUG if args.debug else logging.ERROR)
    log.debug(args)
    try:
        assign = None
        assign = assignment.load_assignment(args.config, args)
        retry = True
        while retry:
            retry = False
            # TODO(Willlin): double email history check
            #       add method to change the email
            #       shall we need a way to get signiture to identify the machine?
            msgs = messages.Messages()
            msgs['username'] = assign.get_student_info('username')
            msgs['email'] = assign.get_student_info('email')
            # In this loop all the registered protocols will be launched.
            # But only those configured to launch in args will actually 
            # have some effect. Others literally do nothing.
            for name, proto in assign.protocol_map.items():
                log.info('Execute {}.run()'.format(name))
                proto.run(msgs)
            msgs['timestamp'] = str(datetime.now())
    except ex.LoadingException as e:
        log.warning('Assignment could not load', exc_info=True)
        print_error('Error loading assignment: ' + str(e))
    except ex.OkException as e:
        log.warning('General OK exception occurred', exc_info=True)
        print_error('Error: ' + str(e))
    except KeyboardInterrupt:
        log.info('KeyboardInterrupt received.')
    finally:
        if assign:
            assign.dump_tests()

if __name__ == '__main__':
    main()