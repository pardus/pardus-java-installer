#!/usr/bin/python3
import gi

gi.require_version('Gtk', '3.0')
from gi.repository import GLib, Gio, Gtk
import sys, os, subprocess

operation = sys.argv[1]
package = sys.argv[2]

commands = {
    "install": ["apt-get", "install", package, "-yq", "-o", "APT::Status-Fd=1"],
    "remove": ["apt", "purge", package, "-yq"],
    "make-default": ["update-alternatives", "--set", "java", package],
    "update-alternatives-auto": ["update-alternatives", "--auto", "java"],
    "update-and-remove": ["/bin/sh", "-c", "update-alternatives --auto java && apt purge " + package + " -yq"]
}

cmd = commands[operation]


# PROCESS SPAWNING:
def startProcess(params):
    status = subprocess.call(params)
    exit(status)

startProcess(cmd)