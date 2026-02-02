import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from PackageManager import PackageManager

import locale, os
from locale import gettext as _

arch = "amd64"
try:
    mainarch = os.uname()[4]
except Exception as e:
    mainarch = ""
    print("mainarch Exception : {}".format(e))

if mainarch == "aarch64":
    arch = "arm64"

print("mainarch : {} | arch : {}".format(mainarch, arch))

packages = {
    "openjdk_25":
        {
            "package": "openjdk-25-jre",
            "path": ["/usr/lib/jvm/java-25-openjdk-{}/bin/java".format(arch)]
        },
    "openjdk_21":
        {
            "package": "openjdk-21-jre",
            "path": ["/usr/lib/jvm/java-21-openjdk-{}/bin/java".format(arch)]
        },
    "oracle_8":
        {
            "package": "oracle-java8-jdk",
            "path": ["/usr/lib/jvm/oracle-java8-jdk-{}/jre/bin/java".format(arch)],
            "javaws_path": ["/usr/lib/jvm/oracle-java8-jdk-{}/jre/bin/javaws".format(arch)]
        },
    "oracle_25":
        {
            "package": "jdk-25",
            "path": ["/usr/lib/jvm/jdk-25.0.2-oracle-x64/bin/java",
                     "/usr/lib/jvm/jdk-25-oracle-x64/bin/java"]
        },
    "oracle_11":
        {
            "package": "jdk-11",
            "path": ["/usr/lib/jvm/jdk-11.0.30-oracle-x64/bin/java"]
        }
}

# Translation Constants:
APPNAME = "pardus-java-installer"
TRANSLATIONS_PATH = "/usr/share/locale"

