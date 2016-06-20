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
"""Databases for associating programs, testcases, and paths"""
from __future__ import print_function
from __future__ import division
import sqlite3
import os
from database import DB

class ProgramMappingDB(DB):
    """
    Program mapping database API provides assocations between program,
    testcase, the program's test list file, it's path, and it's testbed_ap file
    """

    def __init__(self, dbpath):
        super(ProgramMappingDB, self).__init__(dbpath)
        self.dbpath = dbpath
        self.conn = None
        self.c = None
        self.connect()
        self.columns = {'id',
                        'program',
                        'test_list',
                        'cmd_path',
                        'testbed_ap'}

    def create(self):
        try:
            self.execute('''CREATE TABLE "programmap" (
                    "id" INTEGER PRIMARY KEY,
                    "program" TEXT NOT NULL,
                    "test_list" TEXT NOT NULL,
                    "cmd_path" TEXT NOT NULL,
                    "testbed_ap" TEXT NOT NULL);''',
                         commit=True)
        except (sqlite3.Error) as e:
            print(e)

    def add_mapping(self, program, values):
        """
        Add a program mapping to the program mapping database by providing
        the program name and a dictionary of the mappings. The mappings must
        include cmd_path, test_list, and testbed_ap as the keys and provide
        their corresponding values.
        """
        L = []
        L.append(program)
        L.append(values['test_list'])
        L.append(values['cmd_path'])
        L.append(values['testbed_ap'])
        T = tuple(L)
        self.execute("""INSERT INTO programmap (
                program,
                test_list,
                cmd_path,
                testbed_ap) VALUES (?, ?, ?, ?)""",
                     T,
                     commit=True)

    def get_program_list(self):
        """Returns a list of the programs present in the database"""
        self.execute('''SELECT program FROM programmap''')
        fa = self.c.fetchall()
        return [prog[0] for prog in fa]

    def get_cmd_path(self, program):
        """Returns the cmd_path field when given a program"""
        self.execute('''SELECT cmd_path FROM programmap WHERE program=?''',
                     (program,))
        f = self.c.fetchone()
        if f is not None:
            return f['cmd_path']
        else:
            return f

    def get_test_list(self, program):
        """Returns the test_list field when given a program"""
        self.execute('''SELECT test_list FROM programmap WHERE program=?''',
                     (program,))
        f = self.c.fetchone()
        if f is not None:
            return f['test_list']
        else:
            return f

    def get_testbed_ap(self, program):
        """Returns the testbed_ap field when given a program"""
        self.execute('''SELECT testbed_ap FROM programmap WHERE program=?''',
                     (program,))
        f = self.c.fetchone()
        if f is not None:
            return f['testbed_ap']
        else:
            return f

