import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GLib, Gio, Gtk

from PackageManager import PackageManager

packages = [
    { "name":"Java v1", "package":"java-jre-1", "icon":"application-java", "path":"/usr/lib/jvm/java8" },
    { "name":"Java v2", "package":"java-jre-2", "icon":"application-java", "path":"/usr/lib/jvm/java8" },
    { "name":"Java v3", "package":"java-jre-3", "icon":"application-java", "path":"/usr/lib/jvm/java8" },   
]
gridWidth = 3


class MainWindow:
    def __init__(self, application):
        # Gtk Builder
        self.builder = Gtk.Builder()
        self.builder.add_from_file("../ui/MainWindow.glade")
        self.builder.connect_signals(self)

        # Add Window
        self.window = self.builder.get_object("window")
        self.window.set_position(Gtk.WindowPosition.CENTER)
        self.window.set_application(application)
        self.defineComponents()

        # Prepare PackageManager
        self.packageManager = PackageManager(packages)

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
            image.set_pixel_size(72)
            label = Gtk.Label.new(packages[i]["name"])

            # Install or Default button
            btn_install = Gtk.Button.new()
            btn_install.set_name(str(i)) # to identify which button has pressed
            btn_install.connect("clicked", self.btn_install_clicked)

            if not self.packageManager.isInstalled(i):
                btn_install.set_label("Yükle")
                btn_install.get_style_context().remove_class("suggested-action")
                btn_install.set_sensitive(True)
            elif not self.packageManager.isDefault(i):
                btn_install.set_label("Varsayılan Yap")
                btn_install.get_style_context().add_class("suggested-action")
                btn_install.set_sensitive(True)
            else:
                btn_install.set_label("Varsayılan")
                btn_install.get_style_context().remove_class("suggested-action")
                btn_install.set_sensitive(False)
            

            # Remove button:
            btn_remove = Gtk.Button.new()
            btn_remove.set_label("Kaldır")
            btn_remove.set_name(str(i)) # to idenfity which button has pressed
            btn_remove.connect("clicked", self.btn_remove_clicked)
            btn_remove.get_style_context().add_class("destructive-action")
            btn_remove.set_sensitive(self.packageManager.isInstalled(i))

            box.pack_start(image, True, True, 0)
            box.pack_start(label, True, True, 0)
            box.pack_start(btn_install, False, False, 0)
            box.pack_start(btn_remove, False, False, 0)

            self.grid.attach(box, i % gridWidth, i / gridWidth, 1, 1)
    
    def btn_install_clicked(self, button):
        self.packageManager.instalOrMakeDefault(button.get_name())
    
    def btn_remove_clicked(self, button):
        self.packageManager.remove(button.get_name())