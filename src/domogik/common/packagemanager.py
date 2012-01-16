#!/usr/bin/python
# -*- coding: utf-8 -*-

""" This file is part of B{Domogik} project (U{http://www.domogik.org}).

License
=======

B{Domogik} is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

B{Domogik} is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Domogik. If not, see U{http://www.gnu.org/licenses}.

Plugin purpose
==============

Package manager for domogik
A package could be a plugin, a web ui widget, etc

Implements
==========

TODO

@author: Fritz <fritz.smh@gmail.com>
@copyright: (C) 2007-2010 Domogik project
@license: GPL(v3)
@organization: Domogik
"""

from domogik.common.packagexml import PackageXml, PackageException
from domogik.common.packagedata import PackageData
from domogik.common.configloader import Loader
from xml.dom import minidom
import traceback
import tarfile
import tempfile
import os
import pwd
from subprocess import Popen
import urllib
import shutil
import sys
from domogik.common import logger
from distutils2.version import NormalizedVersion, IrrationalVersionError


from domogik import __path__ as domopath
SRC_PATH = "%s/" % os.path.dirname(os.path.dirname(domopath[0]))
PLG_XML_PATH = "src/share/domogik/plugins/"
TMP_EXTRACT_DIR = "%s/%s" % (tempfile.gettempdir(), "domogik-pkg-mgr")
CONFIG_FILE = "%s/.domogik/domogik.cfg" % os.getenv("HOME")
REPO_SRC_FILE = "%s/.domogik/sources.list" % os.getenv("HOME")
REPO_LST_FILE_HEADER = "Domogik Repository"
REPO_CACHE_DIR = "%s/.domogik/cache" % os.getenv("HOME")
PKG_CACHE_DIR = "%s/.domogik/pkg-cache" % os.getenv("HOME")

cfg = Loader('domogik')
config = cfg.load()
conf = dict(config[1])
if conf.has_key('package_path'):
    INSTALL_PATH = conf['package_path']
else:
    INSTALL_PATH = "%s/.domogik/" % os.getenv("HOME")

cfg = Loader('rest')
config = cfg.load()
conf = dict(config[1])
REST_URL = "http://%s:%s" % (conf["rest_server_ip"], conf ["rest_server_port"])

PLUGIN_XML_PATH = "%s/packages/plugins" % INSTALL_PATH
EXTERNAL_XML_PATH = "%s/packages/externals" % INSTALL_PATH

# type of part for a plugin
PKG_PART_XPL = "xpl"
PKG_PART_RINOR = "rinor"

