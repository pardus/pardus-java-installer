import gi

gi.require_version('Gtk', '3.0')
from gi.repository import GLib, Gio, Gtk

from PackageManager import PackageManager

packages = {
    "openjdk_17": {"package": "openjdk-17-jre", "path": "/usr/lib/jvm/java-17-openjdk-amd64/bin/java"},
    "openjdk_11": {"package": "openjdk-11-jre", "path": "/usr/lib/jvm/java-11-openjdk-amd64/bin/java"},
    "openjdk_8": {"package": "openjdk-8-jre", "path": "/usr/lib/jvm/java-8-openjdk-amd64/jre/bin/java"},
    "oracle_8": {"package": "oracle-java8-jdk", "path": "/usr/lib/jvm/oracle-java8-jdk-amd64/jre/bin/java"},
}

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
        self.packageManager = PackageManager(self.on_process_finished, self.on_install_progress, self.stk_pages)

        # Set version
        # If haven't got from __version__ file then accept version in MainWindow.glade file
        try:
            version = open(os.path.dirname(os.path.abspath(__file__)) + "/__version__").readline()
            self.dialog_about.set_version(version)
        except:
            pass

        # Show Screen:
        self.refreshGUI()
        self.window.show_all()

    def defineComponents(self):
        # Display:
        self.fb_applications = self.builder.get_object("fb_applications")
        self.stk_pages = self.builder.get_object("stk_pages")
        self.dialog_about = self.builder.get_object("dialog_about")

        self.lbl_percent = self.builder.get_object("lbl_percent")

        # Buttons:
        self.btn_uninstall_openjdk_17 = self.builder.get_object("btn_uninstall_openjdk_17")
        self.btn_uninstall_openjdk_11 = self.builder.get_object("btn_uninstall_openjdk_11")
        self.btn_uninstall_openjdk_8 = self.builder.get_object("btn_uninstall_openjdk_8")
        self.btn_uninstall_oracle_8 = self.builder.get_object("btn_uninstall_oracle_8")

        # Button Stacks:
        self.stk_openjdk_17 = self.builder.get_object("stk_openjdk_17")
        self.stk_openjdk_11 = self.builder.get_object("stk_openjdk_11")
        self.stk_openjdk_8 = self.builder.get_object("stk_openjdk_8")
        self.stk_oracle_8 = self.builder.get_object("stk_oracle_8")

    def refreshGUI(self):
        # Refresh default information
        self.packageManager.findDefault()

        global packages
        # Uninstall button refresh
        self.btn_uninstall_openjdk_17.set_sensitive(self.packageManager.isInstalled(packages["openjdk_17"]))
        self.btn_uninstall_openjdk_11.set_sensitive(self.packageManager.isInstalled(packages["openjdk_11"]))
        self.btn_uninstall_openjdk_8.set_sensitive(self.packageManager.isInstalled(packages["openjdk_8"]))
        self.btn_uninstall_oracle_8.set_sensitive(self.packageManager.isInstalled(packages["oracle_8"]))

        # Set default button stack
        openjdk_17_installed = self.packageManager.isInstalled(packages["openjdk_17"])
        openjdk_17_default = self.packageManager.isDefault(packages["openjdk_17"])
        if not openjdk_17_installed:
            self.stk_openjdk_17.set_visible_child_name("install")
        elif not openjdk_17_default:
            self.stk_openjdk_17.set_visible_child_name("setdefault")
        else:
            self.stk_openjdk_17.set_visible_child_name("default")

        openjdk_11_installed = self.packageManager.isInstalled(packages["openjdk_11"])
        openjdk_11_default = self.packageManager.isDefault(packages["openjdk_11"])
        if not openjdk_11_installed:
            self.stk_openjdk_11.set_visible_child_name("install")
        elif not openjdk_11_default:
            self.stk_openjdk_11.set_visible_child_name("setdefault")
        else:
            self.stk_openjdk_11.set_visible_child_name("default")

        openjdk_8_installed = self.packageManager.isInstalled(packages["openjdk_8"])
        openjdk_8_default = self.packageManager.isDefault(packages["openjdk_8"])
        if not openjdk_8_installed:
            self.stk_openjdk_8.set_visible_child_name("install")
        elif not openjdk_8_default:
            self.stk_openjdk_8.set_visible_child_name("setdefault")
        else:
            self.stk_openjdk_8.set_visible_child_name("default")

        oracle_8_installed = self.packageManager.isInstalled(packages["oracle_8"])
        oracle_8_default = self.packageManager.isDefault(packages["oracle_8"])
        if not oracle_8_installed:
            self.stk_oracle_8.set_visible_child_name("install")
        elif not oracle_8_default:
            self.stk_oracle_8.set_visible_child_name("setdefault")
        else:
            self.stk_oracle_8.set_visible_child_name("default")
    


    # Installations Signals:
    def on_btn_install_clicked(self, button):
        package = button.get_name()  # like openjdk_11, openjdk_17, oracle_8

        self.packageManager.install(packages[package])

    def on_btn_uninstall_clicked(self, button):
        package = button.get_name()  # like openjdk_11, openjdk_17, oracle_8

        self.packageManager.uninstall(packages[package])

    def on_btn_default_clicked(self, button):
        package = button.get_name()  # like openjdk_11, openjdk_17, oracle_8

        self.packageManager.set_as_default(packages[package])

    def btn_information_clicked(self, button):
        self.dialog_about.run()
        self.dialog_about.hide()

    def btn_apt_ok_clicked(self, button):
        self.stk_pages.set_visible_child_name("page_main")
    
    def on_process_finished(self, status):
        if status == 25600:
            self.stk_pages.set_visible_child_name("page_apt_busy")
        else:
            self.stk_pages.set_visible_child_name("page_main")
        
        self.refreshGUI()

        self.window.set_sensitive(True)
        self.window.show_all()
    
    def on_install_progress(self, percent):
        self.lbl_percent.set_text(f"%{percent}")
    
