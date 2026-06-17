#!/usr/bin/env python3
import os
import subprocess
import sys

import PackageManager

if __name__ == "__main__":
    if len(sys.argv) == 3:
        operation = sys.argv[1]
        package = sys.argv[2]
        path = None
    elif len(sys.argv) == 4:
        operation = sys.argv[1]
        package = sys.argv[2]
        path = sys.argv[3]
    else:
        print("Usage: ./Actions.py operation package (path)")
        sys.exit(1)

    cmd = PackageManager.get_command(operation, package=package, path=path)
    print(f"Action Command: {cmd}")
    if cmd:
        try:
            subprocess.run(cmd)
        except Exception as e:
            print("Exception happened on process run:", e)
            print(sys.argv)
    else:
        print(f"Not valid command tuple: ({operation},{package},{path})")

    sys.exit(0)