class PackageManager():
    """ Tool to create packages
    """

    def __init__(self):
        """ Init tool
        """
        l = logger.Logger("package-manager")
        self._log = l.get_logger("package-manager")

    def log(self, message):
        """ Log and print message
            @param message : data to log
        """
        self._log.info(message)
        print(message)


    def _create_package_for_plugin(self, id, output_dir, force):
        """ Create package for a plugin
            1. read xml file to get informations and list of files
            2. generate package
            @param id : name of plugin
            @param output_dir : target directory for package
            @param force : False : ask for confirmation
        """
        self.log("Plugin id : %s" % id)

        try:
            plg_xml = PackageXml(id)
        except:
            self.log(str(traceback.format_exc()))
            return

        # check release format
        try:
            NormalizedVersion(plg_xml.release)
        except:
            self.log("Plugin release '%s' is not valid. Exiting." % plg_xml.release)
            return
        try:
            NormalizedVersion(plg_xml.domogik_min_release)
        except:
            self.log("Domogik min release '%s' is not valid. Exiting." % plg_xml.domogik_min_release)
            return

        self.log("Xml file OK")

        # check type == plugin
        if plg_xml.type != "plugin":
            self.log("Error : this package is not a plugin")
            return

        # display plugin informations
        plg_xml.display()

        # check file existence
        if plg_xml.files == []:
            self.log("There is no file defined : the package won't be created")
            return

        if force == False:
            self.log("\nAre these informations OK ?")
            resp = raw_input("[o/N]")
            if resp.lower() != "o":
                self.log("Exiting...")
                return

        # Copy xml file in a temporary location in order to complete it
        xml_tmp_file = "%s/plugin-%s-%s.xml" % (tempfile.gettempdir(),
                                                plg_xml.id,
                                                plg_xml.release)
        shutil.copyfile(plg_xml.info_file, xml_tmp_file)
        
        # Update info.xml with generation date
        plg_xml.set_generated(xml_tmp_file)

        # Create .tgz
        self._create_tar_gz("plugin-%s-%s" % (plg_xml.id, plg_xml.release), 
                            output_dir,
                            plg_xml.all_files, 
                            xml_tmp_file,
                            plg_xml.icon_file)

    def _create_package_for_external(self, id, output_dir, force):
        """ Create package for a external
            1. read xml file to get informations and list of files
            2. generate package
            @param id : name of external
            @param output_dir : target directory for package
            @param force : False : ask for confirmation
        """
        self.log("Hardware id : %s" % id)

        try:
            plg_xml = PackageXml(id, pkg_type = "external")
        except:
            self.log(str(traceback.format_exc()))
            return

        # check release format
        try:
            NormalizedVersion(plg_xml.release)
        except:
            self.log("Plugin release '%s' is not valid. Exiting." % plg_xml.release)
            return
        try:
            NormalizedVersion(plg_xml.domogik_min_release)
        except:
            self.log("Domogik min release '%s' is not valid. Exiting." % plg_xml.domogik_min_release)
            return

        self.log("Xml file OK")

        if plg_xml.type != "external":
            self.log("Error : this package is not an external member")
            return

        # display external informations
        plg_xml.display()

        # check file existence
        if plg_xml.files == []:
            self.log("There is no file defined : the package won't be created")
            return

        if force == False:
            self.log("\nAre these informations OK ?")
            resp = raw_input("[o/N]")
            if resp.lower() != "o":
                self.log("Exiting...")
                return

        # Copy xml file in a temporary location in order to complete it
        xml_tmp_file = "%s/external-%s-%s.xml" % (tempfile.gettempdir(),
                                                plg_xml.id,
                                                plg_xml.release)
        shutil.copyfile(plg_xml.info_file, xml_tmp_file)
        
        # Update info.xml with generation date
        plg_xml.set_generated(xml_tmp_file)

        # Create .tgz
        self._create_tar_gz("external-%s-%s" % (plg_xml.id, plg_xml.release), 
                            output_dir,
                            plg_xml.all_files, 
                            xml_tmp_file,
                            plg_xml.icon_file)


    def _create_tar_gz(self, name, output_dir, files, info_file = None, icon_file = None):
        """ Create a .tar.gz file anmmed <name.tgz> which contains <files>
            @param name : file name
            @param output_dir : if != None, the path to put .tar.gz
            @param files : table of file names to add in tar.gz
            @param info_file : path for info.xml file
            @param icon_file : path for icon.png file
        """
        if output_dir == None:
            my_tar = "%s/%s.tgz" % (tempfile.gettempdir(), name)
        else:
            my_tar = "%s/%s.tgz" % (output_dir, name)
        self.log("Generating package : '%s'" % my_tar)
        try:
            tar = tarfile.open(my_tar, "w:gz")
            for my_file in files:
                path =  str(my_file["path"])
                self.log("- %s" % path)
                tar.add(SRC_PATH + path, arcname = path)
            if info_file != None:
                self.log("- info.xml")
                tar.add(info_file, arcname="info.xml")
            if icon_file != None:
                self.log("- icon.png")
                tar.add(icon_file, arcname="icon.png")
            tar.close()

            # delete temporary xml file
            if info_file != None:
                os.unlink(info_file) 
        except: 
            msg = "Error generating package : %s : %s" % (my_tar, traceback.format_exc())
            self.log(msg)
            # delete temporary xml file
            if info_file != None:
                os.unlink(info_file) 
            raise PackageException(msg)
        self.log("OK")
    

    def cache_package(self, cache_folder, pkg_type, id, release):
        """ Download package to put it in cache
            @param cache_folder : folder in which we want to cache the file
            @param pkg_type : package type
            @param id : package id
            @param release : package release
        """
        package = "%s-%s" % (pkg_type, id)
        pkg, status = self._find_package(package, release)
        if status != True:
            return False
        # download package
        path = pkg.package_url
        dl_path = "%s/%s-%s-%s.tgz" % (cache_folder, pkg_type, id, release)
        self.log("Caching package : '%s' to '%s'" % (path, dl_path))
        urllib.urlretrieve(path, dl_path)
        path = dl_path
 
        # extract package to update xml with source repo
        my_tmp_dir = "%s/%s/" % (TMP_EXTRACT_DIR, id)
        self._create_folder(my_tmp_dir)
        self._extract_package(path, my_tmp_dir)

        # update xml
        xml_path = "%s/src/share/domogik/%ss/%s.xml" % (my_tmp_dir, pkg_type, id)
        pkg_xml = PackageXml(path = xml_path)
        pkg_xml.set_repo_source(pkg.source)

        # recreate tgz
        my_tar = path
        self.log("Generating package : '%s'" % my_tar)
        try:
            tar = tarfile.open(my_tar, "w:gz")

            for root, dirnames, filenames in os.walk(my_tmp_dir):
                for filename in filenames:
                    src_file = os.path.join(root, filename)
                    dst_file = src_file.replace(my_tmp_dir, "")
                    tar.add(name = src_file, arcname = dst_file)
            tar.close()
        except: 
            msg = "Error generating package : %s : %s" % (my_tar, traceback.format_exc())
            self.log(msg)
            raise PackageException(msg)
        self.log("OK")
        return True
        




        #self._clean_folder(my_tmp_dir)
        self.log("Package in cache : %s" % path)

    def _create_folder(self, folder):
        """ Try to create a folder (does nothing if it already exists)
            @param folder : folder path
        """
        self.log("Creating directory : %s" % folder)
        try:
            if os.path.isdir(folder) == False:
                os.makedirs(folder)
        except:
            msg = "Error while creating temporary folder '%s' : %s" % (folder, traceback.format_exc())
            self.log(msg)
            raise PackageException(msg)

    def install_package(self, path, release = None, package_part = PKG_PART_XPL):
        """ Install a package
            0. Eventually download package
            1. Extract tar.gz
            2. Install package
            3. Insert data in database
            @param path : path for tar.gz
            @param release : release to install (default : highest)
            @param package_part : PKG_PART_XPL (for manager), PKG_PART_RINOR (for RINOR)
        """
        source = path
        self.log("Start install for part '%s' of '%s'" % (package_part, path))
        if path[0:6] == "cache:":
            path = "%s/package/download/%s" % (REST_URL, path[6:])

        if path[0:5] == "repo:":
            pkg, status = self._find_package(path[5:], release)
            if status != True:
                return status
            path = pkg.package_url

        # get package name
        if path[0:4] == "http": # special process for a http path
            id = full_name = '-'.join(path.split("/")[-3:])
            print("id=%s" % full_name)
        else:
            full_name = os.path.basename(path)
            # twice to remove first .gz and then .tar
            id =  os.path.splitext(full_name)[0]
            id =  os.path.splitext(id)[0] 

        self.log("Ask for installing package id : %s" % id)

        # get temp dir to extract data
        my_tmp_dir_dl = TMP_EXTRACT_DIR
        my_tmp_dir = "%s/%s" % (my_tmp_dir_dl, id)
        self._create_folder(my_tmp_dir)

        # Check if we need to download package
        if path[0:4] == "http":
            dl_path = "%s/%s.tgz" % (my_tmp_dir_dl, full_name)
            self.log("Downloading package : '%s' to '%s'" % (path, dl_path))
            urllib.urlretrieve(path, dl_path)
            path = dl_path
            self.log("Package downloaded : %s" % path)

        # extract in tmp directory
        self.log("Extracting package...")
        try:
            self._extract_package(path, my_tmp_dir)
        except:
            msg = "Error while extracting package '%s' : %s" % (path, traceback.format_exc())
            self.log(msg)
            raise PackageException(msg)
        self.log("Package successfully extracted.")

        # get xml informations
        pkg_xml = PackageXml(path = "%s/info.xml" % my_tmp_dir)

        # check compatibility with domogik installed release
        __import__("domogik")
        dmg = sys.modules["domogik"]
        self.log("Domogik release = %s" % dmg.__version__)
        self.log("Minimum Domogik release required for package = %s" % pkg_xml.domogik_min_release)
        print("%s < %s" % ( pkg_xml.domogik_min_release , dmg.__version__))
        if pkg_xml.domogik_min_release > dmg.__version__:
            msg = "This package needs a Domogik release >= %s. Actual is %s. Installation ABORTED!" % (pkg_xml.domogik_min_release, dmg.__version__)
            self.log(msg)
            raise PackageException(msg)

        # create install directory
        self._create_folder(INSTALL_PATH)

        # install plugin in $HOME
        self.log("Installing package (%s)..." % pkg_xml.type)
        try:
            if pkg_xml.type in ('plugin', 'external'):
                self._install_plugin_or_external(my_tmp_dir, INSTALL_PATH, pkg_xml.type, package_part)
            else:
                raise "Package type '%s' not installable" % pkg_xml.type
        except:
            msg = "Error while installing package : %s" % (traceback.format_exc())
            self.log(msg)
            raise PackageException(msg)
        self.log("Package successfully extracted.")

        # insert data in database
        if pkg_xml.type in ('plugin', 'external'):
            if package_part == PKG_PART_RINOR:
                self.log("Insert data in database...")
                pkg_data = PackageData("%s/info.xml" % my_tmp_dir, custom_path = CONFIG_FILE)
                pkg_data.insert()

        self.log("Package installation finished")
        return True


    def uninstall_package(self, pkg_type, id):
        """ Uninstall a package
            For the moment, we will only delete the package xml file for 
            plugins and external
            @param pkg_type : package type
            @param id : package id
        """
        self.log("Start uninstall for package '%s-%s'" % (type, id))
        self.log("Only xml description file will be deleted in this Domogik version")

        try:
            if pkg_type in ('plugin'):
                os.unlink("%s/packages/plugins/%s.xml" %(INSTALL_PATH, id))
            elif pkg_type in ('external'):
                os.unlink("%s/packages/externals/%s.xml" %(INSTALL_PATH, id))
            else:
                raise "Package type '%s' not uninstallable" % pkg_type
        except:
            msg = "Error while unstalling package : %s" % (traceback.format_exc())
            self.log(msg)
            raise PackageException(msg)
        self.log("Package successfully uninstalled.")

        return True


    def _extract_package(self, pkg_path, extract_path):
        """ Extract package <pkg_path> in <extract_path>
            @param pkg_path : path to package
            @param extract_path : path for extraction
        """
        tar = tarfile.open(pkg_path)
        # check if there is no .. or / in files path
        for fic in tar.getnames():
            if fic[0:1] == "/" or fic[0:2] == "..":
                msg = "Error while extracting package '%s' : filename '%s' in tgz not allowed" % (pkg_path, fic)
                self.log(msg)
                raise PackageException(msg)
        tar.extractall(path = extract_path)
        tar.close()


    def _install_plugin_or_external(self, pkg_dir, install_path, pkg_type, package_part):
        """ Install plugin
            @param pkg_dir : directory where package is extracted
            @param install_path : path where we install packages
            @param pkg_type : plugin, external
            @param pkg_id : package id
            @param package_part : PKG_PART_XPL (for manager), PKG_PART_RINOR (for RINOR)
            @param repo_source : path from which the package comes
        """

        ### create needed directories
        # create install directory
        self.log("Creating directories for %s..." % pkg_type)
        plg_path = "%s/packages/" % (install_path)
        self._create_folder(plg_path)

        ### copy files
        self.log("Copying files for %s..." % pkg_type)
        try:
            # xpl/* and plugins/*.xml are installed on target host 
            if package_part == PKG_PART_XPL:
                if pkg_type == "plugin":
                    copytree("%s/src/domogik/xpl" % pkg_dir, "%s/xpl" % plg_path, self.log)
                    self._create_init_py("%s/" % plg_path)
                    self._create_init_py("%s/xpl/" % plg_path)
                    self._create_init_py("%s/xpl/bin/" % plg_path)
                    self._create_init_py("%s/xpl/lib/" % plg_path)
                    type_path = "plugins"
                if pkg_type == "external":
                    type_path = "externals"
                print("%s => %s" % ("%s/src/share/domogik/%ss" % (pkg_dir, pkg_type), "%s/%s" % (plg_path, type_path)))
                copytree("%s/src/share/domogik/%ss" % (pkg_dir, pkg_type), "%s/%s" % (plg_path, type_path), self.log)

            # design/*
            # stats/* 
            # url2xpl/* 
            # exernal/* are installed on rinor host
            if package_part == PKG_PART_RINOR:
                copytree("%s/src/share/domogik/design/" % pkg_dir, "%s/design/" % plg_path, self.log)
                copytree("%s/src/share/domogik/url2xpl/" % pkg_dir, "%s/url2xpl/" % plg_path, self.log)
                copytree("%s/src/share/domogik/stats/" % pkg_dir, "%s/stats/" % plg_path, self.log)
                copytree("%s/src/external/" % pkg_dir, "%s/external" % plg_path, self.log)
        except:
            msg = "Error while copying %s files : %s" % (pkg_type, traceback.format_exc())
            self.log(msg)
            raise PackageException(msg)


    def _create_init_py(self, path):
        """ Create __init__.py file in path
            param path : path where we wan to create the file
        """
        try:
            self.log("Create __init__.py file in %s" % path)
            open("%s/__init__.py" % path, "a").close()
        except IOError as (errno, strerror):
            if errno == 2:
                self.log("No directory '%s'" % path)
                return
            raise
        except:
            msg = "Error while creating __init__.py file in %s : %s" % (path, traceback.format_exc())
            self.log(msg)
            raise PackageException(msg)



    def update_cache(self):
        """ update local package cache
        """
        # Get repositories list
        try:
            # Read repository source file and generate repositories list
            repo_list = self.get_repositories_list()
        except:
            self.log(str(traceback.format_exc()))
            return False
             
        # Clean cache folder
        try:
            self._clean_cache(REPO_CACHE_DIR)
        except:
            self.log(str(traceback.format_exc()))
            return False
             
        # for each list, get files and associated xml
        try:
            self._parse_repository(repo_list, REPO_CACHE_DIR)
        except:
            self.log(str(traceback.format_exc()))
            return False

        return True

    def get_repositories_list(self):
        """ Read repository source file and return list
        """
        try:
            repo_list = []
            src_file = open(REPO_SRC_FILE, "r")
            for line in src_file.readlines():
                # if the line is not a comment
                if line.strip()[0] != "#": 
                    repo_list.append({"priority" : line.split()[0],
                                      "url" : line.split()[1]})
            src_file.close()
        except:
            msg = "Error reading source file : %s : %s" % (REPO_SRC_FILE, str(traceback.format_exc()))
            self.log(msg)
            raise PackageException(msg)
        # return sorted list
        return sorted(repo_list, key = lambda k: k['priority'], reverse = True)


    def _clean_cache(self, folder):
        """ If not exists, create <folder>
            Then, clean this folder
            @param folder : cache folder to empty
        """
        # Create folder
        self._create_folder(folder)

        # clean folder
        self._clean_folder(folder)


    def _clean_folder(self, folder):
        """ Delete the content of a folder
            @param folder: folder to clean
        """
        # Clean folder
        try:
            for root, dirs, files in os.walk(folder):
                for f in files:
                    os.unlink(os.path.join(root, f))
                for d in dirs:
                    shutil.rmtree(os.path.join(root, d))
        except:
            msg = "Error while cleaning cache folder '%s' : %s" % (folder, traceback.format_exc())
            self.log(msg)
            raise PackageException(msg)


    def _parse_repository(self, repo_list, cache_folder):
        """ For each repo, get file list, check if the file has the higher 
            priority
            @param repo_list : repositories list
            @param cache_folder : package cache folder
        """
        package_list = []

        # get all packages url
        file_list = []
        for repo in repo_list:
            file_list.extend(self._get_files_list_from_repository(repo["url"], repo["priority"]))

        # for each package, put it in cache if it corresponds to priority
        for file_info in file_list:
            try:
                pkg_xml = PackageXml(url = "%s" % file_info["file"])
                priority = self._get_package_priority_in_cache(pkg_xml.fullname, pkg_xml.release)
                # our package has a prioriry >= to other packages with same name/rel
                if priority == None or priority < file_info["priority"]:
                    self.log("Add '%s (%s)' in cache from %s" % (pkg_xml.fullname, pkg_xml.release, file_info["repo_url"]))
                    pkg_xml.cache_xml(cache_folder, file_info["file"].replace("/xml/", "/download/"), file_info["repo_url"], file_info["priority"])
            except:
                self.log("Error while caching file from '%s' : %s" % (file_info["file"], traceback.format_exc()))

    def _get_files_list_from_repository(self, url, priority):
        """ Read packages.lst on repository
            @param url : repo url
            @param prioriry : repo priority
        """
        try:
            resp = urllib.urlopen("%s" % (url))
            my_list = []
            first_line = True
            for data in resp.readlines():
                if first_line == True:
                    first_line = False
                    if data.strip() != REPO_LST_FILE_HEADER:
                        self.log("This is not a Domogik repository : '%s'" %
                                   (url))
                        break
                else:
                    my_list.append({"file" : "%sxml/%s" % (url, data.strip()),
                                    "priority" : priority,
                                    "repo_url" : url})
            return my_list
        except IOError:
            self.log("Bad url :'%s'" % (url))
            return []


    def get_available_updates(self, pkg_type, id, release):
        """ List all available updates for a package
            @param pkg_type : package type
            @param id : package id
            @param release : package release
        """
        upd_list = []
        for root, dirs, files in os.walk(REPO_CACHE_DIR):
            for f in files:
                if f[-4:] == ".xml":
                    pkg_xml = PackageXml(path = "%s/%s" % (root, f))
                    if pkg_xml.type == pkg_type and pkg_xml.id == id \
                       and pkg_xml.release > release:
                        upd_list.append({"type" : pkg_xml.type,
                                         "id" : pkg_xml.id,
                                         "release" : pkg_xml.release,
                                         "priority" : pkg_xml.priority,
                                         "changelog" : pkg_xml.changelog})
        return upd_list

    def list_packages(self):
        """ List all packages in cache folder 
            Used for printing on command line
        """
        pkg_list = []
        for root, dirs, files in os.walk(REPO_CACHE_DIR):
            for f in files:
                if f[-4:] == ".xml":
                    pkg_xml = PackageXml(path = "%s/%s" % (root, f))
                    pkg_list.append({"fullname" : pkg_xml.fullname,
                                     "release" : pkg_xml.release,
                                     "priority" : pkg_xml.priority,
                                     "desc" : pkg_xml.desc})
        pkg_list =  sorted(pkg_list, key = lambda k: (k['fullname'], 
                                                      k['release']))
        for pkg in pkg_list:
             self.log("%s (%s, prio: %s) : %s" % (pkg["fullname"], 
                                               pkg["release"], 
                                               pkg["priority"], 
                                               pkg["desc"]))

    def _get_package_priority_in_cache(self, fullname, release):
        """ Get priority of a cache package/release
            @param fullname : fullname of package
            @param release : package's release
        """
        for root, dirs, files in os.walk(REPO_CACHE_DIR):
            for f in files:
                pkg_xml = PackageXml(path = "%s/%s" % (root, f))
                if fullname == pkg_xml.fullname and release == pkg_xml.release:
                    return pkg_xml.priority
        return None

    def get_packages_list(self, fullname = None, release = None, pkg_type = None):
        """ List all packages in cache folder 
            and return a detailed list
            @param fullname (optionnal) : fullname of a package
            @param release (optionnal) : release of a package (to use with name)
            @param pkg_type (optionnal) : package type
            Used by Rest
        """
        pkg_list = []
        for root, dirs, files in os.walk(REPO_CACHE_DIR):
            for f in files:
                pkg_xml = PackageXml(path = "%s/%s" % (root, f))
                if fullname == None or (fullname == pkg_xml.fullname and release == pkg_xml.release):
                    if pkg_type == None or pkg_type == pkg_xml.type:
                        pkg_list.append({"id" : pkg_xml.id,
                                     "type" : pkg_xml.type,
                                     "fullname" : pkg_xml.fullname,
                                     "release" : pkg_xml.release,
                                     "source" : pkg_xml.source,
                                     "genrated" : pkg_xml.generated,
                                     "techno" : pkg_xml.techno,
                                     "doc" : pkg_xml.doc,
                                     "desc" : pkg_xml.desc,
                                     "changelog" : pkg_xml.changelog,
                                     "author" : pkg_xml.author,
                                     "email" : pkg_xml.email,
                                     "domogik_min_release" : pkg_xml.domogik_min_release,
                                     "priority" : pkg_xml.priority,
                                     "dependencies" : pkg_xml.dependencies,
                                     "package_url" : pkg_xml.package_url})
        return sorted(pkg_list, key = lambda k: (k['id']))

    def get_installed_packages_list(self):
        """ List all packages in install folder 
            and return a detailed list
        """
        pkg_list = []
        for rep in [PLUGIN_XML_PATH, EXTERNAL_XML_PATH]:
            for root, dirs, files in os.walk(rep):
                for f in files:
                    pkg_xml = PackageXml(path = "%s/%s" % (root, f))
                    # filter on rest
                    if pkg_xml.id != "rest":
                        pkg_list.append({"fullname" : pkg_xml.fullname,
                                         "id" : pkg_xml.id,
                                         "release" : pkg_xml.release,
                                         "type" : pkg_xml.type,
                                         "package-url" : pkg_xml.package_url,
                                         "source" : pkg_xml.source})
        return sorted(pkg_list, key = lambda k: (k['fullname'], 
                                                 k['release']))

    def show_packages(self, fullname, release = None):
        """ Show a package description
            @param fullname : fullname of package (type-name)
            @param release : optionnal : release to display (if several)
        """
        pkg, status = self._find_package(fullname, release)
        if status == True:
            pkg.display()


    def _find_package(self, fullname, release = None):
        """ Find a package and return 
                               - xml data or None if not found
                               - a status : True if ok, a message elsewhere
            @param fullname : fullname of package (type-name)
            @param release : optionnal : release to display (if several)
        """
        pkg_list = []
        for root, dirs, files in os.walk(REPO_CACHE_DIR):
            for f in files:
                pkg_xml = PackageXml(path = "%s/%s" % (root, f))
                if release == None:
                    if fullname == pkg_xml.fullname:
                        pkg_list.append({"fullname" : pkg_xml.fullname,
                                         "release" : pkg_xml.release,
                                         "priority" : pkg_xml.priority,
                                         "source" : pkg_xml.source,
                                         "xml" : pkg_xml})
                else:
                    if fullname == pkg_xml.fullname and release == pkg_xml.release:
                        pkg_list.append({"fullname" : pkg_xml.fullname,
                                         "release" : pkg_xml.release,
                                         "priority" : pkg_xml.priority,
                                         "xml" : pkg_xml})
        if len(pkg_list) == 0:
            if release == None:
                release = "*"
            msg = "No package corresponding to '%s' in release '%s'" % (fullname, release)
            self.log(msg)
            return [], msg
        if len(pkg_list) > 1:
            msg = "Several packages are available for '%s'. Please specify which release you choose" % fullname
            self.log(msg)
            for pkg in pkg_list:
                 self.log("%s (%s, prio: %s)" % (pkg["fullname"], 
                                              pkg["release"],
                                              pkg["priority"]))
            return [], msg

        return pkg_list[0]["xml"], True

    def is_root(self):
        """ return True is current user is root
        """
        if pwd.getpwuid(os.getuid())[0] == "root":
            return True
        return False


