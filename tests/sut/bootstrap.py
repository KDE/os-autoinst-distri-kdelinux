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
    type_string('sudo -i\n')
    wait_serial(r'#', timeout=30)

    # stop OSC 3008 escapes screwing with us
    # make it dumb with no readline so assert_script_run will always work in a sane way
    # and so we get good output
    type_string('export TERM=dumb; unset PROMPT_COMMAND; export PS1="# "; set +o emacs +o vi\n')
    wait_serial(r'#', timeout=30)

    # bootstrap the SUT tests
    assert_script_run(f'git clone -b {BRANCH} {REPO_URL} ~/tests')
    assert_script_run('~/tests/sut/bootstrap.sh')

    # go back to the desktop so we don't break any needle tests
    select_console('desktop')

def test_flags(self):
    return {'fatal': 1}
