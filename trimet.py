#!/usr/bin/env python

import pygtk
import sys
pygtk.require('2.0')
import gnomeapplet
import gtk
import urllib2
from xml.dom.minidom import parseString
import time
import ConfigParser
import os

class TransitTracker(gnomeapplet.Applet):

    def cleanup(self,event):
        del self.applet 

    def updateCountdown(self,event):
        if self.i >= self.updateinterval:
            print "checking for updates..."
            self.arrivaltime = False
            xml = parseString(urllib2.urlopen("http://developer.trimet.org/ws/V1/arrivals?locIDs=" + self.stopid + "&appID=" + self.apikey).read())
            print "parsing response..."
            if len(xml.getElementsByTagName("arrival")) > 0:
                if xml.getElementsByTagName("arrival")[0].getAttribute("estimated") != "":
                    self.arrivaltime = int(xml.getElementsByTagName("arrival")[0].getAttribute("estimated"))/1000
            self.i = 0
        else:
            self.i = self.i+1
        if self.arrivaltime:
            eta = time.gmtime(self.arrivaltime-time.time())
            self.button.set_label(str(time.strftime("%H:%M:%S",eta)))
        else:
            self.button.set_label("No Estimate Available")
        self.applet.show_all()
        return 1

    def forceUpdate(self):							# Forces the applet to hit the Trimet API
        self.i = self.updateinterval

    def showMenu(self,widget, event, applet):
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            widget.emit_stop_by_name("button_press_event")
            self.create_menu(applet)
        elif event.type == gtk.gdk.BUTTON_PRESS and event.button == 1:
            self.forceUpdate()
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
        self.prefsWindow = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.prefsWindow.set_title("Trimet Countdown Preferences")
        self.prefsWindow.connect("destroy", gtk.main_quit)
        self.prefsWindow.set_border_width(10)

        mainBox = gtk.VBox()

        apibox = gtk.HBox()
        apilabel = gtk.Label("Trimet API key:")
        apibox.pack_start(apilabel,False,False,0)
        apilabel.show()
        self.prefsAPIkey = gtk.Entry(max=25)
        self.prefsAPIkey.set_text(self.apikey)
        self.prefsAPIkey.connect("focus_out_event",self.savePrefs)
        apibox.pack_start(self.prefsAPIkey,True,False,0)
        self.prefsAPIkey.show()
        mainBox.pack_start(apibox,False,False,0)
        apibox.show()

        stopIDbox = gtk.HBox()
        stopIDlabel = gtk.Label("Trimet Stop ID:")
        stopIDbox.pack_start(stopIDlabel,False,False,0)
        stopIDlabel.show()
        self.prefsStopID = gtk.Entry(max=0)
        self.prefsStopID.set_text(self.stopid)
        self.prefsStopID.connect("focus_out_event",self.savePrefs)
        stopIDbox.pack_start(self.prefsStopID,True,False,0)
        self.prefsStopID.show()
        mainBox.pack_start(stopIDbox,False,False,0)
        stopIDbox.show()

        updateintervalbox = gtk.HBox()
        updateintervallabel = gtk.Label("Update Interval:")
        updateintervalbox.pack_start(updateintervallabel,False,False,0)
        updateintervallabel.show()
        self.prefsupdateinterval = gtk.Entry(max=0)
        self.prefsupdateinterval.set_text(str(self.updateinterval))
        self.prefsupdateinterval.connect("focus_out_event",self.savePrefs)
        updateintervalbox.pack_start(self.prefsupdateinterval,True,False,0)
        self.prefsupdateinterval.show()
        mainBox.pack_start(updateintervalbox,False,False,0)
        updateintervalbox.show()

        self.prefsClose = gtk.Button("Close")
        self.prefsClose.connect_object("clicked", gtk.Widget.destroy, self.prefsWindow)
        mainBox.pack_start(self.prefsClose,False,False,0)
        self.prefsClose.show()

        mainBox.show()
        self.prefsWindow.add(mainBox)
        self.prefsWindow.show()

    def savePrefs(self,widget,data):
        self.apikey = self.prefsAPIkey.get_text()
        self.stopid = self.prefsStopID.get_text()
        self.updateinterval = int(self.prefsupdateinterval.get_text())
        config = ConfigParser.ConfigParser()
        config.add_section("trimet")
        config.set("trimet","stopid",self.stopid)
        config.set("trimet","apikey",self.apikey)
        config.set("trimet","interval",self.updateinterval)
        configfile = open(os.path.expanduser("~/.config/trimetApplet/preferences"),"w")
        config.write(configfile)
        configfile.close()

    def readPrefs(self):
        configPath = os.path.expanduser("~/.config/trimetApplet/preferences")
        if os.path.exists(configPath):
            configfile = open(configPath)
            config = ConfigParser.ConfigParser()
            config.readfp(configfile)
            configfile.close()
            self.stopid = config.get("trimet","stopid")
            self.apikey = config.get("trimet","apikey")
            self.updateinterval = config.getint("trimet","interval")
        else:
            self.stopid="7500"
            self.apikey="7890FE8AA7CC3A7538F10BDFE"
            self.updateinterval = 30
            if not os.path.isdir(os.path.expanduser("~/.config/trimetApplet/")):
                os.mkdir(os.path.expanduser("~/.config/trimetApplet"))
            config = ConfigParser.ConfigParser()
            config.add_section("trimet")
            config.set("trimet","stopid",self.stopid)
            config.set("trimet","apikey",self.apikey)
            config.set("trimet","interval",self.updateinterval)
            configfile = open(configPath,"w")
            config.write(configfile)
            configfile.close()

    def __init__(self,applet,iid):
        self.readPrefs()
        self.i = (self.updateinterval - 1)
        self.applet = applet
        self.button = gtk.Button()
        self.button.set_label("Checking for updates...")
        self.button.set_relief(gtk.RELIEF_NONE)
        self.button.connect("button_press_event", self.showMenu, applet)
        self.applet.add(self.button)
        self.applet.show_all()
        self.arrivaltime = False
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
