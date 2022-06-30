#!/usr/bin/env python3

import subprocess
import imgserver
import sys
from pathlib import Path
from os import environ


VIDEODIR = Path("~/Videos").expanduser()


def run():
    caddypr=subprocess.Popen(['caddy run'],shell=True,stderr=subprocess.STDOUT,env=dict(environ, FLIXVIDEODIR=VIDEODIR))
    
    try:
        imgserver.run(VIDEODIR)

    except KeyboardInterrupt:
        print("\nKeyboard interrupt received, exiting.")
        sys.exit(0)


if __name__ == '__main__':
    run()