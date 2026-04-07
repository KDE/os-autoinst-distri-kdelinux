from testapi import *
import sys
from lib.serial_test import SerialTest

class Test(SerialTest):
    script = 'common/bootup.py'
    timeout = 180