##### shutil.copytree fork #####
# the fork is necessary because original function raise an error if a directory
# already exists. In our case, some directories will exists!

class Error(EnvironmentError):
    pass

try:
    WindowsError
except NameError:
    WindowsError = None


def copytree(src, dst, cb_log):
    """Recursively copy a directory tree using copy2().

    The destination directory must not already exist.
    If exception(s) occur, an Error is raised with a list of reasons.

    If the optional symlinks flag is true, symbolic links in the
    source tree result in symbolic links in the destination tree; if
    it is false, the contents of the files pointed to by symbolic
    links are copied.

    The optional ignore argument is a callable. If given, it
    is called with the `src` parameter, which is the directory
    being visited by copytree(), and `names` which is the list of
    `src` contents, as returned by os.listdir():

        callable(src, names) -> ignored_names

    Since copytree() is called recursively, the callable will be
    called once for each directory that is copied. It returns a
    list of names relative to the `src` directory that should
    not be copied.

    XXX Consider this example code rather than the ultimate tool.

    """
    try:
        names = os.listdir(src)
    except OSError as (errno, strerror):
        if errno == 2:
            cb_log("No data for '%s'" % src)
            return
        raise

    try:
        os.makedirs(dst)
    except OSError as (errno, strerror):
        if errno == 17:
            pass
        else:
            raise
    errors = []
    for name in names:
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        cb_log("%s => %s" % (srcname, dstname))
        try:
            if os.path.isdir(srcname):
                copytree(srcname, dstname, cb_log)
            else:
                shutil.copy2(srcname, dstname)
            # XXX What about devices, sockets etc.?
        except (IOError, os.error), why:
            errors.append((srcname, dstname, str(why)))
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error, err:
            errors.extend(err.args[0])
    try:
        shutil.copystat(src, dst)
    except OSError, why:
        if WindowsError is not None and isinstance(why, WindowsError):
            # Copying file access times may fail on Windows
            pass
        else:
            errors.extend((src, dst, str(why)))
    if errors:
        raise Error, errors
    



