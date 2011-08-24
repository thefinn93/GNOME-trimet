#!/usr/bin/env python

import pygtk
import sys
pygtk.require('2.0')
import gnomeapplet
import gtk
import urllib2
from xml.dom.minidom import parseString
import time

class TransitTracker(gnomeapplet.Applet):

    def cleanup(self,event):
        del self.applet 

    def updateCountdown(self,event):
        if self.i >= self.updateinterval:
            xml = parseString(urllib2.urlopen("http://developer.trimet.org/ws/V1/arrivals?locIDs=" + stopid + "&appID=" + apikey).read())
            self.arrivaltime = int(xml.getElementsByTagName("arrival")[0].getAttribute("estimated"))/1000
            self.i = 0
        else:
            self.i = self.i+1
        eta = time.gmtime(self.arrivaltime-time.time())
        self.button.set_label(str(time.strftime("%H:%M:%S",eta)))
        self.applet.show_all()
        return 1


    def showMenu(self,widget, event, applet):
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            widget.emit_stop_by_name("button_press_event")
            self.create_menu(applet)
        else:
            self.button.set_label("Button press: " + str(event.button))
            self.applet.show_all()

    def create_menu(self,applet):
        propxml="""
			<popup name="button3">
			<menuitem name="Item 3" verb="Preferences" label="_Preferences"/>
			</popup>"""
        verbs = [("Preferences", self.showPrefs)]
        applet.setup_menu(propxml, verbs, None)

    def showPrefs(self,*arguments, **keywords):
        self.prefWindow = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.prefWindow.set_title("Trimet Countdown Preferences")
        self.prefWindow.connect("destroy", gtk.main_quit)
        self.prefWindow.set_border_width(10)
        self.prefButton = gtk.Button("Close")
        self.prefButton.connect_object("clicked", gtk.Widget.destroy, self.prefWindow)
        self.prefWindow.add(self.prefButton)
        self.prefButton.show()
        self.prefWindow.show()



    def __init__(self,applet,iid):
        self.stopid="7500"
        self.apikey="7890FE8AA7CC3A7538F10BDFE"
        self.updateinterval = 30						# Interval at which to hit the Trimet API, in seconds
        self.i = self.updateinterval						# Number of seconds that have passed since last hit
        self.applet = applet
        self.button = gtk.Button()
        self.button.set_relief(gtk.RELIEF_NONE)
        self.button.connect("button_press_event", self.showMenu, applet)
        self.applet.add(self.button)
        self.applet.show_all()
        self.updateCountdown(1)
        gtk.timeout_add(1000, self.updateCountdown, self)


def factory(applet, iid):
    TransitTracker(applet,iid)

if len(sys.argv) == 2:
	if sys.argv[1] == "-w":
		mainWindow = gtk.Window(gtk.WINDOW_TOPLEVEL)
		mainWindow.set_title("Trimet Countdown")
		mainWindow.connect("destroy", gtk.main_quit)
		applet = gnomeapplet.Applet()
		factory(applet, None)
		applet.reparent(mainWindow)
		mainWindow.show_all()
		gtk.main()
		sys.exit()

if __name__ == '__main__':
	print "Starting factory"
	gnomeapplet.bonobo_factory("OAFIID:GNOME_TrimetArrivals_Factory", gnomeapplet.Applet.__gtype__, "Monitor Trimet arrvials", "1.0", factory)
