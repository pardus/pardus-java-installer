import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GLib, Gio, Gtk

from PackageManager import PackageManager
from ProgressWindow import ProgressWindow

packages = [
    { "name":"OpenJDK 11", "package":"openjdk-11-jre", "icon":"openjdk-11", "path":"/usr/lib/jvm/java-11-openjdk-amd64/bin/java" },
    { "name":"OpenJDK 8", "package":"openjdk-8-jre", "icon":"openjdk-8", "path":"/usr/lib/jvm/java-8-openjdk-amd64/jre/bin/java" },
    { "name":"Oracle Java 11", "package":"oracle-jdk-11", "icon":"application-java", "path":"/usr/lib/jvm/jdk-11.0.7/bin/java" }, 
    { "name":"Oracle Java 14", "package":"oracle-jdk-14", "icon":"application-java", "path":"/usr/lib/jvm/jdk-14.0.1/bin/java" },
    { "name":"Nvidia-OpenJDK 8", "package":"nvidia-openjdk-8-jre", "icon":"nvidia", "path":"/usr/lib/jvm/nvidia-java-8-openjdk-amd64/bin/java" }, 
]
gridColumnCount = 3

import locale, os
from locale import gettext as tr

# Translation Constants:
APPNAME = "pardus-java-installer"
TRANSLATIONS_PATH = "/usr/share/locale"
SYSTEM_LANGUAGE = os.environ.get("LANG")

# Translation functions:
locale.bindtextdomain(APPNAME, TRANSLATIONS_PATH)
locale.textdomain(APPNAME)
locale.setlocale(locale.LC_ALL, SYSTEM_LANGUAGE)


class MainWindow:
    def __init__(self, application):
        # Gtk Builder
        self.builder = Gtk.Builder()

         # Translate things on glade:
        self.builder.set_translation_domain(APPNAME)

        self.builder.add_from_file(os.path.dirname(os.path.abspath(__file__)) + "/../ui/MainWindow.glade")
        self.builder.connect_signals(self)

        # Add Window
        self.window = self.builder.get_object("window")
        self.window.set_position(Gtk.WindowPosition.CENTER)
        self.window.set_application(application)
        self.window.connect('destroy', application.onExit)
        self.defineComponents()

        # Prepare PackageManager
        self.packageManager = PackageManager(packages, self.onProcessFinished, ProgressWindow(application))

        # Show Screen:
        self.addApplicationListToGrid()
        self.window.show_all()
    
    def defineComponents(self):
        # Display:
        self.grid = self.builder.get_object("grid")
    
    def addApplicationListToGrid(self):
        for i in range(len(packages)):
            box = Gtk.Box.new(orientation=Gtk.Orientation.VERTICAL, spacing=5)
            
            image = Gtk.Image.new_from_icon_name(packages[i]["icon"], 0)
            image.set_pixel_size(64)
            label = Gtk.Label.new(packages[i]["name"])
            label.set_margin_top(7)
            label.set_margin_bottom(7)

            # Install or Default button
            btn_install = Gtk.Button.new()
            btn_install.set_name(str(i)) # to identify which button has pressed
            btn_install.connect("clicked", self.btn_install_clicked)

            isPackInstalled = self.packageManager.isInstalled(i)
            isPackDefault = self.packageManager.isDefault(i)

            if not isPackInstalled:
                btn_install.set_label(tr("Install"))
                btn_install.set_sensitive(True)
                if btn_install.get_style_context().has_class("suggested-action"):
                    btn_install.get_style_context().remove_class("suggested-action")
            elif not isPackDefault:
                btn_install.set_label(tr("Make Default"))
                btn_install.set_sensitive(True)
                if not btn_install.get_style_context().has_class("suggested-action"):
                    btn_install.get_style_context().add_class("suggested-action")
            else:
                btn_install.set_label(tr("Default"))
                btn_install.set_sensitive(False)
                if btn_install.get_style_context().has_class("suggested-action"):
                    btn_install.get_style_context().remove_class("suggested-action")
            

            # Remove button:
            btn_remove = Gtk.Button.new()
            btn_remove.set_label(tr("Uninstall"))
            btn_remove.set_name(str(i)) # to idenfity which button has pressed
            btn_remove.connect("clicked", self.btn_remove_clicked)
            btn_remove.get_style_context().add_class("destructive-action")
            btn_remove.set_sensitive(isPackInstalled)

            box.pack_start(image, True, True, 0)
            box.pack_start(label, True, True, 0)
            box.pack_start(btn_install, False, False, 0)
            box.pack_start(btn_remove, False, False, 0)

            self.grid.attach(box, i % gridColumnCount, i / gridColumnCount, 1, 1)
    
    def btn_install_clicked(self, button):
        self.window.set_sensitive(False)
        self.packageManager.installOrMakeDefault(int(button.get_name()))
    
    def btn_remove_clicked(self, button):
        self.window.set_sensitive(False)
        self.packageManager.remove(int(button.get_name()))
    
    def onProcessFinished(self):
        # Refresh default information
        self.packageManager.findDefault()

        i = len(self.grid.get_children()) - 1
        for a in range(len(self.grid.get_children())):
            gridElement = self.grid.get_children()[a]
            gridChildren = gridElement.get_children()

            btn_install = gridChildren[2]
            btn_remove = gridChildren[3]

            isPackInstalled = self.packageManager.isInstalled(i)
            isPackDefault = self.packageManager.isDefault(i)

            if not isPackInstalled:
                btn_install.set_label(tr("Install"))
                btn_install.set_sensitive(True)
                if btn_install.get_style_context().has_class("suggested-action"):
                    btn_install.get_style_context().remove_class("suggested-action")
            elif not isPackDefault:
                btn_install.set_label(tr("Make Default"))
                btn_install.set_sensitive(True)
                if not btn_install.get_style_context().has_class("suggested-action"):
                    btn_install.get_style_context().add_class("suggested-action")
            else:
                btn_install.set_label(tr("Default"))
                btn_install.set_sensitive(False)
                if btn_install.get_style_context().has_class("suggested-action"):
                    btn_install.get_style_context().remove_class("suggested-action")
            
            btn_remove.set_sensitive(isPackInstalled)

            i = i - 1
        
        self.window.set_sensitive(True)
        self.window.show_all()
