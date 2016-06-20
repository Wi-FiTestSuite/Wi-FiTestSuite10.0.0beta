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
"""Database API for accessing info related to testbed validation"""
from __future__ import print_function
from __future__ import division
import sqlite3
import os
import common
from database import DB
import datetime

class ValidationService(object):

    def __init__(self):
        self.validationdao = ValidationDAO()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.validationdao.db.close()

    def get_validationDAO(self):
        return self.validationdao

class ValidationDAO(object):

    def __init__(self):
        self.dbpath = os.path.join(common.GlobalConfigFiles.DBPATH,
            common.GlobalConfigFiles.VALIDATIONDBFILE)
        self.db = TestPlanTemplateDB(self.dbpath)

    def get_latest_result_session(self):
        return self.db.get_latest_result_session()

    def create_result_session(self, program):
        return self.db.create_result_session(program)

    def delete_other_result_sessions(self, save, program):
        self.db.delete_other_result_sessions(save, program)

    def get_validation_data(self, data_entity):
        if data_entity.hasAttribute('vd_id') and data_entity.vd_id != '':
            ret = self.db.get_validation_data_byid(data_entity.vd_id)
        elif data_entity.hasAttribute('uwts_name') and data_entity.uwts_name != '':
            ret = self.db.get_validation_data_byuwtsname(data_entity.uwts_name)
        return ret

    def get_capi_block(self, data_entity):
        print(__name__)

    def get_command_list(self, program):
        """
        Returns a dictionary of: 
        {uwts_name : (validation_command_entity, validation_data_entity)}"""
        command_dict = {}
        # 1. Get all data by program
        for data_entity in self.db.get_data_by_program(program):
            uwts_name = data_entity.get('uwts_name')
            # 2. For each data, get command by data's vc_id
            command_entity = self.db.get_command_by_vc_id(data_entity.get('vc_id'))
            # 3. Create dictionary with data.uwts_name : get_command_by_vc_id(vc_di)
            data_command_dict = {'data' : data_entity, 'command' : command_entity}
            t = command_dict.setdefault(uwts_name, data_command_dict)
            if t['command'] != command_entity:
                #There can be only one. Choose the one with a > expiration
                if data_entity.get('expiration') > t['data'].get('expiration'):
                    command_dict[uwts_name] = data_command_dict
                    print('Newer expiration found for {0}'.format(data_entity.get('uwts_name')))
        return command_dict

    def get_validation_fields(self, program='VHT'):
        """
        Returns a set of things that can be used for validation from a 
        data_entity
        """
        return self.db.get_valid_column_set(program)

    def get_pretty_rows(self):
        return self.db.get_validation_description()

    def get_table_entity(self, table, **kwargs):
        return self.db.get_table_entity(table, **kwargs)

