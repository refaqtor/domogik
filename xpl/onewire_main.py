#!/usr/bin/python
# -*- encoding:utf-8 -*-

# Copyright 2008 Domogik project

# This file is part of Domogik.
# Domogik is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Domogik is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Domogik.  If not, see <http://www.gnu.org/licenses/>.

# Author: Maxence Dunnewind <maxence@dunnewind.net>

# $LastChangedBy: mschneider $
# $LastChangedDate: 2008-07-23 21:42:29 +0200 (mer. 23 juil. 2008) $
# $LastChangedRevision: 100 $

from xPLAPI import *
from onewire import *

myow = OneWire()
myow.set_cache_use(False)
myxpl = Manager(ip = "192.168.1.22",port = 5034)
my_temp_message = Message()
my_temp_message.set_type("xpl-trig")
my_temp_message.set_schema("sensor.basic")
my_x10_mess = Message()
my_x10_mess.set_type("xpl-cmnd")
my_x10_mess.set_schema("x10.basic")

def test():
    for  (i, t, v) in myow.get_temperature():
        print "ITEM : "+ i +" - " + v
        my_temp_message.set_data_key("device", i)
        my_temp_message.set_data_key("type", t)
        my_temp_message.set_data_key("current", v) 
        myxpl.send(my_temp_message)
        if float(v) > 23.0:
            my_x10_mess.set_data_key("device","A3")
            my_x10_mess.set_data_key("command","on")
            myxpl.send( my_x10_mess )


t = xPLTimer(15, test)
t.start()

