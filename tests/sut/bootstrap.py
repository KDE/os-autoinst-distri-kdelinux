from testapi import *

REPO_URL = get_var('TEST_REPO', 'https://invent.kde.org/tduck/os-autoinst-distri-kdelinux.git')
BRANCH = get_var('TEST_BRANCH', 'master')

def run(self):
    # log in to the terminal
    select_console('virtio-terminal')
    type_string('\n')
    wait_serial(r"login: ", timeout=30)
    type_string('live' + '\n')
    wait_serial(r'~.*\$', timeout=30)

    # bootstrap the SUT tests
    serial_test.run(f'git clone -b {BRANCH} {REPO_URL} ~/tests')
    serial_test.run('~/tests/sut/bootstrap.sh')

def test_flags(self):
    return {'fatal': 1}
