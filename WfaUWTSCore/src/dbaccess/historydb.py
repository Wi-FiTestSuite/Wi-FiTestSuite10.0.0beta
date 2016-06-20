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
"""History database API for storing log files and related information"""
from __future__ import print_function
from __future__ import division
import sqlite3
import re
import os
import zlib
import time
from database import DB
import common


class HistoryDB(DB):
    """
    History database APIs. Start use by getting a logid from create_entry,
    then use logid to add_line to the entry or update the entry at once
    with add_entry. See other APIs for storing other elements in the db
    such as initenv, status, user_mode, etc.
    """

    def __init__(self, dbpath):
        super(HistoryDB, self).__init__(dbpath)
        self.dbpath = dbpath
        self.conn = None
        self.c = None
        self.connect()
        self.currentlog = {}
        self.columns = {'logid',
                        'testcase',
                        'program',
                        'started',
                        'finshed',
                        'storage',
                        'status',
                        'log_output',
                        'initenv',
                        'invoker',
                        'xml_output',
                        'config',
                        'user_mode'}

    def create(self):
        try:
            self.execute("""CREATE TABLE "history" (
                    "logid" INTEGER PRIMARY KEY,
                    "testcase" TEXT NOT NULL,
                    "program" TEXT NOT NULL,
                    "started" INTEGER NOT NULL,
                    "finished" INTEGER,
                    "storage" TEXT NOT NULL,
                    "status" TEXT,
                    "log_output" BLOB,
                    "initenv" BLOB,
                    "invoker" TEXT,
                    "xml_output" BLOB,
                    "config" BLOB,
                    "user_mode" TEXT,
                    "log_sig" TEXT,
                    "log_digest" BLOB
                    );""", commit=True)
        except (sqlite3.Error) as emsg:
            print(emsg)

    def create_entry(self, testcase, program, user_mode, storage=None):
        """Returns log entry descriptor"""
        L = []
        L.append(testcase)
        L.append(program)
        started = int(time.time())
        L.append(started)
        t = time.localtime()
        if storage is None:
            storage = "logs\\%s_%d-%d-%d_%d-%d.%d" % (
                testcase,
                t.tm_year,
                t.tm_mon,
                t.tm_mday,
                t.tm_hour,
                t.tm_min,
                t.tm_sec)
        L.append(storage)
        L.append(user_mode)
        self.execute("""INSERT INTO history(
                     testcase,
                     program,
                     started,
                     storage,
                     user_mode) VALUES (?, ?, ?, ?, ?)""",
                     tuple(L))
        last = self.c.lastrowid
        if [] != self.currentlog.setdefault(last, []):
            print("Error: Already opened database entry %d" % (last))
        return last

    def add_line(self, logid, line):
        """Add a line to this history entry"""
        #Attempt to add this to to the currentlog[logid], compress, and commit
        if logid in self.currentlog:
            try:
                self.currentlog[logid].append(line)
            except (AttributeError):
                self.currentlog[logid].append(line)
        else:
            return False
        c = ''.join(self.currentlog[logid]).encode('utf-8')
        z = sqlite3.Binary(zlib.compress(c))
        self.execute('UPDATE history SET log_output=? WHERE logid=?', (z, logid))
        self.commit()
        return True

    def get_storage(self, **kwargs):
        """
        Returns the storage value for an entry given a unique set of constraints
        """
        constraints = self.create_constraints(**kwargs)
        args = self.create_args(**kwargs)
        self.execute('SELECT storage FROM history WHERE %s' % (constraints), args)
        f = self.c.fetchone()
        if f is not None:
            return f['storage']
        else:
            return f
    
    def get_log_sig(self, **kwargs):
        """
        Returns the log_sig value for an entry given a unique set of constraints
        """
        constraints = self.create_constraints(**kwargs)
        args = self.create_args(**kwargs)
        self.execute('SELECT log_sig FROM history WHERE %s' % (constraints), args)
        f = self.c.fetchone()
        if f is not None:
            return f['log_sig']
        else:
            return f
    
    def get_log_digest(self, **kwargs):
        """
        Returns the log_digest value for an entry given a unique set of constraints
        """
        constraints = self.create_constraints(**kwargs)
        args = self.create_args(**kwargs)
        self.execute('SELECT log_sig FROM history WHERE %s' % (constraints), args)
        f = self.c.fetchone()
        if f is not None:
            return f['log_digest']
        else:
            return f
        
    def close_entry(self, logid, status='NA'):
        """Optionally add a status and then close entry"""
        #pop the thing from the currentlog, compress, and place/commit
        if logid in self.currentlog:
            closed = self.currentlog.pop(logid)
        else:
            return False
        if len(closed) > 0:
            c = ''.join(closed)
            z = sqlite3.Binary(zlib.compress(c))
            self.execute('UPDATE history SET log_output=? WHERE logid=?', (z, logid))
        finished = int(time.time())
        self.execute('UPDATE history SET status=? WHERE logid=?', (status, logid))
        self.execute('UPDATE history SET finished=? WHERE logid=?', (finished, logid))
        self.commit()
        return True

    def add_xml_output(self, logid, xml_output):
        """Add xml_output to history/log entry given a logid"""
        if logid not in self.currentlog:
            return False
        z = sqlite3.Binary(zlib.compress(xml_output))
        self.execute('UPDATE history SET xml_output=? WHERE logid=?', (z, logid))
        self.commit()
        return True

    def add_log_output(self, logid, log_output):
        """Add log_output to history/log entry given a logid"""
        if logid not in self.currentlog:
            return False
        z = sqlite3.Binary(log_output)
        self.execute('UPDATE history SET log_output=? WHERE logid=?', (z, logid))
        self.commit()
        return True

    def add_initenv(self, logid, initenv):
        """Adds the initenv field when given a logid."""
        if logid not in self.currentlog:
            return False
        else:
            z = sqlite3.Binary(zlib.compress(initenv))
            self.execute('UPDATE history SET initenv=? WHERE logid=?',
                         (z, logid), commit=True)
            return True
    
    def add_log_sig(self, logid, logsig):
        """Adds the log_sig field when given a logid."""
        if logid not in self.currentlog:
            return False
        else:
            self.execute('UPDATE history SET log_sig=? WHERE logid=?',
                         (logsig, logid), commit=True)
            return True
    
    def add_log_digest(self, logid, logdigest):
        """Adds the log_sig field when given a logid."""
        if logid not in self.currentlog:
            return False
        else:
            z = sqlite3.Binary(logdigest)
            self.execute('UPDATE history SET log_digest=? WHERE logid=?',
                         (z, logid), commit=True)
            return True
        
    def add_config(self, logid, config):
        """Adds the config field when given a logid."""
        if logid not in self.currentlog:
            return False
        else:
            z = sqlite3.Binary(zlib.compress(config))
            self.execute('UPDATE history SET config=? WHERE logid=?',
                         (z, logid), commit=True)
            return True

    def update_invoker(self, logid, invoker):
        """Update the invoker given a logid. Return true for success"""
        if logid not in self.currentlog:
            return False
        else:
            self.execute('UPDATE history SET invoker=? WHERE logid=?',
                         (invoker, logid), commit=True)
            return True

    def get_log_output(self, decompress=True, **kwargs):
        """Return the log_output of a log entry"""
        constraints = self.create_constraints(**kwargs)
        args = self.create_args(**kwargs)
        self.execute('SELECT log_output FROM history WHERE %s' % (constraints), args)
        zt = self.c.fetchone()
        if zt is not None:
            z = zt['log_output']
            if decompress:
                d = zlib.decompress(z)
            else:
                d = z
            return d
        else:
            return zt

    def get_xml_output(self, decompress=True, **kwargs):
        """Return the xml_output of a log entry"""
        constraints = self.create_constraints(**kwargs)
        args = self.create_args(**kwargs)
        self.execute('SELECT xml_output FROM history WHERE %s' % (constraints), args)
        zt = self.c.fetchone()
        if zt is not None:
            z = zt['xml_output']
            if decompress:
                d = zlib.decompress(z)
            else:
                d = z
            return d
        else:
            return zt

    def get_initenv_output(self, decompress=True, **kwargs):
        """Return the xml_output of a log entry"""
        constraints = self.create_constraints(**kwargs)
        args = self.create_args(**kwargs)
        self.execute('SELECT initenv FROM history WHERE %s' % (constraints), args)
        zt = self.c.fetchone()
        if zt is not None:
            z = zt['initenv']
            if decompress:
                d = zlib.decompress(z)
            else:
                d = z
            return d
        else:
            return zt

    def get_log_list_by_status(self, status):
        """Returns list of 'storage' for testcases that have a give status"""
        self.execute('SELECT storage FROM history WHERE status=?', (status,))
        stores = self.c.fetchall()
        if stores is not None:
            return [store[0] for store in stores]
        else:
            return []

    def get_currentlog(self):
        """Returns current log dictionary which indicates which logs are open"""
        return self.currentlog


