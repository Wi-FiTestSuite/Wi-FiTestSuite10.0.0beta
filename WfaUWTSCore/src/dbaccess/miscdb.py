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
"""Databases focused on storing previously hard-coded values"""
from __future__ import print_function
from __future__ import division
import sqlite3
import os
from database import DB

class BandCommonNameDB(DB):
    """
    Database APIS for storing hard-coded values
    pertaining to a band common name vs. it's real name
    """

    def __init__(self, dbpath):
        super(BandCommonNameDB, self).__init__(dbpath)
        self.dbpath = dbpath
        self.conn = None
        self.c = None
        self.connect()
        self.columns = {'bid',
                        'common_name',
                        'true_name'}

    def create(self):
        try:
            self.execute('''CREATE TABLE "commonbandnames" (
                        "bid" INTEGER PRIMARY KEY,
                        "common_name" TEXT NOT NULL,
                        "true_name" TEXT NOT NULL);''',
                         commit=True)
        except (sqlite3.Error) as emsg:
            print(emsg)

    def add_name_mapping(self, common_name, true_name):
        """Adds an entry to the commonbandnames database"""
        T = (common_name, true_name)
        self.execute('''INSERT INTO commonbandnames (
                     common_name, true_name) VALUES (?, ?)''', T, commit=True)

    def get_true_name(self, common_name):
        """Returns the true_name of an entry when given the common_name"""
        self.execute('''SELECT true_name FROM commonbandnames
                                WHERE common_name=?''', (common_name,))
        fo = self.c.fetchone()
        if fo is not None:
            return fo['true_name']
        else:
            return fo

class BandSelectionListDB(DB):
    """
    BandSelectionList database APIs. This database is used to store
    hard-coded values pertaining to band listings
    """

    def __init__(self, dbpath):
        super(BandSelectionListDB, self).__init__(dbpath)
        self.dbpath = dbpath
        self.conn = None
        self.c = None
        self.connect()
        self.columns = {'bandid',
                        'bandkey',
                        'bandvalue'}

    def create(self):
        try:
            self.execute('''CREATE TABLE "bandmap" (
                        "id" INTEGER PRIMARY KEY,
                        "bandkey" TEXT NOT NULL,
                        "bandvalue" TEXT NOT NULL);''',
                         commit=True)
        except (sqlite3.Error) as emsg:
            print(emsg)

    def add_bandmap(self, bandkey, bandvalue):
        """Adds a bandmapping when given the bandkey and bandvalue"""
        T = (bandkey, bandvalue)
        self.execute('''INSERT INTO bandmap (
                bandkey, bandvalue) VALUES (?, ?)''', T, commit=True)

    def delete_bandmap(self, **kwargs):
        """Removes a bandmapping entry given some parameters"""
        constraints = self.create_constraints(**kwargs)
        args = self.create_args(**kwargs)
        self.execute('DELETE FROM bandmap WHERE %s' % (constraints),
                     args, commit=True)

    def update_bandvalue(self, bandvalue, **kwargs):
        """Updates the bandvalue given some parameters"""
        constraints = self.create_constraints(**kwargs)
        L = []
        L.append(bandvalue)
        args = self.create_args(**kwargs)
        [L.append(arg) for arg in args]
        T = tuple(L)
        self.execute('UPDATE bandmap SET bandvalue=? WHERE %s' % (constraints),
                     T, commit=True)

    def read_bandvalue(self, **kwargs):
        """Reads a bandvalue given some parameters"""
        constraints = self.create_constraints(**kwargs)
        args = self.create_args(**kwargs)
        self.execute('SELECT bandvalue FROM bandmap WHERE %s' %
                     (constraints), args)
        fo = self.c.fetchone()
        if fo is not None:
            return fo['bandvalue']
        else:
            return fo

    def create_band_dictionary(self):
        """Returns a dictionary of bandkey : bandvalue pairs"""
        d = {}
        self.execute('SELECT bandkey,bandvalue FROM bandmap')
        fa = self.c.fetchall()
        for item in fa:
            if d.setdefault(item['bandkey'],
                            item['bandvalue']) != item['bandvalue']:
                print('Entry for %s already exists old: %s, new: %s' %
                      (item['bandkey'], d[item['bandkey']], item['bandkey']))
        return d