class InitMappingDB(DB):
    """
    Init mapping database API provides a database for mapping a test case to
    it's program, initfile, test case file, whether it's mandatory or optional,
    and what the dut type is for that test case.
    """

    def __init__(self, dbpath):
        super(InitMappingDB, self).__init__(dbpath)
        self.dbpath = dbpath
        self.conn = None
        self.c = None
        self.connect()
        self.columns = {'id',
                        'program',
                        'testcase',
                        'initfile',
                        'testcasefile',
                        'mandatory',
                        'dut_type'}

    def create(self):
        try:
            self.execute('''CREATE TABLE "initmap" (
                    "id" INTEGER PRIMARY KEY,
                    "program" TEXT NOT NULL,
                    "testcase" TEXT NOT NULL,
                    "initfile" TEXT NOT NULL,
                    "testcasefile" TEXT NOT NULL,
                    "mandatory" TEXT NOT NULL,
                    "dut_type" TEXT NOT NULL);''',
                         commit=True)
        except (sqlite3.Error) as e:
            print(e)

    def add_entry(self, program, testcase, initfile,
                  testcasefile, mandatory='U', dut_type='unknown'):
        """Adds an entry to the initmap table with the given parameters"""
        t = (program, testcase, initfile, testcasefile, mandatory, dut_type)
        self.execute('''INSERT INTO initmap (
                program, testcase, initfile, testcasefile, mandatory, dut_type)
                VALUES (?, ?, ?, ?, ?, ?)''', t, commit=True)

    def update_mandatory(self, mandatory, **kwargs):
        """Updates the mandatory field"""
        constraints = self.create_constraints(**kwargs)
        L = []
        L.append(mandatory)
        args = self.create_args(**kwargs)
        [L.append(arg) for arg in args]
        self.execute('''UPDATE initmap SET mandatory=? WHERE %s''' %
                     (constraints),
                     tuple(L), commit=True)

    def update_dut_type(self, dut_type, **kwargs):
        """Updates the mandatory field"""
        constraints = self.create_constraints(**kwargs)
        L = []
        L.append(dut_type)
        args = self.create_args(**kwargs)
        [L.append(arg) for arg in args]
        self.execute('''UPDATE initmap SET dut_type=? WHERE %s''' %
                     (constraints),
                     tuple(L), commit=True)

    def get_testcasefile(self, **kwargs):
        """Returns the testcasefile value given some constraints"""
        constraints = self.create_constraints(**kwargs)
        args = self.create_args(**kwargs)
        self.execute('SELECT testcasefile FROM initmap WHERE %s' %
                     (constraints),
                     args)
        f = self.c.fetchone()
        if f is not None:
            return f['testcasefile']
        else:
            return f

    def get_initfile(self, **kwargs):
        """Returns the initfile value given some constraints"""
        constraints = self.create_constraints(**kwargs)
        args = self.create_args(**kwargs)
        self.execute('SELECT initfile FROM initmap WHERE %s' %
                     (constraints),
                     args)
        f = self.c.fetchone()
        if f is not None:
            return f['initfile']
        else:
            return f

    def get_mandatory_list(self, program, mandatory):
        """Returns a list of testcases given a program and mandatory"""
        self.execute("""SELECT testcase FROM initmap
                     WHERE program=? AND mandatory=?""",
                     (program, mandatory))
        fa = self.c.fetchall()
        return [tc[0] for tc in fa]

    def get_testcase_list(self, program):
        """Returns a list of testcase names when given a program"""
        self.execute('SELECT testcase FROM initmap WHERE program=?',
                     (program,))
        fa = self.c.fetchall()
        return [tc[0] for tc in fa]

    def get_dut_type_list(self, program, dut_type):
        """Returns a list of testcases give a program and dut_type"""
        self.execute("""SELECT testcase FROM initmap
                     WHERE program=? AND dut_type=?""",
                     (program, dut_type))
        fa = self.c.fetchall()
        return [tc[0] for tc in fa]

