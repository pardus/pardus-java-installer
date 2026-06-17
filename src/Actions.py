#!/usr/bin/env python3
import subprocess
import sys

import PackageManager

if __name__ == "__main__":
    if len(sys.argv) == 2:
        pid = sys.argv[1]
        # Kill root installing process
        subprocess.run(["kill", "-2", pid])  # SIGINT: -2
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
            proc = subprocess.Popen(cmd)
            code = proc.wait()
            sys.exit(code)
        except KeyboardInterrupt:
            if proc and proc.poll() is None:  # still runs?
                proc.terminate()  # SIGTERM
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()  # SIGKILL
                    sys.exit(1)
        except Exception as e:
            print("Exception happened on process run:", e)
            print(sys.argv)
    else:
        print(f"Not valid command tuple: ({operation},{package},{path})")

    sys.exit(0)
