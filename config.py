#!/usr/bin/env python2.7
import os
import json

try:
	jsonconfig = json.load(open(os.path.expanduser('~/.config/transmgmt/config.json')))
except IOError as e:
    print "I/O error({0}): {1}".format(e.errno, e.strerror)
    if not os.path.isdir(os.path.expanduser('~/.config/transmgmt')):
    	os.makedirs(os.path.expanduser('~/.config/transmgmt'))
    jsonconfig = {'clients' : {'transmission.01': {'directory':'/home/user/transmission-daemon/01','password':'p4$$w0rd'}}}
    json.dump(jsonconfig, open(os.path.expanduser('~/.config/transmgmt/config.json'), 'w'), indent=4, sort_keys=True)
