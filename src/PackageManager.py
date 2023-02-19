import gi

gi.require_version('Gtk', '3.0')
from gi.repository import GLib, Gio, Gtk
import os, sys
from Actions import Action


class PackageManager:
    def __init__(self, on_process_finished, on_progress):
        # Get packages array
        self.on_process_finished = on_process_finished
        self.on_progress = on_progress
        self.defaultJavaPath = ""

        # Commands
        currentPath = os.path.dirname(os.path.abspath(__file__))

        # - Installation commands
        self.autoAlternativeCommand = ["/usr/bin/pkexec", currentPath + "/Actions.py", "update-alternatives-auto"]

        # - Info commands:
        self.isInstalledCommand = ["dpkg", "-s", "--PACKAGE--"]
        self.getAlternativesListCommand = ["update-alternatives", "--query", "java"]

        # Get initialize infos:
        self.findDefault()

    def install(self, packageObject):
        act = Action(packageObject["package"])
        act.startCommand("install")

        self.on_progress("%0", "Downloading")

    def set_as_default(self, packageObject):
        act = Action(packageObject["path"])
        act.startCommand("make-default")

    def uninstall(self, packageObject):
        act = Action(packageObject["package"] + "*")
        if self.isDefault(packageObject):
            act.startCommand("update-and-remove")
        else:
            act.startCommand("remove")

    # CHECK BOOLEANS:
    def isInstalled(self, packageObject):
        isInstalledCommand = self.isInstalledCommand
        isInstalledCommand[2] = packageObject["package"]
        _, stdout, stderr, exit_status = self.startProcessSync(isInstalledCommand)
        return exit_status == 0

    def isDefault(self, packageObject):
        return packageObject["path"] == self.defaultJavaPath

    # TOOLS:
    def findDefault(self):
        _, stdout, stderr, exit_status = self.startProcessSync(self.getAlternativesListCommand)

        for i in stdout.splitlines(0):
            line = i.decode("utf-8").split(": ")
            if str(line[0]) == "Value":
                self.defaultJavaPath = line[1]
                return

    # PROCESS SPAWNING:
    def startProcess(self, params):
        pid, stdin, stdout, stderr = GLib.spawn_async(params,
                                                      flags=GLib.SPAWN_SEARCH_PATH | GLib.SPAWN_LEAVE_DESCRIPTORS_OPEN | GLib.SPAWN_DO_NOT_REAP_CHILD,
                                                      standard_input=False, standard_output=True, standard_error=True)
        GLib.io_add_watch(GLib.IOChannel(stdout), GLib.IO_IN | GLib.IO_HUP, self.onProcessStdout)
        GLib.io_add_watch(GLib.IOChannel(stderr), GLib.IO_IN | GLib.IO_HUP, self.onProcessStderr)
        GLib.child_watch_add(GLib.PRIORITY_DEFAULT, pid, self.onProcessExit)

    def startProcessSync(self, params):
        return GLib.spawn_sync(None, params, None, GLib.SPAWN_SEARCH_PATH)

    def onProcessStdout(self, source, condition):
        if condition == GLib.IO_HUP:
            return False

        line = source.readline()
        params = line.split(":")
        print(line.rstrip())
        if 'dlstatus' in params:
            self.on_progress(f"%{params[2].split('.')[0]}", "Downloading")
        elif 'pmstatus' in params:
            self.on_progress(params[3].rstrip(), "Installing")
        
        return True

    def onProcessStderr(self, source, condition):
        if condition == GLib.IO_HUP:
            return False
        line = source.readline()
        return True

    def onProcessExit(self, pid, status):
        self.on_process_finished(status)
