import gi

import Arch
import Dialogs

gi.require_version("Gtk", "3.0")
import locale
import os
from locale import gettext as _

from gi.repository import Gtk

from PackageManager import PACKAGES, PackageManager, get_package_info

# Translation Constants:
APPNAME = "pardus-java-installer"
TRANSLATIONS_PATH = "/usr/share/locale"

# Translation functions:
locale.bindtextdomain(APPNAME, TRANSLATIONS_PATH)
locale.textdomain(APPNAME)


class MainWindow:
    def __init__(self, application):
        self.application = application

        self.setup_ui_builder()

        self.setup_window()

        self.define_variables()

        self.define_widgets()

        self.setup_about_dialog()

        self.setup_ui()

        self.window.show_all()

    def setup_ui_builder(self):
        self.builder = Gtk.Builder()
        self.builder.set_translation_domain(APPNAME)
        self.builder.add_from_file(
            os.path.dirname(os.path.abspath(__file__)) + "/../ui/MainWindow.glade"
        )
        self.builder.connect_signals(self)

    def setup_window(self):
        self.window = self.builder.get_object("window")
        self.window.set_position(Gtk.WindowPosition.CENTER)
        self.window.set_application(self.application)
        self.window.connect("destroy", lambda _: self.application.quit())

    def define_variables(self):
        # Prepare PackageManager
        self.package_manager = PackageManager(
            self.on_process_finished, self.on_install_progress
        )

    def define_widgets(self):
        def UI(a):
            return self.builder.get_object(a)

        # Display:
        self.fb_applications = UI("fb_applications")
        self.stk_pages = UI("stk_pages")
        self.dialog_about = UI("dialog_about")

        self.pb_progress = UI("pb_progress")
        self.lbl_install_status = UI("lbl_install_status")
        self.lbl_download_name = UI("lbl_download_name")

        # Box
        self.box_java_list = UI("box_java_list")

    def setup_about_dialog(self):
        self.dialog_about = self.builder.get_object("dialog_about")
        self.dialog_about.set_program_name(_("Pardus Java Installer"))
        if self.dialog_about.get_titlebar() is None:
            about_headerbar = Gtk.HeaderBar.new()
            about_headerbar.set_show_close_button(True)
            about_headerbar.set_title(_("About Pardus Java Installer"))
            about_headerbar.pack_start(
                Gtk.Image.new_from_icon_name(
                    "pardus-java-installer", Gtk.IconSize.LARGE_TOOLBAR
                )
            )
            about_headerbar.show_all()
            self.dialog_about.set_titlebar(about_headerbar)

        try:
            version = open(
                os.path.dirname(os.path.abspath(__file__)) + "/__version__"
            ).readline()
            self.dialog_about.set_version(version)
        except:
            pass

    def setup_ui(self):
        # Refresh default information
        self.package_manager.find_default()
        self.package_manager.find_default_javaws()

        # Delete old children
        self.box_java_list.foreach(lambda w: self.box_java_list.remove(w))

        for p in PACKAGES:
            # p = apt package name
            package_info = PACKAGES[p]

            if Arch.arch() not in package_info["architectures"]:
                continue

            box = Gtk.Box(spacing=21, homogeneous=True)
            box.add(Gtk.Label(label=package_info["name"], hexpand=True, halign="start"))

            is_installed = self.package_manager.is_installed(p)
            is_default = self.package_manager.is_default(p)

            # Install/Set as Default Button
            if is_installed:
                if is_default:
                    box.add(Gtk.Label(label=_("Default")))
                else:
                    btn_set_default = Gtk.Button(label=_("Set as Default"))
                    btn_set_default.get_style_context().add_class("suggested-action")
                    btn_set_default.connect("clicked", self.on_btn_default_clicked, p)
                    btn_set_default.set_sensitive(is_installed and not is_default)
                    box.add(btn_set_default)

                btn_uninstall = Gtk.Button(label=_("Uninstall"))
                btn_uninstall.get_style_context().add_class("destructive-action")
                btn_uninstall.connect("clicked", self.on_btn_uninstall_clicked, p)
                box.add(btn_uninstall)
            else:
                box.add(Gtk.Label())

                btn_install = Gtk.Button(label=_("Install"))
                btn_install.connect("clicked", self.on_btn_install_clicked, p)
                box.add(btn_install)

            self.box_java_list.add(box)

    # Installations Signals:
    def on_btn_install_clicked(self, btn, package):
        package_info = get_package_info(package)
        if not package_info:
            return

        self.lbl_download_name.set_text(package_info["name"])
        self.stk_pages.set_visible_child_name("page_downloading")

        self.package_manager.install(package)

    def on_btn_uninstall_clicked(self, btn, package):
        self.stk_pages.set_visible_child_name("page_processing")

        self.package_manager.uninstall(package)

    def on_btn_default_clicked(self, btn, package):
        self.package_manager.set_as_default(package)

    def btn_information_clicked(self, button):
        self.dialog_about.run()
        self.dialog_about.hide()

    def btn_apt_ok_clicked(self, button):
        self.stk_pages.set_visible_child_name("page_main")

    def on_process_finished(self, status):
        print("Subprocess exit code:", status)
        if status == 25600:
            self.stk_pages.set_visible_child_name("page_apt_busy")
        else:
            self.stk_pages.set_visible_child_name("page_main")

        self.setup_ui()

        self.window.show_all()

    def on_install_progress(self, percent, status):
        # print(f"on_install_progress:{percent}, {status}")
        self.lbl_install_status.set_text(_(status))
        self.pb_progress.set_fraction(int(percent) / 100)

    def on_btn_cancel_install_clicked(self, btn):
        result = Dialogs.ask(_("Are you sure?"), _("Operation will be cancelled"))
        if result == Gtk.ResponseType.OK:
            self.package_manager.cancel_install()
