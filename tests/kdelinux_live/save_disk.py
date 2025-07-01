from testapi import *

def run(self):
    overlay = '/var/lib/openqa/pool/1/raid/hd0-overlay0'
    target = '/var/lib/openqa/factory/hdd/installed.qcow2'
    script_run(f"nice ionice qemu-img convert -c -W -O qcow2 {overlay} {target}")
