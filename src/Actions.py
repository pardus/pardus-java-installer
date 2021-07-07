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

    # pid, stdin, stdout, stderr = GLib.spawn_async(params,
    #                            flags=GLib.SpawnFlags.SEARCH_PATH | GLib.SpawnFlags.LEAVE_DESCRIPTORS_OPEN | GLib.SpawnFlags.DO_NOT_REAP_CHILD,
    #                            standard_input=False, standard_output=True, standard_error=True)
    # GLib.io_add_watch(GLib.IOChannel(stdout), GLib.IO_IN | GLib.IO_HUP, onProcessStdout)
    # GLib.io_add_watch(GLib.IOChannel(stderr), GLib.IO_IN | GLib.IO_HUP, onProcessStderr)
    # GLib.child_watch_add(GLib.PRIORITY_DEFAULT, pid, onProcessExit)


'''
def onProcessStdout( source, condition):
    if condition == GLib.IO_HUP:
        return False

    line = source.readline()
    print(line.rstrip())
    sys.stdout.flush()
    return True

def onProcessStderr( source, condition):
    if condition == GLib.IO_HUP:
        return False
    
    line = source.readline()
    print(line.rstrip())
    sys.stdout.flush()
    return True

def onProcessExit( pid, status):
    print("Exited:" + status)
    exit(status)
'''

startProcess(cmd)

# Gtk.main()
