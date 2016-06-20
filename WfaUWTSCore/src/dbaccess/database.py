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
"""Base database module"""
from __future__ import print_function
from __future__ import division
import sqlite3
import os

class DB(object):
    """Class DB contains common methods used across DB APIs"""
    def __init__(self, dbpath):
        self.dbpath = dbpath
        self.conn = None
        self.c = None
        self.columns = set()

    def __str__(self):
        return os.path.basename(self.dbpath) + 'DB'

    def __repr__(self):
        return 'DB(%s)' % self.dbpath

    def connect(self):
        """
        Attempt connection to database. Call self.create() if it doesn't
        exist
        """
        if not os.path.exists(self.dbpath):
            createtable = True
        else:
            createtable = False
        self.conn = sqlite3.connect(self.dbpath,
                                    detect_types=sqlite3.PARSE_DECLTYPES)
        self.conn.text_factory = sqlite3.OptimizedUnicode
        self.conn.row_factory = sqlite3.Row
        self.c = self.conn.cursor()
        if createtable:
            self.create()
        #self.execute('VACUUM')

    def create(self):
        """
        Inheritors should replace this method with a method specific to their
        database
        """
        print("Replace this method")

    def execute(self, command, args=(), commit=False):
        """Execute command and args of this command and optionally save"""
        try:
            self.c.execute(command, args)
            if commit:
                self.commit()
        except (sqlite3.Error) as emsg:
            print(emsg)
            print(command, args)

    def commit(self):
        """
        Called by execute if commit flag is True. Commits execute command
        to DB
        """
        try:
            self.conn.commit()
        except (sqlite3.Error) as emsg:
            print(emsg)

    def close(self):
        """Close connections to cursor and database"""
        try:
            self.c.close()
            self.conn.close()
        except (sqlite3.Error) as emsg:
            print(emsg)

    def evalsql(self, command, args=()):
        """
        Similar to self.execute() but will return fetchall().
        TODO: Temporary method?
        """
        try:
            fa = self.c.execute(command, args)
            return fa.fetchall()
        except (sqlite3.Error) as emsg:
            print(emsg)
            return []

    def create_constraints(self, **kwargs):
        """
        Returns a string of the constraints based on kwargs if they're also
        present in the self.columns class attribute that was setup during init.
        The string will be of the form kwargs1=? AND kwargs2=? AND ...
        """
        constraints = ' AND '.join([constraint + '=?' for constraint in kwargs if constraint in self.columns])
        return constraints

    def create_args(self, **kwargs):
        """
        Returns an argument tuple based on the given kwargs if they're
        present in the self.columns class attribute that was setup during init
        """
        args = tuple([kwargs.get(key) for key in kwargs if key in self.columns])
        return args

    def get_last_rowid(self):
        """Returns last rowid inserted with this object's cursor"""
        return self.c.lastrowid
