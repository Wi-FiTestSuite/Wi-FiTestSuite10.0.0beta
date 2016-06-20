###############################################################################
#
# Copyright (c) 2016 Wi-Fi Alliance
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY
# SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER
# RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT,
# NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE
# USE OR PERFORMANCE OF THIS SOFTWARE.
#
###############################################################################

#!/usr/bin/env python
#!/usr/bin/env python
"""Database APIs for mapping and checking user mode features"""
from __future__ import print_function
from __future__ import division
import sqlite3
import os
from database import DB
import common
import logging

_current_mode = None #"atl" "matl" "precert" "plugfest"

class UserModeObj(object):
    """User mode object is used for storing usermode with the user mode DAO."""

    def __init__(self, 
                 mode=None,
                 description=None,
                 edit_scripts=None,
                 validation=None,
                 tms=None,
                 scripts_read_access=None,
                 scripts_write_access=None,
                 init_map_read_access=None,
                 multi_user=None,
                 no_sigma_support=None,
                 result_protection=None,
                 script_protection=None,
                 app_id=None):
        self.kwargs = {}
        self.mode = self.kwargs.setdefault('mode', mode)
        self.description = self.kwargs.setdefault('description', description)
        self.edit_scripts = self.kwargs.setdefault('edit_scripts', edit_scripts)
        self.validation = self.kwargs.setdefault('validation', validation)
        self.tms = self.kwargs.setdefault('tms', tms)
        self.scripts_read_access = self.kwargs.setdefault('scripts_read_access', scripts_read_access)
        self.scripts_write_access = self.kwargs.setdefault('scripts_write_access', scripts_write_access)
        self.init_map_read_access = self.kwargs.setdefault('init_map_read_access', init_map_read_access)
        self.multi_user = self.kwargs.setdefault('multi_user', multi_user)
        self.no_sigma_support = self.kwargs.setdefault('no_sigma_support', no_sigma_support)
        self.result_protection = self.kwargs.setdefault('result_protection', result_protection)
        self.script_protection = self.kwargs.setdefault('script_protection', script_protection)
        self.app_id = self.kwargs.setdefault('app_id', app_id)

    def __repr__(self):
        S = []
        S2 = []
        S.append('UserModeObj(')
        for key, value in self.kwargs.iteritems():
            S2.append('%s=%s' % (key, value))
        return ''.join(S) + ', '.join(S2) + ')'

    def __str__(self):
        return self.__repr__()

class UserModeService(object):
    """
    UserModeService provides access to SettingsDAO. Recommended usage is with
    the with-statement.
    """

    def __init__(self, usermodeobj=None):
        self.usermodedao = UserModeDAO(usermodeobj)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.usermodedao.db.close()

    def get_usermodeDAO(self):
        """Returns access to SettingsDAO object."""
        return self.usermodedao

class UserModeDAO(object):
    """UserModeDAO provides methods for changing user mode settings"""

    def __init__(self, usermodeobj=None):
        self.usermodeobj = usermodeobj
        self.dbpath = os.path.join(common.GlobalConfigFiles.DBPATH,
            common.GlobalConfigFiles.USERMODEDBFILE)
        self.db = UserModeDB(self.dbpath)

    def get_current_mode(self):
        """Returns the string value of the current user mode"""
        global _current_mode
        return _current_mode

    def set_current_mode(self, mode):
        """
        Sets the current user mode and returns the value of the current user
        mode. If the mode is invalid, then it returns -1.
        """
        global _current_mode
        valid_modes = set(self.db.get_available_modes())
        if mode not in valid_modes:
            logging.error('Could not set unknown mode "%s" to current user mode' % (mode))
            return -1
        else:
            _current_mode = mode
            return _current_mode

    def get_available_modes(self):
        """Returns a list of the currently available user modes"""
        return self.db.get_available_modes()

    def get_mode_description(self, mode):
        """Returns the string description of the requested user mode"""
        modes = set(self.db.get_available_modes())
        if mode not in modes:
            logging.error('Could not get user mode description for "%s" user mode' % (mode))
            return ''
        else:
            return self.db.get_mode_description(mode)

    def check_feature(self, feat):
        """
        Checks to see if the given feature is true or false for the current 
        user mode
        """
        global _current_mode
        return self.db.check_feature(feat, _current_mode)

