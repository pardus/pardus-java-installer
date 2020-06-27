import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GLib, Gio, Gtk

class PackageManager:
    def __init__(self, packages, onProcessFinished, dlg_pb_percent, dialog_progress):
        # Get packages array
        self.packages = packages
        self.onProcessFinished = onProcessFinished
        self.dlg_pb_percent = dlg_pb_percent
        self.dialog_progress = dialog_progress

        # Commands
        self.installCommand = ["pkexec", "apt-get", "install", "--PACKAGE--" , "-yq", "-o", "APT::Status-Fd=1"]
        self.removeCommand = ["pkexec", "apt", "purge", "--PACKAGE--", "-yq"]
        self.makeDefaultCommand = ["pkexec", "update-alternatives", "--set", "java", "--PATH--"]
        self.isInstalledCommand = ["dpkg", "-s", "--PACKAGE--"]
        self.getAlternativesListCommand = ["update-alternatives", "--query", "java"]
        self.autoAlternativeCommand = ["pkexec", "update-alternatives", "--auto", "java"]
        self.updateAndRemoveCommand = ["pkexec", "/bin/sh", "-c", "update-alternatives --auto java && apt purge --PACKAGE-- -yq"]

        # Get initialize infos:
        self.findDefault()

    def installOrMakeDefault(self, packageIndex):
        pack = self.packages[packageIndex]

        if self.isInstalled(packageIndex):
            # Make default
            makeDefaultCommand = self.makeDefaultCommand
            makeDefaultCommand[4] = pack['path']
            self.startProcess(makeDefaultCommand)
        else:
            # Install
            installCommand = self.installCommand
            installCommand[3] = pack['package']
            self.startProcess(installCommand)
    
    def remove(self, packageIndex):
        pack = self.packages[packageIndex]

        if self.isDefault(packageIndex):
            updateAndRemoveCommand = self.updateAndRemoveCommand
            updateAndRemoveCommand[3] = updateAndRemoveCommand[3].replace("--PACKAGE--", pack['package'] + "*")
            self.startProcess(updateAndRemoveCommand)
        else:
            removeCommand = self.removeCommand
            removeCommand[3] = pack['package'] + "*"
            self.startProcess(removeCommand)

    def onProgress(self, percent):
        self.dlg_pb_percent.set_fraction(float(percent) / 100)

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
        
        self.dlg_pb_percent.set_fraction(0)
        self.dialog_progress.run()
    
    def startProcessSync(self, params):
        return GLib.spawn_sync(None, params, None, GLib.SPAWN_SEARCH_PATH)

    def onProcessStdout(self, source, condition):
        if condition == GLib.IO_HUP:
            return False

        line = source.readline()
        print(line)
        if 'dlstatus' in line.split(':'):
            self.onProgress(line.split(':')[2])
        return True
    
    def onProcessStderr(self, source, condition):
        if condition == GLib.IO_HUP:
            return False
        line = source.readline()
        return True

    def onProcessExit(self, pid, status):
        print(status)
        self.dialog_progress.hide()
        self.onProcessFinished()