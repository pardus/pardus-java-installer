import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GLib, Gio, Gtk

class PackageManager:
    def __init__(self, packages):
        # Gtk Builder
        self.packages = packages

    def isInstalled(self, packageIndex):
        pack = self.packages[packageIndex]

        return True
    
    def isDefault(self, packageIndex):
        pack = self.packages[packageIndex]

        return True