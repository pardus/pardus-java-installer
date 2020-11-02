import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GLib, Gio, Gtk

from PackageManager import PackageManager

packages = [
    { "name":"OpenJDK 11", "package":"openjdk-11-jre", "icon":"openjdk-11", "path":"/usr/lib/jvm/java-11-openjdk-amd64/bin/java" },
    { "name":"OpenJDK 8", "package":"openjdk-8-jre", "icon":"openjdk-8", "path":"/usr/lib/jvm/java-8-openjdk-amd64/jre/bin/java" },
    #{ "name":"Oracle Java 11", "package":"oracle-jdk-11", "icon":"application-java", "path":"/usr/lib/jvm/jdk-11.0.7/bin/java" }, 
    #{ "name":"Oracle Java 14", "package":"oracle-jdk-14", "icon":"application-java", "path":"/usr/lib/jvm/jdk-14.0.1/bin/java" },
    #{ "name":"Nvidia Cuda JDK 8", "package":"nvidia-openjdk-8-jre", "icon":"nvidia", "path":"/usr/lib/jvm/nvidia-java-8-openjdk-amd64/bin/java" }, 
]

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
        self.packageManager = PackageManager(packages, self.onProcessFinished, self.pb_percent, self.stk_pages)

        # Set version
        # If not getted from __version__ file then accept version in MainWindow.glade file
        try:
            version = open(os.path.dirname(os.path.abspath(__file__)) + "/__version__").readline()
            self.dialog_about.set_version(version)
        except:
            pass

        # Show Screen:
        self.addApplicationListToGrid()
        self.window.show_all()
    
    def defineComponents(self):
        # Display:
        self.fb_applications = self.builder.get_object("fb_applications")
        self.stk_pages = self.builder.get_object("stk_pages")

        self.dialog_about = self.builder.get_object("dialog_about")

        self.pb_percent = self.builder.get_object("pb_percent")
        self.lbl_packageName = self.builder.get_object("lbl_packageName")
    
    def addApplicationListToGrid(self):
        for i in range(len(packages)):
            box = Gtk.Box.new(orientation=Gtk.Orientation.VERTICAL, spacing=5)
            box.set_size_request(96, -1)
            
            # Java Icon:
            javaIcon = Gtk.Image.new_from_icon_name(packages[i]["icon"], 0)
            javaIcon.set_pixel_size(72)

            # Label & Tick
            labelBox = Gtk.Box.new(orientation=Gtk.Orientation.HORIZONTAL, spacing=3)
            packageName = Gtk.Label.new(packages[i]["name"])

            installedTick = Gtk.Image.new_from_icon_name("dialog-ok", 0)
            installedTick.set_pixel_size(16)
            installedTick.set_halign(Gtk.Align.START)
            installedTick.set_no_show_all(True)

            labelBox.set_center_widget(packageName)
            labelBox.pack_end(installedTick, True, True, 0)
            labelBox.set_margin_bottom(11)


            # Install or Default button
            btn_install = Gtk.Button.new()
            btn_install.set_name(str(i)) # to identify which button has pressed
            btn_install.connect("clicked", self.btn_install_clicked)

            isPackInstalled = self.packageManager.isInstalled(i)
            isPackDefault = self.packageManager.isDefault(i)

            installedTick.set_visible(isPackDefault)

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

            box.pack_start(javaIcon, True, True, 0)
            box.pack_start(labelBox, True, True, 0)
            box.pack_start(btn_install, False, False, 0)
            box.pack_start(btn_remove, False, False, 0)

            self.fb_applications.insert(box, -1)
    
    def btn_install_clicked(self, button):
        index = int(button.get_name())
        self.lbl_packageName.set_text(self.packageManager.packages[index]['name'])
        self.packageManager.installOrMakeDefault(index)
    
    def btn_remove_clicked(self, button):
        index = int(button.get_name())
        self.packageManager.remove(index)

    def btn_information_clicked(self, button):
        self.dialog_about.run()
        self.dialog_about.hide()
    
    def btn_apt_ok_clicked(self, button):
        self.stk_pages.set_visible_child_name("page_main")
    
    def onProcessFinished(self, status):
        if status == 25600:
            self.stk_pages.set_visible_child_name("page_apt_busy")
        else:
            self.stk_pages.set_visible_child_name("page_main")
        print(status)
        
        # Refresh default information
        self.packageManager.findDefault()

        global packages
        for i in range(len(packages)):
            flowboxItem = self.fb_applications.get_child_at_index(i)
            box = flowboxItem.get_child()

            box_children = box.get_children()

            labelBox = box_children[1]
            installedTick = labelBox.get_children()[1]
            btn_install = box_children[2]
            btn_remove = box_children[3]

            isPackInstalled = self.packageManager.isInstalled(i)
            isPackDefault = self.packageManager.isDefault(i)

            # Show tick
            installedTick.set_visible(isPackDefault)

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
        
        self.window.set_sensitive(True)
        self.window.show_all()
