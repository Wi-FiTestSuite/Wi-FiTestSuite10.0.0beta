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

"""Validation module, providing validation services"""
from __future__ import print_function
from __future__ import division
#import sqlite3
import os
import re
#from WTSDBAccess.validationdb import ValidationDAO
#from WTSDBAccess.validationdb import ValidationGeneric
from dbaccess.validationdb import ValidationService
#import datetime
import telnetlib
import urllib2
from HTMLParser import HTMLParser
from core.configservice import TestConfigService
from pprint import pprint

_vrl = []

def get_validation_results_handle():
    global _vrl
    return _vrl

class HTML_AP_Helper(HTMLParser):

    def handle_data(self, data):
        if data.strip() != '':
            try:
                self.data_list.append(data.strip())
            except (AttributeError):
                self.data_list = [data.strip()]

    def get_data_list(self):
        return self.data_list

class ValidationExternal(object):
    """
    This class has methods for obtaining validation information from stations
    that do not support obtaining validation information via CAPI commands.
    Generally the names of the methods will be stored in a database.
    """

    def broadcomVHTGet(self, host, port=23, user=None, password=None):
        """Collects information from Broadcom VHT AP via telnet"""
        #This can't actually work. UCC has no knowledge of this AP's IP address
        #only the broadcom CA does. Luckily capi commands work for it.
        if host is None:
            return {}
        try:
            tn = telnetlib.Telnet(host)
        except (IOError):
            return {}
        tn.read_until("# ", 3)
        tn.write("wl ver\r\n")
        version = tn.read_until("# ", 3)
        tn.write("exit\r\n")
        tn.close()
        sw_version = version.split('\r\n')[2]
        return {'sw_version' : sw_version}

    def ralinkAc_AP_VHT_get(self, host, port=23, user=None, password=None):
        """Collects information from a Ralink AC VHT AP via telnet"""
        if host is None:
            return {}
        try:
            tn = telnetlib.Telnet(host=host, port=port)
        except (IOError):
            return {}
        tn.read_until('# ', 3)
        tn.write('dmesg -c > /dev/null;iwpriv ra0 show driverinfo; dmesg\r\n')
        raw_ret = tn.read_until('# ', 3)
        tn.write('exit\r\n')
        tn.close()
        try:
            sw_version = raw_ret.split('\r\n')[1]
        except (IndexError, AttributeError, TypeError):
            return {}
        return {'sw_version' : sw_version}

    def qualcommVHTGet(self, host, port=23, user=None, password=None):
        """Collects information from Qualcomm VHT AP via telnet"""
        if host is None:
            return {}
        try:
            tn = telnetlib.Telnet(host=host, port=port)
        except (IOError):
            return {}
        tn.read_until("(none) login: ", 3)
        #tn.write("{0}\n".format(user))
        tn.write('root\r\n')
        tn.read_until("Password: ", 3)
        #tn.write("{0}\n".format(password))
        tn.write('5up\r\n')
        tn.read_until("~ # ", 3)
        tn.write("sigma_dut -v\r\n")
        raw_ca_version = tn.read_until("~ # ", 3)
        tn.write("uname -a\r\n")
        raw_sw_version = tn.read_until("~ # ", 3)
        tn.write("exit\r\n")
        tn.close()
        try:
            ca_version = raw_ca_version.split('\r\n')[1]
        except (IndexError, AttributeError, TypeError):
            return {}
        try:
            sw_version = raw_sw_version.split('\r\n')[1]
        except (IndexError, AttributeError, TypeError):
            return {}
        return {'sw_version' : sw_version, 'ca_version' : ca_version}

    def marvell8864VHTGet(self, host, port=23, user=None, password=None):
        """Collects information from Marvell 8864 VHT AP via telnet"""
        if host is None:
            return {}
        try:
            tn = telnetlib.Telnet(host=host, port=port)
        except (IOError):
            return {}
        tn.read_until("MarvellAP login: ", 3)
        tn.write("{0}\r\n".format(user))
        tn.read_until("Password: ", 3)
        tn.write("{0}\r\n".format(password))
        tn.read_until("~ $ ", 3)
        tn.write("iwpriv wdev1ap0 version\r\n")
        raw_sw_version = tn.read_until("~ ", 3)
        tn.write("exit\r\n")
        tn.close()
        try:
            sw_version = raw_sw_version.split('\r\n')[1]
        except (IndexError, AttributeError, TypeError):
            return {}
        return {'sw_version' : sw_version}

    def marvell11n_AP_validation(self, host, port=80, user=None, password=None):
        if host is None:
            return {}
        url = 'http://{0}/fw_upgrade.asp'.format(host)
        req = urllib2.Request(url)
        try:
            response = urllib2.urlopen(req)
        except (IOError):
            return {}
        helper = HTML_AP_Helper()
        helper.feed(response.read())
        l = helper.get_data_list()
        if len(l) >= 3:
            sl = l[-3:]
            d = {}
            d['sw_version'] = '\n'.join(sl)
            return d
        else:
            return {}

    def realtekAc_AP_validation(self, host, port=80, user=None, password=None):
        if host is None:
            return {}
        url = 'http://{0}/upload.htm'.format(host)
        req = urllib2.Request(url)
        response = urllib2.urlopen(req)
        helper = HTML_AP_Helper()
        helper.feed(response.read())
        l = helper.get_data_list()
        wanted_idx = None
        for idx, val in enumerate(l):
            if re.search('Firmware Version:', val):
                wanted_idx = idx + 1
                break
        try:
            ret = l[wanted_idx]
        except (IndexError):
            return {}
        return {'sw_version' : ret}

    def get_method(self, method_name):
        """Retrieves a method or None when given a method_name"""
        if hasattr(self, method_name):
            return getattr(self, method_name)
        else:
            return None

