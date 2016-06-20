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
    
from time import gmtime, strftime
import sys, time
import re
import struct
import logging
import ctypes
import thread
import threading
import random
import subprocess, platform, os
from socket import *
from select import select
from random import randrange

from netcomm.netsocket import NetCommClient, NetCommServer
from testinfo.datastream import streamInfo, streamResult
from core.symtable import TestScriptSymbolTable
from util.misc import Util
from features.validation import ValidationExternal


class ValueTable:
    ret = {"$WTS_ControlAgent_Support" : 1, "$DUT_IF" : "wifi0", "$PING1" : "9"}
    var = {"ifCondBit" : True, "socktimeout" : 60, "iDNB" : 0}
    displayName = {}
    recv_id = {}
    oplist = []
    traffic_done = False
    client_net = None
    clisock_ip = {}
    lock = threading.RLock()
    
    @staticmethod
    def sock_tcp_conn(ipa, ipp):        
        if "%s:%s" %(ipa, ipp) in NetCommServer.conntable:
            #logging.info('Already Connected to - IP Addr = %s Port =%s', ipa, ipp)
            #client_sock = NetCommServer.conntable["%s:%s" %(ipa, ipp)]
            return
        
        ValueTable.client_net = NetCommClient(AF_INET,SOCK_STREAM)
        ValueTable.client_net.networkClientSockConnect(ipa, ipp)            
        NetCommServer.conntable["%s:%s" %(ipa, ipp)] = ValueTable.client_net.sock
        ValueTable.clisock_ip["%s:%s" %(ipa, ipp)] = ValueTable.client_net

