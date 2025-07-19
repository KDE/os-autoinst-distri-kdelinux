from lib.strategies.kickoff import KickoffOpenStrategy
from lib.strategies.konsole import KonsoleOpenStrategy
from lib.strategies.krunner import KRunnerOpenStrategy
from lib.strategies.tty import TTYOpenStrategy
from testapi import *

OPEN_STRATEGIES = {
    'krunner' : KRunnerOpenStrategy(),
    'tty' : TTYOpenStrategy(),
    'konsole' : KonsoleOpenStrategy(),
    'kickoff' : KickoffOpenStrategy()
}