class ValidationResult(object):
    """Result class for validation"""

    def __init__(self, device_name, data_entity, tbd_result, results, program, ip_dict={}):
        self.device_name = device_name
        self.data_entity = data_entity
        self.tbd_result = tbd_result
        self.results = results
        self.ip_dict = ip_dict
        self.program = program
        overall_success = True
        for success in results.values():
            overall_success = overall_success and success[0]
        self.overall = overall_success

    def __repr__(self):
        L2 = ['ValidationResult(']
        L = []
        L.append(self.device_name)
        L.append(repr(self.data_entity)) 
        L.append(repr(self.tbd_result))
        L.append(str(self.results))
        L2.append(', '.join(L))
        L2.append(')')
        return ''.join(L2)

    def __str__(self):
        L = ['ValidationResult(']
        L.append('overall: ')
        if self.overall:
            L.append('success')
        else:
            L.append('failure')
        L.append(str(self.results))
        L.append(')')
        return ''.join(L)

    def get_name(self):
        return self.device_name

    def create_report(self, suppress_expiration=True):
        final = [[]]
        pretty_row = Validation().get_pretty_rows()
        for net_name, ip_address in self.ip_dict.items():
            final.append([net_name, ip_address])
        final.append(['Program:', '{0}'.format(self.program)])
        if not self.overall:
            final.append(['Overall validation for this device:', 'Failed'])
            #final.append(['Device may be out of date or not responding', ' '])
            rset = set()
            #{x.add(res_tuple[2]) for res_tuple in self.results.values()}
            for res_tuple in self.results.values():
                rset.add(res_tuple[2])
            if rset == {''}:
                final.append(['Device could not be validated due to connection issues', ''])
                final.append(['Please check network and try again', ''])
            else:
                final.append(['Device may require updates, see test plan and tech ops manual for details', ''])
                final.append(['The details below indicate the values expected to be returned by the device and the actual values given by the device', ''])
        else:
            final.append(['Overall validation for this device:', 'Passed'])
        for validation_field, result_tuple in self.results.items():
            L = []
            if validation_field == 'expiration' and suppress_expiration:
                #suppress expiration in results
                continue
            if result_tuple[0]:
                left = pretty_row.get(validation_field)
                if left is None:
                    left = validation_field
                if result_tuple[1] == '':
                    #sig-1746:
                    right = 'Device does not support retrieval of this information'
                else:
                    right = result_tuple[2]
                L.append('{0}:'.format(left))
                L.append('{0}'.format(right))
                final.append(L)
            else:
                dbleft = pretty_row.get(validation_field)
                if dbleft is None:
                    dbleft = validation_field
                dbright = self.data_entity.get(validation_field)
                L.append('Expected {0}:'.format(dbleft))
                #sig-1746
                if dbright == '':
                    L.append('Device does not support retrieval of this information')
                else:
                    L.append('{0}'.format(dbright))
                final.append(L)
                L = []
                tbdleft = pretty_row.get(validation_field)
                if tbdleft is None:
                    tbdleft = validation_field
                tbdright = self.tbd_result.get(validation_field)
                L.append('{0} reported by device:'.format(tbdleft))
                L.append('{0}'.format(tbdright))
                final.append(L)
        return final