class ExecutionTask(object):
    """Execution Task to be enqueued into Execution Queue.


    Attributes:
        cmd: A string representing CAPI command
        param: A dictionary of parameters with key/value pairs 
        ret: A dictionary of return variables with initial values set to an empty string
        ip: A string representing the IP address and port number
    """
    def __init__(self, test_mngr_initr):
        ret = {}
        self.cmd = "" # string
        self.param = "" # string
        self.ret = {} # dict
        self.ipport = "" # string
        self.recv = ""
        self.device_id = ""
        self.test_mngr_initr = test_mngr_initr
        self.testBedDeviceList = test_mngr_initr.test_prog_mngr.test_prog.testbed_dev_list
        #self.runningPhase = test_mngr_initr.test_data_strm_mngr.running_phase
        #self.streamSendResultArray = test_mngr_initr.test_data_strm_mngr.data_strm.streamSendResultArray
        #self.streamRecvResultArray = test_mngr_initr.test_data_strm_mngr.data_strm.streamRecvResultArray
        #self.streamInfoArray = test_mngr_initr.test_data_strm_mngr.data_strm.streamInfoArray
        #self.RTPCount = test_mngr_initr.test_data_strm_mngr.RTPCount
        #self.multicast = test_mngr_initr.test_data_strm_mngr.multicast
        #self.client = None #NetCommClient(AF_INET,SOCK_STREAM)
        self.sendStatus = False
        self.recvStatus = False
        #self.DisplayNameTable = {}
        self.DisplayNameTable = self.set_displayname()
        self.ori_param = ''

        self.parallel = False
        self.queue_parallel_id = None
        self.sub_queue_id = None
        self.type = None

        self.check_parallel(self.cmd)
        self.queue_parallel_id = self.check_parallel_id(self.cmd)
        self.set_type(self.ipport)
        self.countablesock = {}
        
    @property
    def multicast(self):
        return self.test_mngr_initr.test_data_strm_mngr.multicast

    @multicast.setter
    def multicast(self, value):
        self.test_mngr_initr.test_data_strm_mngr.multicast = value

    @property
    def running_phase(self):
        return self.test_mngr_initr.test_data_strm_mngr.running_phase

    @running_phase.setter
    def running_phase(self, value):
        self.test_mngr_initr.test_data_strm_mngr.running_phase = value

    @property
    def RTPCount(self):
        return self.test_mngr_initr.test_data_strm_mngr.RTPCount

    @RTPCount.setter
    def RTPCount(self, value):
        self.test_mngr_initr.test_data_strm_mngr.RTPCount = value

    @property
    def resultPrinted(self):
        return self.test_mngr_initr.test_data_strm_mngr.resultPrinted

    @resultPrinted.setter
    def resultPrinted(self, value):
        self.test_mngr_initr.test_data_strm_mngr.resultPrinted = value


    def condreplace(self, exprs):
        if re.search(r"<>", self.param) or re.search(r"<=", self.param) or re.search(r">=", self.param):
            return
        elif self.param.find(exprs) != -1:
            new_exprs = "!" + exprs + "!"
            self.param = self.param.replace(exprs, new_exprs)

    def execute(self):
	    #ret_data_def_type = self.ret.split(',')
        #logging.debug("Command Return Type = %s" % (ret_data_def_type[0].lower()))
        #if ret_data_def_type[0] == 'STREAMID' or ret_data_def_type[0] == 'INTERFACEID' or ret_data_def_type[0] == 'PING':
        #    self.ret = 
        #    ret_data_idx = ret_data_def_type[1]
        #elif ret_data_def_type[0] == 'RECV_ID':
        #    recv_value = ret_data_def_type[1].split(' ')
        #    i = 0
        #    for r in recv_value:
        #        ValueTable.recv_id[i] = r
        #        i += 1
        #    logging.debug('RECV ID %s', ValueTable.recv_id)
        #print "self.param = " + self.param
        if TestScriptSymbolTable.test_script_sym_tab["ifCondBit"] == False:
            if self.cmd == "if":
                return getattr(self, "if_statement")()
            elif self.cmd == "else":
                return getattr(self, "else_statement")()
            elif self.cmd == "endif":
                return getattr(self, "endif_statement")()
            else:
                return 'SKIP'
        self.ori_param = self.param
        flag = 0
        if self.cmd == "":
            return
        if (self.param.find("$") != -1): 
            if self.cmd == "if":
                self.param = self.param.replace(" or ", "!or!")
                self.param = self.param.replace(" and ", "!and!")
                self.param = self.param.replace("=", "!=!")
                self.param = self.param.replace("<", "!<!")
                self.param = self.param.replace(">", "!>!")
                self.param = self.param.replace("!!", "")
                capi_elem = self.param.split('!')
                #print "self.param = " + self.param
            elif self.cmd == "ResultCheck":
                capi_elem_temp = self.param.split('!')
                #print "capi_elem_temp = " + capi_elem_temp[1]
                capi_elem = capi_elem_temp[1].split(',')
            elif self.cmd == "CheckThroughput":
                capi_elem_temp = self.param.split('!')
                #print "capi_elem_temp = " + capi_elem_temp[1]
                capi_elem = capi_elem_temp[1].split(',')
            elif self.cmd == 'define':
                capi_elem_temp = self.param.split('!')
                #print 'self.param'
                #print self.param
                capi_elem = capi_elem_temp
                flag = 1
            elif self.cmd == "traffic_agent_send":
                capi_elem_temp = self.param.split(',')
                #print "capi_elem_temp = " + capi_elem_temp[1]
                capi_elem = capi_elem_temp[1].split(' ')
            elif self.cmd == "traffic_agent_receive_stop":
                capi_elem_temp = self.param.split(',')
                #print "capi_elem_temp = " + capi_elem_temp[1]
                capi_elem = capi_elem_temp[1].split(' ')
            elif self.cmd == "math" or self.cmd =="config_multi_subresults" or self.cmd =="cat":
                #skip for loop below
                flag = 1
            elif self.cmd == "getuserinput":
                #skip for loop below
                capi_elem = self.param.split(',')
                flag = 1
            elif self.cmd == "StoreThroughput":
                capi_elem_temp = self.param.split('!')
                #print "capi_elem_temp = " + capi_elem_temp[1]
                capi_elem = capi_elem_temp[1].split(',')
                #flag = 1
            else:
                capi_elem = self.param.split(',')
            if flag != 1:
                index = 0
                for i in capi_elem:
                    #print "capi_elem[index] = " + capi_elem[index]
                    if (capi_elem[index].find("$") != -1):
                        try:
                            if capi_elem[index] in TestScriptSymbolTable.capi_cmd_ret_sym_tab:
                                self.param = self.param.replace(capi_elem[index], str(TestScriptSymbolTable.capi_cmd_ret_sym_tab[capi_elem[index]]))
                            elif capi_elem[index] in TestScriptSymbolTable.test_script_sym_tab:
                                self.param = self.param.replace(capi_elem[index], str(TestScriptSymbolTable.test_script_sym_tab[capi_elem[index]]))
                            else:
                                if (capi_elem[index].find("!") == -1):
                                    print "KEY NOT FOUND : " + capi_elem[index]									
                            #print "after self.param = " + self.param
                            
                        except:
                            raise Exception('Error to replace  - %s' % capi_elem[index])
                    index = index + 1

        #self.setRetVal(self.getRetKey(retDict), ret_val)
        if self.ret:
            logging.debug ("ret    : %s" % str(self.ret))
            retKey = ""

            for key, val in self.ret.items():
                retKey = val.keys()[0]
            #ret_data_def_type = self.getRetKey(retDict)self.ret.split(',')
            if self.ret.keys()[0] == 'STREAMID' or self.ret.keys()[0] == 'INTERFACEID' or self.ret.keys()[0] == 'PING':
                ret_data_idx = retKey
            elif self.ret.keys()[0] == 'RECV_ID':
                recv_value = retKey.split(' ')
                i = 0
                for r in recv_value:
                    ValueTable.recv_id[i] = TestScriptSymbolTable.capi_cmd_ret_sym_tab[r]
                    i += 1
                logging.debug('RECV ID %s', ValueTable.recv_id)

        if self.type == "UCCAction":
            if self.cmd == "if":
                return getattr(self, "if_statement")()
            elif self.cmd == "else":
                return getattr(self, "else_statement")()
            elif self.cmd == "endif":
                return getattr(self, "endif_statement")()
            elif self.cmd == "SEPRATROR":
                return 
            elif self.cmd == "ResultCheck":
                return
            elif self.cmd == "CheckThroughput":
                return
            elif self.cmd == "config_multi_subresults":
                return
            if TestScriptSymbolTable.test_script_sym_tab["ifCondBit"] == False:
                return
            else:
                return getattr(self, self.cmd.lower())()
        elif self.type == "UCCCommand":
            if self.cmd.lower() == "traffic_agent_send":
                self.traffic_agent_send()
                return
            elif self.cmd.lower() == "traffic_agent_receive_stop":
                self.traffic_agent_receive_stop()
                return
            elif self.cmd.lower() == "sta_is_connected":
                self.sta_is_connected()
                return
            elif self.cmd.lower() == "sniffer_control_stop":
                self.sniffer_control_stop()
            elif self.cmd.lower() == "externalfunc":
                self.validation_external()
                return
            return self.send_capi()            
        return

    def setRetVal(self, key, val):
        """
        set capi return to global symbol table
        """
        if isinstance(key, str):
            TestScriptSymbolTable.insert_sym_tab(key, val, TestScriptSymbolTable.capi_cmd_ret_sym_tab)
        elif isinstance(key, dict):
            if key:
                for i in len(key):
                    TestScriptSymbolTable.insert_sym_tab(key[i], val[i], TestScriptSymbolTable.capi_cmd_ret_sym_tab)
        elif isinstance(key, list):
            if key:
                i = 0
                for kVal in key:
                    TestScriptSymbolTable.insert_sym_tab(kVal, val[i], TestScriptSymbolTable.capi_cmd_ret_sym_tab)
                    i = i+1
        else:
            logging.debug ("setRetVal error : wrong type..")
            return

    def getRetKey(self, dict):
        """
        return list of keys from Exectuion.ret dictionary
        """
        retKey = ""
        try:
            if dict:
                for key, val in dict.items():
                    retKey = val.keys()[0]
        except TypeError:
            logging.debug ("type error--> %s" % Util.dump(dict))
        
        return retKey


    def get_ap_name(self):
        """
        def get_ap_name(self):
            paramSplit = self.param.split(',')
            if paramSplit[1]:
                return paramSplit[1]
            else:
                return None
        """
        line = self.param
        var = line.split(",")
        if len(var) >=2:
            if self.cmd == "AccessPoint":
                return re.sub('AP', '', var[0])
            else:
                return var[1]
        else:
            return False

    def pinginternalchk(self):
        val = self.get_param()
        TestScriptSymbolTable.insert_sym_tab('PingInternalChk', val, TestScriptSymbolTable.test_script_sym_tab)


    def check_parallel(self, cmd=None):
        """
        Checks to see the cmd has configuration CAPI command to determine
        whether to set to parallel or not
        """
        
        if "ap_reset_default" in cmd:
            self.parallel = True
        elif "ap_set_radius" in cmd:
            self.parallel = True
        elif "ap_set_hs2" in cmd:
            self.parallel = True
        elif "ap_set_apqos" in cmd:
            self.parallel = True
        elif "ap_set_pmf" in cmd:
            self.parallel = True
        elif "ap_get_mac_address" in cmd:
            self.parallel = True
        elif "ap_set_wireless" in cmd:
            self.parallel = True
        elif "ap_set_11n_wireless" in cmd:
            self.parallel = True
        elif "ap_set_security" in cmd:
            self.parallel = True
        elif "ap_config_commit" in cmd:
            self.parallel = True
        elif "AccessPoint" in cmd:
            self.parallel = True
        elif "ap_set_staqos" in cmd:
            self.parallel = True
        return

    def is_parallel(self):
        """
        Get parallel configuration
        """
        return self.parallel

    def is_sub_queue_required(self):
        """
        Checks to see if parallel configuration or if/else statement 
        """
        if self.parallel or self.cmd == "if" or self.cmd == "else":
            return True
        return False

    def get_cmd(self):
        """
        Get cmd string, which is the CAPI command in this case
        """
        return self.cmd

    def set_cmd(self, cmd):
        """
        Set cmd string, which is the CAPI command in this case
        """
        self.check_parallel(cmd)
        self.cmd = cmd
        return self.cmd
    
    def get_device_id(self):
        """
        Get device_id string, which is the CAPI command in this case
        """
        return self.device_id
    
    def set_device_id(self, device_id):
        """
        Set device_id string, which is the CAPI command in this case
        """
        self.device_id = device_id

    def get_param(self):
        """
        Get param dictionary, which is the CAPI parameter key/value pairs in this case
        """
        return self.param

    def set_param(self, param):
        """
        Set param dictionary, which is the CAPI parameter key/value pairs in this case
        """
        self.param = param
        return self.param

    def get_ret(self):
        """
        Get return dictionary, which is the key/value pair returns in this case
        """
        return self.ret

    def set_ret(self, ret):
        """
        Set return dictionary, which is the key/value pair returns in this case
        """
        self.ret = ret
        return self.ret

    def get_ipport(self):
        """
        Get IP address string
        """
        return self.ipport

    def set_ipport(self, ipport):
        """
        Set IP address string
        """
        self.ipport = ipport
        self.set_type(ipport)
        return self.ipport



    def set_type(self, ipport):
        """
        Set the type of task, which could be either UCCAction or UCCExecute.
        """
        if ipport == "":
            self.type = "UCCAction"
        else:
            self.type = "UCCCommand"
        return

    def get_type(self):
        """
        Get the type of task, which could be either UCCAction or UCCExecute.
        """

        return self.type

    def check_parallel_id(self, cmd=None):
        """
        check parallel id
        """
        if "queue_parallel_id" in cmd:
            split_raw_data = self.param.split(',')
            self.sub_queue_id = split_raw_data[1]
        return

    def get_sub_queue_id(self):
        """
        Get sub queue id
        """    
        #print self.sub_queue_id
        return self.sub_queue_id

    def set_status(self, status=""):
        """
        Sets the status of the task
        """
        self.status = status

    def get_status(self):
        """
        Gets the status of the task
        """
        return self.status

    def ping(self, host):
        """
        Returns True if host responds to a ping request
        """
        # Ping parameters as function of OS
        ping_str = "-n 1" if  platform.system().lower()=="windows" else "-c 1"
        args = "ping " + " " + ping_str + " " + host
        #need_sh = False if  platform.system().lower()=="windows" else True

        # Ping
        return subprocess.call(args, stdout=open(os.devnull, 'wb')) == 0

        

    def send_capi(self):
        buffer = 2048
        split_ipport_data = self.ipport.split(':')
        #print "send_capi: ip ", split_ipport_data[0], " port", split_ipport_data[1]

        #copy_param = self.param
        #print copy_param
        if self.param is '':
            cmd = self.cmd + " \r\n"
        else:     
            cmd = self.cmd + "," + self.param + " \r\n"

        #check cmd
        if(cmd.find("$") != -1):
            Util.set_color(Util.FOREGROUND_RED | Util.FOREGROUND_INTENSITY)
            logging.info("Test Case Criteria Failure - Found uninitialized variable ($)")
            Util.set_color(Util.FOREGROUND_INTENSITY)
            return "FAIL"
        
        pingchk = self.ping(split_ipport_data[0])
        pingchk = self.ping(split_ipport_data[0])
        if pingchk == False and self.parallel == False:
            Util.set_color(Util.FOREGROUND_RED | Util.FOREGROUND_INTENSITY)
            logging.info("Network Connection Failure - NO IP Connection -- Aborting the test")
            Util.set_color(Util.FOREGROUND_INTENSITY)
            return "FAIL"

        try:       

            ValueTable.lock.acquire()
            
            #print "create new socket"
            ValueTable.sock_tcp_conn(split_ipport_data[0], split_ipport_data[1])
            client = ValueTable.clisock_ip[self.ipport]
            ValueTable.lock.release()
            
            client.networkClientSockSend(cmd)

            socktimeout = TestScriptSymbolTable.get_value_from_sym_tab("socktimeout", TestScriptSymbolTable.test_script_sym_tab)
            if socktimeout > 0 :
                client.networkClientSockTimeout(int(socktimeout))
            else:
                client.networkClientSockTimeout(240)

            self.recv = client.networkClientSockRecv(buffer)

        except:
            return "FAIL"
        

        # Status,Running
        # Quick fix for case where AzWTG sends response RUNNING and COMPLETED in one read

        if len(self.recv) > 25:
            if self.recv.find("status,RUNNING\n") != -1:
                self.recv = self.recv.split('\n')
                self.recv = self.recv[1]
            elif self.recv.find("status,RUNNING\r\n") != -1:
                self.recv = self.recv.replace('status,RUNNING\r\n', '')
            elif self.recv.find("status,RUNNING\n\r") != -1:
                self.recv = self.recv.replace('status,RUNNING\n\r', '')
            elif self.recv.find("status,RUNNING") != -1:
                logging.info("Missing new line after status,RUNNING")
                self.recv = self.recv.replace('status,RUNNING', '')
        else:
            if TestScriptSymbolTable.test_script_sym_tab["iDNB"] == 0:
                self.recv = client.networkClientSockRecv(buffer)
            else:
                TestScriptSymbolTable.test_script_sym_tab["iDNB"] = 0
        #ExecConnect.networkClientSockClose()
        return
    
    
    def send_capi_select(self):        
        buffer = 1024
        split_ipport_data = self.ipport.split(':')
        #print "send_capi: ip ", split_ipport_data[0], " port", split_ipport_data[1]
        ValueTable.sock_tcp_conn(split_ipport_data[0], split_ipport_data[1])
        
        client = ValueTable.clisock_ip[self.ipport]
        
        #=======================================================================
        # for tbd in self.testBedDeviceList:
        #     self.DisplayNameTable.setdefault(self.ipport, tbd.displayname)
        #=======================================================================
            
        cmd = self.cmd + "," + self.param + " \r\n"
        client.networkClientSockSend(cmd)
        #self.client.networkClientSockTimeout(120)
        ##client.networkClientSockTimeout(10)
        ##time.sleep(2)
        return


    def done(self, data):
        """
        Mark a task as complete (done), but don't delete it.
        Replaces task data with the supplied data.
        :param data: Data for pushing into queue
        """

    # UCC Command Methods
    def read1line(self, s):
        """To resolve a readline problem with multiple messages in one line"""
        ret = ''
        c = ''
        while True:
            try:
                c = s.recv(1)
                c.strip()
            except OSError, e:
                logging.info("Recv error: " + e)
                #print "Socket error " + e
            except :
                #print "exception----"
                pass

            if c == '\n' or c == '':
                if c == '':
                    #logging.info("get a null char")
                    pass
                    
                break
            else:
                ret += c

        return ret + '\n'	

    
    def set_displayname(self):
        displayNameTable = {}      
        for tbd in self.test_mngr_initr.test_prog_mngr.test_prog.testbed_dev_list:
            displayNameTable.setdefault("%s:%s" % (tbd.ctrlipaddr, tbd.ctrlport), tbd.displayname)
        
        return displayNameTable


    def responseWaitThreadFunc(self, _threadID, command, addr, receiverStream):
                
        """Thread runs until send string completion or when test stops running"""
        if "$MT" in TestScriptSymbolTable.capi_cmd_ret_sym_tab:
            logging.info("MT START")
            while 1:
                if TestScriptSymbolTable.capi_cmd_ret_sym_tab["$MT"] == "0":
                    break
                time.sleep(0.1)
            logging.info("MT STOP")
        #=======================================================================
        # for tbd in self.testBedDeviceList:
        #     self.DisplayNameTable.setdefault(tbd.ctrlipaddr, tbd.displayname)	
        #=======================================================================
        
        #=======================================================================
        # split_ipport_data = addr.split(':')
        # ipaddr = split_ipport_data[0]
        # 
        # ipport = split_ipport_data[1]
        # 
        # thr_ip_port = ipaddr + ":" + ipport
        #=======================================================================
        #print self.DisplayNameTable
        #print NetCommServer.conntable
        #thread_sock = self.sock
        logging.debug("responseWaitThreadFunc started %s" % TestScriptSymbolTable.test_script_sym_tab["testRunning"])
        while TestScriptSymbolTable.test_script_sym_tab["testRunning"] > 0:
            #print "in thread while---" + str(TestScriptSymbolTable.test_script_sym_tab["testRunning"])
            #Temporarily commented. Will be tested on VHT to confirm removal
            readables, writeables, exceptions = select(NetCommServer.SOCK_READABLE, NetCommServer.SOCK_WRITABLE, NetCommServer.SOCK_ERROR, 0.1)
            for sockobj in readables:
                if sockobj in NetCommServer.SOCK_WAIT:
                    #Resolve the issue in reading 1 single line with multiple messages
                    resp = self.read1line(sockobj)
                    #print "thread while after read1line resp---> " + resp
                    #responseIPAddress = ""
                    resp_arr = resp.split(',')
                    
                    responseIPAddress = ""
                    for sock in NetCommServer.conntable:
                        if sockobj == NetCommServer.conntable[sock]:
                            responseIPAddress = sock
                            #print "response IP address %s ..." % responseIPAddress
                    displayname = responseIPAddress
                    #displayaddr = ""     
                    if responseIPAddress in self.DisplayNameTable:
                        displayname = self.DisplayNameTable[responseIPAddress]
                        #print "self.ipport:%s" % self.ipport
                    #if not resp:
                    logging.info("%-15s <--1 %s" % (displayname, resp))

                    if re.search("RUNNING", resp):
                        resp = resp.strip()
                        resp = resp.lstrip('status,RUNNING')
                        resp = resp.strip() 
                        #print " RUNNING ---"
                        continue
                    elif re.search("COMPLETE", resp):
                        logging.debug("THREAD ---- > Complete Returned")
                        self.recv = resp
                    else:
                        #logging.debug("Did not receive expected RUNNING or COMPLETE response, check device local log for additional information")
                        continue
                    
                    #logging.info("%-15s <--1 %s" % (displayname, resp))
                    
                    #logging.debug("%-15s <--2 %s" % (displayname, resp))
                    
                    #===========================================================
                    #if self.test_mngr_initr.test_data_strm_mngr.data_strm.event:
                    #    self.test_mngr_initr.test_data_strm_mngr.data_strm.event.set()
                    #    time.sleep(2)
                    #===========================================================
                    
                    # Check for send stream completion
                    if len(resp_arr) > 2:
                        if resp_arr[3] == '':
                            logging.error("NULL streamID returned from %s" % self.ipport)
                            continue
                        if resp_arr[2] == 'streamID':
                            logging.debug("STREAM COMPLETED = %s" % (resp_arr[3]))

                            # spliting the values of multiple streams
                            idx = resp_arr[3].strip()
                            idx = idx.split(' ')
                            sCounter = 0 # For mutliple stream value returns
                            if resp_arr[7].split(' ')[sCounter] == '':
                                sCounter = 1
                            
                            for i in idx:
                                txFrames = resp_arr[5].split(' ')[sCounter]
                                logging.debug(" TXFRAMES = %s" % txFrames)
                                #i = ("%s;%s"%(i, self.ipport))
                                if txFrames != '0':
                                    logging.info("%s (%-15s) <--  SEND Stream - %s Completed " % (displayname, responseIPAddress, i))
                                    
                                    # Setting status complete
                                    for p in self.test_mngr_initr.test_data_strm_mngr.data_strm.streamInfoArray:
                                        if p.IPAddress == responseIPAddress and p.streamID == i and p.phase == self.running_phase:
                                            p.status = 1
                                            #print "set status ---> 1"
                                            #print "response ip ----> %s" % responseIPAddress
                                    self.test_mngr_initr.test_data_strm_mngr.data_strm.streamSendResultArray.append(streamResult(i, responseIPAddress, resp_arr[7].split(' ')[sCounter], resp_arr[5].split(' ')[sCounter], resp_arr[11].split(' ')[sCounter], resp_arr[9].split(' ')[sCounter], self.running_phase))

                                else:
                                    self.test_mngr_initr.test_data_strm_mngr.data_strm.streamRecvResultArray.append(streamResult(i, responseIPAddress, resp_arr[7].split(' ')[sCounter], resp_arr[5].split(' ')[sCounter], resp_arr[11].split(' ')[sCounter], resp_arr[9].split(' ')[sCounter], self.running_phase))
                                    logging.info("%s (%-15s) <----  RECV Stream - %s Completed " % (displayname, responseIPAddress, i))
                                    #ValueTable.traffic_done = True
    
                                sCounter += 1
                            
                            #sockobj.close()
                            #print "closing the socket %s ..." % responseIPAddress
                            #if sockobj in NetCommServer.conntable:
                            #    del NetCommServer.conntable[sockobj]
                            #print NetCommServer.SOCK_READABLE
                            ##NetCommServer.SOCK_READABLE.remove(sockobj)
                            ##NetCommServer.SOCK_WAIT.remove(sockobj)
                            #print NetCommServer.SOCK_READABLE
                else:
                    #logging.debug('Unwanted data on socket')
                    pass    
        #print "TEST---->  THREAD ENDS!!!"
        return

    def sniffer_control_stop(self):
        time.sleep(2)
        TestScriptSymbolTable.test_script_sym_tab["testRunning"] = 0
        time.sleep(2)

    def traffic_agent_receive_stop(self):
        
        capi_run = self.cmd + ',' + self.param
        capi_elem = self.param.split(',')
        idx = capi_elem.index('streamID')
        #print "traffic_agent_receive_stop --->"
        # Wait for Send to finish, in case of receive_stop
        sid = capi_elem[1].split(' ')

        #print "capi_elem --: " + str(capi_elem)
        #print "capi_elem[1] --: " + str(capi_elem[1])
        #print "idx : " + str(idx)
        
        capi_elem[idx+1] = ''
        for i in sid:
            val = i
            logging.debug("val--->%s" % val)
            if re.search(";", i):
                val = i.split(";")[0]

            for p in self.test_mngr_initr.test_data_strm_mngr.data_strm.streamInfoArray:
                #print "in for loop ---> p.pairID / p.phase / p.status :" + str(p.pairID) +'/'+  p.phase + '/' + str(p.status)
                #print "in for loop ---> i / self.runningPhase / p.status : " + i +'/'+ self.running_phase + '/' + str(p.status)
                if p.pairID == i and p.phase == self.running_phase:
                    while (p.status != 1):
                        #Minor sleep to avoid 100% CPU Usage by rapid while
                        #print "waiting..."
                        time.sleep(0.5)
                    #print "status %s ..." % p.status
                    ##print "pairID %s ..." % p.pairID
                    #print "running_phase %s ..." % p.phase
                    break
        
        ##logging.info("(%-10s) --> %s" % (self.ipport, self.cmd))
        self.send_capi_select()
        #while ValueTable.traffic_done == False:
        #    time.sleep(0.5)
        
        #time.sleep(1)
        time.sleep(2)
        return

    def traffic_agent_send(self):
        
        capi_run = self.cmd + ',' + self.param
        capi_elem = self.param.split(',')
        rCounter = 0
        sid = capi_elem[1].split(' ')
        
        #print "TRAFFIC_AGENT_SEND!!!"
        for i in sid:
            #Making Send-receive Pair
            #print "sid : " + i
            for s in self.test_mngr_initr.test_data_strm_mngr.data_strm.streamInfoArray:
                #print "s.IPAddress : " + s.IPAddress
                #print "self.ipport : " + self.ipport
                if s.IPAddress == self.ipport and s.streamID == i and s.phase == self.running_phase:
                    #print "ValueTable.recv_id[rCounter] : " + ValueTable.recv_id
                    s.pairID = ValueTable.recv_id[rCounter]

            rCounter += 1
        
        #self.test_mngr_initr.test_data_strm_mngr.data_strm.event = threading.Event()
        
        # Start the response wait thread (only once)
        if TestScriptSymbolTable.test_script_sym_tab["threadCount"] == 0:
            TestScriptSymbolTable.test_script_sym_tab["testRunning"] = 1
            #print "starting thread"
            thread.start_new(self.responseWaitThreadFunc, (TestScriptSymbolTable.test_script_sym_tab["threadCount"], capi_run, self.ipport, ValueTable.recv_id))
            TestScriptSymbolTable.test_script_sym_tab["threadCount"] = TestScriptSymbolTable.test_script_sym_tab["threadCount"] + 1
            #Temporary Addition for VHT
        
        self.send_capi_select()
        return
    # UCC Action Methods

    def _dnb_(self):
        TestScriptSymbolTable.test_script_sym_tab["iDNB"] = 1
        return

    def _inv(self):
        TestScriptSymbolTable.test_script_sym_tab["iINV"] = 1
        return

    def inv_(self):
        TestScriptSymbolTable.test_script_sym_tab["iINV"] = 0
        return

    def add_media_file(self):
        '''
        add media file to report...for WFD program..
        '''
        command = self.param
        #TBD
        #need to decide weather we are goint to keep XML result summary or add this into DB....
        

    def adddutversioninfo(self):
        #handle in addwtscompversioninfo...
        self.addwtscompversioninfo()
        return

    def addwtscompversioninfo(self):

        vInfo = self.param.split(",")
        i = 0

        if len(vInfo) < 5:
            logging.info("Incorrect version format...")
            return

        #print vInfo
        #print len(TestScriptSymbolTable.capi_cmd_ret_sym_tab)
        for c in vInfo:
            if c in TestScriptSymbolTable.capi_cmd_ret_sym_tab:
                vInfo[i] = TestScriptSymbolTable.capi_cmd_ret_sym_tab[c]
            if vInfo[i] in ValueTable.displayName:
                vInfo[i] = ValueTable.displayName[vInfo[i]]
            i = i + 1

        if self.cmd.lower() == 'adddutversioninfo':
            logging.debug("DUT INFO [%s][%s][%s][%s]" % (vInfo[1], vInfo[2], vInfo[3], vInfo[4]))
        else:
            logging.debug("WTS Comp[%s][%s][%s][%s]" % (vInfo[1], vInfo[2], vInfo[3], vInfo[4]))
            
        logging.debug(vInfo)
        return

    def addstaversioninfo(self):
        vInfo = self.param.split(",")
        i = 0

        if len(vInfo) < 5:
            logging.info("Incorrect version format")
            return

        if vInfo[0] not in TestScriptSymbolTable.capi_cmd_ret_sym_tab:
            logging.debug("Unknown Component[1] %s", vInfo[0])
            return

        #tbd
        #if TestScriptSymbolTable.capi_cmd_ret_sym_tab[vInfo[0]] not in conntable:
        #    if TestScriptSymbolTable.capi_cmd_ret_sym_tab[TestScriptSymbolTable.capi_cmd_ret_sym_tab[vInfo[0]]] not in conntable:
        #        logging.debug("Unknown Component[3] %s", vInfo[0])
        #        return

        #print vInfo
        #print len(TestScriptSymbolTable.capi_cmd_ret_sym_tab)
        for c in vInfo:
            if c in TestScriptSymbolTable.capi_cmd_ret_sym_tab:
                vInfo[i] = TestScriptSymbolTable.capi_cmd_ret_sym_tab[c]
            if vInfo[i] in ValueTable.displayName:
                vInfo[i] = ValueTable.displayName[vInfo[i]]
            i = i + 1
        
        #XLogger.AddTestbedDevice(vInfo[1], vInfo[2], vInfo[3], vInfo[4])
        #tbd
        #need to add this info into DB or XML report...
        logging.debug(vInfo)
        return

    def adduccscriptversion(self):
        wholeCommand = self.cmd + "!" + self.param
        command = wholeCommand.split('!')
        #XLogger.AddWTSComponent("UCC", VERSION, self.param)

    def append(self):
        wholeCommand = self.cmd + "!" + self.param
        command = wholeCommand.split('!')
        cmd = command[2].split(" ")
        logging.debug("..append %s = %s %s using %s"%(command[1], cmd[0], cmd[1], command[3]))
        if command[1] in TestScriptSymbolTable.capi_cmd_ret_sym_tab:
            if cmd[0] in TestScriptSymbolTable.capi_cmd_ret_sym_tab:
                cmd[0] = TestScriptSymbolTable.capi_cmd_ret_sym_tab[cmd[0]]
            if cmd[1] in TestScriptSymbolTable.capi_cmd_ret_sym_tab:
                cmd[1] = TestScriptSymbolTable.capi_cmd_ret_sym_tab[cmd[1]]
            TestScriptSymbolTable.capi_cmd_ret_sym_tab[command[1]] = "%s%s%s" %(cmd[0], command[3], cmd[1])
        else:
            if cmd[0] in TestScriptSymbolTable.capi_cmd_ret_sym_tab:
                cmd[0] = TestScriptSymbolTable.capi_cmd_ret_sym_tab[cmd[0]]
            if cmd[1] in TestScriptSymbolTable.capi_cmd_ret_sym_tab:
                cmd[1] = TestScriptSymbolTable.capi_cmd_ret_sym_tab[cmd[1]]
            TestScriptSymbolTable.capi_cmd_ret_sym_tab.setdefault(command[1], "%s%s%s" %(cmd[0], command[3], cmd[1]))
        return

    def calculate_ext_listen_values(self):
        command = self.param.split('!')
        probe_req_interval = int(command[1]) / 2
        probe_req_count = int(command[0]) / (int(command[1]) / 2)
        self.setRetVal("$PROBE_REQ_INTERVAL", probe_req_interval)
        self.setRetVal("$PROBE_REQ_COUNT", probe_req_count)
        return

    def cat(self):
        #wholeCommand = self.cmd + "!" + self.param
        command = self.param.split('!')
        var = ""
        if len(command) < 3:
            #print "Invalid CAT command"
            logging.debug("Invalid CAT command")
        else:
            varlist = command[1].split(",")

            for v in varlist:
                if '$' in v:
                    if v in TestScriptSymbolTable.capi_cmd_ret_sym_tab:
                        v = TestScriptSymbolTable.capi_cmd_ret_sym_tab[v]

                if var:
                    var = ("%s%s%s" % (var, command[2], v))
                else:
                    var = ("%s" % (v))

        logging.debug("VAR=[%s]" % var)

        if command[0] in TestScriptSymbolTable.capi_cmd_ret_sym_tab:
            TestScriptSymbolTable.capi_cmd_ret_sym_tab[command[0]] = var
        else:
            TestScriptSymbolTable.capi_cmd_ret_sym_tab.setdefault(command[0], var)
        return


    def define(self):
        wholeCommand = self.cmd + "!" + self.param
        command = wholeCommand.split('!')
        logging.debug("..Define %s = %s"%(command[1], command[2]))
        if command[1] in TestScriptSymbolTable.capi_cmd_ret_sym_tab:
            if command[2] in TestScriptSymbolTable.capi_cmd_ret_sym_tab:
                command[2] = TestScriptSymbolTable.capi_cmd_ret_sym_tab[command[2]]
            TestScriptSymbolTable.capi_cmd_ret_sym_tab[command[1]] = command[2]
        else:
            if command[2] in TestScriptSymbolTable.capi_cmd_ret_sym_tab:
                command[2] = TestScriptSymbolTable.capi_cmd_ret_sym_tab[command[2]]
            TestScriptSymbolTable.capi_cmd_ret_sym_tab.setdefault(command[1], command[2])

        return

    def displayname(self):
        command = self.cmd
        if (command[1] in TestScriptSymbolTable.capi_cmd_ret_sym_tab):
            ValueTable.displayName.setdefault(ValueTable[command[1]],command[2])
        else:
            ValueTable.displayName.setdefault(command[1],command[2])
        return

    def echo(self):
        if self.param in TestScriptSymbolTable.capi_cmd_ret_sym_tab:
            print "%s=%s" % (self.param, TestScriptSymbolTable.capi_cmd_ret_sym_tab[self.param])
        else:
            print "echo -> %s" % self.param
        return

    def echo_ifnowts(self):
        wholeCommand = self.cmd + "!" + self.param
        command = wholeCommand.split('!')
        if TestScriptSymbolTable.get_value_from_sym_tab("$WTS_ControlAgent_Support", TestScriptSymbolTable.test_script_sym_tab) == "0":
            Util.set_color(Util.FOREGROUND_BLUE |Util.FOREGROUND_INTENSITY)
            if command[1] in  TestScriptSymbolTable.test_script_sym_tab:
                logging.info("-%s=%s-" % (command[1], TestScriptSymbolTable.test_script_sym_tab[command[1]]))
            else:
                logging.info("%s" % command[1])
            Util.set_color(Util.FOREGROUND_WHITE | Util.FOREGROUND_INTENSITY)
            return

    def else_statement(self):
        if TestScriptSymbolTable.test_script_sym_tab["ifCondBit"] == True:
            #print "else setting to false"
            TestScriptSymbolTable.test_script_sym_tab["ifCondBit"] = False
        else:
            #print "else setting to true"
            TestScriptSymbolTable.test_script_sym_tab["ifCondBit"] = True
        return

    def endif_statement(self):
        TestScriptSymbolTable.test_script_sym_tab["ifCondBit"] = True
        #print "endif setting to true"
        return

    def exit(self):
        Util.set_color(Util.FOREGROUND_CYAN | Util.FOREGROUND_INTENSITY)
        print "EXIT----- TBD"
        return
        #wfa_sys_exit("CAPI exit command - %s" % command[1])

    def extract_p2p_ssid(self):
        wholeCommand = self.cmd + "!" + self.param
        command = wholeCommand.split('!')
        if command[1] in TestScriptSymbolTable.capi_cmd_ret_sym_tab:
            command[1] = TestScriptSymbolTable.capi_cmd_ret_sym_tab[command[1]]
        p2p_ssid = command[1].split(' ')
        if len(p2p_ssid) > 1:
            TestScriptSymbolTable.capi_cmd_ret_sym_tab.setdefault("$P2P_SSID", "%s" % p2p_ssid[1])
        else:
            #set_color(FOREGROUND_RED | FOREGROUND_INTENSITY)
            print "Test Case Criteria Failure - Invalid P2P Group ID"
            #logging.info("Test Case Criteria Failure - Invalid P2P Group ID")
            #set_color(FOREGROUND_INTENSITY)
            #logging.error("Test Case Criteria Failure - Invalid P2P Group ID")
        return

    def generate_randnum(self):
        wholeCommand = self.cmd + "!" + self.param
        command = wholeCommand.split('!')
        logging.debug("In generate_randnum...")
        if re.search('null',command[1]):
            cmd1 = "null"
        else:
            if command[1] in TestScriptSymbolTable.capi_cmd_ret_sym_tab:
                cmd1 = TestScriptSymbolTable.capi_cmd_ret_sym_tab[command[1]].split(" ")
            else:
                cmd1 = command[1].split(" ")

        TestScriptSymbolTable.capi_cmd_ret_sym_tab[command[2]] = "0"

        if command[3] in TestScriptSymbolTable.capi_cmd_ret_sym_tab:
            cmd3 = int(TestScriptSymbolTable.capi_cmd_ret_sym_tab[command[3]])
        else:
            cmd3 = int(command[3])

        i = 0
        while True:
            randnum = random.randint(0, 65535)
            for c in cmd1:
                if isinstance(c, int):
                    if(randnum == int(c)):
                        del randnum
                        break
            try:
                ValueTable.oplist.append(randnum)
                i = i + 1
            except NameError:
                logging.debug("Not defined")
            if (i == cmd3):
                break

        TestScriptSymbolTable.capi_cmd_ret_sym_tab[command[2]] = ' '.join("%d" % x for x in ValueTable.oplist)
        logging.debug(" %s" % TestScriptSymbolTable.capi_cmd_ret_sym_tab[command[2]])
        ValueTable.oplist = []

        return

    def get_rnd_ip_address(self):
        wholeCommand = self.cmd + "!" + self.param
        command = wholeCommand.split('!')
        if command[1] in TestScriptSymbolTable.capi_cmd_ret_sym_tab:
            command[1] = TestScriptSymbolTable.capi_cmd_ret_sym_tab[command[1]]
        if command[2] in TestScriptSymbolTable.capi_cmd_ret_sym_tab:
            command[2] = TestScriptSymbolTable.capi_cmd_ret_sym_tab[command[2]]
        ip1 = command[1].split(".")
        ip2 = command[2].split(".")
        if (int(ip2[3]) + 1) != int(ip1[3]):
            rnd_ip = ("%s.%s.%s.%s" % (ip2[0], ip2[1], ip2[2], int(ip2[3]) + 1))
        else:
            rnd_ip = ("%s.%s.%s.%s" % (ip2[0], ip2[1], ip2[2], int(ip2[3]) + 2))
        TestScriptSymbolTable.capi_cmd_ret_sym_tab.setdefault(command[3], "%s" % rnd_ip)
        return

    def getuccsystemtime(self):
        timeStr = time.strftime("%H-%M-%S-%m-%d-%Y", time.localtime())
        logging.debug("\n Reading UCC System time %s" % timeStr)
        t = timeStr.split("-")
        TestScriptSymbolTable.capi_cmd_ret_sym_tab.setdefault("$month", t[3])
        TestScriptSymbolTable.capi_cmd_ret_sym_tab.setdefault("$date", t[4])
        TestScriptSymbolTable.capi_cmd_ret_sym_tab.setdefault("$year", t[5])
        TestScriptSymbolTable.capi_cmd_ret_sym_tab.setdefault("$hours", t[0])
        TestScriptSymbolTable.capi_cmd_ret_sym_tab.setdefault("$minutes", t[1])
        TestScriptSymbolTable.capi_cmd_ret_sym_tab.setdefault("$seconds", t[2])
        logging.debug("""\n UCC System Time- Month:%s: 
                                            Date:%s: 
                                            Year:%s: 
                                            Hours:%s: 
                                            Minutes:%s: 
                                            Seconds:%s:""" %
                                            (TestScriptSymbolTable.capi_cmd_ret_sym_tab["$month"],
                                             TestScriptSymbolTable.capi_cmd_ret_sym_tab["$date"],
                                             TestScriptSymbolTable.capi_cmd_ret_sym_tab["$year"],
                                             TestScriptSymbolTable.capi_cmd_ret_sym_tab["$hours"],
                                             TestScriptSymbolTable.capi_cmd_ret_sym_tab["$minutes"],
                                             TestScriptSymbolTable.capi_cmd_ret_sym_tab["$seconds"]))
        return

    def getuserinput(self):
        print "[USER INPUT REQUIRED]"
        Util.set_color(Util.FOREGROUND_YELLOW | Util.FOREGROUND_INTENSITY)
        logging.info("[USER INPUT REQUIRED]")
        paramSplit = self.param.split('!')
        udata = raw_input(paramSplit[0])
        if paramSplit[1] in TestScriptSymbolTable.capi_cmd_ret_sym_tab:
            TestScriptSymbolTable.capi_cmd_ret_sym_tab[paramSplit[1]] = udata
        else:
            TestScriptSymbolTable.capi_cmd_ret_sym_tab.setdefault(paramSplit[1], udata)
        Util.set_color(Util.FOREGROUND_INTENSITY)
        return

    def if_statement(self):
        itern = 0
        boolOp = []
        lhs = []
        rhs = []
        oper = []
        rtVlTbl = TestScriptSymbolTable.capi_cmd_ret_sym_tab
        symTbl = TestScriptSymbolTable.test_script_sym_tab
        wholeCommand = self.cmd + "!" + self.param
        command = wholeCommand.split('!')
        ifcondBit = -1
        for count, val in enumerate(command):
            if count % 4 == 0:
                itern = itern + 1
                boolOp.append(val)
                #print "boolOp = " + str(val)
            elif count % 4 == 1:
                lhs.append(val)
                #print "lhs = " + str(val)
            elif count % 4 == 2:
                oper.append(val)
                #print "oper.append" + str(val)
            elif count % 4 == 3:
                rhs.append(val)
                #print "rhs = " + str(val)

        #itern = itern - 1
        for iCount in range(0, itern):
            if lhs[iCount] in rtVlTbl:
                lhs[iCount] = rtVlTbl[lhs[iCount]]
            elif lhs[iCount] in symTbl:
                lhs[iCount] = symTbl[lhs[iCount]]
            if rhs[iCount] in rtVlTbl:
                rhs[iCount] = rtVlTbl[rhs[iCount]]
            elif rhs[iCount] in symTbl:
                rhs[iCount] = symTbl[rhs[iCount]]
            if(oper[iCount]).lower() == "=":
                if lhs[iCount].lower() == rhs[iCount].lower():
                    ifcondBit = 1
                else:
                    ifcondBit = 0
            elif (oper[iCount]).lower() == ">":
                if float(lhs[iCount]) > float(rhs[iCount]):
                    ifcondBit = 1
                else:
                    ifcondBit = 0
            elif (oper[iCount]).lower() == "<":
                if float(lhs[iCount]) < float(rhs[iCount]):
                    ifcondBit = 1
                else:
                    ifcondBit = 0
            elif (oper[iCount]).lower() == ">=":
                if float(lhs[iCount]) >= float(rhs[iCount]):
                    ifcondBit = 1
                else:
                    ifcondBit = 0
            elif (oper[iCount]).lower() == "<=":
                if float(lhs[iCount]) <= float(rhs[iCount]):
                    ifcondBit = 1
                else:
                    ifcondBit = 0
            elif (oper[iCount]).lower() == "<>":
                if lhs[iCount].lower() == rhs[iCount].lower():
                    ifcondBit = 0
                else:
                    ifcondBit = 1
            #print "icount = " + str(boolOp[iCount])
            if boolOp[iCount] == "if":
                ifCondBit = ifcondBit
            elif boolOp[iCount] == "or":
                temp_or = ifcondBit
                #print "temp_or " + str(temp_or)
                if ifCondBit or temp_or:
                    ifCondBit = 1
                else:
                    ifCondBit = 0
            elif boolOp[iCount] == "and":
                temp_and = ifcondBit
                if ifCondBit and temp_and:
                    ifCondBit = 1
                else:
                    ifCondBit = 0
            #print "ifConBit " + str(ifCondBit)
        if ifCondBit == 0:
            #print "setting to false"
            TestScriptSymbolTable.test_script_sym_tab["ifCondBit"] = False
            return False
        else:
            #print "setting to true"
            TestScriptSymbolTable.test_script_sym_tab["ifCondBit"] = True
            return True

    def ifnowts(self):
        wholeCommand = self.cmd + "!" + self.param
        command = wholeCommand.split('!')
        if TestScriptSymbolTable.get_value_from_sym_tab("$WTS_ControlAgent_Support", TestScriptSymbolTable.test_script_sym_tab) == "0":
            Util.set_color(Util.FOREGROUND_YELLOW | Util.FOREGROUND_INTENSITY)
            if len(command) > 3 and command[2] in TestScriptSymbolTable.test_script_sym_tab:
                s = "- %s" % TestScriptSymbolTable.test_script_sym_tab[command[2]]
            else:
                s = ""
            logging.info("%s %s\n        Press any key to continue after done" % (command[1], s))

            sys.stdin.read(1)
            Util.set_color(Util.FOREGROUND_WHITE | Util.FOREGROUND_INTENSITY)
        return

    def info(self):
        wholeCommand = self.cmd + "!" + self.param
        command = wholeCommand.split('!')
        Util.set_color(Util.FOREGROUND_CYAN | Util.FOREGROUND_INTENSITY)
        if command[1] in TestScriptSymbolTable.test_script_sym_tab:
            command[1] = TestScriptSymbolTable.test_script_sym_tab[command[1]]
        #logging.info("\n %7s ~~~~~ %s ~~~~~ \n" %("", command[1]))
        Util.set_color(Util.FOREGROUND_INTENSITY)
        return
        print self.param 
        return

    def manual_check_info(self):
        wholeCommand = self.cmd + "!" + self.param
        command = wholeCommand.split('!')
        #XLogger.setManualCheckInfo(command[1])

    def math(self):
        #wholeCommand = self.cmd + "!" + self.param
        command = self.param
        #"$S1+5"
        if '+' in command:
            #print "math - +"
            cmd = '+'
            temp = command.split('+')
        elif '-' in command:
            #print "math - -"
            cmd = '-'
            temp = command.split('-')
        elif '*' in command:
            #print "math - *"
            cmd = '*'
            temp = command.split('*')
        elif '/' in command:
            #print "math - /"
            cmd = '/'
            temp = command.split('/')
        elif '%' in command:
            #print "math - %"
            cmd = '%'
            temp = command.split('%')
        elif 'rand' in command:
            #print "math - rand"
            cmd = 'rand'
            temp = command.split('rand')
        tmp = temp[0]
                        
        #Error handling for math operators, excluding rand
        if cmd != "rand":
            val = []
            for v in temp:
                if '$' in v:
                    val.append(TestScriptSymbolTable.capi_cmd_ret_sym_tab[v])
                else:
                    val.append(v)
            try:
                vara = float(val[0])
            except ValueError:
                print "You must enter a number"
                #set_color(FOREGROUND_RED | FOREGROUND_INTENSITY)
                #logging.info("Test Case Criteria Failure - You must enter a number")
                #set_color(FOREGROUND_INTENSITY)
            try:
                varb = float(val[1])
            except ValueError:
                print "You must enter a number"
                #set_color(FOREGROUND_RED | FOREGROUND_INTENSITY)
                #logging.info("Test Case Criteria Failure - You must enter a number")
                #set_color(FOREGROUND_INTENSITY)
        if cmd == "+":
            cal_val = "%s" % (float(val[0]) +  float(val[1]))
        elif cmd == "-":
            cal_val = "%s" % (float(val[0]) -  float(val[1]))
        elif cmd == "*":
            cal_val = "%s" % (float(val[0]) *  float(val[1]))
        elif cmd == "/":
            cal_val = "%s" % (float(val[0]) /  float(val[1]))
        elif cmd == "%":
            cal_val = "%s" % (int(val[0]) % int(val[1]))
        
        elif cmd == "rand":
            #List of allowed values
            varlist = temp[1].split(":")
            random_index = randrange(0, len(varlist))
            cal_val = "%s" % int(varlist[random_index])
            
        TestScriptSymbolTable.insert_sym_tab(tmp, cal_val, TestScriptSymbolTable.capi_cmd_ret_sym_tab)
        #print "after math ---> "  + TestScriptSymbolTable.capi_cmd_ret_sym_tab[tmp]

    def mexpr(self):
        wholeCommand = self.cmd + "!" + self.param
        command = wholeCommand.split('!')
        if command[1] not in TestScriptSymbolTable.capi_cmd_ret_sym_tab:
            return
        if command[3] in TestScriptSymbolTable.capi_cmd_ret_sym_tab:
            command[3] = TestScriptSymbolTable.capi_cmd_ret_sym_tab[command[3]]
        if command[2] == "%":
            ValueTable[command[1]].ret = (int(TestScriptSymbolTable.capi_cmd_ret_sym_tab[command[1]]) * int(command[3])) / 100
        return

    def pause(self):
        wholeCommand = self.cmd + "!" + self.param
        command = wholeCommand.split('!')
        Util.set_color(Util.FOREGROUND_YELLOW | Util.FOREGROUND_INTENSITY)
        logging.info("Exeuction Paused - %s \n Press any key to continue..." % command[1])
        print "Exeuction Paused - \n Press any key to continue..."
        sys.stdin.read(1)
        Util.set_color(Util.FOREGROUND_INTENSITY)
        return

    def phase(self):
        self.RTPCount = 1
        time.sleep(3)
        logging.debug("Starting Phase - %s ..." % self.param)
        self.running_phase = self.param
        TestScriptSymbolTable.test_script_sym_tab["threadCount"] = 0
        TestScriptSymbolTable.test_script_sym_tab["testRunning"] = 0
        time.sleep(2)
        return

    def r_info(self):
        wholeCommand = self.cmd + "!" + self.param
        command = wholeCommand.split('!')
        rdata = "-"

        #resultPrinted = 1
        #set_test_result(command[1], rdata, "-")
        #wfa_sys_exit_0()
        return

    def reopen_conn(self):
        wholeCommand = self.cmd + "!" + self.param
        command = wholeCommand.split('!')
        if command[1] in TestScriptSymbolTable.capi_cmd_ret_sym_tab:
            command[1] = TestScriptSymbolTable.capi_cmd_ret_sym_tab[command[1]]
        if command[2] in TestScriptSymbolTable.capi_cmd_ret_sym_tab:
            command[2] = TestScriptSymbolTable.capi_cmd_ret_sym_tab[command[2]]

        #process_ipadd("ipaddr=%s, port=%s" % (command[1], command[2]), 1)
        return

    def sta_is_connected(self):
        isConnRetry = 0
        while isConnRetry < 10:
            
            self.send_capi()
            ret_chk = self.recv.split(',')
            
            if '1' in ret_chk[3]:
                return
            else:
                print "retry!!!"
                isConnRetry = isConnRetry + 1
            
            time.sleep(5)
        
        return

    def search(self):
        wholeCommand = self.cmd + "!" + self.param
        command = wholeCommand.split('!')
        if re.search('exact', command[4]):
            if command[1] in TestScriptSymbolTable.capi_cmd_ret_sym_tab:
                cmd1 = TestScriptSymbolTable.capi_cmd_ret_sym_tab[command[1]]
            else:
                cmd1 = command[1]

            if command[2] in TestScriptSymbolTable.capi_cmd_ret_sym_tab:
                cmd2 = TestScriptSymbolTable.capi_cmd_ret_sym_tab[command[2]]
            else:
                cmd2 = command[2]

            TestScriptSymbolTable.capi_cmd_ret_sym_tab[command[3]] = "0"
            if (sorted(cmd1) == sorted(cmd2)):
                TestScriptSymbolTable.capi_cmd_ret_sym_tab[command[3]] = "1"
            return

        elif re.search('diff', command[4]):
            if command[1] in TestScriptSymbolTable.capi_cmd_ret_sym_tab:
                cmd1 = TestScriptSymbolTable.capi_cmd_ret_sym_tab[command[1]]
            else:
                cmd1 = command[1]

            if command[2] in TestScriptSymbolTable.capi_cmd_ret_sym_tab:
                cmd2 = TestScriptSymbolTable.capi_cmd_ret_sym_tab[command[2]]
            else:
                cmd2 = command[2]

            TestScriptSymbolTable.capi_cmd_ret_sym_tab[command[3]] = "0"
            if sorted(cmd1) == sorted(cmd2):
                TestScriptSymbolTable.capi_cmd_ret_sym_tab[command[3]] = "1"
            else:
                logging.debug("cmd1 %s, cmd2 %s" %(cmd1, cmd2))
                cmd1 = set(cmd1.split(' '))
                cmd2 = set(cmd2.split(' '))
                cmd3 = cmd1.difference(cmd2)
                logging.debug("Diff List %s" % cmd3)
                TestScriptSymbolTable.capi_cmd_ret_sym_tab[command[3]] = "%s" %(' '.join(list(cmd3)))
            return

        else:
            if command[1] in TestScriptSymbolTable.capi_cmd_ret_sym_tab:
                cmd1 = TestScriptSymbolTable.capi_cmd_ret_sym_tab[command[1]]
            else:
                cmd1 = command[1]

            if command[2] in TestScriptSymbolTable.capi_cmd_ret_sym_tab:
                cmd2 = TestScriptSymbolTable.capi_cmd_ret_sym_tab[command[2]].split(" ")
            else:
                cmd2 = command[2].split(" ")

            TestScriptSymbolTable.capi_cmd_ret_sym_tab[command[3]] = "0"
            i = 0

            #Check for NULL before comparison
            if cmd2 != "":
                for c in cmd2:
                    logging.info("Search \"%s\" in \"%s\"" %(cmd2[i], cmd1))
                    if re.search('%s' % cmd2[i], cmd1, re.IGNORECASE):
                        TestScriptSymbolTable.capi_cmd_ret_sym_tab[command[3]] = "1"
                    i += 1
            return

    def sleep(self):
        logging.info("Sleep... %s seconds" %(self.param))
        time.sleep(float(self.param))
        return

    def socktimeout(self):
        if int(self.param) > 0:
            logging.info("Setting socket timeout=%d secs" % int(self.param))
            TestScriptSymbolTable.test_script_sym_tab["socktimeout"] = self.param
        else:
            logging.info("Resetting socket timeout")
            socktimeout = 0
        return

    def storethroughput(self):
        #wholeCommand = self.cmd + "!" + self.param
        #command = wholeCommand.split('!')
        cmd = self.param.split("!")
        values = cmd[1].split(',')
        streamid = values[0]
        phase = values[1]
        duration = values[2]
        percentage = values[3]
        storevar = cmd[0]
        logging.debug("Storing the Throughput(Mbps) value of stream %s[%s %s] in %s  duration=%s p=%s", streamid, percentage, "%", storevar, duration, phase)
        P1 = -1
        for p in self.test_mngr_initr.test_data_strm_mngr.data_strm.streamRecvResultArray:
            if p.streamID == streamid and int(p.phase) == int(phase):
                P1 = p.rxBytes
                P1 = int(int(P1) / 100) * int(percentage)
                P1 = ((float(P1) * 8)) / (1000000 * int(duration))
                
        logging.info("Storing %s = %s [Mbps]", storevar, P1)
        self.setRetVal(storevar, P1)
        
        return

    def ucc_form_device_discovery_frame(self):
        wholeCommand = self.cmd + "!" + self.param
        command = wholeCommand.split('!')
        iCn = 0
        for c in command:
            if iCn > 1 and c in command:
                print "Invalid UCC Command... TBD"
                #wfa_sys_exit("Invalid UCC command")
                #command[1] Frame command[2] GOUT Device Address command[3] group ID command[4] Injector source Address command[5] Testbed Client address

        f = command[1].split('*')
        iCn = 0

        #Hex SSID
        SSID = TestScriptSymbolTable.capi_cmd_ret_sym_tab[command[3]].split(" ")[1]
        SSIDLength = len(SSID)
        SSIDLen1 = hex(int(SSIDLength) + 22).split("0x")[1]
        SSIDLen2 = "%s 00" % hex(int(SSIDLength + 6)).split("0x")[1]
        if int(len(SSIDLen2)) < 5:
            SSIDLen2 = "0%s" % SSIDLen2
        hexSSID = ""
        for s in SSID:
            h = hex(ord(s)).split("0x")[1]
            hexSSID = hexSSID + h
        logging.debug("hexSSID = %s hexLength %s" % (hexSSID, SSIDLength))
        FrameData = "%s%s%s%s%s%s%s%s%s%s%s%s" % (f[0],
                                                  TestScriptSymbolTable.capi_cmd_ret_sym_tab[command[2]],
                                                  TestScriptSymbolTable.capi_cmd_ret_sym_tab[command[4]],
                                                  TestScriptSymbolTable.capi_cmd_ret_sym_tab[command[2]],
                                                  f[3],
                                                  SSIDLen1,
                                                  f[4],
                                                  TestScriptSymbolTable.capi_cmd_ret_sym_tab[command[5]],
                                                  f[5],
                                                  SSIDLen2,
                                                  TestScriptSymbolTable.capi_cmd_ret_sym_tab[command[2]],
                                                  hexSSID)
        logging.debug (FrameData)
        TestScriptSymbolTable.capi_cmd_ret_sym_tab.setdefault("$INJECT_FRAME_DATA",FrameData)

    def userinput(self):
        wholeCommand = self.cmd + "!" + self.param
        command = wholeCommand.split('!')
        Util.set_color(Util.FOREGROUND_YELLOW | Util.FOREGROUND_INTENSITY)
        logging.info("[USER INPUT REQUIRED]")
        udata = raw_input(command[1])
        if command[2] in TestScriptSymbolTable.test_script_sym_tab:
            TestScriptSymbolTable.test_script_sym_tab[command[2]] = udata
        else:
            TestScriptSymbolTable.test_script_sym_tab.setdefault(command[2], udata)

        Util.set_color(Util.FOREGROUND_WHITE | Util.FOREGROUND_INTENSITY)
        return

    def userinput_ifnowts(self):
        wholeCommand = self.cmd + "!" + self.param
        command = wholeCommand.split('!')



        if TestScriptSymbolTable.get_value_from_sym_tab("$WTS_ControlAgent_Support", TestScriptSymbolTable.test_script_sym_tab) == "0":
            Util.set_color(Util.FOREGROUND_YELLOW | Util.FOREGROUND_INTENSITY)
            logging.info("[USER INPUT REQUIRED]")
            udata = raw_input(command[1])
            if command[2] in TestScriptSymbolTable.test_script_sym_tab:
                TestScriptSymbolTable.test_script_sym_tab[command[2]] = udata
            else:
                TestScriptSymbolTable.test_script_sym_tab.setdefault(command[2], udata)
                
            Util.set_color(Util.FOREGROUND_WHITE | Util.FOREGROUND_INTENSITY)
        return

    def validation_external(self):
        
        print "call external func for validation!"

        validation_obj = ValidationExternal()
        validation_func = validation_obj.get_method(self.param)
        username = ""
        password = ""
        ret_dict = {}

        
        for tbd in self.test_mngr_initr.test_prog_mngr.test_prog.testbed_dev_list:
            if tbd.alias == self.device_id or tbd.dev_name == re.sub('AP', '', self.device_id):
                if tbd.alias != '':
                    print "AP info found! --- '%s'" % tbd.alias
                else:
                    print "AP info found! --- '%s'" % tbd.dev_name
                username = tbd.username
                password = tbd.password
                print "username : " + username
                print "password : " + password
                if tbd.testipaddr == '':
                    ip_address = tbd.ctrlipaddr
                else:
                    ip_address = tbd.testipaddr
        
                if validation_func != None:
                    ret_dict = validation_func(host=ip_address,user=username,password=password)

                tbd.validation_dict = ret_dict
                #print "return value from external func : " + ret_dict
                break
        
        return

    def wfa_tester(self):
        if self.cmd in TestScriptSymbolTable.capi_cmd_ret_sym_tab:
            self.cmd = TestScriptSymbolTable.capi_cmd_ret_sym_tab[self.cmd]
        else:
            return