if __name__ == '__main__':
    import xml.etree.ElementTree as ET
    import re
    dbpath = 'initmap.db3'
    filltable = False
    if not os.path.exists(dbpath):
        filltable = True
    programdb = ProgramMappingDB(dbpath)
    program = {}
    basepath = '..\\config'
    wtsuccfilename = os.path.join(basepath, 'WTS-UCC.txt')
    with open(wtsuccfilename) as f:
        for line in f:
            if re.search(r'^#', line) or re.search(r'^\s*$', line):
                continue
            l = line.strip().split('=')
            if re.search(r'_TEST_LIST$', l[0]):
                progname = l[0].split('_TEST_LIST')[0]
                program.setdefault(progname, {})
                program[progname].setdefault('test_list', l[1].strip('"'))
            elif re.search(r'_CMD_PATH$', l[0]):
                progname = l[0].split('_CMD_PATH')[0]
                program.setdefault(progname, {})
                program[progname].setdefault('cmd_path', l[1].strip('"'))
            elif re.search(r'_TESTBED_AP$', l[0]):
                progname = l[0].split('_TESTBED_AP')[0]
                program.setdefault(progname, {})
                program[progname].setdefault('testbed_ap', l[1].strip('"'))
    initmapdb = InitMappingDB(dbpath)
    if filltable:
        for prog in program:
            programdb.add_mapping(prog, program[prog])
    # programdb is now created and ready for use
    # Now to create the initmapping table
    programs = programdb.get_program_list()
    basepath = '..\\config'
    if filltable:
        initmapdb.create()
        initmapdb.commit()
        for prog in programs:
            tl = programdb.get_test_list(prog)
            full_tl = os.path.join(basepath, tl)
            with open(full_tl, 'rb') as f:
                for line in f:
                    l = line
                    if re.search(r'^#', l) or re.search(r'^\s*$', l):
                        continue
                    L = l.strip().split('!')
                    initmapdb.add_entry(prog, L[0], L[1], L[2])
    # Random unit tests:
    t = programdb.get_testbed_ap('AC-11AG')
    u = programdb.get_testbed_ap('N')
    v = programdb.get_program_list()
    w = programdb.get_cmd_path('VHT')
    x = initmapdb.get_dut_type_list('VHT', 'unknown')
    y = initmapdb.get_mandatory_list('VHT', 'U')
    z = initmapdb.get_initfile(program='VHT', testcase='VHT-5.2.1')
    # For the final part, add in the mandatory and dut_type information.
    # Mandatory/optional can be determined from the test plan or from
    # MasterTestInfo.xml. See SIG-1459 for how this might work
    # Data loading for optional or mandatory
    masters = {}
    missingmaster = {}
    optionals = {}
    specific_tags = {}
    for prog in programdb.get_program_list():
        master = os.path.join(programdb.get_cmd_path(prog),
                              'MasterTestInfo.xml')
        if os.path.exists(master):
            #print(master)
            masters[prog] = master
            optionals.setdefault(prog, set())
            specific_tags.setdefault(prog, set())
            # Get the specific tags:
            dutinfo = os.path.join(programdb.get_cmd_path(prog), 'DUTInfo.txt')
            with open(dutinfo) as f:
                for line in f:
                    if not (re.search(r'^#', line) or re.search(r'^\s*$', line)):
                        L = line.strip().split('!')[0]
                        specific_tags[prog].add(L)
        else:
            missingmaster[prog] = master
    newway = {'P2P', 'TDLS', 'HS2', 'WFD', 'WFDS', 'HS2-R2', 'NAN'}
    for prog in masters:
        if prog not in newway:
            x = ET.parse(masters[prog])
            y = x.getroot()
            for i in y.getchildren():
                if i.find('CheckFlag11n') is not None or \
                            i.find('checkFeatureFlag') is not None:
                    #print(prog, i.tag)
                    optionals[prog].add(i.tag)
        else:
            x = ET.parse(masters[prog])
            y = x.getroot()
            for i in y.getchildren():
                for j in i.getiterator():
                    if j.tag in specific_tags[prog]:
                        optionals[prog].add(i.tag)
    if filltable:
        for prog in optionals:
            for testcase in optionals[prog]:
                initmapdb.update_mandatory('O', program=prog, testcase=testcase)
        for prog in optionals:
            L = initmapdb.get_mandatory_list(prog, 'U')
            for i in L:
                if i not in optionals[prog]:
                    #print(i)
                    initmapdb.update_mandatory('M', program=prog, testcase=i)
    # Start of dataloading for dut_type column. Use regexes to determine
    # type. Add regex rule to dut_rules and what the result is if matched
    testcases = {}
    dut_rules = {}
    for prog in programdb.get_program_list():
        testcases.setdefault(prog, set())
        dut_rules.setdefault(prog, {})
        for tc in initmapdb.get_testcase_list(prog):
            if tc in testcases[prog]:
                print('%s already present' % (tc))
            testcases[prog].add(tc)
    STAUT = 'STAUT'
    APUT = 'APUT'
    dut_rules['N'][r'^N-4\.\d\.\d{1,2}'] = APUT
    dut_rules['N'][r'^N-5\.\d\.\d{1,2}'] = STAUT
    dut_rules['N'][r'^N-ExA\d{1,2}'] = APUT
    dut_rules['N'][r'^N-ExS\d{1,2}'] = STAUT
    dut_rules['WPA2'][r'^N-4\.\d\.\d{1,2}'] = APUT
    dut_rules['WPA2'][r'^N-5\.\d\.\d{1,2}'] = STAUT
    dut_rules['WPA2'][r'^N-ExA\d{1,2}'] = APUT
    dut_rules['WPA2'][r'^N-ExS\d{1,2}'] = STAUT
    dut_rules['VHT'][r'^VHT-5\.\d\.\d{1,2}'] = STAUT
    dut_rules['VHT'][r'^VHT-4\.\d\.\d{1,2}'] = APUT
    dut_rules['WFD'][r'^WFD-6\.\d\.\d{1,2}'] = 'P-SnUT'
    dut_rules['WFD'][r'^WFD-5\.\d\.\d{1,2}'] = 'SoUT'
    dut_rules['WFD'][r'^WFD-4\.\d\.\d{1,2}'] = 'WFD_DUT'
    dut_rules['PMF'][r'^PMF-4\.\d'] = APUT
    dut_rules['PMF'][r'^PMF-5\.\d'] = STAUT
    dut_rules['WMM'][r'^N-5\.\d\.\d{1,2}'] = STAUT
    dut_rules['WMM'][r'^N-4\.\d\.\d{1,2}'] = APUT
    dut_rules['HS2-R2'][r'^HS2-5\.\d{1,2}[-\w]{0,1}'] = STAUT
    dut_rules['HS2-R2'][r'^HS2-4\.\d{1,2}[-\w]{0,1}'] = APUT
    dut_rules['HS2'][r'^HS2-5\.\d{1,2}[-\w]{0,1}'] = STAUT
    dut_rules['HS2'][r'^HS2-4\.\d{1,2}[-\w]{0,1}'] = APUT
    dut_rules['WFDS'][r'^WFDS-4\.\d\.\d\.\d{1,2}_[SEND|PRINT|PLAY|ENABLE|DISPLAY]'] = 'GENERAL'
    dut_rules['WFDS'][r'^WFDS-5\.\d\.\d[\.\d]{0,1}'] = 'SEND'
    dut_rules['WFDS'][r'^WFDS-6\.\d_\w'] = 'PLAY'
    dut_rules['WFDS'][r'^WFDS-7\.\d_\w'] = 'DISPLAY'
    dut_rules['WFDS'][r'^WFDS-8\.\d\.\d\.\d{1,2}'] = 'PRINT'
    dut_rules['WFDS'][r'^WFDS-9\.\d_\w'] = 'ENABLE'
    dut_rules['VE'][r'^V-E-4\.\d'] = APUT
    dut_rules['VE'][r'^V-E-5\.\d'] = STAUT
    dut_rules['WMMPS'][r'^WMMPS-4'] = STAUT
    dut_rules['WMMPS'][r'^WMMPS-5'] = APUT
    dut_rules['NAN'][r'^NAN-5\.\d\.\d\w{0,1}'] = STAUT
    dut_rules['AC-11AG'][r'^WMM-AC-5\.\d\.\d'] = STAUT
    dut_rules['AC-11AG'][r'^WMM-AC-4\.\d\.\d'] = APUT
    dut_rules['AC-11B'][r'^WMM-AC-5\.\d\.\d'] = STAUT
    dut_rules['AC-11B'][r'^WMM-AC-4\.\d\.\d'] = APUT
    dut_rules['AC-11N'][r'^WMM-AC-5\.\d\.\d'] = STAUT
    dut_rules['AC-11N'][r'^WMM-AC-4\.\d\.\d'] = APUT
    dut_rules['P2P'][r'^P2P-4\.1'] = 'DEVUT'
    dut_rules['P2P'][r'^P2P-4\.2'] = 'GOUT'
    dut_rules['P2P'][r'^P2P-4\.3'] = 'CLUT'
    dut_rules['P2P'][r'^P2P-5'] = 'DEVUT'
    dut_rules['P2P'][r'^P2P-6'] = 'GOUT'
    dut_rules['P2P'][r'^P2P-7'] = 'CLUT'
    dut_rules['TDLS'][r'TDLS-5\.\d'] = STAUT
    if filltable:
        for prog in testcases:
            for rule in dut_rules[prog]:
                for tc in testcases[prog]:
                    if re.search(rule, tc):
                        initmapdb.update_dut_type(dut_rules[prog][rule],
                                                  program=prog, testcase=tc)
    programdb.close()
    initmapdb.close()