class Validation(object):

    def validate(self, tbd_result, data_entity, name='', ip_dict={}):
        """
        Compares CAPI block results with a data_entity that is filled with
        known validation data
        """
        global _vrl
        program = data_entity.get('program')
        #program = 'VHT'
        validation_fields = self.get_validation_fields(program)
        #validation_fields.remove('expiration')
        if name != '':
            device_name = name
        else:
            device_name = data_entity.get('uwts_name')
        #print(validation_fields)
        results = {}
        for field in validation_fields:
            #Unconditionally validate each field thanks to sig-1746
            #if data_entity.get(field) != '':
            dfield = data_entity.get(field).strip()
            rfield = tbd_result.get(field).strip()
            results[field] = (dfield.lower() == rfield.lower(), dfield, rfield)
        vr = ValidationResult(device_name, data_entity, tbd_result, results, program, ip_dict)
        _vrl.append(vr)
        #pprint(results)
        return vr

    def new_session(self, program):
        with ValidationService() as vs:
            vdao = vs.get_validationDAO()
            ret = vdao.create_result_session(program)
            vdao.delete_other_result_sessions(ret, program)
        return ret

    def get_latest_result_session(self):
        with ValidationService() as vs:
            vdao = vs.get_validationDAO()
            ret = vdao.get_latest_result_session()
        return ret

    def commence_validation(self, program, tbd_list):
        print('commence_validation')
        self.new_session(program)
        v_cmd_data = self.get_validation_routines(program)
        data_table = 'validation_data'
        for tbd in tbd_list:
            ip_dict = {}
            if tbd.alias in v_cmd_data:
                print('Do validation for %s' % tbd.alias)
                if tbd.ctrlipaddr != '' and tbd.ctrlipaddr != '127.0.0.1':
                    ip_dict['Control Network IP Address'] = tbd.ctrlipaddr
                if tbd.testipaddr != '' and tbd.testipaddr != '127.0.0.1':
                    ip_dict['Test Network IP Address'] = tbd.testipaddr
                tbd_data = self.get_validation_entity(data_table, **tbd.validation_dict)
                if tbd.displayname != ''and tbd.displayname != 'DUT':
                    name = tbd.displayname
                else:
                    name = v_cmd_data[tbd.alias]['data'].get('uwts_name')
                val_result = self.validate(tbd_data, v_cmd_data[tbd.alias]['data'], name, ip_dict) 
            else:
                if tbd.alias == '':
                    tbd_alias = 'wfa_control_agent_' + tbd.dev_name.lower() + '_ap'
                    if tbd_alias in v_cmd_data:
                        print('Do validation for %s' % tbd_alias)
                        if tbd.ctrlipaddr != '' and tbd.ctrlipaddr != '127.0.0.1':
                            ip_dict['Control Network IP Address'] = tbd.ctrlipaddr
                        if tbd.testipaddr != '' and tbd.testipaddr != '127.0.0.1':
                            ip_dict['Test Network IP Address'] = tbd.testipaddr
                        tbd_data = self.get_validation_entity(data_table, **tbd.validation_dict)
                        if tbd.displayname != '' and tbd.displayname != 'DUT':
                            name = tbd.displayname
                        else:
                            name = v_cmd_data[tbd_alias]['data'].get('uwts_name')
                        val_result = self.validate(tbd_data, v_cmd_data[tbd_alias]['data'], name, ip_dict)
                    else:
                        print('will not validate "%s" AKA "%s" AKA "%s"' % (tbd.alias, tbd.dev_name, tbd.displayname))

    def get_validation_entity(self, table, **kwargs):
        with ValidationService() as vs:
            vdao = vs.get_validationDAO()
            table_entity = vdao.get_table_entity(table, **kwargs)
        return table_entity

    def get_validation_routines(self, program):
        """
        Given a program, will return a dictionary of 
        {uwts_name : {'command':command, 'data':data}} for obtaining data 
        needed for validation
        """
        with ValidationService() as vs:
            vdao = vs.get_validationDAO()
            commandlist = vdao.get_command_list(program)
        return commandlist
    
    def get_validation_fields(self, program='VHT'):
        with ValidationService() as vs:
            vdao = vs.get_validationDAO()
            valid_set = vdao.get_validation_fields(program)
        return valid_set

    def get_pretty_rows(self):
        with ValidationService() as vs:
            vdao = vs.get_validationDAO()
            pr = vdao.get_pretty_rows()
        return pr

if __name__ == '__main__':
    from pprint import pprint
    os.chdir('src')
    v = Validation()
    l = v.get_validation_routines('VHT')
    pprint(l)
    s = v.get_validation_fields()
    #pprint(s)
    #Realtek:
    r_d = l['wfa_control_agent_realtekvht_sta']['data']
    r_c = l['wfa_control_agent_realtekvht_sta']['command']
    print(r_c)
    print(r_d)
    #Intel:
    i_d = l['wfa_control_agent_intelvht_sta']['data']
    i_c = l['wfa_control_agent_intelvht_sta']['command']
    print(i_d)
    print(i_c)
    #We mixed up realtek and intel:
    vr = v.validate(r_d, i_d)
    pprint(vr.results)
    print(vr)
    pprint(vr.create_report(True))
    pprint(vr.overall)
    vr2 = v.validate(r_d, r_d)
    print(vr2)
    print(vr2.overall)
    pprint(vr2.create_report())
