import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GLib, Gio, Gtk
import os, sys

class PackageManager:
    def __init__(self, packages, onProcessFinished, pb_percent, stk_pages):
        # Get packages array
        self.packages = packages
        self.onProcessFinished = onProcessFinished
        self.pb_percent = pb_percent
        self.stk_pages = stk_pages
        self.defaultJavaPath = ""

        # Commands
        currentPath = os.path.dirname(os.path.abspath(__file__))

        # - Installation commands
        self.installCommand = ["/usr/bin/pkexec", currentPath + "/Actions.py", "install", "--PACKAGE--"] 
        self.removeCommand = ["/usr/bin/pkexec", currentPath + "/Actions.py", "remove", "--PACKAGE--"]
        self.makeDefaultCommand = ["/usr/bin/pkexec", currentPath + "/Actions.py", "make-default", "--PATH--"]
        self.autoAlternativeCommand = ["/usr/bin/pkexec", currentPath + "/Actions.py", "update-alternatives-auto"]
        self.updateAndRemoveCommand = ["/usr/bin/pkexec", currentPath + "/Actions.py", "update-and-remove", "--PACKAGE--"]

        # - Info commands:
        self.isInstalledCommand = ["dpkg", "-s", "--PACKAGE--"]
        self.getAlternativesListCommand = ["update-alternatives", "--query", "java"]

        # Get initialize infos:
        self.findDefault()

    def installOrMakeDefault(self, packageIndex):
        pack = self.packages[packageIndex]

        if self.isInstalled(packageIndex):
            # Make default
            makeDefaultCommand = self.makeDefaultCommand
            makeDefaultCommand[3] = pack['path']

            self.startProcess(makeDefaultCommand)
            #self.stk_pages.set_visible_child_name("page_processing")
        else:
            # Install
            installCommand = self.installCommand
            installCommand[3] = pack['package']

            self.startProcess(installCommand)

            self.pb_percent.set_fraction(0)
            self.stk_pages.set_visible_child_name("page_downloading")
    
    def remove(self, packageIndex):
        pack = self.packages[packageIndex]

        if self.isDefault(packageIndex):
            updateAndRemoveCommand = self.updateAndRemoveCommand
            updateAndRemoveCommand[3] = updateAndRemoveCommand[3].replace("--PACKAGE--", pack['package'] + "*")
            
            self.startProcess(updateAndRemoveCommand)
            self.stk_pages.set_visible_child_name("page_processing")
        else:
            removeCommand = self.removeCommand
            removeCommand[3] = pack['package'] + "*"

            self.startProcess(removeCommand)
            self.stk_pages.set_visible_child_name("page_processing")

    def onProgress(self, percent):
        self.pb_percent.set_fraction(float(percent) / 100)

    # CHECK BOOLEANS:
    def isInstalled(self, packageIndex):
        pack = self.packages[packageIndex]

        isInstalledCommand = self.isInstalledCommand
        isInstalledCommand[2] = pack['package']
        _, stdout, stderr, exit_status = self.startProcessSync(isInstalledCommand)
        return exit_status == 0

    def isDefault(self, packageIndex):
        pack = self.packages[packageIndex]
        return pack['path'] == self.defaultJavaPath

    

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
        print(line.rstrip())
        if 'dlstatus' in line.split(':'):
            self.onProgress(line.split(':')[2])
        if 'dpkg-exec' in line.split(':'):
            self.onProgress(100)
        return True
    
    def onProcessStderr(self, source, condition):
        if condition == GLib.IO_HUP:
            return False
        line = source.readline()
        print(line.rstrip())
        return True

    def onProcessExit(self, pid, status):
        self.onProcessFinished(status)