class HistoryService:
    def __init__(self, history):
        self.historyDAO = HistoryDAO(history)
        # can have other DAOs        
    
    def add(self, hsDAO):
        self.historyDAO.save(hsDAO)
    
    def updateHistoryByInitEnv(self, initEnv):
        self.historyDAO.update("INITENV", initEnv)
        
    def updateHistoryByLogOuput(self, log_output, log_sig, log_digest):
        self.historyDAO.update("LOGOUTPUT", log_output, log_sig, log_digest)
        
    #===========================================================================
    # def updateHistoryByLogSig(self, log_sig):
    #     self.historyDAO.update("LOGSIG", log_sig)
    #===========================================================================


class HistoryDAO:
    def __init__(self, history):
        self.dbpath = os.path.join(common.GlobalConfigFiles.DBPATH,
            common.GlobalConfigFiles.HISTORYDBFILE)
        self.history_db = HistoryDB(self.dbpath)
        self.history = history
    
    def save(self, hsDAO):        
        pass
    
    def update(self, fieldName, *args):
        logid = self.history_db.create_entry(self.history.tc_name, self.history.prog_name, self.history.user_mode, self.history.location)
        if fieldName == "INITENV":
            self.history_db.add_initenv(logid, args[0])
        if fieldName == "LOGOUTPUT":
            self.history_db.add_log_output(logid, args[0])  
        #if fieldName == "LOGSIG":
            self.history_db.add_log_sig(logid, args[1])     
            self.history_db.add_log_digest(logid, args[2])     
        self.history_db.close_entry(logid)
        
        
        