# Translation functions:
locale.bindtextdomain(APPNAME, TRANSLATIONS_PATH)
locale.textdomain(APPNAME)


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
        self.packageManager = PackageManager(self.on_process_finished, self.on_install_progress)

        # Set version
        # If haven't got from __version__ file then accept version in MainWindow.glade file
        try:
            version = open(os.path.dirname(os.path.abspath(__file__)) + "/__version__").readline()
            self.dialog_about.set_version(version)
        except:
            pass
        self.dialog_about.set_program_name(_("Pardus Java Installer"))
        if self.dialog_about.get_titlebar() is None:
            about_headerbar = Gtk.HeaderBar.new()
            about_headerbar.set_show_close_button(True)
            about_headerbar.set_title(_("About Pardus Java Installer"))
            about_headerbar.pack_start(
                Gtk.Image.new_from_icon_name("pardus-java-installer", Gtk.IconSize.LARGE_TOOLBAR))
            about_headerbar.show_all()
            self.dialog_about.set_titlebar(about_headerbar)

        # Show Screen:
        self.refreshGUI()
        self.window.show_all()

        # openjdk8 arm64 package is not available
        if arch == "arm64":
            self.box_openjdk_8.set_visible(False)

    def defineComponents(self):
        # Display:
        self.fb_applications = self.builder.get_object("fb_applications")
        self.stk_pages = self.builder.get_object("stk_pages")
        self.dialog_about = self.builder.get_object("dialog_about")

        self.lbl_percent = self.builder.get_object("lbl_percent")
        self.lbl_install_status = self.builder.get_object("lbl_install_status")

        # Buttons:
        self.btn_uninstall_openjdk_25 = self.builder.get_object("btn_uninstall_openjdk_25")
        self.btn_uninstall_openjdk_21 = self.builder.get_object("btn_uninstall_openjdk_21")
        self.btn_uninstall_oracle_8 = self.builder.get_object("btn_uninstall_oracle_8")
        self.btn_uninstall_oracle_25 = self.builder.get_object("btn_uninstall_oracle_25")
        self.btn_uninstall_oracle_11 = self.builder.get_object("btn_uninstall_oracle_11")

        # Button Stacks:
        self.stk_openjdk_25 = self.builder.get_object("stk_openjdk_25")
        self.stk_openjdk_21 = self.builder.get_object("stk_openjdk_21")
        self.stk_openjdk_8 = self.builder.get_object("stk_openjdk_8")
        self.stk_oracle_8 = self.builder.get_object("stk_oracle_8")
        self.stk_oracle_25 = self.builder.get_object("stk_oracle_25")
        self.stk_oracle_11 = self.builder.get_object("stk_oracle_11")
        # Boxes:
        self.box_openjdk_8 = self.builder.get_object("box_openjdk_8")

    def refreshGUI(self):
        # Refresh default information
        self.packageManager.findDefault()
        self.packageManager.findDefaultJavaWS()

        global packages
        # Uninstall button refresh
        self.btn_uninstall_openjdk_25.set_sensitive(self.packageManager.isInstalled(packages["openjdk_25"]))
        self.btn_uninstall_openjdk_21.set_sensitive(self.packageManager.isInstalled(packages["openjdk_21"]))
        self.btn_uninstall_oracle_8.set_sensitive(self.packageManager.isInstalled(packages["oracle_8"]))
        self.btn_uninstall_oracle_25.set_sensitive(self.packageManager.isInstalled(packages["oracle_25"]))
        self.btn_uninstall_oracle_11.set_sensitive(self.packageManager.isInstalled(packages["oracle_11"]))
        
        # Set default button stack
        openjdk_25_installed = self.packageManager.isInstalled(packages["openjdk_25"])
        openjdk_25_default = self.packageManager.isDefault(packages["openjdk_25"])
        if not openjdk_25_installed:
            self.stk_openjdk_25.set_visible_child_name("install")
        elif not openjdk_25_default:
            self.stk_openjdk_25.set_visible_child_name("setdefault")
        else:
            self.stk_openjdk_25.set_visible_child_name("default")

        openjdk_21_installed = self.packageManager.isInstalled(packages["openjdk_21"])
        openjdk_21_default = self.packageManager.isDefault(packages["openjdk_21"])
        if not openjdk_21_installed:
            self.stk_openjdk_21.set_visible_child_name("install")
        elif not openjdk_21_default:
            self.stk_openjdk_21.set_visible_child_name("setdefault")
        else:
            self.stk_openjdk_21.set_visible_child_name("default")

        oracle_8_installed = self.packageManager.isInstalled(packages["oracle_8"])
        oracle_8_default = (self.packageManager.isDefault(packages["oracle_8"]) and
                            self.packageManager.isDefaultJavaWS(packages["oracle_8"]))
        if not oracle_8_installed:
            self.stk_oracle_8.set_visible_child_name("install")
        elif not oracle_8_default:
            self.stk_oracle_8.set_visible_child_name("setdefault")
        else:
            self.stk_oracle_8.set_visible_child_name("default")

        oracle_25_installed = self.packageManager.isInstalled(packages["oracle_25"])
        oracle_25_default = self.packageManager.isDefault(packages["oracle_25"])
        if not oracle_25_installed:
            self.stk_oracle_25.set_visible_child_name("install")
        elif not oracle_25_default:
            self.stk_oracle_25.set_visible_child_name("setdefault")
        else:
            self.stk_oracle_25.set_visible_child_name("default")

        oracle_11_installed = self.packageManager.isInstalled(packages["oracle_11"])
        oracle_11_default = self.packageManager.isDefault(packages["oracle_11"])
        if not oracle_11_installed:
            self.stk_oracle_11.set_visible_child_name("install")
        elif not oracle_11_default:
            self.stk_oracle_11.set_visible_child_name("setdefault")
        else:
            self.stk_oracle_11.set_visible_child_name("default")
    # Installations Signals:
    def on_btn_install_clicked(self, button):
        package = button.get_name()  # like openjdk_21, openjdk_25, oracle_8

        self.packageManager.install(packages[package])
        self.stk_pages.set_visible_child_name("page_downloading")

    def on_btn_uninstall_clicked(self, button):
        package = button.get_name()  # like openjdk_21, openjdk_25, oracle_8

        self.packageManager.uninstall(packages[package])
        self.stk_pages.set_visible_child_name("page_processing")

    def on_btn_default_clicked(self, button):
        package = button.get_name()  # like openjdk_21, openjdk_25, oracle_8

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

        # openjdk8 arm64 package is not available
        if arch == "arm64":
            self.box_openjdk_8.set_visible(False)

    def on_install_progress(self, percent, status):
        self.lbl_install_status.set_text(_(status))
        self.lbl_percent.set_text(percent)