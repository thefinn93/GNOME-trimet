#!/usr/bin/env python

import pygtk
import sys
pygtk.require('2.0')

import gnomeapplet
import gtk

def factory(applet, iid):
	button = gtk.Button()
	button.set_relief(gtk.RELIEF_NONE)
	button.set_label("I love Trimet")
	button.connect("button_press_event", showMenu, applet)
	applet.add(button)
	applet.show_all()
	return True

def showMenu(widget, event, applet):
	if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
		widget.emit_stop_by_name("button_press_event")
		create_menu(applet)

def create_menu(applet):
	propxml="""
			<popup name="button3">
			<menuitem name="Item 3" verb="About" label="_About" pixtype="stock" pixname="gtk-about"/>
			</popup>"""
	verbs = [("About", showAboutDialog)]
	applet.setup_menu(propxml, verbs, None)

def showAboutDialog(*arguments, **keywords):
	pass

if len(sys.argv) == 2:
	if sys.argv[1] == "run-in-window":
		mainWindow = gtk.Window(gtk.WINDOW_TOPLEVEL)
		mainWindow.set_title("Ubuntu System Panel")
		mainWindow.connect("destroy", gtk.main_quit)
		applet = gnomeapplet.Applet()
		factory(applet, None)
		applet.reparent(mainWindow)
		mainWindow.show_all()
		gtk.main()
		sys.exit()

if __name__ == '__main__':
	print "Starting factory"
	gnomeapplet.bonobo_factory("OAFIID:Trimet_Factory", gnomeapplet.Applet.__gtype__, "Monitor Trimet arrvials", "1.0", factory)
