import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GLib, Gio, Gtk
from threading import Timer


class ProgressWindow:
    def __init__(self, application):
        # Gtk Builder
        self.builder = Gtk.Builder()
        self.builder.add_from_file("../ui/ProgressWindow.glade")
        self.builder.connect_signals(self)

        # Add Window
        self.window = self.builder.get_object("window")
        self.window.set_position(Gtk.WindowPosition.CENTER)
        self.window.set_application(application)
        self.defineComponents()

    
    def defineComponents(self):
        # Display:
        self.outputBuffer = self.builder.get_object("outputBuffer")
        self.progressBar = self.builder.get_object("progressBar")
        self.scrolledWindow = self.builder.get_object("scrolledWindow")
        
    
    def appendText(self, text):
        self.outputBuffer.insert_at_cursor(text)
        adj = self.scrolledWindow.get_vadjustment()
        adj.set_value(adj.get_upper())
    
    def show(self):
        self.outputBuffer.set_text("")
        self.startProgressAnimation(500)
        self.window.show_all()
    
    def hide(self):
        self.stopProgressAnimation()
        self.window.hide()


    def startProgressAnimation(self,ms):
        def func_wrapper():
            self.progressBar.pulse()
            self.startProgressAnimation(ms)
        self.t = Timer(ms/1000, func_wrapper)
        self.t.start()
    
    def stopProgressAnimation(self):
        try:
            self.t.cancel()
        except AttributeError:
            pass
