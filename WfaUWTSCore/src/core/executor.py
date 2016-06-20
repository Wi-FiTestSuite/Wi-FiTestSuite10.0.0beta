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

""" This module is the core of execution module. """
import logging
import threading
import sys
import re

from scriptinfo.scriptsource import TestLogFileSource
from core.executiontask import ExecutionTask
from core.executionqueue import ExecutionQueue
from core.resultprocessor import ResultProcessor
from core.symtable import TestScriptSymbolTable
from util.misc import Util


# logging.basicConfig(level=logging.DEBUG,
#                     format='(%(threadName)-10s) %(message)s',)

class Executor(object):
    def __init__(self):
        self.test_mngr_initr = None
        self.capi_script_parser = None
        self.main_exec_q = None
        self.completed_q = []
        self.sub_q_list = []
        self.parallel_enable = False
        self.test_status = "CONTINUE"
        self.active_ap_counter = 0
        self.ap_counter = 0
        self.involved_ap_list = []
        self.thread_error_flag = False
        self.separator_flag = True
        self.ap_dict = {}
        self.device_dict = {}
        self.aput_name = None
        self.aput_flag = 0
        self.aput_ipport = None
        self.offset = 0
        self.port_offset = 0
        self.resultprocess_obj = None
        self.is_validation = False
        self.exe_result = "None"
        self.ap_config_port = 7000
        self.ap_port_map = {}

    def init_exec_q(self):
        return ExecutionQueue()

    def search_ap_agent_ipport(self):
        for tbd in self.test_mngr_initr.test_prog_mngr.test_prog.testbed_dev_list:
            if tbd.alias == 'TestbedAPConfigServer':
                ipport = tbd.ctrlipaddr + ':' + tbd.ctrlport
        return ipport
    
    def get_ap_agent_port(self):
        for tbd in self.test_mngr_initr.test_prog_mngr.test_prog.testbed_dev_list:
            if tbd.alias == 'TestbedAPConfigServer':
                return tbd.ctrlport

    def search_testbed_device(self, dev_name):
        """ This function is searching in the testbed device list
        based on the device name and return the string of IP and port """
        ipport = None
        if dev_name.startswith('$'):
            for tbd in self.test_mngr_initr.test_prog_mngr.test_prog.testbed_dev_list:
                if tbd.numVarName == dev_name:
                    ipport = tbd.ctrlipaddr + ':' + tbd.ctrlport
        else:
            for tbd in self.test_mngr_initr.test_prog_mngr.test_prog.testbed_dev_list:
                if not re.search('wfa', dev_name,  re.IGNORECASE) and tbd.dev_type == 'AP':
                    if tbd.alias == dev_name or tbd.dev_name == re.sub('AP', '', dev_name):
                        if tbd.ctrlipaddr == '':
                            ipport = self.search_ap_agent_ipport()
                        else:
                            ipport = tbd.ctrlipaddr + ':' + tbd.ctrlport
                else:
                    if tbd.alias == dev_name:
                        ipport = tbd.ctrlipaddr + ':' + tbd.ctrlport
        return ipport

    def storethroughput_converter(self, value):
        """ convert the value from dictionary to string"""
        ret = (value.get('STOREVAR') + '!' +
               value.get('STREAMID') + ',' +
               value.get('PHASE') + ',' +
               value.get('DURATION') + ',' +
               value.get('PERCENTAGE'))
        return ret

    def create_task(self, node):
        """ create execution task based on the parser linked list """
        if node.tag == "END":
            return
        else:
            new_task = ExecutionTask(self.test_mngr_initr)

        while node.tag != "END":  # and node.next.tag != 'END':
            if node.tag == "TESTBEDDEVICE":
                device_name = (node.data.keys())[0]
                new_task.set_device_id(device_name)
                new_task.set_ipport(self.search_testbed_device(device_name))
            elif node.tag == "CAPICOMMAND":
                new_task.set_cmd((node.data.keys())[0])
                new_task.set_param((node.data.values())[0])
            elif node.tag == "CAPIRETVAR":
                new_task.ret = {(node.data.keys())[0]:{(node.data.values())[0]:None}}
            elif node.tag == "FUNCCALLER":
                new_task.set_cmd((node.data.keys())[0])
                new_task.set_param((node.data.values())[0].get('EXTERNALFUNC'))
            elif node.tag == 'IFCOND':
                new_task.set_cmd('if')
                new_task.set_param((node.data.keys())[0])
            elif node.tag == 'ELSE':
                new_task.set_cmd('else')
            elif node.tag == 'ENDIF':
                new_task.set_cmd('endif')
            elif node.tag == 'UCCACTION':
                cmd = (node.data.keys())[0]
                new_task.set_cmd(cmd)
                cmd = cmd.lower()
                if (cmd == 'info' or
                        cmd == 'echo' or
                        cmd == 'pause'):
                    new_task.set_param((node.data.values())[0].get('MSG'))
                if (cmd.lower() == 'sleep' or
                        cmd.lower() == 'phase' or
                        cmd.lower() == 'manual_check_info' or
                        cmd.lower() == 'socktimeout' or
                        cmd.lower() == 'addstaversioninfo' or
                        cmd.lower() == 'math'):
                    new_task.set_param((node.data.values())[0])
                if cmd == 'config_multi_subresults':
                    new_task.set_param(str(node.data.values()[0]))
                if cmd == 'cat':
                    new_task.set_param((node.data.values())[0].get('FIRSTVAR') + '!' +
                                       (node.data.values())[0].get('VARLIST') + '!' +
                                          (node.data.values())[0].get('DELIMITER'))
                if cmd == 'userinput_ifnowts':
                    new_task.set_param((node.data.values())[0].get('MSG') + '!' +
                                       (node.data.values())[0].get('EXPRVAR'))
                if cmd == 'getuserinput':
                    new_task.set_param((node.data.values())[0].get('MSG') + '!' +
                                       (node.data.values())[0].get('INPUTVAL'))
                if cmd == 'r_info':
                    if 'MSG' in (node.data.values())[0]:
                        new_task.set_param((node.data.values())[0].get('RESULT') + '!' +
                                          (node.data.values())[0].get('MSG'))
                    else:
                        new_task.set_param((node.data.values())[0].get('RESULT'))
                if cmd == 'search':
                    if 'LASTWORD' in (node.data.values())[0]:
                        new_task.set_param((node.data.values())[0].get('LISTNAME') + '!' +
                                           (node.data.values())[0].get('SEARCHITEM') + '!' +
                                           (node.data.values())[0].get('SEARCHRESULT') + '!' +
                                              (node.data.values())[0].get('LASTWORD'))
                    else:
                        new_task.set_param((node.data.values())[0].get('LISTNAME') + '!' +
                                           (node.data.values())[0].get('SEARCHITEM') + '!' +
                                              (node.data.values())[0].get('SEARCHRESULT') + '!contains')

            elif node.tag == 'SEPRATROR':
                """
                The purpose to have this is
                UCC won't call the result processor
                """
                self.separator_flag = False
            elif node.tag == 'RESULTCHECK':
                new_task.set_cmd('ResultCheck')
                new_task.set_param((node.data.keys())[0] + '!' + (node.data.values())[0])
            elif node.tag == 'UCCINTERNALVAR':
                new_task.set_cmd('PingInternalChk')
                new_task.set_param((node.data.values())[0])
            elif node.tag == 'STREAMCHECK':
                new_task.set_cmd('CheckThroughput')
                new_task.set_param((node.data.keys())[0] + '!' + (node.data.values())[0])
            elif node.tag == 'TRAFFICSTREAM':
                new_task.set_cmd('StoreThroughput')
                new_task.set_param(self.storethroughput_converter((node.data.values())[0]))
            elif node.tag == 'UCCDEFINEVAR':
                new_task.set_param((node.data.keys())[0] + '!' + (node.data.values())[0])
                new_task.set_cmd('define')
            else:
                logging.debug("TBD : %s\n" % node.tag)
            node = node.next
        return new_task

    def add_task(self, active_q, curr_task):
        """ A wrapper to add task into the Q"""
        active_q.enqueue(curr_task)

    def check_ap_involved(self):
        """ Count number of AP  """
