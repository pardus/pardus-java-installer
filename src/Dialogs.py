import gi

gi.require_version("Gtk", "3.0")

from gi.repository import Gtk


def info(title, subtitle, use_markup=False):
    dialog = Gtk.MessageDialog(
        buttons=Gtk.ButtonsType.OK,
        text=title,
        secondary_use_markup=use_markup,
        secondary_text=subtitle,
    )
    dialog.run()
    dialog.hide()


def ask(title, subtitle, use_markup=False):
    dialog = Gtk.MessageDialog(
        buttons=Gtk.ButtonsType.OK_CANCEL,
        text=title,
        secondary_use_markup=use_markup,
        secondary_text=subtitle,
    )
    r = dialog.run()
    dialog.hide()

    return r
