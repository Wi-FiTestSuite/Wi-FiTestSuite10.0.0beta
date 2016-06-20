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
    Module :    Front end controller
    Purpose:    To perform CLI command parse and call the respective function
    Assumption: 
    Note:       
"""


from common import *

import logging
import time
import argparse
import os
import sys
import threading
import Queue
import socket
from random import randint
import select


logging.basicConfig(level=logging.DEBUG,
                    format='%(name)s: %(message)s',
                    )


class FrontendQueueMsg:
    def __init__(self, dst, src, msgId, msgType, message ):
        self.dst = dst
        self.src = src
        self.msgId = msgId
        self.msgType = msgType
        self.message = message
        
    def __del__(self):
        print self.msgId, ' deleted'
 


class CmdList:
    command_list = [
    {'cmd':'--prog -p', 'type' : '', 'required' : False, 'nargs' : 1, 'action': 'append', 'default' : '',  'help': "             : Program name", 'cb_funct' : None },
    {'cmd':'--group -g', 'type' : '', 'required' : False, 'nargs' : 1, 'action': 'append', 'default' : ' ',  'help': "             : Group name", 'cb_funct' : None },
    {'cmd':'--validate -val', 'type' : '', 'required' : False, 'nargs' : '*', 'action': 'store_true', 'default' : ' ', 'help': "             : Test bed Validation", 'cb_funct' : None },
    {'cmd':'--ver -v', 'type' : '', 'required' : False, 'nargs' : '?', 'action': 'store_true', 'default' : ' ',  'help': "             : Version for the wts", 'cb_funct' : None },
    {'cmd':'--qual -q', 'type' : '', 'required' : False, 'nargs' : 1, 'action': 'append', 'default' : '',  'help': "             : Qualification <qual file>", 'cb_funct' : None },
    {'cmd':'--testcase -t', 'type' : '', 'required' : False, 'nargs' : 1, 'action': 'append', 'default' : '',  'help': "             : Testcase <test case file> ", 'cb_funct' : None },
    {'cmd':'--tcdir ', 'type' : '', 'required' : False, 'nargs' : 1, 'action': 'append', 'default' : '',  'help': "             : Testcase directory <dir path> ", 'cb_funct' : None },
    {'cmd':'--remote -r', 'type' : '', 'required' : False, 'nargs' : '?', 'action': 'append', 'default' : 'localhost',  'help': "             : remote wts IP address ", 'cb_funct' : None },
    {'cmd':'--set-default-usermode', 'type' : '', 'required' : False, 'nargs' : 1, 'action': 'append', 'default' : '',  'help': "             : set default user mode", 'cb_funct' : None },
    {'cmd':'--get-default-usermode', 'type' : '', 'required' : False, 'nargs' : '*', 'action': 'store_true', 'default' : '',  'help': "             : get default user mode", 'cb_funct' : None },
    {'cmd':'--set-current-usermode', 'type' : '', 'required' : False, 'nargs' : 1,   'action': 'append', 'default' : '',  'help': "             : set current user mode", 'cb_funct' : None },
    {'cmd':'--get-current-usermode', 'type' : '', 'required' : False, 'nargs' : '*', 'action': 'store_true', 'default' : '',  'help': "             : get current user mode", 'cb_funct' : None },
    {'cmd':'--show-usermode', 'type' : '', 'required' : False, 'nargs' : '*', 'action': 'store_true', 'default' : '',  'help': "             : show avialble user modes", 'cb_funct' : None },
    ]
    #def __init__(self):
        #print "class CmdList"


        
        
class FrontendCliClient():
    def __init__(self,(client,address)):
        self.client = client
        self.address = address
        self.size = 1024

    def recv_data(self):
        if self.client:
            self.data = self.client.recv(self.size)
            #print self.data
            if self.data:
                #print "data receive ****"
                #self.client.send(self.data)
                return
            else:
                self.client.close()


class FrontendCliServer(threading.Thread):
    """
        Frontend Cli will receive the client socket call and 
        start the client thread for the same
    """
    USER_QUERY = "Uquery"
    TEST_EXECUTION = "TestExec"
    REQUEST = "Req"
    RESPONSE = "Resp"
    def __init__(self, name = 'FCtcpserver', num_client = 4, server_port = 8559):
        threading.Thread.__init__(self, name = name)
        self._start_event =  threading.Event()
        self._stop_event =  threading.Event()
        self.name = name
        
        self.num_client = num_client
        self.host_address = "127.0.0.1"
        self.server_port = server_port
        self.server = None
        self.server_thread = None
        self.clients = []
        self.msg_id = randint(1000,9999)
        
        #  define all queue for the task
        self.cli_req_queue = None
        self.flowCtrl_req_queue = None
        self.flowCtrl_resp_queue = None
        self.getReqObject = None
        self._type = FrontendCliServer.REQUEST
        self._cmdCat = FrontendCliServer.USER_QUERY
        self._cmdCatlist = []

    def register_parent(self, parent):
        if isinstance(parent, FrontendCli):
            self.owner_ = parent
        else:
            logging.error("Parent object error")
        return self

    def register_QCB(self, **reg):
        self.cli_req_queue = reg.get('cli_req_Q', Queue.Queue(5))
        self.flowCtrl_req_queue = reg.get('Cli_Fl_ctrl_req_Q', None)
        self.flowCtrl_resp_queue = reg.get('Cli_Fl_ctrl_resp_Q', None)

    def Cli_to_Flctl_req(self, msg, val):
        if GlobalConfigFiles.usr_req_que is not None:
            #print "Put the msg, val into Request Queue"
            #print msg
            #print val[0]
            if self._cmdCat == FrontendCliServer.USER_QUERY:
                if val[0] == "":
                    mode = None
                else:
                    mode = val[0]
                if msg == "show_usermode":
                    userCmd = UserCommand.SHOW_USER_MODE
                elif msg == "get_default_usermode":
                    userCmd = UserCommand.GET_DEFAULT_USER_MODE
                elif msg == "set_default_usermode":
                    userCmd = UserCommand.SET_DEFAULT_USER_MODE                    
                elif msg == "get_current_usermode":
                    userCmd = UserCommand.GET_CURRENT_USER_MODE
                elif msg == "set_current_usermode":
                    userCmd = UserCommand.SET_CURRENT_USER_MODE
                elif msg == "show_wts_version":
                    userCmd = UserCommand.SHOW_WTS_VERSION
                else:
                    userCmd = "nothing"
                    userCmdVal = "nothing"
                try:
                    self._type = FrontendCliServer.REQUEST
                    Q_message = self.get_user_item_object(userCmd, mode, None)
                    GlobalConfigFiles.usr_req_que.enqueue(Q_message)
                    self._cmdCatlist.append(FrontendCliServer.USER_QUERY)
                except Exception as e:
                    print(e)
            elif self._cmdCat == FrontendCliServer.TEST_EXECUTION:
                prog = msg
                tcid = ""
                group_run = False
                group_file = ""
                if val[0] == "group":
                    group_run = True
                    group_file = val[1]
                    if len(val) > 2 and val[2] == "Val" :
                        testcase_val = True
                elif val[0] != "Val":
                    tcid = val[0]
                    group_run = False
                    group_file = ""
                    if len(val) > 1 and val[1] == "Val":
                        testcase_val = True                    
                    #print " Executing " + tcid

                if len(val) == 2 and val[1] == "Val":
                        testcase_val = True
                        testbed_val = False
                elif len(val) == 1 and val[0] == "Val":   
                        testcase_val = False
                        testbed_val = True
                else:
                    testcase_val = False
                    testbed_val = False

                try:
                    self._type = FrontendCliServer.REQUEST
                    Q_message = self.get_test_item_object(prog, tcid, group_run, group_file, testbed_val, testcase_val, None)
                    GlobalConfigFiles.usr_req_que.enqueue(Q_message)
                    self._cmdCatlist.append(FrontendCliServer.TEST_EXECUTION)
                except Exception as e:
                    print(e)

    #######################################################################################
    def get_user_item_object(self, userCmd, mode, item):
        if self._type == FrontendCliServer.REQUEST and self._cmdCat == FrontendCliServer.USER_QUERY:
            try:
                req_item = UserInteractQueueItem()
                req_item.itemId = time.time()
                req_item.cmd = UserQueryCommand()
                req_item.cmd.cmd_name = userCmd
                if (mode is not None):
                    req_item.cmd.mode = mode
                    print req_item.cmd.mode
                return req_item
            except Exception as e:
                print(e)
        elif self._type == FrontendCliServer.RESPONSE and self._cmdCat == FrontendCliServer.USER_QUERY:
            resp_item = UserInteractQueueItem()
            resp_item.itemId = item.itemId
            resp_item.cmd = item.cmd
            if resp_item.cmd.status == UserCommand.COMPLETE:
                if resp_item.cmd.cmd_name == UserCommand.SHOW_USER_MODE or resp_item.cmd.cmd_name == UserCommand.GET_DEFAULT_USER_MODE or resp_item.cmd.cmd_name == UserCommand.GET_CURRENT_USER_MODE:
                    return resp_item.cmd.result
                elif resp_item.cmd.cmd_name == UserCommand.SET_DEFAULT_USER_MODE or resp_item.cmd.cmd_name == UserCommand.SET_CURRENT_USER_MODE:
                    return "SET mode operation successful"
                elif resp_item.cmd.cmd_name == UserCommand.SHOW_WTS_VERSION:
                    return resp_item.cmd.result
                else:
                    return "Error in completing the command"
            if resp_item.cmd.status == UserCommand.INVALID:
                return "INVALID command"
            if resp_item.cmd.status == UserCommand.ERROR:
                return resp_item.cmd.err_msg
            else:
                #Error in command completion
                return "ERROR in completing user command"
        return None

    def get_test_item_object(self, prog, tcid, group_run, group_file, testbed_val, testcase_val, item):
        if self._type == FrontendCliServer.REQUEST and self._cmdCat == FrontendCliServer.TEST_EXECUTION:
            try:
                req_item = UserInteractQueueItem()
                req_item.itemId = time.time()
                req_item.cmd = TestExecutionCommand()
                req_item.cmd.prog_name = prog
                req_item.cmd.test_case_id = tcid
                req_item.cmd.is_group_run = group_run
                req_item.cmd.group_file_name = group_file
                req_item.cmd.is_testbed_val = testbed_val
                req_item.cmd.is_testcase_val = testcase_val
                return req_item
            except Exception as e:
                print(e)
        elif self._type == FrontendCliServer.RESPONSE and self._cmdCat == FrontendCliServer.TEST_EXECUTION:
            resp_item = UserInteractQueueItem()
            resp_item.itemId = item.itemId
            resp_item.cmd = item.cmd
            if resp_item.cmd.status == UserCommand.COMPLETE:
                return ""
            if resp_item.cmd.status == UserCommand.ERROR:
                return resp_item.cmd.err_msg
            else:
                #Error in command completion
                return "ERROR in completing user command"
        return None

    def Cli_to_Flctl_resp(self):
        self._type = FrontendCliServer.RESPONSE
        if GlobalConfigFiles.usr_resp_que is not None:
            item = GlobalConfigFiles.usr_resp_que.dequeue()
            if len(self._cmdCatlist) > 0: 
                self._cmdCat = self._cmdCatlist.pop(0)
            if item is not None:
                #print "Got response from Test Flow Controller"
                return item
            else:
                return None
        return None

    def createServer(self):
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #print str(self.host_address) + ":" + str(self.server_port)
            self.server.bind((self.host_address, self.server_port))
            self.server.listen(self.num_client)
            #print "after listen >>" + str(self.server)
            return 0
        except socket.error, (value, message):
            if self.server:
                self.server.close()
            print "socket create fail " + message 
            return 1
    
    def run(self):
        #print "server thread started  "
        if (self.createServer() > 0):
            print "server socket fail "
            self._start_event.set()
        list_r = [self.server]
        while not self._start_event.isSet():
            try:
                read_list, _, _ = select.select(list_r, [], [], 1)
            except Exception as e:
                #Closing server sock generates an exception on select
                break
            #if self.server:
            for s_socket in read_list:
                # handle the server socket
                try:
                    client, address = s_socket.accept()
                    #print str(client) + " addr" + str(address)
                    c = FrontendCliClient((client, address))
                    c.recv_data()
                    #print "Output client data:"
                    #print c.data  # here is the client data
                except Exception as e:
                    #Closing server sock generates an exception on accept
                    break
          
                # check for valid command
                try:
                    supported_cmd, ret_msg = self.process_request(c.data)
                    if supported_cmd:
                        self.msg_id += 1
                        self.clients.append([c, self.msg_id])
                    else:
                        c.client.send(ret_msg)
                        c.client.shutdown(socket.SHUT_RDWR)
                        c.client.close()
                except Exception as e:
                    print(e)
                    print "Error occur"
                    print c
                    c.client.send("Error occur")
                    c.client.close()
                    print "error 2"
            # check for the resp Queue from the Flow controller
            resp_msg = self.Cli_to_Flctl_resp()
            if resp_msg is not None:
                if self._cmdCat == FrontendCliServer.USER_QUERY:
                    msg_result = self.get_user_item_object(None, None, resp_msg)
                if self._cmdCat == FrontendCliServer.TEST_EXECUTION:
                    msg_result = self.get_test_item_object(None, None, None, None, None, None,resp_msg)
                for tcp_client in self.clients:
                    tcp_client[0].client.send(msg_result)
                    tcp_client[0].client.shutdown(socket.SHUT_RDWR)
                    tcp_client[0].client.close()
                if self.clients:    
                    self.clients.pop()
        for c in self.clients:
            if isinstance(c[0], FrontendCliClient):
                print "client :" + str(c[0].address)
            else:
                print " C is not object of FrontendCliClient"
            c[0].client.shutdown(socket.SHUT_RDWR)
            c[0].client.close()
    
    def join(self, timeout=None):
        """ Stop the thread and wait for it to end. """
        self._stop_event.set()
        threading.Thread.join(self, timeout)
        #print "TCP server thread stopped"
    
    def stop_server(self):
        """ Close server socket"""
        self.server.close()
        #print "TCP server socket closed"

    def process_request(self, msg_string):
        supported_cmd = False
        return_msg = ""
        result = self.owner_.fec_check_cli_cmd(msg_string.split())

        if result is not None and isinstance(result, basestring):
            print "error on remote command"
            return_msg = result

        elif result is None:
            self._cmdCat = FrontendCliServer.TEST_EXECUTION
            #supported_cmd = False
            #print "TestExec command received"
            test_exec_cmd = msg_string.split()
            if test_exec_cmd[2] == "group":
                self.Cli_to_Flctl_req(test_exec_cmd[1], [test_exec_cmd[2], test_exec_cmd[3]])
            else:
                self.Cli_to_Flctl_req(test_exec_cmd[1], [test_exec_cmd[2]])
            supported_cmd = True
        else:
            self._cmdCat = FrontendCliServer.USER_QUERY
            #supported_cmd = False
            if  result.show_usermode:
                #print "its show_usermode"
                self.Cli_to_Flctl_req("show_usermode", [''])
                supported_cmd = True
            elif  result.get_default_usermode:
                #print "its get_default_usermode"
                self.Cli_to_Flctl_req("get_default_usermode", [''])
                supported_cmd = True
            elif  result.set_default_usermode is not None:
                #print "its set_default_usermode"
                self.Cli_to_Flctl_req("set_default_usermode", result.set_default_usermode)
                supported_cmd = True
            elif  result.get_current_usermode:
                #print "its get_current_usermode"
                self.Cli_to_Flctl_req("get_current_usermode", [''])
                supported_cmd = True
            elif  result.set_current_usermode is not None:
                #print "its set_current_usermode"
                self.Cli_to_Flctl_req("set_current_usermode", result.set_current_usermode)

                if result.prog is not None and result.testcase is not None:
                    self._cmdCat = FrontendCliServer.TEST_EXECUTION
                    self.Cli_to_Flctl_req(result.prog[0], [result.testcase[0]] )

                supported_cmd = True
            elif result.ver and result.ver is not None:
                self.Cli_to_Flctl_req("show_wts_version", [''])
                supported_cmd = True            
            elif  result.prog is not None and (result.testcase is not None or result.validate is not False):
                #command_error = True
                self._cmdCat = FrontendCliServer.TEST_EXECUTION
                #test_exec_cmd = msg_string.split()
                cmd_val = []
                if result.group is not None:
                    cmd_val = ["group", result.group[0]]
                elif result.testcase is not None:
                    cmd_val = [result.testcase[0]]

                if result.validate :
                    cmd_val.append("Val")
                print cmd_val
                if len(cmd_val) != 0:
                    self.Cli_to_Flctl_req(result.prog[0], cmd_val )
                    #command_error = False
                supported_cmd = True
            else:
                print "Not yet Supported"
                return_msg = "Not yet Supported"
        return supported_cmd, return_msg
    
    

class FrontendCli(argparse.ArgumentParser):

    """
        FrontendCli is the main module base class. Only one instance should be creted
        It communicate with command line / tcp server for the input from the user.
        And based on the request it may format and send request to Flowcontrol module
    """

    def __init__(self, prog_name = "N", default_cbf = None):
        self.default_cbf =  default_cbf
        if prog_name != "":
            self.prog_name = prog_name.split()
        else:
            self.prog_name =[]

        self.server_port = 8559
        self.parser = argparse.ArgumentParser(prog='WTS ',formatter_class=argparse.RawTextHelpFormatter )
        self.cmd_list = CmdList()
        self.testProgName = ""
        self.testCaseName = ""
        self.testGroup = ""
        self.testQual = ""
        self.show_usermode = False
        self.get_default_usermode = False
        self.set_default_usermode = False
        self.get_current_usermode = False
        self.set_current_usermode = False
        self.remote = None
        self.validate = False
        self.legacy_cmd = False


    def __str__(self):
        return("\n")
    
    def error(self, message):
        print "Error " + str(message)

        exc = sys.exc_info()[1]
        if exc:
            exc.argument = "do nothing" #self._get_action_from_name(exc.argument_name)
            raise exc
        super(argparse.ArgumentParser, self).error(message)

    def fec_check_cli_cmd(self, argv, consol_print = False):
        #command line argument
        if (len(argv) <= 1):
            print "\n -h --help "
            help_string = self.fec_cli_help(consol_print)
            return help_string
        argv_cli = argv
        del argv_cli[0]
        #print(argv_cli)

        # check the legacy command
        if argv_cli[0][0] == '-':
            try:
                #Perform new UWTS command parsing and validation
                result_2 = self.fec_cmd_parse(argv_cli, consol_print)
                #print "Output result_2:"
                #print result_2
                if result_2 is list(): #not None :
                    self.testProgName = result_2.prog
                    self.testCaseName = result_2.testcase
                    self.testGroup = result_2.group
                    self.testQual = result_2.qual
                    self.show_usermode = result_2.show_usermode
                    self.get_default_usermode = result_2.get_default_usermode
                    self.set_default_usermode = result_2.set_default_usermode
                    self.get_current_usermode = result_2.get_current_usermode
                    self.set_current_usermode = result_2.set_current_usermode
                else:
                    self.testProgName = result_2.prog
                    self.testCaseName = result_2.testcase
                    self.testGroup = result_2.group
                    self.remote = result_2.remote
                    self.validate = result_2.validate
                    return result_2
            except:
                #print "Error 123"
                return -1
        else:
            #Perform legacy command parsing and validation
            self.legacy_cmd = True
            result = self.fec_legacy_cli(argv_cli)
            if result is not None:
                print "\n### Error found in legacy Cli *************"
                if consol_print:
                    print result
                return result
        return None

    def fec_cmd_parse(self, cmd_line_option, consol_print = False):
        try:
            results = self.parser.parse_args(cmd_line_option)
        except: #argparse.ArgumentError, SystemExit :
            exc = sys.exc_info()[1]
            if exc:
                #print "Command line error" + str(exc)
                help_string = self.fec_cli_help(consol_print)
                results = help_string
          
        return results

    def fec_register_cmd(self):
        for c in self.cmd_list.command_list:
            commands = c['cmd'].split()
            if commands[0] == '--remote' :
                self.parser.add_argument(commands[0],commands[1], help = c['help'], required = c['required'], nargs=c['nargs'], default= ['localhost'])
                continue 
            if len(commands) == 2:
                if c['action'] == 'store_true':
                    self.parser.add_argument(commands[0],commands[1], help = c['help'], required = c['required'], action=c['action'])
                else:
                    self.parser.add_argument(commands[0],commands[1], help = c['help'], required = c['required'], nargs=c['nargs']) 
            elif len(commands) == 1:
                if c['action'] == 'store_true':
                    self.parser.add_argument(commands[0], help = c['help'], required = c['required'], action=c['action'])
                else:
                    self.parser.add_argument(commands[0], help = c['help'], required = c['required'], nargs=c['nargs'])
        return self

    def fec_cli_help(self, consol_print = False):
        cli_help_str = "\n" + "*" * 80 + "\n" + self.parser.format_help()
        if consol_print:
            print cli_help_str
        return cli_help_str
        
    def fec_legacy_cli_help(self, consol_print = False):
        prog_name_str =""
        if self.prog_name != "":
            for prog in self.prog_name:
                prog_name_str =  prog_name_str + "\n                      " + prog
        else:
            prog_name_str = "<Prog name>"
            
        legacy_cli_help_str = "\n\t USAGE : wts <Program Name> <Test ID> \n          OR wts <Program Name> group <group file name> \
            \n\t [1] Program Name :" \
            + prog_name_str + \
            "\n\n\t [2] Test ID : Test case ID for that program            OR\
            \n\n\t [2] group : group if running group of test cases followed by group file name\
            \n\n\t [3] group file name: Group file name which contains list of test cases\
            \n\n\t\t For example, To run test P2P-4.1.1 of P2P(Wi-Fi Direct) program,\
            \n\t\t    wts P2P P2P-4.1.1        OR\
            \n\n\t\t For example, To run group of P2P test cases listed in file L1.txt\
            \n\t\t    wts P2P group L1.txt"
        legacy_cli_help_str = legacy_cli_help_str + "\n" + "*" * 80 + "\n" + " " * 23 +  "* Please use new commands from below  *" \
            + "\n" + "*" * 80 + "\n"

        legacy_cli_help_str = legacy_cli_help_str + self.parser.format_help()
        if consol_print:
            print legacy_cli_help_str
        print legacy_cli_help_str
        return legacy_cli_help_str

    def fec_legacy_cli(self, argv):
        nargs = len(argv)
        if (nargs < 2) or (  2 >= nargs < 3 and ( argv[1] == 'group'  or argv[1] == 'qual') ) or (nargs >= 4):
            if (nargs >= 4):
                print "ERROR More number of Argument in Legacy CLi : " + str(nargs) 
            help_string = self.fec_legacy_cli_help()
            return help_string
        else:
            maching_prog = [ s for s in self.prog_name if s == argv[0]]
            if len(maching_prog) == 0:
                print "Error not supported program name"
                help_string = self.fec_legacy_cli_help()
                return help_string
            # program name
            self.testProgName = [argv[0]]
            if (nargs > 2) and (argv[1] == "group"):
                self.testGroup = [argv[2]]
            elif (nargs > 2) and (argv[1] == "qual" ):
                self.testQual = [argv[2]]
            else:
                self.testCaseName = [argv[1]]
        return None

    def handle_cli_cmd(self, argv):
        HOST = '127.0.0.1'    # The remote host
        PORT = 8559              # The same port as used by the server
        msg =""
        if (len(sys.argv) >= 1):
            msg = "uwts.exe "
            for s in sys.argv :
                msg +=  str(s) + " "
            #print "{ " + msg + " }" 
        
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.connect((HOST, PORT))
        s.sendall(msg)
        data = s.recv(4096)
        s.shutdown(socket.SHUT_RDWR)
        s.close()
        #print 'Received', repr(data)
        print "\n"
        print str(data)

    def check_instance(self, argv):
        server_ip = ""
        need_to_start = True
        if self.legacy_cmd :
            return "Start"
        if self.remote is not None: 
            if self.remote[0] != "localhost":
                try:
                    socket.inet_aton(self.remote)
                    server_ip = self.remote
                except socket.error:
                    print "Invalid IP address for remote ip " + self.remote
                    return "Error"
                need_to_start = False
            else :
                server_ip = socket.gethostbyname("localhost")
        else:
            need_to_start = False
            server_ip = socket.gethostbyname("localhost")

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex((server_ip, self.server_port))
        if result == 0:
            try:
                send_msg = "wts.exe " + ' '.join(argv)
                sock.sendall(send_msg)
                print "posted the msg to server"
                response = sock.recv(4096)
                print "Received: {}".format(response)
            finally:
                sock.close()
            return "Client"
        else:
            #print " Not able to connect to remote server"
            #print result
            sock.close()
            if need_to_start == True:
                return "Start"
            else: 
                return "No server"

    def client(self, ip, port, message):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, port))
        try:
            sock.sendall(message)
            response = sock.recv(1024)
            print "Received: {}".format(response)
        finally:
            sock.close()
        sock.close()

def main():
    fec = FrontendCli('AC-11AG/AC-11B/AC-11N HS2 HS2-R2 N P2P PMF TDLS WFD WMM WPA2 WFDS VHT WMMPS NAN VE')
    sys.argv = ['wts.exe',  '--set-default-usermode', 'atl']
    print sys.argv
    
    check_cmd_result = fec.fec_register_cmd().fec_check_cli_cmd(sys.argv)
    if check_cmd_result is not None and not isinstance(check_cmd_result, argparse.Namespace):
        #print "Error in command line parse"
        sys.exit(1)

    GlobalConfigFiles.usr_req_que = UserInteractQueue("REQUEST")
    GlobalConfigFiles.usr_resp_que = UserInteractQueue("RESPONSE")
    # check the WTS is running on local machine or given with remote command
    if fec.check_instance(sys.argv) != "Start":
        print "posted the msg to server" 
        return
    #register the Queue for FrontendCli
    #===========================================================================
    if fec is not None:
        #start the tcp server here after one successful cli command
        fec_server = FrontendCliServer()
        fec_server.register_parent(fec).register_QCB(Cli_Fl_ctrl_req_Q = GlobalConfigFiles.usr_req_que, \
            Cli_Fl_ctrl_resp_Q = GlobalConfigFiles.usr_resp_que)
        fec_server.start()
        #need to do process client command and 
    else:
        print "Remote command not able to activate "
    #===========================================================================
    
    fec.handle_cli_cmd(sys.argv)
    
    if fec_server is not None:
        fec_server.stop_server()
        fec_server.join()

if __name__ == "__main__":
    main()