class TestPlanTemplateDB(DB):
    """
    TestPlanTemplateDB class provides access methods to the validation tables. 
    The current tables are validation_command, validation_data, and 
    validation_vars.
    """

    def __init__(self, dbpath):
        super(TestPlanTemplateDB, self).__init__(dbpath)
        self.dbpath = dbpath
        self.conn = None
        self.c = None
        self.connect()
        self.columns = {}
        self.tables = set()
        self.table_columns_sql = {'validation_command' : 'SELECT * FROM validation_command',
                                  'validation_data' : 'SELECT * FROM validation_data',
                                  'validation_columns' : 'SELECT * FROM validation_columns',
                                  'validation_pretty' : 'SELECT * FROM validation_pretty',
                                  'validation_result_session' : 'SELECT * FROM validation_result_session'}
        for table, sqlcmd in self.table_columns_sql.items():
            self.columns.setdefault(table, [])
            self.tables.add(table)
            self.execute(sqlcmd)
            for description in self.c.description:
                self.columns[table].append(description[0])
            self.columns[table] = tuple(self.columns[table])

    def create(self):
        try:
            # This has commands on how to get the results from a device
            self.execute('''CREATE TABLE validation_command (
                        vc_id INTEGER PRIMARY KEY,
                        program TEXT NOT NULL,
                        command_type TEXT NOT NULL,
                        description TEXT NOT NULL,
                        command TEXT NOT NULL);''',
                        commit=True)
        except (sqlite3.Error) as emsg:
            print(emsg)

        try:
            # This is what is expected from the device; obtained from testplan or device
            self.execute('''CREATE TABLE validation_data (
                        vd_id INTEGER PRIMARY KEY,
                        program TEXT NOT NULL,
                        testplan_latest TEXT NOT NULL,
                        testplan_list TEXT,
                        model TEXT,
                        vendor TEXT,
                        uwts_name TEXT NOT NULL,
                        dut_type TEXT,
                        ca_version TEXT,
                        interfaceid TEXT,
                        sw_version TEXT,
                        hw_version TEXT,
                        fw_version TEXT,
                        host_os TEXT,
                        product_id TEXT,
                        tbd_info1 TEXT,
                        tbd_info2 TEXT,
                        tbd_info3 TEXT,
                        expiration TIMESTAMP,
                        description TEXT,
                        vc_id INTEGER NOT NULL,
                        FOREIGN KEY(vc_id) REFERENCES validation_command(vc_id));''',
                        commit=True)
        except (sqlite3.Error) as emsg:
            print(emsg)

        try:
            self.execute('''CREATE TABLE validation_columns (
                        vco_id INTEGER PRIMARY KEY,
                        program TEXT NOT NULL,
                        valid_column TEXT NOT NULL);''',
                        commit=True)
        except (sqlite3.Error) as emsg:
            print(emsg)

        try:
            self.execute('''CREATE TABLE validation_pretty (
            model TEXT NOT NULL,
            vendor TEXT NOT NULL,
            ca_version TEXT NOT NULL,
            interfaceid TEXT NOT NULL,
            sw_version TEXT NOT NULL,
            hw_version TEXT NOT NULL,
            fw_version TEXT NOT NULL,
            host_os TEXT NOT NULL,
            product_id TEXT NOT NULL,
            tbd_info1 TEXT NOT NULL,
            tbd_info2 TEXT NOT NULL,
            tbd_info3 TEXT NOT NULL,
            expiration TEXT NOT NULL);''',
            commit=True)
        except (sqlite3.Error) as emsg:
            print(emsg)

        try:
            self.execute('''CREATE TABLE validation_result_session (
                        session INTEGER PRIMARY KEY,
                        program TEXT NOT NULL,
                        timestamp TIMESTAMP NOT NULL);''', commit=True)
        except (sqlite3.Error) as emsg:
            print(emsg)

    def get_latest_result_session(self):
        table = 'validation_result_session'
        self.execute('''SELECT * 
                        FROM validation_result_session 
                        ORDER BY timestamp DESC
                        LIMIT 1''')
        fa = self.c.fetchall()
        if len(fa) != 0:
            #just get the latest entry based on timestamp
            return self.get_table_entity(table,
                                  session=fa[0]['session'],
                                  timestamp=fa[0]['timestamp'])
        else:
            #No entries. So, validation hasn't run before
            return None

    def create_result_session(self, program):
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.execute('''INSERT INTO validation_result_session 
                    (timestamp, program) 
                    VALUES 
                    (?, ?)''', (now, program), commit=True)
        return self.c.lastrowid

    def delete_other_result_sessions(self, save, program, commit=True):
        """
        There should generally be one result session in the 
        validation_result_session table. When given a value for save, this 
        deletes all other entries. This should only be called after the 
        validation_results table has been cleared of entries.
        """
        self.execute('''DELETE FROM validation_result_session 
                        WHERE session 
                        IS NOT ? AND program IS NOT ?''', (save, program), commit=commit)

    def get_data_entry_by_vd_id(self, vd_id):
        table = 'validation_data'
        d = {}
        self.execute('SELECT * FROM validation_data WHERE vd_id=?',
                     (vd_id,))
        f = self.c.fetchone()
        if f is not None:
            for key in f.keys():
                d[key] = f[key]
            return self.get_table_entity(table, **d)
        else:
            return f

    def add_pretty_entry(self, d, commit=True):
        table = 'validation_pretty'
        L = []
        for i in self.columns[table]:
            L.append(d[i])
        self.execute('''INSERT INTO validation_pretty (
        model, vendor, ca_version,
        interfaceid, sw_version, hw_version,
        fw_version, host_os, product_id,
        tbd_info1, tbd_info2, tbd_info3, expiration)
        VALUES 
        (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        tuple(L), commit=commit)
        return self.c.lastrowid
    
    def get_validation_description(self):
        #table = 'validation_pretty'
        self.execute('SELECT * FROM validation_pretty')
        f = self.c.fetchone()
        d = {}
        for key in f.keys():
            d[key] = f[key]
        return d

    def add_validation_column_entry(self, column_entity, commit=True):
        """
        Adds an entry to the validation_columns table which indicates which 
        columns from validation_data can actually be used in the validation 
        process
        """
        table = 'validation_columns'
        L = []
        for element in self.columns[table][1:]:
            item = column_entity.get(element)
            if item is not None:
                L.append(item)
            else:
                L.append('')
        self.execute('''INSERT INTO validation_columns
                    (program, valid_column)
                    VALUES
                    (?, ?)''',
                    tuple(L), commit=commit)
        return self.c.lastrowid
    
    def get_valid_column_set(self, program='VHT'):
        '''Returns a set of columns that can be used to validate against'''
        #table = 'validation_columns'
        #self.execute('''SELECT * FROM validation_columns WHERE program=?''',
        #             (program,), commit=True)
        self.execute('''SELECT * FROM validation_columns''')
        fa = self.c.fetchall()
        return {vc['valid_column'] for vc in fa}

    def add_command_entry(self, command_entity, commit=True):
        """
        Adds an entry to the validation_command table when given a 
        command_entity. Returns the rowid of this inserted object.
        vc_id should NOT be included in command_entity.
        """
        table='validation_command'
        L = []
        for element in self.columns[table][1:]:
            item = command_entity.get(element)
            if item is not None:
                L.append(item)
            else:
                #print('Not a valid column for table %s: %s' % (table, str(item)))
                L.append('')
        self.execute('''INSERT INTO validation_command
                    (program, command_type, description, command)
                    VALUES
                    (?, ?, ?, ?)''',
                    tuple(L), commit=commit)
        return self.c.lastrowid

    def add_data_entry(self, data_entity, commit=True):
        """
        Adds an entry to the validation_data table when given a data_entity.
        Returns the rowid of the inserted data.
        vd_id should NOT be included in data_entity.
        """
        table = 'validation_data'
        L = []
        for element in self.columns[table][1:]:
            item = data_entity.get(element)
            if item is not None:
                L.append(item)
            else:
                #print('Not a valid column for table %s: %s' % (table, str(item)))
                L.append('')
        self.execute('''INSERT INTO validation_data (
                    program, testplan_latest, testplan_list,
                    model, vendor,
                    uwts_name, dut_type,
                    ca_version, interfaceid,
                    sw_version, hw_version,
                    fw_version, host_os,
                    product_id, tbd_info1,
                    tbd_info2, tbd_info3,
                    expiration, description, vc_id)
                    VALUES
                    (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    tuple(L),
                    commit=commit)
        return self.c.lastrowid

    def get_table_entity(self, table, **kwargs):
        """
        Friendly interface for obtaining a validation entity. Provide a table 
        and key value arguments for that table to receive a validation entity.
        """
        if table not in self.tables:
            print('Error unknown table {0}'.format(table))
            return None
        else:
            v = ValidationGeneric(table, self.columns[table], **kwargs)
            return v

    def get_table_set(self):
        """Returns a set of the tables defined for the validation database."""
        return self.tables

    def update_expiration_byid(self, data_entity, commit=True):
        """Updates the expiration of a entry in the validation_data table."""
        table = 'validation_data'
        vd_id = data_entity.get('vd_id')
        expiration = data_entity.get('expiration')
        if data_entity.table != table:
            print('Cannot update expiration for wrong table ({0})'.format(data_entity.table))
            return
        if vd_id is None:
            print('Cannot update expiration without vd_id')
            return
        if expiration is None:
            print('Cannot update expiration without new expiration')
            return
        T = (expiration, vd_id)
        self.execute('UPDATE validation_data SET expiration=? WHERE vd_id=?',
                     T, commit=commit)

    def get_commands_by_program(self, program):
        """Returns a list of validation_command entities for the given program"""
        table = 'validation_command'
        entities = []
        self.execute('SELECT * FROM validation_command WHERE program=?',
                     (program,))
        fa = self.c.fetchall()
        for command in fa:
            d = {}
            for key in command.keys():
                d[key] = command[key]
            entities.append(self.get_table_entity(table, **d))
        return entities

    def get_command_by_vc_id(self, vc_id):
        """Returns a specific validation_command entity when given a vc_id"""
        table = 'validation_command'
        self.execute('SELECT * FROM validation_command WHERE vc_id=?',
                     (vc_id,))
        fa = self.c.fetchall()
        for command in fa:
            #Should only loop once since vc_id is primary key or not at all
            d = {}
            for key in command.keys():
                d[key] = command[key]
            entity = self.get_table_entity(table, **d)
        return entity

    def get_data_by_program(self, program):
        """Returns a list of validation_data entities for the given program"""
        table = 'validation_data'
        entities = []
        self.execute('SELECT * FROM validation_data WHERE program=?',
                     (program,))
        fa = self.c.fetchall()
        for command in fa:
            d = {}
            for key in command.keys():
                d[key] = command[key]
            entities.append(self.get_table_entity(table, **d))
        return entities

class ValidationGeneric(object):
    """
    ValidationGeneric class provides a data structure to provide 
    input/output interaction storage for validation database methods
    """

    def __init__(self, table, columns, **kwargs):
        self.d = {}
        self.unknowns = []
        self.table = table
        self.columns = columns
        for element in columns:
            if kwargs.get(element) is not None:
                self.d.setdefault(element, kwargs.get(element))
        for element in kwargs:
            if element not in columns:
                print('Unknown key value pair for table {2}: ({0}, {1})'.format(element, kwargs[element], self.table))
                self.unknowns.append((element, kwargs[element]))

    def __repr__(self):
        s = []
        s2 = []
        s.append(self.__class__.__name__)
        s.append('(')
        #s2.append(repr(self.table))
        s2.append('table={0}'.format(repr(self.table)))
        #s2.append(repr(self.columns))
        s2.append('columns={0}'.format(repr(self.columns)))
        for key, value in self.d.items():
            s2.append('{0}={1}'.format(str(key), repr(value)))
        s.append(', '.join(s2))
        s.append(')')
        return ''.join(s)

    def __str__(self):
        s = []
        s2 = []
        s.append('Validation Entity for {0} ('.format(self.table))
        for key, value in self.d.items():
            s2.append('{0}={1}'.format(str(key), repr(value)))
        s.append(', '.join(s2))
        s.append(')')
        return ''.join(s)

    #def get(self, key):
    #    return self.d.get(key)
    def get(self, key):
        if hasattr(self, key):
            return getattr(self, key)
        else:
            if self.d.get(key) is not None:
                return self.d.get(key)
            else:
                return ''

if __name__ == '__main__':
    from pprint import pprint
    dbpath = r'db\validation.db3'
    if os.path.exists(dbpath):
        os.unlink(dbpath)
    valid = TestPlanTemplateDB(dbpath)
    future_expiration = datetime.datetime(2465, 6, 5, 10, 44, 52)
    #Pretty generic command, applicable to stations and Broadcom AP:
    vcmd = valid.get_table_entity('validation_command',
                                  program='VHT',
                                  command_type='CAPI',
                                  description='CAPI block to obtain info for broadcom AP and all vht stations except Marvel',
                                  command='device_get_info!ID,$vendor,$model,$sw_version')
    vc_id = valid.add_command_entry(vcmd)
    #Intel VHT STA data:
    vdata = valid.get_table_entity('validation_data',
                                   program='VHT',
                                   testplan_latest='1.5',
                                   model='7260-1',
                                   vendor='Intel',
                                   uwts_name='wfa_control_agent_intelvht_sta',
                                   dut_type='staut',
                                   sw_version='16.0.1.22',
                                   expiration=future_expiration,
                                   description='Manually entered Intel VHT station info',
                                   vc_id=vc_id)

    valid.add_data_entry(vdata)
    #BroadcomVHT AP data
    vdata = valid.get_table_entity('validation_data',
                                   program='VHT',
                                   testplan_latest='1.5',
                                   model='4360',
                                   vendor='Broadcom',
                                   uwts_name='wfa_control_agent_broadcomvht_ap',
                                   ca_version='1.38',
                                   dut_type='aput',
                                   sw_version='6.30.190.10',
                                   expiration=future_expiration,
                                   description='Manually entered Broadcom VHT AP info',
                                   vc_id=vc_id)
    valid.add_data_entry(vdata)
    #Realtek VHT Station:
    vdata = valid.get_table_entity('validation_data',
                                   program='VHT',
                                   testplan_latest='1.5',
                                   model='RT8192-1',
                                   vendor='Realtek',
                                   uwts_name='wfa_control_agent_realtekvht_sta',
                                   dut_type='staut',
                                   sw_version='2008.2.1215.201',
                                   expiration=future_expiration,
                                   description='Manually entered Realtek VHT station info',
                                   vc_id=vc_id)
    valid.add_data_entry(vdata)
    #Ralink VHT station:
    vdata = valid.get_table_entity('validation_data',
                                   program='VHT',
                                   testplan_latest='1.5',
                                   model='V12.23.34',
                                   vendor='Ralink',
                                   uwts_name='wfa_control_agent_ralinkvht_sta',
                                   dut_type='staut',
                                   sw_version='3.2.12.4944',
                                   expiration=future_expiration,
                                   description='Manually entered Ralink VHT station info',
                                   vc_id=vc_id)
    valid.add_data_entry(vdata)
    #Broadcom VHT station:
    vdata = valid.get_table_entity('validation_data',
                                   program='VHT',
                                   testplan_latest='1.5',
                                   model='4360MC',
                                   vendor='Broadcom',
                                   uwts_name='wfa_control_agent_broadcomvht_sta',
                                   ca_version='1.38',
                                   dut_type='staut',
                                   sw_version='6.30.190.10',
                                   expiration=future_expiration,
                                   description='Manually entered Broadcom VHT station info',
                                   vc_id=vc_id)
    valid.add_data_entry(vdata)
    #Broadcom VHT 11n
    vdata = valid.get_table_entity('validation_data',
                                   program='VHT',
                                   testplan_latest='1.5',
                                   model='4360MCB',
                                   vendor='Broadcom',
                                   uwts_name='wfa_control_agent_broadcomvht_11n_sta',
                                   ca_version='1.38',
                                   dut_type='staut',
                                   sw_version='6.30.190.17',
                                   expiration=future_expiration,
                                   description='Manually entered Broadcom 11n VHT station info',
                                   vc_id=vc_id)
    valid.add_data_entry(vdata)
    #Qualcom VHT station:
    vdata = valid.get_table_entity('validation_data',
                                   program='VHT',
                                   testplan_latest='1.5',
                                   model='Linux',
                                   vendor='Qualcomm Atheros',
                                   uwts_name='wfa_control_agent_qualcommvht_sta',
                                   ca_version='1.0',
                                   dut_type='staut',
                                   sw_version='drv=/wpas=v2.0-devel',
                                   expiration=future_expiration,
                                   description='Manually entered Qualcomm VHT station info',
                                   vc_id=vc_id)
    valid.add_data_entry(vdata)
    #Marvell VHT station:
    #This station uniquely is unable to return a lot of useful data from
    #device_get_info capi
    vdata = valid.get_table_entity('validation_data',
                                   program='VHT',
                                   testplan_latest='1.5',
                                   uwts_name='wfa_control_agent_marvellvht_sta',
                                   ca_version='M-Qual-15.build(11:26:18 Dec 15 2014)',
                                   dut_type='staut',
                                   sw_version='DUT-2.0',
                                   expiration=future_expiration,
                                   description='Manually entered Marvell VHT station info',
                                   vc_id=vc_id)
    valid.add_data_entry(vdata)
    #Marvell 11n VHT station:
    #This happens to have same info
    vdata.uwts_name = 'wfa_control_agent_marvellvht_11n_sta'
    valid.add_data_entry(vdata)
    #Intel 11n station for VHT:
    vdata = valid.get_table_entity('validation_data',
                                   program='VHT',
                                   testplan_latest='1.5',
                                   model='6300-1',
                                   vendor='Intel',
                                   uwts_name='wfa_control_agent_intel11n_sta',
                                   dut_type='staut',
                                   sw_version='13.5.0.6',
                                   expiration=future_expiration,
                                   description='Manually entered Intel 11n for VHT station info',
                                   vc_id=vc_id)
    valid.add_data_entry(vdata)
    vcmd = valid.get_table_entity('validation_command',
                           program='VHT',
                           command_type='external',
                           description='External reference command for Qualcomm VHT AP',
                           command='qualcommVHTGet')
    vc_id = valid.add_command_entry(vcmd)
    #vdata for qualcomm with external
    vdata = valid.get_table_entity('validation_data',
                                    program='VHT',
                                    testplan_latest='1.5',
                                    uwts_name='wfa_control_agent_qualcommvht_ap',
                                    dut_type='aput',
                                    ca_version='Sigma_dut version is PlugFest_1.0.9',
                                    sw_version='Linux (none) 2.6.31--LSDK-10.1_PF6.2 #2 Fri Apr 26 10:38:37 PDT 2013 mips unknown',
                                    expiration=future_expiration,
                                    description='Manually entered data for QualcommVHT AP',
                                    vc_id=vc_id)
    valid.add_data_entry(vdata)
    #Both VHT Ralink APs command:
    vcmd = valid.get_table_entity('validation_command',
                                  program='VHT',
                                  command_type='external',
                                  description='External reference command for Ralink AC AP in VHT',
                                  command='ralinkAc_AP_VHT_get')
    vc_id = valid.add_command_entry(vcmd)
    #Ralink 11n AP for VHT data:
    vdata = valid.get_table_entity('validation_data',
                                   program='VHT',
                                   testplan_latest='1.5',
                                   uwts_name='wfa_control_agent_ralink_ap',
                                   dut_type='aput',
                                   sw_version='<4>Driver version: 2.4.3.5',
                                   expiration=future_expiration,
                                   description='Manually entered Ralink (11n) AP VHT info',
                                   vc_id=vc_id)
    valid.add_data_entry(vdata)
    #RalinkAc data:
    vdata = valid.get_table_entity('validation_data',
                                   program='VHT',
                                   testplan_latest='1.5',
                                   uwts_name='wfa_control_agent_ralinkac_ap',
                                   dut_type='aput',
                                   sw_version='Driver version: 3.0.0.0-VHT-TB-140711',
                                   expiration=future_expiration,
                                   description='Manually entered RalinkAc AP VHT info',
                                   vc_id=vc_id)
    valid.add_data_entry(vdata)
    #Marvell 8864:
    vcmd = valid.get_table_entity('validation_command',
                                  program='VHT',
                                  command_type='external',
                                  description='External reference command for Marvell 8864 VHT AP',
                                  command='marvell8864VHTGet')
    vc_id = valid.add_command_entry(vcmd)
    vdata = valid.get_table_entity('validation_data',
                                   program='VHT',
                                   testplan_latest='1.5',
                                   uwts_name='wfa_control_agent_marvell8864vht_ap',
                                   dut_type='aput',
                                   sw_version='wdev1ap0  version:Driver version: 7.2.6.4-W8864, Firmware version: 7.2.6.3',
                                   expiration=future_expiration,
                                   description='Manually entered data for Marvell8864VHT AP',
                                   vc_id=vc_id)
    valid.add_data_entry(vdata)
    #Realtek AC VHT AP
    vcmd = valid.get_table_entity('validation_command',
                                  program='VHT',
                                  command_type='external',
                                  description='External reference command for RealtekAc VHT AP',
                                  command='realtekAc_AP_validation')
    vc_id = valid.add_command_entry(vcmd)
    vdata = valid.get_table_entity('validation_data',
                                   program='VHT',
                                   testplan_latest='1.5',
                                   uwts_name='wfa_control_agent_realtekac_ap',
                                   sw_version='vht5g-05 (05.23)',
                                   expiration=future_expiration,
                                   description='Manually entered info for RealtekAc VHT AP',
                                   vc_id=vc_id)
    valid.add_data_entry(vdata)
    #Marvell11n VHT AP:
    vcmd = valid.get_table_entity('validation_command',
                                  program='VHT',
                                  command_type='external',
                                  description='External reference command for Marvell 11n VHT AP',
                                  command='marvell11n_AP_validation')
    vc_id = valid.add_command_entry(vcmd)
    vdata = valid.get_table_entity('validation_data',
                                   program='VHT',
                                   testplan_latest='1.5',
                                   uwts_name='wfa_control_agent_marvell11n_ap',
                                   sw_version='Wireless Version: 5.0.6.p2-W8366\nSystem Version: AP95-5.0.6.2C-HW-6281GTWGE\nLSP Version: 2010.11.05-LSP-2.6.29-RC7',
                                   expiration=future_expiration,
                                   description='Manually entered info for Marvell 11n VHT AP',
                                   vc_id=vc_id)
    valid.add_data_entry(vdata)
    #==============P2P=============
    p2p_tp_ver='1.3'
    #Generic capi block for P2P:
    vcmd = valid.get_table_entity('validation_command',
                                  program='P2P',
                                  command_type='CAPI',
                                  description='CAPI block to obtain info for P2P stations',
                                  command='device_get_info!ID,$vendor,$model,$sw_version')
    vc_id = valid.add_command_entry(vcmd)
    #ATHEROS_P2P:
    vdata = valid.get_table_entity('validation_data',
                                   program='P2P',
                                   testplan_latest=p2p_tp_ver,
                                   uwts_name='wfa_control_agent_atherosp2p_sta',
                                   ca_version='02.04.09',
                                   sw_version='12',
                                   vendor='Atheros',
                                   model='P2P (Linux)',
                                   expiration=future_expiration,
                                   description='manually entered ATHEROS_P2P station info',
                                   vc_id=vc_id)
    valid.add_data_entry(vdata)
    #BROADCOM_P2P:
    vdata = valid.get_table_entity('validation_data',
                                   program='P2P',
                                   testplan_latest=p2p_tp_ver,
                                   uwts_name='wfa_control_agent_broadcomp2p_sta',
                                   ca_version='DUT-4.0.0',
                                   sw_version='R22-0',
                                   vendor='Broadcom',
                                   model='6.29.4-167.fc11',
                                   expiration=future_expiration,
                                   description='manually entered BROADCOM_P2P station info',
                                   vc_id=vc_id)
    valid.add_data_entry(vdata)
    #INTEL_P2P:
    vdata = valid.get_table_entity('validation_data',
                                   program='P2P',
                                   testplan_latest=p2p_tp_ver,
                                   uwts_name='wfa_control_agent_intelp2p_sta',
                                   sw_version='15.4.0.11',
                                   vendor='Intel',
                                   model='6300-1',
                                   expiration=future_expiration,
                                   description='manually entered INTEL_P2P station info',
                                   vc_id=vc_id)
    valid.add_data_entry(vdata)
    #RALINK_P2P:
    vdata = valid.get_table_entity('validation_data',
                                   program='P2P',
                                   testplan_latest=p2p_tp_ver,
                                   uwts_name='wfa_control_agent_ralinkp2p_sta',
                                   sw_version='3.1.9.6031',
                                   vendor='Ralink',
                                   model='RA3592-1',
                                   expiration=future_expiration,
                                   description='manually entered RALINK_P2P station info',
                                   vc_id=vc_id)
    valid.add_data_entry(vdata)
    #REALTEK_P2P:
    vdata = valid.get_table_entity('validation_data',
                                   program='P2P',
                                   testplan_latest=p2p_tp_ver,
                                   uwts_name='wfa_control_agent_realtekp2p_sta',
                                   sw_version='1015.8.1209.201',
                                   vendor='Realtek',
                                   model='RT8192-1',
                                   expiration=future_expiration,
                                   description='manually entered REALTEK_P2P station info',
                                   vc_id=vc_id)
    valid.add_data_entry(vdata)
    #=========Valid columns===========
    vco = valid.get_table_entity('validation_columns', program='VHT',
                                 valid_column='model')
    valid.add_validation_column_entry(vco)
    vco = valid.get_table_entity('validation_columns', program='VHT',
                                 valid_column='vendor')
    valid.add_validation_column_entry(vco)
#     vco = valid.get_table_entity('validation_columns', program='VHT',
#                                  valid_column='ca_version')
#     valid.add_validation_column_entry(vco)
#     vco = valid.get_table_entity('validation_columns', program='VHT',
#                                  valid_column='interfaceid')
#     valid.add_validation_column_entry(vco)
    vco = valid.get_table_entity('validation_columns', program='VHT',
                                 valid_column='sw_version')
    valid.add_validation_column_entry(vco)
#     vco = valid.get_table_entity('validation_columns', program='VHT',
#                                  valid_column='hw_version')
#     valid.add_validation_column_entry(vco)
#     vco = valid.get_table_entity('validation_columns', program='VHT',
#                                  valid_column='fw_version')
#     valid.add_validation_column_entry(vco)
#     vco = valid.get_table_entity('validation_columns', program='VHT',
#                                  valid_column='host_os')
#     valid.add_validation_column_entry(vco)
#     vco = valid.get_table_entity('validation_columns', program='VHT',
#                                  valid_column='product_id')
#     valid.add_validation_column_entry(vco)
#     vco = valid.get_table_entity('validation_columns', program='VHT',
#                                  valid_column='tbd_info1')
#     valid.add_validation_column_entry(vco)
#     vco = valid.get_table_entity('validation_columns', program='VHT',
#                                  valid_column='tbd_info2')
#     valid.add_validation_column_entry(vco)
#     vco = valid.get_table_entity('validation_columns', program='VHT',
#                                  valid_column='tbd_info3')
#     valid.add_validation_column_entry(vco)
#     vco = valid.get_table_entity('validation_columns', program='VHT',
#                                  valid_column='expiration')
#     valid.add_validation_column_entry(vco)
    pretty_row = {'model' : 'Device Name',
              'vendor' : 'Vendor',
              'ca_version' : 'Control Agent Version',
              'interfaceid' : 'Interface ID',
              'sw_version' : 'Software Version',
              'hw_version' : 'Hardware Version',
              'fw_version' : 'Firmware Version',
              'host_os' : 'Host Operating System',
              'product_id' : 'Product ID',
              'tbd_info1' : 'Testbed Device Information',
              'tbd_info2' : 'Testbed Device Information',
              'tbd_info3' : 'Testbed Device Information',
              'expiration' : 'Expiration'}
    valid.add_pretty_entry(pretty_row)
    vp = valid.get_validation_description()
    pprint(vp)