#         print "check ap involved"
        if self.test_mngr_initr.test_config_info_mngr.test_config_info.var_list.has_key('APUT_state'):
            if self.test_mngr_initr.test_config_info_mngr.test_config_info.var_list['APUT_state'] == 'on':
                self.aput_name = re.sub('AP', '', TestScriptSymbolTable.test_script_sym_tab["$DUT_Name"])
                self.aput_flag = 1
                
        for tbd in self.test_mngr_initr.test_prog_mngr.test_prog.testbed_dev_list:
            if tbd.dev_type == "AP" and tbd.state == "On":
                self.active_ap_counter = self.active_ap_counter + 1
                self.involved_ap_list.append(tbd.dev_name)
            if self.aput_flag == 1 and tbd.dev_name == "DUT":
                self.aput_ipport = tbd.ctrlipaddr + ':' + tbd.ctrlport

    def validate_task(self, task):
        """ check the task whether a valid CAPI command type 
        The attribute ipport is None means IP/port is not available for 
        CAPI command type of task 
        Note: empty string for others  """
        if task.ipport == None:
            return False
        return True
    
    def construct_valiadate_q(self, test_mngr_initr, capi_script_parser, test_configure):
        """Initialized the validate Queue """
        self.main_exec_q = self.init_exec_q()
        self.test_mngr_initr = test_mngr_initr
        self.capi_script_parser = capi_script_parser
        self.test_configure = test_configure
        self.is_validation = True
        
        curr_node = node = capi_script_parser.qll.head

        while node:
            if node.tag == 'END':
                new_task = self.create_task(curr_node)
                if new_task == None or self.validate_task(new_task) == False:
                    logging.debug("construct_valiadate_q: new task is invalid: [%s!%s]" , new_task.cmd, new_task.param)
                    curr_node = node.next
                    node = node.next
                    continue
                else: #add into the sub Q
                    if self.device_dict.has_key(new_task.get_device_id()):
                        logging.debug("construct_valiadate_q: add task [%s!%s] into subQ", new_task.cmd, new_task.param)
                        sub_q = self.device_dict.get(new_task.get_device_id())
                    else:
                        sub_q = ExecutionQueue()
                        logging.debug("construct_valiadate_q: create subQ for new added task [%s!%s]", new_task.cmd, new_task.param)
                        self.device_dict[new_task.get_device_id()] = sub_q
                        self.ap_counter = self.ap_counter + 1
                self.add_task(sub_q, new_task)
                curr_node = node.next
                node = node.next
            else:
                node = node.next

        for subq_ref in self.device_dict.itervalues():
            self.main_exec_q.enqueue(subq_ref)

        # enqueue all the sub Q
    def construct_exec_q(self, test_mngr_initr, capi_script_parser, test_configure):
        """Initialized the main Queue"""
        self.main_exec_q = self.init_exec_q()
        self.test_mngr_initr = test_mngr_initr
        self.capi_script_parser = capi_script_parser
        self.test_configure = test_configure

        active_q = self.main_exec_q
        curr_node = node = capi_script_parser.qll.head
        
        ap_commit_counter = 0
        task_counter = 1

        self.check_ap_involved()
        while node:
            if node.tag == 'END':# and node.next.tag != 'END':
                """ create a new task """
                task_counter += 1
                new_task = self.create_task(curr_node)
                if new_task == None or self.validate_task(new_task) == False:
                    logging.debug("construct_exec_q: new task is invalid: [%s!%s]" , new_task.cmd, new_task.param)
                    curr_node = node.next
                    node = node.next
                    continue
                else:
                    if self.parallel_enable == True and self.active_ap_counter == ap_commit_counter:
                        logging.debug("construct_exec_q: insert subq1")
                        for subq_ref in self.ap_dict.itervalues():
                            self.main_exec_q.enqueue(subq_ref)
                        self.parallel_enable = False
                    if (self.parallel_enable == True and new_task.cmd == 'ap_config_commit' and 
                            new_task.get_ap_name() in self.involved_ap_list):
                        ap_commit_counter = ap_commit_counter + 1
                    if new_task.ret == {}:
                        ret = 'DEFAULT'
                    else:
                        ret = new_task.ret
                    logging.debug("construct_exec_q: %s!%s!%s!%s!" % (new_task.device_id, new_task.cmd,
                                                   new_task.param,
                                                  ret))
                if new_task.is_parallel() == False and self.parallel_enable and new_task.cmd != 'info' and self.ap_counter > 0:
                    logging.debug("construct_exec_q: insert subq2")
                    for subq_ref in self.ap_dict.itervalues():
                        self.main_exec_q.enqueue(subq_ref)
                        self.parallel_enable = False

                if new_task.is_parallel() and self.parallel_enable and new_task.get_ipport() != self.aput_ipport: #new_task.get_ap_name() != self.aput_name:
                    if self.ap_dict.has_key(new_task.get_ap_name()):
                        sub_q = self.ap_dict.get(new_task.get_ap_name())
                    else:
                        sub_q = ExecutionQueue()
                        sub_q.name = new_task.device_id
                        self.ap_dict[new_task.get_ap_name()] = sub_q
                        self.ap_counter = self.ap_counter + 1
                    active_q = sub_q
                else:
                    active_q = self.main_exec_q
                if self.validate_task(new_task) == True:
                    self.add_task(active_q, new_task)
                curr_node = node.next
                node = node.next
            else:
                node = node.next

    def replace_port(self, ipport, port):
        """ replace the port for parallel configuration """
        ipPortRef = ipport.split(":")[0]
        res = ipPortRef + ":" + str(port)
        return res

    def append_subq_compq(self, completedSubQList):
        """ This function appends the completed sub Q into completed Q """
        for completedSubQ in completedSubQList:
            while completedSubQ.is_empty() == False:
                self.completed_q.append(completedSubQ.dequeue())

    def proc_subq_task(self, sub_q, port, completed_sub_q):
        """ This function process task based on a given sub Q and append the 
        completed task into completed sub Q"""

        try:
            while sub_q.is_empty() == False:
                curr_task = sub_q.dequeue()
                if (self.search_testbed_device("TestbedAPConfigServer")
                == self.search_testbed_device(sub_q.name)):
                    #if curr_task.get_ipport().strip().split(':')[1] == str(self.ap_config_port):
                    ipPort = self.replace_port(curr_task.get_ipport(), port)
                    curr_task.set_ipport(ipPort)
                    #self.port_offset += 1
                logging.debug("proc_subq_task: [%s!%s]", curr_task.cmd, curr_task.param)
                self.exe_result = curr_task.execute()
                self.log_currObj(curr_task)
                if self.exe_result == 'FAIL':
                    self.thread_error_flag = True
                    completed_sub_q.enqueue(curr_task)
                    break
                #    self.resultprocess_obj.setTestResult('FAIL')
                #    self.test_status = 'STOP'
                # else:
                self.test_status = ResultProcessor(curr_task).getStatus(self.test_mngr_initr)
                #print "subq:test_status : " + self.test_status
                self.log_exectask(curr_task, ResultProcessor(curr_task))
                completed_sub_q.enqueue(curr_task)
        except:
            if self.thread_error_flag == False:
                self.thread_error_flag = True
            completed_sub_q.enqueue(curr_task)

    def proc_subQ_tasks_parallel(self, para_q_list):
        """ This is a multi-thread function to spwan threads"""
        length = len(para_q_list)
        threads = []
        completed_subq_list = []
        
        if self.search_testbed_device("PowerSwitch"):
            self.ap_config_port = int(self.get_ap_agent_port()) + 1
        else:
            self.ap_config_port = int(self.get_ap_agent_port())
            
        if length == 0:
            return
        else:
            #print "thread count:", length
            for num in range(0, length):
                tmp = ExecutionQueue()
                completed_subq_list.append(tmp)

        for curr_subq in para_q_list:
            thread = threading.Thread(target=self.proc_subq_task,
                                        args=[curr_subq, self.ap_config_port + self.port_offset,
                                        completed_subq_list[self.offset]])
            self.offset += 1
            if (self.search_testbed_device("TestbedAPConfigServer")
                == self.search_testbed_device(curr_subq.name)):
                for ap_name, subq_ref in self.ap_dict.iteritems():
                    if subq_ref == curr_subq:
                        self.ap_port_map[ap_name] =  self.ap_config_port + self.port_offset
                self.port_offset += 1

            thread.start()
            threads.append(thread)

        for thread in threads:
            if self.thread_error_flag == True and self.is_validation == False:
                self.test_status = 'STOP'
                self.exe_result = 'FAIL'
            thread.join()
        if self.thread_error_flag == True:
            logging.info("Error: one or more parallel execution failed\n")
        
        #print self.ap_port_map
        self.append_subq_compq(completed_subq_list)
        return

    def log_currObj(self, curr_obj):
        """Logs an outgoing CAPI in the style of old UCC"""
        displaynamevalue = self.get_displayname(curr_obj)
        print_set = {'info', 'echo', 'AddSTAVersionInfo'}
        no_log_set = {'sleep', 'Phase'}
        stream_messages = {'max_throughput' : 'Maximum Throughput %s Mbps',
                           'payloadvalue' : 'Payload = %s Bytes',
                           'stream1' : 'stream1 %s Frames / second',
                           'stream2' : 'stream2 %s Frames / second',
                           'stream3' : 'stream3 %s Frames / second',
                           'stream_mt' : 'stream_mt %s Frames / second',
                           'stream_trans' : 'stream_trans %s Frames / second'}
        if curr_obj.get_cmd().lower() in print_set:
            Util.set_color(Util.FOREGROUND_CYAN | Util.FOREGROUND_INTENSITY)
            logging.info('\n%s%s %s %s\n' % (' '*8, '~'*5, curr_obj.param, '~'*5))
            Util.set_color(Util.FOREGROUND_WHITE)
        elif curr_obj.get_cmd().lower() in stream_messages:
            logging.info(stream_messages[curr_obj.get_cmd().lower()] % (curr_obj.get_param()))
        elif curr_obj.get_cmd().lower() in no_log_set:
            logging.debug('%s %s' % (curr_obj.get_cmd().lower(),curr_obj.get_param()))
        else:
            if (displaynamevalue is None or displaynamevalue == '') and curr_obj.get_ipport() != '':
                displaynamevalue = curr_obj.get_ipport()
            if displaynamevalue is not None and displaynamevalue != '':
                if curr_obj.get_param() != '':
                    logging.info('%s (%s) ---> %s,%s' % (displaynamevalue,
                                                         curr_obj.get_ipport(),
                                                         curr_obj.get_cmd(),
                                                         curr_obj.get_param()))
                else:
                    logging.info('%s (%s) ---> %s' % (displaynamevalue,
                                                      curr_obj.get_ipport(),
                                                      curr_obj.get_cmd()))

                if displaynamevalue == "SNIFFER":
                    TestLogFileSource.log_file_source_obj_list[2].write_log_message("%s ---> %s,%s" % (displaynamevalue, curr_obj.get_cmd(), curr_obj.get_param()), TestLogFileSource.log_file_hdl_list[2], "SNIFFERLOG")
		
    def get_displayname(self, curr_obj):
        displaynamevalue = None
        try:
            ip = curr_obj.get_ipport().strip().split(':')[0]
            port = curr_obj.get_ipport().strip().split(':')[1]
        except IndexError:
            ip = None
            port = None
        for tbd in self.test_mngr_initr.test_prog_mngr.test_prog.testbed_dev_list:
            if tbd.ctrlipaddr == ip:
                displaynamevalue = tbd.displayname
        if displaynamevalue is not None:
            return displaynamevalue
        else:
            return curr_obj.get_ipport()

    def log_exectask(self, curr_obj, rp):        
        displaynamevalue = self.get_displayname(curr_obj)
        cmd = rp.ExecutionTask.cmd
        ipport = rp.ExecutionTask.ipport
        #recv = rp.ExecutionTask.recv
        non_net_set = {'info',
                       'math',
                       'Phase',
                       'traffic_agent_send',
                       'traffic_agent_receive_stop',
                       'echo', 
                       'sleep',
                       'r_info',
                       'search',
                       'userinput_ifnowts',
                       'cat',
                       'config_multi_subresults',
                       'resultcheck',
                       'PingInternalChk',
                       'CheckThroughput',
                       'StoreThroughput',
                       'socktimeout',
                       'AddSTAVersionInfo'}
        if cmd not in non_net_set:
            if (displaynamevalue is None or displaynamevalue == '') and curr_obj.get_ipport() != '':
                displaynamevalue = curr_obj.get_ipport()
            #===================================================================
            # if self.test_mngr_initr.test_data_strm_mngr.data_strm.event is not None and not self.test_mngr_initr.test_data_strm_mngr.data_strm.event.isSet():
            #     print "I am waiting ...."
            #     self.test_mngr_initr.test_data_strm_mngr.data_strm.event.wait()
            #     self.test_mngr_initr.test_data_strm_mngr.data_strm.event.clear()
            #===================================================================
            recv = rp.ExecutionTask.recv
            logging.info('%s (%s) <-- %s' % (displaynamevalue, ipport, recv))
            if displaynamevalue == "SNIFFER":
                TestLogFileSource.log_file_source_obj_list[2].write_log_message("%s <-- %s\n" % (displaynamevalue, recv), TestLogFileSource.log_file_hdl_list[2], "SNIFFERLOG")


    def proc_mainQ_task(self, curr_obj):
        """ This is a function to process task in the main Q"""
        self.resultprocess_obj = ResultProcessor(curr_obj)
        if type(curr_obj) is ExecutionQueue:
            self.sub_q_list.append(curr_obj)
            if len(self.sub_q_list) == self.ap_counter:
                self.proc_subQ_tasks_parallel(self.sub_q_list)
                self.sub_q_list[:] = []

        if type(curr_obj) is ExecutionTask:
            if (curr_obj.get_cmd() != 'info' 
                and len(self.sub_q_list) > 0 
                and len(self.sub_q_list) < self.ap_counter):
                self.proc_subQ_tasks_parallel(self.sub_q_list)
                self.ap_counter = self.ap_counter - len(self.sub_q_list)
                self.sub_q_list[:] = []

            if  self.ap_port_map.has_key(curr_obj.get_ap_name()):
                ipPort = self.replace_port(curr_obj.get_ipport(), self.ap_port_map.get(curr_obj.get_ap_name()))
                curr_obj.set_ipport(ipPort)
            self.exe_result = curr_obj.execute()
            self.log_currObj(curr_obj)
            if self.exe_result != 'SKIP':
                logging.debug("proc_mainQ_task: [%s!%s]", curr_obj.cmd, curr_obj.param)
            else:
                logging.debug("proc_mainQ_task skipping: [%s!%s]", curr_obj.cmd, curr_obj.param)			
            self.completed_q.append(curr_obj)

            if self.exe_result == 'FAIL':
                self.resultprocess_obj.setTestResult('FAIL')
                self.test_status = 'STOP'
            else:
                if TestScriptSymbolTable.test_script_sym_tab["ifCondBit"] == True:
                    self.test_status = self.resultprocess_obj.getStatus(self.test_mngr_initr)
                    #print "mainq:test_status : " + self.test_status
                    self.log_exectask(curr_obj, self.resultprocess_obj)
                else:
                    logging.debug("Skip --> It doesn't meet the if condition")
           
            # if self.test_status == 'STOP':
            #    self.resultprocess_obj.generateFinalResult()
            #    print "TEST ENDS"

    def process_exec_q(self):
        while self.main_exec_q.is_empty() == False:
            obj = self.main_exec_q.dequeue()
            self.proc_mainQ_task(obj)
            if self.test_status == 'STOP':
                if self.exe_result == 'FAIL':
                    self.resultprocess_obj.setTestResult('FAIL')
                self.resultprocess_obj.generateFinalResult()
                return
        if self.main_exec_q.is_empty() == True:
            if self.exe_result == 'FAIL':
                self.resultprocess_obj.setTestResult('FAIL')
            self.resultprocess_obj.generateFinalResult()

    def display_completed_q(self):
        """ This is an API to display the completed Q"""
        print "\n=== completed Q ===\n"
        for task in self.completed_q:
            if task.ret == {}:
                ret = 'DEFAULT'
            else:
                ret = task.ret
            logging.info("completed_q: %s!%s!%s!%s!" % (task.device_id, task.cmd,
                                                    task.param,
                                                    ret))
