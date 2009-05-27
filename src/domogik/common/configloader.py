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

# $LastChangedBy: maxence $
# $LastChangedDate: 2009-03-04 22:29:01 +0100 (mer. 04 mars 2009) $
# $LastChangedRevision: 404 $

#Path to the configuration directory
global config_path

####################################################
#       DON'T CHANGE ANYTHING AFTER THIS LINE      #
####################################################
from os.path import *
import os
import ConfigParser


class Loader():
    '''
    Parse Domogik config files
    '''

    def __init__(self, module_name=None):
        '''
        Load the configuration for a part of the Domogik system
        @param module_name name of the module to load config from
        '''
        self.main_conf_name = "domogik.cfg"
        self.module_name = module_name

    def load(self):
        '''
        Parse the config
        @return pair (main_config, plugin_config)
        '''
        main_result = {}
        config = ConfigParser.ConfigParser()
        config.read([os.getenv("HOME") + "/." + self.main_conf_name,
            '/etc/' + self.main_conf_name,
            '/usr/local/etc/' + self.main_conf_name])
        result = config.items('domogik')
        main_result = {}
        for k, v in result:
            main_result[k] = v
        #Check the plugin conf file if defined
        if self.module_name == None:
            return (main_result, None)

        #To find the plugin conf, we try all files in conf.d until we
        #find the corresponding section
        plugin_conf_dir = config_path + "conf.d/"
        if exists(plugin_conf_dir + self.module_name + ".cfg"):
            plugin_config = config.read(plugin_conf_dir + self.module_name +
                    ".cfg")
            if self.module_name in plugin_config:
                return (main_result, plugin_config[self.module_name])

        #If we are here, it's because the plugin conf file hasn't the same
        #name as the plugin name
        files = os.listdir(plugin_conf_dir)
        for file in files:
            if isfile(plugin_conf_dir + file):
                plugin_config = config.read(plugin_conf_dir + self.module_name
                        + ".cfg")
                if self.module_name in plugin_config:
                    return (main_result, plugin_config[self.module_name])

        #If we're here, there is no plugin config
        return (main_result, None)
