#!/usr/bin/env python

stopid="7500"
apikey=""
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

    def __init__(self,applet,iid):
        self.updateinterval = 10
        self.i = 10
        self.applet = applet
        self.button = gtk.Button()
        self.button.set_relief(gtk.RELIEF_NONE)
#       self.button.connect("button_press_event", showMenu, applet)
        self.applet.add(self.button)
        self.applet.show_all()
        self.updateCountdown(1)
        gtk.timeout_add(1000, self.updateCountdown, self)


def factory(applet, iid):
    TransitTracker(applet,iid)

def showMenu(widget, event, applet):
	if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
		widget.emit_stop_by_name("button_press_event")
		create_menu(applet)

def create_menu(applet):
	propxml="""
			<popup name="button3">
			<menuitem name="Item 3" verb="About" label="_About" pixtype="stock" pixname="gtk-about"/>
			<menuitem name="Item 3" verb="Preferences" label="_Preferences" />
			</popup>"""
	verbs = [("About", showAboutDialog)]
	applet.setup_menu(propxml, verbs, None)

def showAboutDialog(*arguments, **keywords):
	pass

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
	gnomeapplet.bonobo_factory("OAFIID:Trimet_Factory", gnomeapplet.Applet.__gtype__, "Monitor Trimet arrvials", "1.0", factory)
