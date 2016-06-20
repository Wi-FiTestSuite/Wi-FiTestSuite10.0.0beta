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
"""Database APIs for accessing and setting persistent application settings"""
from __future__ import print_function
from __future__ import division
import sqlite3
import os
import common
#import logging
from database import DB

class Settings(object):

    def __init__(self, sid=None, key=None, value=None):
        self.kwargs = {}
        self.sid = self.kwargs.setdefault('sid', sid)
        self.key = self.kwargs.setdefault('key', key)
        self.value = self.kwargs.setdefault('value', value)

    def __repr__(self):
        S = []
        S2 = []
        S.append('Settings(')
        for key, value in self.kwargs.iteritems():
            S2.append('%s=%s' % (key, value))
        return ''.join(S) + ', '.join(S2) + ')'
        
    def __str__(self):
        L = [self.sid, self.key, self.value]
        S = []
        for item in L:
            if item is not None:
                S.append(str(item))
        return ' '.join(S)

class SettingsDAO(object):
    """SettingsDAO provides methods for changing settings"""
    
    def __init__(self, settings=None):
        self.settings = settings
        self.dbpath = os.path.join(common.GlobalConfigFiles.DBPATH,
            common.GlobalConfigFiles.SETTINGSDBFILE)
        self.db = SettingsDB(self.dbpath)

    def upsert_setting(self, newsetting):
        """Updates setting if key already exists, otherwise inserts setting"""
        d = {}
        for key, value in self.settings.kwargs.iteritems():
            if key != 'value' and value is not None:
                d[key] = value
        if self.db.key_exists(self.settings.key):
            self.db.update_settings_value(newsetting.value,
                **d)
        else:
            self.db.add_settings_entry(settings.key, settings.value)

    def insert_setting(self, newsetting):
        """Inserts new setting and returns its rowid (sid)"""
        self.db.add_settings_entry(newsetting.key, newsetting.value)
        return self.db.get_last_rowid()

    def get_setting_by_key(self, setting):
        """
        Returns a list of Settings objects when given a Settings object 
        filled in with the target key.
        """
        if self.settings is None:
            #return self.db.get_setting(setting.key)
            return self.db.get_setting(setting.key)
        else:
            return self.db.get_setting(self.settings.key)

class SettingsService(object):
    """
    SettingsService provides access to SettingsDAO. Recommended usage is with
    the with-statement.
    """
    
    def __init__(self, settings=None):
        self.settingsdao = SettingsDAO(settings)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.settingsdao.db.close()
        
    def get_settingsDAO(self):
        """Returns access to SettingsDAO object."""
        return self.settingsdao

class SettingsDB(DB):
    """Settings database API for persistent application settings"""

    def __init__(self, dbpath):
        super(SettingsDB, self).__init__(dbpath)
        self.dbpath = dbpath
        self.conn = None
        self.c = None
        self.connect()
        self.columns = set()
        self.execute('SELECT * FROM settings')
        for description in self.c.description:
            self.columns.add(description[0])

    def create(self):
        try:
            self.execute('''CREATE TABLE "settings" (
                        "sid" INTEGER PRIMARY KEY,
                        "key" TEXT NOT NULL,
                        "value" TEXT NOT NULL);''',
                         commit=True)
        except (sqlite3.Error) as e:
            print(e)

    def add_settings_entry(self, key, value):
        """Adds a setting for UWTS in the form of a key value pair."""
        self.execute('INSERT INTO settings (key, value) VALUES (?, ?)',
                     (key, value), commit=True)

    def get_setting(self, key):
        """
        Retrieves the values for a given key. If there are multiple entries
        for a key, then the values will be returned as a list
        """
        self.execute('SELECT * FROM settings WHERE key=?', (key,))
        #return [val['value'] for val in self.c.fetchall()]
        fa = self.c.fetchall()
        return [Settings(sid=tup['sid'], key=tup['key'], value=tup['value']) for tup in fa]

    def update_settings_value(self, value, **kwargs):
        """
        Updates the contents of a value in settings when given some combination
        of sid and key. Since keys are not unique, it may be necessary to
        include a sid to update a specific value. Failure to provide a sid for
        non-unique keys will result in all values of said key being updated to
        the new value. See method get_sids if needed.
        """
        args = self.create_args(**kwargs)
        constraints = self.create_constraints(**kwargs)
        L = []
        L.append(value)
        [L.append(arg) for arg in args]
        T = tuple(L)
        self.execute('UPDATE settings SET value=? WHERE %s' % (constraints),
                     T, commit=True)

    def get_settings_dictionary(self):
        """
        Returns a dictionary of all settings. Each key will be a key of the
        dictionary. For keys where there are multiple values, the values
        will be stored in the dictionary as a list. In Fact all keys' values
        will be stored in a list even if there is only one value for a key.
        """
        d = {}
        self.execute('SELECT key,value FROM settings')
        fa = self.c.fetchall()
        for pair in fa:
            d.setdefault(pair['key'], [])
            d[pair['key']].append(pair['value'])
        return d
    
    def get_settings_dictionary_full(self):
        """
        Returns a dictionary where they keys are the key in the database and 
        the value is itself a dictionary where the key is the sid and the 
        value is the database value.
        """
        d = {}
        self.execute('SELECT sid,key,value FROM settings')
        fa = self.c.fetchall()
        for tup in fa:
            d.setdefault(tup['key'], {})
            d[tup['key']].setdefault(tup['sid'], tup['value'])
        return d

    def get_sids(self):
        """
        Returns an associative array of settings ID (sid) to key, value 
        pairs stored in a tuple.
        """
        d = {}
        self.execute('SELECT sid,key,value FROM settings')
        fa = self.c.fetchall()
        for tup in fa:
            pair = (tup['key'], tup['value'])
            if d.setdefault(tup['sid'], pair) != pair:
                print('Duplicate settings ID in DB: %d' % (tup['sid']))
        return d

    def get_sid(self, key, value):
        """
        Returns a possibly empty list of sid(s) when given a key, value
        combination.
        """
        self.execute('SELECT sid FROM settings WHERE key=? AND value=?',
                     (key, value))
        fa = self.c.fetchall()
        L = []
        for sid in fa:
            L.append(sid['sid'])
        return L

    def key_exists(self, key):
        """
        Returns True if key is already present in database,
        otherwise false.
        """
        self.execute('SELECT sid FROM settings WHERE key=?', (key,))
        fa = self.c.fetchall()
        if len(fa) == 0:
            return False
        else:
            return True

if __name__ == '__main__':
    if os.path.exists('settings.db3'):
        os.unlink('settings.db3')
    # Various unit tests:
    settings = SettingsDB('settings.db3')
    #Not sure what the point is of a user_mode setting in persistent storage
    settings.add_settings_entry('user_mode', 'precert')
    settings.add_settings_entry('default_user_mode', 'precert')
##    settings.add_settings_entry('user_mode', 'atl')
##    x = settings.get_settings('user_mode')
##    settings.update_settings_value('matl', key='user_mode', sid=1)
##    y = settings.get_settings('user_mode')
    z = settings.get_settings_dictionary()
##    w = settings.get_sids()
##    t = settings.get_sid('user_mode', 'atl')
##    s = settings.key_exists('user_mode')
##    r = settings.key_exists('user_m0de')
    settings.close()