if __name__ == '__main__':
    #from pprint import pprint
    dbpath = 'miscdb.db3'
    # If the database doesn't already exist on disk, then it will be created
    filltable = not os.path.exists(dbpath)
    miscdb = BandSelectionListDB(dbpath)
    if filltable:
        miscdb.add_bandmap("A:BG", "11g")
        miscdb.add_bandmap("B:BG", "11b")
        miscdb.add_bandmap("G:BG", "11g")
        miscdb.add_bandmap("AG:BG", "11g")
        miscdb.add_bandmap("AB:BG", "11b")

        #DUT Mode A only
        miscdb.add_bandmap("A:A", "11a")
        miscdb.add_bandmap("B:A", "11a")
        miscdb.add_bandmap("G:A", "11a")
        miscdb.add_bandmap("AG:A", "11a")
        miscdb.add_bandmap("AB:A", "11a")

        #DUT Mode ABG
        miscdb.add_bandmap("A:ABG", "11a")
        miscdb.add_bandmap("B:ABG", "11b")
        miscdb.add_bandmap("G:ABG", "11g")
        miscdb.add_bandmap("AG:ABG", "11a")
        miscdb.add_bandmap("AB:ABG", "11a")

        #DUT Mode b only
        miscdb.add_bandmap("A:B", "11g")
        miscdb.add_bandmap("B:B", "11b")
        miscdb.add_bandmap("G:B", "11g")
        miscdb.add_bandmap("AG:B", "11g")
        miscdb.add_bandmap("AB:B", "11b")

        #DUT Mode G only
        miscdb.add_bandmap("A:G", "11g")
        miscdb.add_bandmap("B:G", "11g")
        miscdb.add_bandmap("G:G", "11g")
        miscdb.add_bandmap("AG:G", "11g")
        miscdb.add_bandmap("AB:G", "11b")

        # DUT mode A and b only
        miscdb.add_bandmap("A:AB", "11a")
        miscdb.add_bandmap("B:AB", "11b")
        miscdb.add_bandmap("G:AB", "11b")
        miscdb.add_bandmap("AG:AB", "11b")
        miscdb.add_bandmap("AB:AB", "11a")

        #DUT mode ABGN
        miscdb.add_bandmap("A:ABGN", "11a")
        miscdb.add_bandmap("B:ABGN", "11b")
        miscdb.add_bandmap("G:ABGN", "11g")
        miscdb.add_bandmap("AG:ABGN", "11a")
        miscdb.add_bandmap("AB:ABGN", "11a")

        miscdb.add_bandmap("AGN:ABGN", "11na")
        miscdb.add_bandmap("AN:ABGN", "11na")
        miscdb.add_bandmap("GN:ABGN", "11ng")

        #DUT mode GN
        miscdb.add_bandmap("A:GN", "11g")
        miscdb.add_bandmap("B:GN", "11b")
        miscdb.add_bandmap("G:GN", "11g")
        miscdb.add_bandmap("AG:GN", "11g")
        miscdb.add_bandmap("AB:GN", "11b")

        miscdb.add_bandmap("AGN:GN", "11ng")
        miscdb.add_bandmap("AN:GN", "11ng")
        miscdb.add_bandmap("GN:GN", "11ng")

        #DUT mode AN
        miscdb.add_bandmap("A:AN", "11a")
        miscdb.add_bandmap("B:AN", "11a")
        miscdb.add_bandmap("G:AN", "11a")
        miscdb.add_bandmap("AG:AN", "11a")
        miscdb.add_bandmap("AB:AN", "11a")

        miscdb.add_bandmap("AGN:AN", "11na")
        miscdb.add_bandmap("AN:AN", "11na")
        miscdb.add_bandmap("GN:AN", "11na")

        miscdb.add_bandmap("AGN:ABG", "11a")
        miscdb.add_bandmap("AGN:BG", "11g")
        miscdb.add_bandmap("AGN:B", "11b")
        miscdb.add_bandmap("AN:ABG", "11a")
        miscdb.add_bandmap("AN:BG", "11g")
        miscdb.add_bandmap("AN:B", "11b")
        miscdb.add_bandmap("GN:ABG", "11g")
        miscdb.add_bandmap("GN:BG", "11g")
        miscdb.add_bandmap("GN:B", "11b")

        # DUT Mode AC
        miscdb.add_bandmap("A:AC", "11a")
        miscdb.add_bandmap("AN:AC", "11na")
        miscdb.add_bandmap("AC:AC", "11ac")
        miscdb.add_bandmap("B:BGNAC", "11b")
        miscdb.add_bandmap("BG:BGNAC", "11g")
        miscdb.add_bandmap("BGN:BGNAC", "11ng")
    # Create a dictionary from the database data
    d = miscdb.create_band_dictionary()
    # Separately create the commonbandnames databse
    band_name_db = BandCommonNameDB(dbpath)
    if filltable:
        band_name_db.create()
        band_name_db.add_name_mapping('A/G', 'AG')
        band_name_db.add_name_mapping('A/G/N', 'AGN')
        band_name_db.add_name_mapping('G/N', 'GN')
        band_name_db.add_name_mapping('A/N', 'AN')
        band_name_db.add_name_mapping('A/B', 'AB')
        band_name_db.add_name_mapping('AC', 'AC')
    Band = band_name_db.get_true_name('A/G/N')
