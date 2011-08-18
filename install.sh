#!/bin/bash
cp trimet.server /usr/lib/bonobo/servers/trimet.server
chmod +x trimet.py
cp trimet.py /usr/bin/trimet.py
cp trimet-48.png /usr/share/icons/gnome/48x48/apps/trimet.png
echo "Thank you for riding Trimet"