class UserModeDB(DB):

        def __init__(self, dbpath):
            super(UserModeDB, self).__init__(dbpath)
            self.dbpath = dbpath
            self.conn = None
            self.c = None
            self.connect()
            self.columns = set()
            self.execute('SELECT * FROM usermode')
            for description in self.c.description:
                self.columns.add(description[0])
        
        def create(self):
            try:
                self.execute('''CREATE TABLE "usermode" (
                            "mode" TEXT PRIMARY KEY,
                            "description" INTEGER NOT NULL,
                            "edit_scripts" INTEGER NOT NULL,
                            "validation" INTEGER NOT NULL,
                            "tms" INTEGER NOT NULL,
                            "scripts_read_access" INTEGER NOT NULL,
                            "scripts_write_access" INTEGER NOT NULL,
                            "init_map_read_access" INTEGER NOT NULL,
                            "multi_user" INTEGER NOT NULL,
                            "no_sigma_support" INTEGER NOT NULL,
                            "result_protection" INTEGER NOT NULL,
                            "script_protection" INTEGER NOT NULL,
                            "app_id" INTEGER NOT NULL);''',
                             commit=True)
            except (sqlite3.Error) as e:
                print(e)
                
        def add_usermode_entry(self, mode, description, edit_scripts, validation, tms, scripts_read_access,
                        scripts_write_access, init_map_read_access, multi_user, no_sigma_support, result_protection,
                        script_protection, app_id):
            """Adds a user mode for UWTS and creates mapping of features relevant for specific user modes"""
            self.execute('''INSERT INTO usermode (mode, description, edit_scripts, validation, tms, scripts_read_access,
                        scripts_write_access, init_map_read_access, multi_user, no_sigma_support, result_protection,
                        script_protection, app_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                         (mode, description, edit_scripts, validation, tms, scripts_read_access,
                        scripts_write_access, init_map_read_access, multi_user, no_sigma_support, result_protection,
                        script_protection, app_id), commit=True)
            
        def get_modes(self, feat):
            """Returns the modes of an entry when given the feature"""
            query = "SELECT mode FROM usermode WHERE " + feat + "=1"
            self.execute(query)
            fa = self.c.fetchall()
            modes = []
            for mode in fa:
                modes.append(mode['mode'])
            return modes
        
        def get_available_modes(self):
            """Returns a list of user modes"""
            self.execute('SELECT mode FROM usermode')
            fa = self.c.fetchall()
            avail_modes = []
            for mode in fa:
                avail_modes.append(mode['mode'])
            return avail_modes
        
        def get_mode_description(self, mode):
            """Get mode description"""
            self.execute('''SELECT description FROM usermode WHERE mode=?''', (mode,))
            f = self.c.fetchone()
            if f is not None:
                return f['description']
            else:
                return ''
        
        def check_feature(self, feat, mode):
            """Checks if the specific feature is available in current mode"""
            query = "SELECT " + feat + " FROM usermode WHERE mode= '" + mode + "'"
            self.execute(query)
            f = self.c.fetchone()
            if f is not None:
                if f[feat] == 1:
                    return True
                else:
                    return False
            else:
                #Database returned None, thus feat is not present
                return False
    
if __name__ == '__main__':
    if os.path.exists('usermode.db3'):
        os.unlink('usermode.db3')
    # Various unit tests:
    usermode = UserModeDB('usermode.db3')
    #usermode.create()
    usermode.add_usermode_entry('precert', 'If no default mode is set, UWTS will default to mode pre-certification',
                                1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0)
    usermode.add_usermode_entry('atl', 'Advance Testing Labs', 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0)
    usermode.add_usermode_entry('matl-mrcl', 'Member Labs', 0, 1, 0, 1, 0, 1, 0, 0, 1, 1, 1)
    usermode.add_usermode_entry('plugfest', 'Only used during Plugfests', 1, 0, 1, 1, 0, 1, 0, 1, 0, 0, 0)
    x1 = usermode.get_modes('validation')
    x2 = usermode.get_available_modes()
    x3 = usermode.get_mode_description('atl')
    x4 = usermode.check_feature('validation')
    usermode.close()
