import gi

gi.require_version('Gtk', '3.0')
from gi.repository import GLib, Gio, Gtk
import os, sys


class PackageManager:
    def __init__(self, on_process_finished, on_progress, stk_pages):
        # Get packages array
        self.on_process_finished = on_process_finished
        self.on_progress = on_progress
        self.stk_pages = stk_pages
        self.defaultJavaPath = ""

        # Commands
        currentPath = os.path.dirname(os.path.abspath(__file__))

        # - Installation commands
        self.installCommand = ["/usr/bin/pkexec", currentPath + "/Actions.py", "install", "--PACKAGE--"]
        self.removeCommand = ["/usr/bin/pkexec", currentPath + "/Actions.py", "remove", "--PACKAGE--"]
        self.makeDefaultCommand = ["/usr/bin/pkexec", currentPath + "/Actions.py", "make-default", "--PATH--"]
        self.autoAlternativeCommand = ["/usr/bin/pkexec", currentPath + "/Actions.py", "update-alternatives-auto"]
        self.updateAndRemoveCommand = ["/usr/bin/pkexec", currentPath + "/Actions.py", "update-and-remove",
                                       "--PACKAGE--"]

        # - Info commands:
        self.isInstalledCommand = ["dpkg", "-s", "--PACKAGE--"]
        self.getAlternativesListCommand = ["update-alternatives", "--query", "java"]

        # Get initialize infos:
        self.findDefault()

    def install(self, packageObject):
        installCommand = self.installCommand
        installCommand[3] = packageObject["package"]

        self.startProcess(installCommand)

        self.on_progress("0")
        self.stk_pages.set_visible_child_name("page_downloading")

    def set_as_default(self, packageObject):
        makeDefaultCommand = self.makeDefaultCommand
        makeDefaultCommand[3] = packageObject["path"]

        self.startProcess(makeDefaultCommand)

    def uninstall(self, packageObject):
        if self.isDefault(packageObject):
            updateAndRemoveCommand = self.updateAndRemoveCommand
            updateAndRemoveCommand[3] = updateAndRemoveCommand[3].replace("--PACKAGE--", packageObject["package"] + "*")

            self.startProcess(updateAndRemoveCommand)
            self.stk_pages.set_visible_child_name("page_processing")
        else:
            removeCommand = self.removeCommand
            removeCommand[3] = packageObject["package"] + "*"

            self.startProcess(removeCommand)
            self.stk_pages.set_visible_child_name("page_processing")


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
        if 'dlstatus' in line.split(':'):
            self.on_progress(line.split(':')[2].split('.')[0])
        if 'dpkg-exec' in line.split(':'):
            self.on_progress("100")
        
        return True

    def onProcessStderr(self, source, condition):
        if condition == GLib.IO_HUP:
            return False
        line = source.readline()
        return True

    def onProcessExit(self, pid, status):
        self.on_process_finished(status)
