#!/usr/bin/env python

""" config.py: System-specific settings and paths set here, then read in our codebase """

import socket

__author__ = "Duncan McElfresh and John P. Dickerson"

hostname = socket.gethostname()
if hostname=='spooktop':
    snapdir = r'/home/spook/code/snap/'
elif hostname=='DUNCAN-RUN-"HOSTNAME"-AND-PUT-THAT-STRING-HERE':
    snapdir = r'/Users/duncan/Documents/Software/snap/'
else:
    snapdir = r'/YOUR/SNAP/INSTALL/HERE/'

