import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GLib, Gio, Gtk

class PackageManager:
    def __init__(self, packages, onProcessFinished, progressWindow):
        # Get packages array
        self.packages = packages
        self.onProcessFinished = onProcessFinished
        self.progressWindow = progressWindow

        # Commands
        self.installCommand = ["pkexec", "apt", "install", "--PACKAGE--" , "-yq"]
        self.removeCommand = ["pkexec", "apt", "purge", "--PACKAGE--", "-yq"]
        self.makeDefaultCommand = ["pkexec", "update-alternatives", "--set", "java", "--PATH--"]
        self.isInstalledCommand = ["dpkg", "-s", "--PACKAGE--"]
        self.getAlternativesListCommand = ["update-alternatives", "--query", "java"]
        self.autoAlternativeCommand = ["pkexec", "update-alternatives", "--auto", "java"]

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
            self.startProcessSync(self.autoAlternativeCommand)

        removeCommand = self.removeCommand
        removeCommand[3] = pack['package']
        self.startProcess(removeCommand)

    

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
            print(line)
            if str(line[0]) == "Value":
                self.defaultJavaPath = line[1]
                print(self.defaultJavaPath)
                return



    # PROCESS SPAWNING:
    def startProcess(self, params):
        self.progressWindow.show()        

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

        print(f"[stdout]: {line}")

        self.progressWindow.appendText(line)
        return True
    
    def onProcessStderr(self, source, condition):
        if condition == GLib.IO_HUP:
            return False
        line = source.readline()

        print(f"[stderr]: {line}")

        self.progressWindow.appendText(line)
        return True

    def onProcessExit(self, pid, status):
        print(f"{pid}: {status}")
        self.progressWindow.hide()
        self.onProcessFinished()