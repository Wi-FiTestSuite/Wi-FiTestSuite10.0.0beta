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

"""
This script processes each excution task's recevied value
"""

import logging
import time
import sys
import re

from core.executiontask import ExecutionTask
from core.symtable import TestScriptSymbolTable
from core.streamhandler import StreamHandler
from core.tmshandler import TMSProcessor
from util.misc import Util
from testinfo.datastream import streamInfo
from common import GlobalConfigFiles

#tms setting
tmsPacket = TMSProcessor()

def setRetVal(key, val):
    """
    set capi return to global ValueTable
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
        logging.debug("setRetVal error : wrong type..")
        return


def getRetKey(dictionary):
    """
    return list of keys from Exectuion.ret dictionary
    """
    retKey = ""
    try:
        if dictionary:
            retKey = dictionary.values()[0].keys()[0]
    except TypeError:
        logging.debug("type error")

    return retKey

class ResultProcessor(object):
    """Analyze ExecutionTask object and determine result"""

    def __init__(self, param=ExecutionTask):
        #proceed/stop

        #status => CONTINUE or STOP
        self.__status = 'CONTINUE'

        #result => FAIL or PASS
        self.__testResult = 'NONE'

        self.tmsPacket = tmsPacket
        self.ExecutionTask = param

        self.test_mngr_initr = None

    def getStatus(self, test_mngr_initr):
        """
        get status of process stop/proceed will be return after call anayzeTask()
        """
        self.test_mngr_initr = test_mngr_initr
        self.processTask()

        return self.__status

    def setStatus(self, status):
        """
        set status of process stop/proceed
        """
        self.__status = status


    def setTestResult(self, rlt):
        """
        set test result, and it will lead to print final test result...
        """
        self.__testResult = rlt

        total_count = TestScriptSymbolTable.get_value_from_sym_tab("total_count", TestScriptSymbolTable.test_result_tab) + 1
        TestScriptSymbolTable.insert_sym_tab("total_count", total_count, TestScriptSymbolTable.test_result_tab)
        #if rlt == 'PASS':
        if 'PASS' in rlt:
            pass_count = TestScriptSymbolTable.get_value_from_sym_tab("pass_count", TestScriptSymbolTable.test_result_tab) + 1
            TestScriptSymbolTable.insert_sym_tab("pass_count", pass_count, TestScriptSymbolTable.test_result_tab)
        else:
            fail_count = TestScriptSymbolTable.get_value_from_sym_tab("fail_count", TestScriptSymbolTable.test_result_tab) + 1
            TestScriptSymbolTable.insert_sym_tab("fail_count", fail_count, TestScriptSymbolTable.test_result_tab)
        
        #self.generateFinalResult()

    def setCheckResult(self, rlt):
        """
        set check result, and this will save each sub-result, and not print final test result..
        """
        total_count = TestScriptSymbolTable.get_value_from_sym_tab("total_count", TestScriptSymbolTable.test_result_tab) + 1
        TestScriptSymbolTable.insert_sym_tab("total_count", total_count, TestScriptSymbolTable.test_result_tab)
        
        #if rlt == 'PASS':
        if 'PASS' in rlt:
            pass_count = TestScriptSymbolTable.get_value_from_sym_tab("pass_count", TestScriptSymbolTable.test_result_tab) + 1
            TestScriptSymbolTable.insert_sym_tab("pass_count", pass_count, TestScriptSymbolTable.test_result_tab)
        else:
            fail_count = TestScriptSymbolTable.get_value_from_sym_tab("fail_count", TestScriptSymbolTable.test_result_tab) + 1
            TestScriptSymbolTable.insert_sym_tab("fail_count", fail_count, TestScriptSymbolTable.test_result_tab)
        
    def setValidationInfo(self, displayname, recvstring):
        """
        set testbed information after receving return from capi call
        """
        response = recvstring
        companyTestBed = ""
        modelTestBed = ""
        firmwareTestBed = ""
        Sniffer_WTS_VER = ""
        Sniffer_VendorName = ""
        Sniffer_DeviceModel = ""
        Sniffer_DeviceFirmware = ""
        ret_dict = {}

        if displayname.lower() == 'sniffer':
            #wfa_sniffer!sniffer_get_info!ID,$Sniffer_WTS_VER,$Sniffer_VendorName,$Sniffer_DeviceModel,$Sniffer_DeviceFirmware
            #status,COMPLETE,WfaSnifferVersion,$WfaSnifferVersion,SnifferSTA,$SnifferSTA,SwInfo,$DeviceSwInfo\_$kernel_Ver,WiresharkVersion,$WiresharkInfo\r\n
            ret_items = response.split(',')
            
            
            if len(ret_items) > 9:
                Sniffer_WTS_VER = ret_items[3]
                Sniffer_VendorName = ret_items[5]
                Sniffer_DeviceModel = ret_items[7]
                Sniffer_DeviceFirmware = ret_items[9]
            else:
                if re.search(r"status,COMPLETE", response):
                    if re.search(r"WfaSnifferVersion", response):
                        posVendor = response.index('WfaSnifferVersion,') + len('WfaSnifferVersion,')
                        data = response[posVendor:]
                        data = data.lstrip()
                        try:
                            posSym = data.index(',')
                            Sniffer_WTS_VER = data[:posSym]
                        except Exception:
                            Sniffer_WTS_VER = data.rstrip('\n')

                    if re.search(r"SnifferSTA", response):
                        posVendor = response.index('SnifferSTA,') + len('SnifferSTA,')
                        data = response[posVendor:]
                        data = data.lstrip()
                        try:
                            posSym = data.index(',')
                            Sniffer_VendorName = data[:posSym]
                        except Exception:
                            Sniffer_VendorName = data.rstrip('\n')

                    if re.search(r"SwInfo", response):
                        posVendor = response.index('SwInfo,') + len('SwInfo,')
                        data = response[posVendor:]
                        data = data.lstrip()
                        try:
                            posSym = data.index(',')
                            Sniffer_DeviceModel = data[:posSym]
                        except Exception:
                            Sniffer_DeviceModel = data.rstrip('\n')

                    if re.search(r"WiresharkVersion", response):
                        posVendor = response.index('WiresharkVersion,') + len('WiresharkVersion,')
                        data = response[posVendor:]
                        data = data.lstrip()
                        try:
                            posSym = data.index(',')
                            Sniffer_DeviceFirmware = data[:posSym]
                        except Exception:
                            Sniffer_DeviceFirmware = data.rstrip('\n')

            setRetVal('$ca_version', Sniffer_WTS_VER)
            setRetVal('$tbd_info1', Sniffer_VendorName)
            setRetVal('$sw_version', Sniffer_DeviceModel)
            setRetVal('$tbd_info2', Sniffer_DeviceFirmware)                            

            ret_dict['ca_version'] = Sniffer_WTS_VER
            ret_dict['tbd_info1'] = Sniffer_VendorName
            ret_dict['sw_version'] = Sniffer_DeviceModel
            ret_dict['tbd_info2'] = Sniffer_DeviceFirmware

            for tbd in self.test_mngr_initr.test_prog_mngr.test_prog.testbed_dev_list:

                if tbd.dev_type == "SNIFFER":
                    tbd.vendor = Sniffer_VendorName
                    tbd.model = Sniffer_DeviceModel
                    tbd.firmver = Sniffer_DeviceFirmware
                    tbd.wtsver = Sniffer_WTS_VER
                    tbd.validation_dict = ret_dict

                    break


        else:
            if re.search(r"status,COMPLETE", response):
                if re.search(r"vendor", response):
                    posVendor = response.index('vendor,') + 7
                    data = response[posVendor:]
                    data = data.lstrip()
                    try:
                        posSym = data.index(',')
                        companyTestBed = data[:posSym]
                    except Exception:
                        companyTestBed = data.rstrip('\n')

                if re.search(r"model", response):
                    posVendor = response.index('model,') + 6
                    data = response[posVendor:]
                    data = data.lstrip()
                    try:
                        posSym = data.index(',')
                        modelTestBed = data[:posSym]
                    except Exception:
                        modelTestBed = data.rstrip('\n')

                if re.search(r"version", response):
                    posVendor = response.index('version,') + 8
                    data = response[posVendor:]
                    data = data.lstrip()
                    try:
                        posSym = data.index(',')
                        firmwareTestBed = data[:posSym]
                    except Exception:
                        firmwareTestBed = data.rstrip('\n')
                        
                if re.search(r"firmware", response):
                    posVendor = response.index('firmware,') + 9
                    data = response[posVendor:]
                    data = data.lstrip()
                    try:
                        posSym = data.index(',')
                        firmwareTestBed = data[:posSym]
                    except Exception:
                        firmwareTestBed = data.rstrip('\n')
                                                                            
                                                    
                                                            
            for tbd in self.test_mngr_initr.test_prog_mngr.test_prog.testbed_dev_list:
                
                
                if tbd.ctrlipaddr == self.ExecutionTask.get_ipport().split(':')[0]:
                    #
                    if companyTestBed != "":
                        tbd.vendor = companyTestBed
                    if modelTestBed != "":
                        tbd.model = modelTestBed
                    if firmwareTestBed != "":
                        if self.ExecutionTask.get_cmd() == "ca_get_version":
                            tbd.ca_version = firmwareTestBed
                        else:
                            tbd.sw_version = firmwareTestBed
                                    
                    if self.ExecutionTask.get_cmd() == "ca_get_version":
                        
                        tbd.validation_dict['ca_version'] = firmwareTestBed
                    else:
                        tbd.validation_dict['sw_version'] = firmwareTestBed 
                        tbd.validation_dict['vendor'] = companyTestBed
                        tbd.validation_dict['model'] = modelTestBed 
                                                                      
                    break


    def processTask(self):
        """
        Analyze ExecutionTask and decide weather test to continue or stop
        """
        #Util.set_color(Util.FOREGROUND_YELLOW | Util.FOREGROUND_INTENSITY)
        #logging.info("cmd    : %s", self.ExecutionTask.get_cmd())
        #logging.info("param  : %s", self.ExecutionTask.get_param())
        #logging.info("ret    : %s", str(self.ExecutionTask.get_ret()))
        #logging.info("ipport : %s", self.ExecutionTask.get_ipport())
        #Util.set_color(Util.FOREGROUND_WHITE)

        ##############################################################
        # Process for any commands without received messages.....
        ##############################################################
        if self.ExecutionTask.get_cmd() == 'PASS' or self.ExecutionTask.get_cmd() == 'FAIL':
            logging.debug("result is %s", self.ExecutionTask.get_cmd())
            self.setStatus('STOP')
            self.setTestResult(self.ExecutionTask.get_cmd())
            return

        if self.ExecutionTask.get_cmd() == 'r_info':
            rinfo_result = self.ExecutionTask.get_param().split('!')

            if len(rinfo_result) > 1:
                msg = rinfo_result[1]
                logging.debug("%s", msg)

            self.setStatus('STOP')
            self.setTestResult(rinfo_result[0])
            return

        if self.ExecutionTask.get_cmd() == 'ResultCheck':
            time.sleep(5)
            self.process_ResultCheck()
            return

        if self.ExecutionTask.get_cmd() == 'CheckThroughput':
            time.sleep(5)
            throughputChk = StreamHandler(self.test_mngr_initr)
            chk_result = throughputChk.processStreamResults(self.ExecutionTask.get_param())
            self.setCheckResult(chk_result)
            #if 'FAIL' in chk_result:
            #    self.setStatus('STOP')
            return

        if self.ExecutionTask.get_cmd() == 'config_multi_subresults':
            self.process_config_multi_subresults()
            return

        ##############################################################
        # Process for any commands with received messages......
        ##############################################################
        status = ""
        retDict = self.ExecutionTask.get_ret()
        recvStr = ""
        if self.ExecutionTask.recv:
            recvStr = self.ExecutionTask.recv.rstrip('\r\n')
            #print "recv : " + recvStr
        
        if GlobalConfigFiles.curr_prog_name == "WMMPS" and "sniffer_control_subtask" in self.ExecutionTask.get_cmd():
            logging.debug('In WMMPS, before parsing the recvStr: %s' % recvStr)
            lines = re.split('\n', recvStr)
            for line in lines:
                if re.search("RESULT", line, re.I):
                    if "FAIL" in line:
                        self.setStatus('STOP')
                        self.setTestResult('FAIL')
                        logging.debug('set test result to FAIL')
                        return
                    if "PASS" in line:
                        self.setTestResult('PASS')
                        logging.debug('set test result to Pass')
                        return
            return
        
        stitems = recvStr.split(',')        
        if len(stitems) < 2:
            #logging.debug("Bypassing this cmd..")
            return

        status = stitems[1]
        iDNB = TestScriptSymbolTable.get_value_from_sym_tab("iDNB", TestScriptSymbolTable.test_script_sym_tab)
        iINV = TestScriptSymbolTable.get_value_from_sym_tab("iINV", TestScriptSymbolTable.test_script_sym_tab) 
                
        if iINV is None:
            iINV = 0
        
        if 'ERROR' in recvStr or 'INVALID' in recvStr and (iDNB == 0 or iDNB is None) and (iINV == 0 or iINV is None):
            #error case...
            logging.debug("Return ERROR or INVALID---> STOP process ")
            self.setStatus('STOP')
            self.setTestResult('FAIL')
        elif status != 'COMPLETE' and iDNB == 0 and iINV == 0:
            #incomplete case...(running?)
            logging.debug("Command %s not completed", self.ExecutionTask.get_cmd())
        else:
            displayname = ""
            for tbd in self.test_mngr_initr.test_prog_mngr.test_prog.testbed_dev_list:
                if tbd.ctrlipaddr == self.ExecutionTask.get_ipport():
                    displayname = tbd.displayname
                    break
            
            if "FAIL" in recvStr and (iINV == 0 or iINV is None):
                if "SNIFFER" in displayname or "sniffer" in self.ExecutionTask.get_cmd():
                    logging.info("Test Case Criteria Failure - Command returned FAIL")
                    self.setStatus('STOP')
                    self.setTestResult('FAIL')

            elif self.ExecutionTask.get_cmd() == 'device_get_info':
                try:
                    if displayname == '':
                        self.tmsPacket.setDutDeviceInfo(recvStr)
                    else:
                        self.tmsPacket.setTestbedInfo(displayname, recvStr)

                    #for validation
                    self.setValidationInfo(displayname, recvStr)

                except OSError:
                    logging.debug("exception -- device_get_info capi call")
            elif self.ExecutionTask.get_cmd() == 'ca_get_version':
                self.setValidationInfo(displayname, recvStr)

            elif self.ExecutionTask.get_cmd() == 'sniffer_get_info':
                self.setValidationInfo('sniffer', recvStr)

            elif self.ExecutionTask.get_cmd() == 'sta_associate':
                time.sleep(10)

            if len(stitems) > 2:
                retParam = self.ExecutionTask.get_param().split(',')
                streamFlag = ""
                if len(retParam) > 4:
                    streamFlag = retParam[3]

                if stitems[2] == 'streamID':
                    streamHndler = StreamHandler(self.test_mngr_initr)
                    logging.debug("stream config - streamID : %s", stitems[3])
                    if streamFlag == 'send':
                        logging.debug("traffic config - send : streamInfo append")
                        streamPacket = streamInfo("%s" % (stitems[3]), self.ExecutionTask.get_ipport(), -1, 'send',
                                                  retParam[15], retParam[17], streamHndler.running_phase, streamHndler.RTPCount)
                        streamHndler.add_streamInfo(streamPacket)
                        streamHndler.RTPCount = streamHndler.RTPCount + 1

                    elif streamFlag == 'receive':
                        logging.debug("traffic config - receive : streamInfo append")
                        streamPacket = streamInfo("%s" % (stitems[3]), self.ExecutionTask.get_ipport(), -1, 'receive',
                                                  -1, -1, streamHndler.running_phase, -1)
                        streamHndler.add_streamInfo(streamPacket)

                    else:
                        logging.debug("traffic config - else : ")



                    if retParam[1] == 'Multicast':
                        logging.debug("----MULTICAST----")
                        streamHndler.multicast = 1

                    if self.ExecutionTask.get_cmd() != "traffic_agent_send":
                        ret_val = "%s" %(stitems[3].strip())
                        logging.debug("traffic config - ret_val : %s", ret_val)
                        setRetVal(getRetKey(retDict), ret_val)

                elif stitems[2].lower() == 'interfacetype':
                    ret_val = ("%s" %(stitems[5]))
                    setRetVal(getRetKey(retDict), ret_val)

                elif stitems[2].lower() == 'interfaceid':
                    ret_val = stitems[3].split('_')[0]
                    setRetVal(getRetKey(retDict), ret_val)

                elif self.ExecutionTask.get_cmd() == 'traffic_stop_ping':

                    keyVal = retParam[1]
                    #"%s;%s"%(retParam[1], self.ExecutionTask.get_ipport())
                    setRetVal(keyVal, stitems[5])
                    #print("%s = %s" %  (retParam[1], stitems[5]))
                    pinginternalchk = TestScriptSymbolTable.get_value_from_sym_tab("PingInternalChk", TestScriptSymbolTable.test_script_sym_tab)
                    temp_key = getRetKey(self.ExecutionTask.get_ret())
                    
                    if "$" in temp_key:
                        sent_reply = temp_key.split(',')
                        #print "SLIM==> ping result save..."
                        #print sent_reply[0]
                        #print sent_reply[1]
                        setRetVal(sent_reply[0], stitems[3])
                        setRetVal(sent_reply[1], stitems[5])    

                    setRetVal("$pingResp", stitems[5])
                    if pinginternalchk == '0':
                        logging.debug("Ping Internal Check")
                        
                    elif stitems[5] == '0':
                        logging.debug ("Test Case Criteria Failure - NO IP Connection -- Aborting the test")
                        self.setStatus('STOP')
                        self.setTestResult('FAIL')
                    else:
                        if stitems[5] == '0':
                            logging.debug ("Test Case Criteria Failure - NO IP Connection -- Aborting the test")
                            self.setStatus('STOP')
                            self.setTestResult('FAIL')
                else:
                    if len(retDict) > 0:
                        tempKey = getRetKey(retDict)
                        temp_val = tempKey.split(',')
                        count = 0
                        item_len = len(stitems)
                        for i in temp_val:
                            if item_len > count + 3:
                                setRetVal(i, stitems[3+count])
                                count = count + 2

        if self.__status == 'STOP':
            logging.debug("generate final result if task stops.")
            #self.generateFinalResult()
        else:
            pass
            #logging.debug("Continue---")
        return

    def generateFinalResult(self):
        """
        Print ending result to console
        """
        if self.__testResult == 'FAIL':
            Util.set_color(Util.FOREGROUND_RED | Util.FOREGROUND_INTENSITY)
        elif self.__testResult == 'PASS':
            Util.set_color(Util.FOREGROUND_GREEN | Util.FOREGROUND_INTENSITY)
        elif self.__testResult == 'NONE':
            Util.set_color(Util.FOREGROUND_GREEN | Util.FOREGROUND_INTENSITY) 
            self.__testResult = 'PASS'
        #else:
        total_count = int(TestScriptSymbolTable.get_value_from_sym_tab("total_count", TestScriptSymbolTable.test_result_tab))
        pass_count = int(TestScriptSymbolTable.get_value_from_sym_tab("pass_count", TestScriptSymbolTable.test_result_tab))
        fail_count = int(TestScriptSymbolTable.get_value_from_sym_tab("fail_count", TestScriptSymbolTable.test_result_tab))
        conditional_chk_flag = int(TestScriptSymbolTable.get_value_from_sym_tab("conditional_chk_flag", TestScriptSymbolTable.test_result_tab))
        num_of_pass_required = int(TestScriptSymbolTable.get_value_from_sym_tab("num_of_pass_required", TestScriptSymbolTable.test_result_tab))
            
        if total_count >= 1:
            if conditional_chk_flag == 1:
                if num_of_pass_required <= pass_count:
                    Util.set_color(Util.FOREGROUND_GREEN | Util.FOREGROUND_INTENSITY)
                    self.__testResult = 'PASS'
                else:
                    Util.set_color(Util.FOREGROUND_RED | Util.FOREGROUND_INTENSITY)
                    self.__testResult = 'FAIL'
            else:
                if fail_count > 0:
                    Util.set_color(Util.FOREGROUND_RED | Util.FOREGROUND_INTENSITY)
                    self.__testResult = 'FAIL'
                else:
                    Util.set_color(Util.FOREGROUND_GREEN | Util.FOREGROUND_INTENSITY)
                    self.__testResult = 'PASS'
        else:
            if GlobalConfigFiles.curr_tc_name != "":
                Util.set_color(Util.FOREGROUND_RED | Util.FOREGROUND_INTENSITY)
                logging.debug("\n   TEST COMPLETED without FINAL RESULT...")

            self.__testResult = 'FAIL'

        self.tmsPacket.TestResult = self.__testResult
        if GlobalConfigFiles.curr_tc_name != "":
            logging.info("\n    FINAL TEST RESULT  ---> %15s", self.__testResult)
            logging.info('     END: TEST CASE [%s]', GlobalConfigFiles.curr_tc_name)

        Util.set_color(Util.FOREGROUND_WHITE)
        GlobalConfigFiles.test_result = self.__testResult

        self.tmsPacket.TimeStamp = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.localtime())
        if GlobalConfigFiles.curr_tc_name != "":
            self.tmsPacket.writeTMSJson()

        return

    def process_ResultCheck(self):
        """Determines pass or fail at the end of the test run"""
        try:
            cmd = self.ExecutionTask.get_param().split(',')
            logging.debug("%s-%s-%s-%s-%s" % ( TestScriptSymbolTable.get_value_from_sym_tab(cmd[0], TestScriptSymbolTable.test_script_sym_tab),cmd[0], cmd[1], cmd[2], cmd[3]))

            checkval = cmd[0].split('!') 
            
            cval = TestScriptSymbolTable.get_value_from_sym_tab(checkval[1], TestScriptSymbolTable.capi_cmd_ret_sym_tab)

            if int(cval) >= int(cmd[1]):
                result = cmd[2]
            else:
                result = cmd[3]

            logging.info("\nRESULT CHECK---> %15s", result)            
            self.setTestResult(result)
                
            #if result == 'FAIL':
            if 'FAIL' in result:
                self.setStatus('STOP')
                self.setTestResult('FAIL')
        except OSError:
            logging.info("\nException - ResultCheck")


    def process_config_multi_subresults(self):
        #global num_of_pass_required, total_checks
        try:
            cmd=self.ExecutionTask.get_param()
            
            cmd = eval(cmd)
            pass_required = cmd.get('NUMOFPASSREQ')
            total_checks = cmd.get('NUMOFCHECK')

            #reset previous results..
            TestScriptSymbolTable.insert_sym_tab("pass_count", 0, TestScriptSymbolTable.test_result_tab)
            TestScriptSymbolTable.insert_sym_tab("fail_count", 0, TestScriptSymbolTable.test_result_tab)

            logging.info("\n----------------Pass condition---------------------------\n")
            logging.info("Total number of checks = %s", total_checks)
            logging.info("Number of pass required = %s", pass_required)

            if pass_required == total_checks:
                TestScriptSymbolTable.insert_sym_tab("conditional_chk_flag", 1, TestScriptSymbolTable.test_result_tab)
                TestScriptSymbolTable.insert_sym_tab("num_of_pass_required", total_checks, TestScriptSymbolTable.test_result_tab)
            elif pass_required < total_checks:
                TestScriptSymbolTable.insert_sym_tab("conditional_chk_flag", 1, TestScriptSymbolTable.test_result_tab)
                TestScriptSymbolTable.insert_sym_tab("num_of_pass_required", pass_required, TestScriptSymbolTable.test_result_tab)
            
        except:
            exc_info = sys.exc_info( )
            logging.error('Invalid Pass/Fail Formula - %s' % exc_info[1])

