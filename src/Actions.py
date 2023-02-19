#!/usr/bin/python3
import gi

gi.require_version('Gtk', '3.0')
import sys, subprocess

class Action:
    def __init__(self, package) -> None:
        self.package = package
        self.commands = {
            "install": ["apt-get", "install", package, "-yq", "-o", "APT::Status-Fd=1"],
            "remove": ["apt", "purge", package, "-yq"],
            "make-default": ["update-alternatives", "--set", "java", package],
            "update-alternatives-auto": ["update-alternatives", "--auto", "java"],
            "update-and-remove": ["/bin/sh", "-c", "update-alternatives --auto java && apt purge " + package + " -yq"]
        }

    # PROCESS SPAWNING:
    def startProcess(self, params):
        status = subprocess.call(params)
        exit(status)

    def startCommand(self, cmd):
        self.startProcess(self.commands[cmd])

if __name__ == '__main__':
    operation = sys.argv[1]
    package = sys.argv[2]
    act = Action(package)
    act.startCommand(operation)