class History:
    def __init__(self, prog_name, tc_name, user_mode='precert', location=''):
        self.prog_name = prog_name
        self.tc_name = tc_name
        self.user_mode = user_mode
        self.location = location


        
if __name__ == '__main__':
    hdbname = 'history.db3'
    if not os.path.exists(hdbname):
        history_db = HistoryDB('history.db3')
        storage2logid = {}
        for idx, listing in enumerate(os.walk('log')):
            if idx == 0:
                continue
            storage = listing[0]
            testcase = os.path.basename(listing[0]).split('_')[0]
            program = testcase.split('-')[0]
            logid = history_db.create_entry(testcase, program, 'precert', storage)
            storage2logid.setdefault(storage, logid)
            for file1 in listing[2]:
                if re.search(r'^log_VHT', file1):
                    storage_example = os.path.join(storage, file1)
                    with open(storage_example, 'rb') as f:
                        d = f.read()
                    if re.search(r'FINAL TEST RESULT  --->\s*PASS', d):
                        status = 'PASS'
                    else:
                        status = 'FAILURE'
                    history_db.add_log_output(logid, d)

                if re.search(r'\.xml', file1):
                    xml_example = os.path.join(storage, file1)
                    with open(xml_example, 'rb') as f:
                        d = f.read()
                    history_db.add_xml_output(logid, d)
            history_db.close_entry(logid, status=status)
    else:
        history_db = HistoryDB('history.db3')
    passed = history_db.get_log_list_by_status('PASS')
    failed = history_db.get_log_list_by_status('FAILURE')
    history_entry = history_db.create_entry('VHT-5.2.1', 'VHT', 'precert', storage=None)
    print(history_entry)
    history_db.add_line(history_entry, 'This is a test!\r\n')
    history_db.add_line(history_entry, 'See you soon!\r\n')
    history_db.close_entry(history_entry, status='PASS')
    storage = history_db.get_storage(logid=history_entry)
    print(storage)
    print(history_db.get_log_output(storage=storage))
    print(history_db.get_log_output(logid=history_entry))
    history_db.close()
