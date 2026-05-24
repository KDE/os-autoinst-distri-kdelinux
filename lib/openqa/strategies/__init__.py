# SPDX-License-Identifier: CC0-1.0
# SPDX-FileCopyrightText: None
from testapi import *
from lib.strategies.kickoff import KickoffOpenStrategy
from lib.strategies.konsole import KonsoleOpenStrategy
from lib.strategies.krunner import KRunnerOpenStrategy
from lib.strategies.tty import TTYOpenStrategy

OPEN_STRATEGIES = {
    'krunner' : KRunnerOpenStrategy(),
    'tty' : TTYOpenStrategy(),
    'konsole' : KonsoleOpenStrategy(),
    'kickoff' : KickoffOpenStrategy()
}