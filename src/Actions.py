#!/usr/bin/env python3

import gi

gi.require_version('Gtk', '3.0')
import sys, subprocess

operation = sys.argv[1]
package = sys.argv[2]

commands = {
    "install": ["apt", "install", package, "-yq", "-o", "APT::Status-Fd=1"],
    "remove": ["apt", "remove", "--purge", package, "-yq"],
    "make-default": ["update-alternatives", "--set", "java", package],
    "make-default-javaws": ["update-alternatives", "--set", "javaws", package],
    "update-alternatives-auto": ["update-alternatives", "--auto", "java"],
    "update-and-remove": ["/bin/sh", "-c", "update-alternatives --auto java && apt purge " + package + " -yq"]
}

cmd = commands[operation]


# PROCESS SPAWNING:
def startProcess(params):
    status = subprocess.call(params)
    exit(status)


startProcess(cmd)
