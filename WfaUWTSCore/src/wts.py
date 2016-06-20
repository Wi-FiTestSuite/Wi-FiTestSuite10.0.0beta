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
import argparse
from operator import itemgetter
import sys
import os
import re
import threading
from socket import *
import core.parser
import scriptinfo.scriptsource
import core.initializer
from common import *
from util.misc import Util
from core.executor import Executor
from features import display_val_result
from features.usermode import UserMode
from frontend.cli import FrontendCli, FrontendCliServer
from scriptinfo.scriptsource import TestLogFileSource
from security.filesec import ScriptsSecurity
from dbaccess import historydb
from core.symtable import TestScriptSymbolTable
from security.filelocker import ReadFileBusy
from features.validation import Validation
from netcomm.netsocket import NetCommClient
from netcomm.netsocket import NetCommServer


class UserRequestAction:
    """A thread class to handle user requests passed in through front end controller.

    Attributes:
        usr_in_cmd (object): The object of UserCommand class.
        user_mode (object): The object of UserMode class.
        is_running (boolean): The while loop stops when it is False.
        req_hdl_dict (dictionary): Store the mappings of user command to its handling function
    """
    def __init__(self):
        self.is_running = True
        self.usr_in_cmd = None
        self.user_mode = UserMode()
        self.req_hdl_dict = {
            UserCommand.GET_DEFAULT_USER_MODE: self.get_default_user_mode,
            UserCommand.GET_CURRENT_USER_MODE: self.get_curr_user_mode,
            UserCommand.SET_DEFAULT_USER_MODE: self.set_default_user_mode,
            UserCommand.SET_CURRENT_USER_MODE: self.set_curr_user_mode,
            UserCommand.SHOW_USER_MODE: self.show_user_mode,
            UserCommand.STOP_TEST_RUN: self.stop_test_run,
            UserCommand.SHOW_WTS_VERSION: self.get_wts_ver
        }


    def user_request_dispatcher(self):
        """Dispatches user requests to different user mode request handlers.
        """
        while self.is_running:
            item = GlobalConfigFiles.usr_req_que.dequeue()
            if item is not None:
                if isinstance(item.cmd, TestExecutionCommand):
                    run_status = TestFlowController.get_test_flow_status()
                    if run_status == TestFlowController.TEST_FLOW_STATUS_RUNNING:
                        resp_item = item
                        resp_item.cmd.status = UserCommand.ERROR
                        resp_item.cmd.err_msg = "Test case %s currently running, please wait or stop the test" % GlobalConfigFiles.curr_tc_name
                        GlobalConfigFiles.usr_resp_que.enqueue(resp_item)
                    else:
                        self.usr_in_cmd = item.cmd
                        self.start_test_run(item)
                        #self.is_running = False
                        #break
                elif isinstance(item.cmd, UserQueryCommand):
                    cmd_str = item.cmd.cmd_name
                    #print "**************** %s *******************" % cmd_str
                    if cmd_str in self.req_hdl_dict:
                        run_status = TestFlowController.get_test_flow_status()
                        if run_status == TestFlowController.TEST_FLOW_STATUS_RUNNING:
                            if cmd_str == UserCommand.SET_CURRENT_USER_MODE or cmd_str == UserCommand.SET_DEFAULT_USER_MODE:
                                resp_item = item
                                resp_item.cmd.status = UserCommand.ERROR
                                resp_item.cmd.err_msg = "Test case %s currently running, cannot complete the request" % GlobalConfigFiles.curr_tc_name
                                GlobalConfigFiles.usr_resp_que.enqueue(resp_item)
                                continue

                        self.req_hdl_dict[cmd_str](item)
                        #if not (run_status == TestFlowController.TEST_FLOW_STATUS_RUNNING):
                        #    self.is_running = False
                        #    break
                    else:
                        logging.error("Unknown command - %s ###" % cmd_str)
                        resp_item = item
                        resp_item.cmd.status = UserCommand.INVALID
                        resp_item.cmd.err_msg = "User command not identified"
                        ##print resp_item
                        GlobalConfigFiles.usr_resp_que.enqueue(resp_item)
            else:
                #print "######################### in while"
                pass
            time.sleep(1)


    def start_test_run(self, item):
        """Handles the request to start test.
        """
        resp_item = UserInteractQueueItem()
        resp_item.itemId = item.itemId
        resp_item.cmd = item.cmd
        resp_item.cmd.status = UserCommand.COMPLETE
        #print "*********************** start to run test ********************"
        GlobalConfigFiles.usr_resp_que.enqueue(resp_item)


    def stop_test_run(self):
        """Handles stop test run request.
        """
        self.is_running = False


    def get_wts_ver(self, item=None):
        """Gets the WTS version.
        """
        resp_item = UserInteractQueueItem()
        resp_item.itemId = item.itemId
        resp_item.cmd = item.cmd
        resp_item.cmd.status = UserCommand.COMPLETE
        resp_item.cmd.result = GlobalConfigFiles.VERSION
        
        GlobalConfigFiles.usr_resp_que.enqueue(resp_item)

    
    def get_default_user_mode(self, item=None):
        """Gets the default user mode.

        Args:
            item (object): The object of UserInteractQueueItem class.
        """
        default_mode = self.user_mode.get_default_mode()
        #print "*********************** get default user mode %s ********************" % default_mode

        if item is not None:
            resp_item = UserInteractQueueItem()
            resp_item.itemId = item.itemId
            resp_item.cmd = item.cmd
            resp_item.cmd.status = UserCommand.COMPLETE
            resp_item.cmd.result = default_mode

            GlobalConfigFiles.usr_resp_que.enqueue(resp_item)
        else:
            return default_mode


    def get_curr_user_mode(self, item=None):
        """Gets the current user mode.

        Args:
            item (object): The object of UserInteractQueueItem class.
        """
        curr_mode = self.user_mode.get_current_mode()
        #print "*********************** get current user mode %s ********************" % curr_mode

        if item is not None:
            resp_item = UserInteractQueueItem()
            resp_item.itemId = item.itemId
            resp_item.cmd = item.cmd
            resp_item.cmd.status = UserCommand.COMPLETE
            resp_item.cmd.result = curr_mode

            GlobalConfigFiles.usr_resp_que.enqueue(resp_item)
        else:
            return curr_mode


    def set_default_user_mode(self, item):
        """Sets the default user mode.

        Args:
            item (object): The object of UserInteractQueueItem class.
        """
        resp_item = UserInteractQueueItem()
        resp_item.itemId = item.itemId
        resp_item.cmd = item.cmd

        if item.cmd.mode != "":
            ret_val = self.user_mode.set_default_mode(item.cmd.mode)
            if ret_val == -1:
                resp_item.cmd.status = UserCommand.INVALID
                resp_item.cmd.err_msg = "invalid mode, please check"
            else:
                resp_item.cmd.status = UserCommand.COMPLETE
        else:
            resp_item.cmd.status = UserCommand.ERROR
            resp_item.cmd.err_msg = "test flow controller error: parameter is empty"

        #print "*********************** set default user mode done ********************"
        GlobalConfigFiles.usr_resp_que.enqueue(resp_item)


    def set_curr_user_mode(self, item):
        """Sets the current user mode.

        Args:
            item (object): The object of UserInteractQueueItem class.
        """
        resp_item = UserInteractQueueItem()
        resp_item.itemId = item.itemId
        resp_item.cmd = item.cmd

        if item.cmd.mode != "":
            ret_val = self.user_mode.set_current_mode(item.cmd.mode)
            if ret_val == "-1":
                resp_item.cmd.status = UserCommand.INVALID
                resp_item.cmd.err_msg = "invalid mode, please check"
            else:
                resp_item.cmd.status = UserCommand.COMPLETE
        else:
            resp_item.cmd.status = UserCommand.ERROR
            resp_item.cmd.err_msg = "test flow controller error: parameter is empty"

        #print "*********************** set current user mode done ********************"
        GlobalConfigFiles.usr_resp_que.enqueue(resp_item)


    def show_user_mode(self, item):
        """Displays all available user modes.

        Args:
            item (object): The object of UserInteractQueueItem class.
        """
        all_user_modes = self.user_mode.get_available_modes()

        resp_item = UserInteractQueueItem()
        resp_item.itemId = item.itemId
        resp_item.cmd = item.cmd
        resp_item.cmd.status = UserCommand.COMPLETE
        resp_item.cmd.result = all_user_modes

        #print "*********************** %s ********************" % all_user_modes
        GlobalConfigFiles.usr_resp_que.enqueue(resp_item)


    def check_user_mode_permission(self, feat):
        """Checks user mode permission for a specific feature.

        Args:
            feat (str): The string of user mode feature.
        """
        return self.user_mode.check_feature(feat)



class TestFlowController:
    """A class to control test flow including configuration and executioin.

    Attributes:
        capi_script_parser (object): The object of TestScriptParser class.
        xml_file_parser (object): The object of XmlFileParser class.
        test_mngr_initr (object): The object of TestManagerInitializer class.
        usr_input_handle_thr (boolean): The user input command handling thread object.
        usr_action_cls (object): The object of UserRequestAction class.
        executor_inst (object): The object of Executor class.
    """
    TEST_FLOW_STATUS_RUNNING = "RUNNING"
    TEST_FLOW_STATUS_NOTSTART = "NOTSTART"
    TEST_FLOW_STATUS_EXECUTING = "EXECUTING"

    capi_script_parser = None
    xml_file_parser = None
    test_mngr_initr = None
    usr_input_handle_thr = None
    usr_action_cls = None
    executor_inst = None
    file_busy = None
    start_time = None

    @staticmethod
    def reset_test_environment():
        """Resets test execution environment.
        """
        TestFlowController.test_mngr_initr.test_case_mngr = None
        TestFlowController.test_mngr_initr.test_script_mngr = None
        TestFlowController.test_mngr_initr.test_config_info_mngr.sll = None
        TestFlowController.test_mngr_initr.testbed_dev_mngr.ill = None
        TestFlowController.test_mngr_initr.test_data_strm_mngr = None
        TestFlowController.test_mngr_initr.test_prog_mngr = None
        TestFlowController.test_mngr_initr.test_feat_mngr = None

        TestFlowController.test_mngr_initr.test_configurator = None
        TestFlowController.test_mngr_initr.test_config_cxt = None
        TestFlowController.test_mngr_initr.test_config_service = None
        core.parser.TestScriptParser.qll = None
        core.parser.TestScriptParser.ill = None
        TestLogFileSource.log_file_source_obj_list = []
        core.parser.TestScriptParser.sub_file_call_dict = {}
        TestLogFileSource.log_file_hdl_list = []
        TestLogFileSource.log_file_source_obj_list = []
        core.parser.test_script_sym_tab = {"ifCondBit" : True, "socktimeout" : 60, "iDNB" : 0, "testRunning" : 0, "threadCount" : 0}
        core.parser.capi_cmd_ret_sym_tab = {}


    @staticmethod
    def start_test_execution_controller(usr_in_cmd):
        """Starts test case execution as either a group or a single case

        Args:
            usr_in_cmd (object): The object of UserCommand class.
        """
        GlobalConfigFiles.curr_prog_name = usr_in_cmd.prog_name

        if usr_in_cmd.is_group_run:
            if os.path.exists(usr_in_cmd.group_file_name):
                grp_files = open(usr_in_cmd.group_file_name, 'r')
                for tc in grp_files:
                    if not tc:
                        break
                    tc = tc.strip()
                    usr_in_cmd.test_case_id = tc

                    if TestFlowController.test_mngr_initr is not None:
                        TestFlowController.test_mngr_initr.tc_name = tc

                    TestFlowController.initialize_test_environment(usr_in_cmd)
                    GlobalConfigFiles.curr_tc_name = tc

                    TestFlowController.run_test_case(usr_in_cmd)
                    TestFlowController.reset_test_environment()
            else:
                raise OSError(usr_in_cmd.group_file_name + " not exists")
        else:
            GlobalConfigFiles.curr_tc_name = usr_in_cmd.test_case_id
            #===================================================================
            # if usr_in_cmd.is_testcase_val:
            #     TestFlowController.initialize_test_environment(usr_in_cmd)
            #     TestFlowController.run_test_case(usr_in_cmd)
            #     TestFlowController.reset_test_environment()
            #     usr_in_cmd.is_testcase_val = False
            #===================================================================

            TestFlowController.initialize_test_environment(usr_in_cmd)
            TestFlowController.run_test_case(usr_in_cmd)
            TestFlowController.reset_test_environment()


    @staticmethod
    def initialize_test_environment(usr_in_cmd):
        """Initializes test execution environment including domain object managers.

        Args:
            usr_in_cmd (object): The object of UserCommand class.
        """
        if TestFlowController.test_mngr_initr == None:
            TestFlowController.test_mngr_initr = core.initializer.TestManagerInitializer(usr_in_cmd.prog_name, usr_in_cmd.test_case_id)

        TestFlowController.test_mngr_initr.init_test_config_context(usr_in_cmd)
        # gets the current user mode
        TestFlowController.test_mngr_initr.test_config_cxt.user_mode = TestFlowController.usr_action_cls.get_curr_user_mode()
        if TestFlowController.test_mngr_initr.test_config_cxt.user_mode != "precert":
            #TestFlowController.test_mngr_initr.test_config_cxt.is_testbed_validation_set = TestFlowController.usr_action_cls.check_user_mode_permission("validation")
            TestFlowController.test_mngr_initr.test_config_cxt.is_app_id_set = TestFlowController.usr_action_cls.check_user_mode_permission("app_id")
            TestFlowController.test_mngr_initr.test_config_cxt.is_script_protection_set = TestFlowController.usr_action_cls.check_user_mode_permission("script_protection")
            TestFlowController.test_mngr_initr.test_config_cxt.is_result_protection_set = TestFlowController.usr_action_cls.check_user_mode_permission("result_protection")
            TestFlowController.test_mngr_initr.test_config_cxt.is_edit_script_flag_set = TestFlowController.usr_action_cls.check_user_mode_permission("edit_scripts")

        TestFlowController.test_mngr_initr.init_test_manager()
        TestFlowController.test_mngr_initr.init_testbed_device()

        if TestFlowController.test_mngr_initr.test_config_cxt.is_testcase_ignored: return

        TestFlowController.test_mngr_initr.init_test_case()


    @staticmethod
    def run_test_case(usr_in_cmd):
        """Executes a single test case

        Args:
            usr_in_cmd (object): The object of UserCommand class.
        """
        try:
            TestFlowController.prepare_log_files(usr_in_cmd)

            core.parser.TestScriptParser.sub_file_call_dict["%s:%s:1" % (TestFlowController.test_mngr_initr.test_script_mngr.test_case_file, TestFlowController.test_mngr_initr.test_script_mngr.test_case_file)] = 1

            test_file_source_facotry_list = TestFlowController.get_config_files_list(usr_in_cmd)     

            for test_file_source_facotry in test_file_source_facotry_list:
                test_file_source = test_file_source_facotry.file_factory_method()
                if test_file_source_facotry.file_type == "TXT":
                    for tc in TestFlowController.test_mngr_initr.test_prog_mngr.test_prog.tc_list:
                        if test_file_source_facotry.file_name == tc.tc_name:
                            TestFlowController.test_mngr_initr.test_config_cxt.is_test_case_file = True
                            #TestFlowController.print_config_files_info(test_file_source_facotry.file_name, usr_in_cmd.test_case_id)                         
                            break
                    
                    TestFlowController.print_config_files_info(test_file_source_facotry.file_name, TestFlowController.test_mngr_initr.test_config_cxt.is_test_case_file)
                    
                    if test_file_source_facotry.file_name == GlobalConfigFiles.dut_info_file:
                        TestLogFileSource.log_file_source_obj_list[0].write_log_message("Read DUT Info Function", TestLogFileSource.log_file_hdl_list[0])

                    if test_file_source_facotry.file_name == GlobalConfigFiles.init_config_file:
                        TestFlowController.test_mngr_initr.test_config_cxt.is_all_init_config_file = True
                        #TestFlowController.print_config_files_info(test_file_source_facotry.file_name)                       

                    if test_file_source_facotry.file_name == GlobalConfigFiles.init_cmd_file or test_file_source_facotry.file_name == GlobalConfigFiles.device_id_file:
                        TestFlowController.test_mngr_initr.test_config_cxt.is_all_init_command_file = True
                    
                    TestFlowController.capi_script_parser = core.parser.TestScriptParserFactory.create_parser(test_file_source, TestFlowController.test_mngr_initr)
                    TestFlowController.test_mngr_initr.test_configurator.configure(TestFlowController.test_mngr_initr, TestFlowController.capi_script_parser)

                    if TestFlowController.test_mngr_initr.test_config_cxt.is_all_init_command_file:
                        TestFlowController.test_mngr_initr.test_config_cxt.is_all_init_config_file = False
                        TestFlowController.test_mngr_initr.test_config_cxt.is_all_init_command_file = False

                if test_file_source_facotry.file_type == "XML":
                    TestFlowController.print_config_files_info(test_file_source_facotry.file_name, TestFlowController.test_mngr_initr.test_config_cxt.is_test_case_file)
                    xml_file_parser = core.parser.TestScriptParserFactory.create_parser(test_file_source, TestFlowController.test_mngr_initr, True)
                    TestFlowController.test_mngr_initr.test_configurator.configure(TestFlowController.test_mngr_initr, xml_file_parser)
            # end of for loop

            if usr_in_cmd.is_testbed_val or usr_in_cmd.is_testcase_val:
                TestLogFileSource.log_file_source_obj_list[0].close_log_file(TestLogFileSource.log_file_hdl_list[0]) # TestLogFileSource.log_file_hdl_list[0]
            else:
                TestLogFileSource.log_file_source_obj_list[0].close_log_file(TestLogFileSource.log_file_hdl_list[0]) # TestLogFileSource.log_file_hdl_list[0]
                TestLogFileSource.log_file_source_obj_list[1].close_log_file(TestLogFileSource.log_file_hdl_list[1]) # TestLogFileSource.log_file_hdl_list[1]
                TestLogFileSource.log_file_source_obj_list[3].close_log_file(TestLogFileSource.log_file_hdl_list[3])

            if TestFlowController.test_mngr_initr.test_config_cxt.is_script_protection_set:
                TestFlowController.check_file_integrity()
            
            logging.debug("Executor start...")
            count = 0
            currNode = TestFlowController.capi_script_parser.qll.head
            while currNode is not None:
                logging.debug("TAG: " + currNode.tag)
                logging.debug(currNode.data)
                logging.debug("\n")
                #print "GROUP_TAG: " + currNode.group_tag
                #print "\n"
                currNode = currNode.next
                count += 1
            logging.debug("the count %s" % str(count))

            executor_inst = Executor()
            executor_inst.parallel_enable = True
            
            if usr_in_cmd.is_testbed_val or usr_in_cmd.is_testcase_val:
                executor_inst.construct_valiadate_q(TestFlowController.test_mngr_initr,
                                                    TestFlowController.capi_script_parser,
                                                    TestFlowController.test_mngr_initr)
            else:
                executor_inst.construct_exec_q(TestFlowController.test_mngr_initr,
                                               TestFlowController.capi_script_parser,
                                               TestFlowController.test_mngr_initr)
                            
            tbd_list = TestFlowController.test_mngr_initr.test_config_service.get_test_prog_tbd_list("APConfig", "APCONFIG")
            if len(tbd_list) == 1:
                num_of_aps = 0
                if not (TestFlowController.test_mngr_initr.test_config_cxt.is_testbed_validation_set or TestFlowController.test_mngr_initr.test_config_cxt.is_testcase_validation_set):
                    #for ap in executor_inst.involved_ap_list:
                    ap_list = TestFlowController.test_mngr_initr.test_config_service.get_test_prog_tbd_list("", "AP")
                    for ap in ap_list:
                        logging.debug("%s[%s:%s:%s]" % (ap.dev_name, ap.ctrlipaddr, ap.ctrlport, ap.testipaddr))
                        if ap.ctrlipaddr == "" and ap.testipaddr != "":
                            num_of_aps += 1
                        if ap.ctrlipaddr == tbd_list[0].ctrlipaddr:# and ap.ctrlport == tbd_list[0].ctrlport:
                            num_of_aps += 1
                    
                    ps_list = TestFlowController.test_mngr_initr.test_config_service.get_test_prog_tbd_list("PowerSwitch", "POWERSWITCH")
                    for ps in ps_list:
                        if ps.ctrlipaddr != "":
                            num_of_aps += 1
                            
                if num_of_aps > 0:
                    reply = ""
                    try:
                        net_cli = NetCommClient(AF_INET,SOCK_STREAM)
                        net_cli.networkClientSockConnect(tbd_list[0].ctrlipaddr, '8800')
                        data = "startport=%s" % tbd_list[0].ctrlport + ",numofaps=%s" % num_of_aps
                        NetCommServer.SOCK_READABLE.remove(net_cli.sock)
                        NetCommServer.SOCK_WAIT.remove(net_cli.sock)
                        net_cli.networkClientSockSend(data)
                        net_cli.networkClientSockTimeout(240)        
                        reply = net_cli.networkClientSockRecv(1024)
                    except:
                        if re.search(r"status,ERROR", reply):
                            logging.error(reply)
                        #print error msg instead of raise exception..
                        logging.info("=============================================")
                        logging.info("Please check AP config agent is running.")
                        logging.info("END: TEST CASE [%s] " % usr_in_cmd.test_case_id)
                        elapsed = (time.time() - TestFlowController.start_time)
                        logging.info("Execution Time [%s] seconds" % round(elapsed,2))
                        return
                        #raise Exception(reply)
            
            time.sleep(num_of_aps)
            executor_inst.process_exec_q()
            #executor_inst.display_completed_q()

            if usr_in_cmd.is_testbed_val or usr_in_cmd.is_testcase_val:
                tbd_list = TestFlowController.test_mngr_initr.test_prog_mngr.test_prog.testbed_dev_list
                program = TestFlowController.test_mngr_initr.prog_name
                v = Validation()
                ts = v.get_latest_result_session()
                if ts is not None:
                    logging.info('Last validation was at: %s' % str(ts.get('timestamp')))
                v.commence_validation(program, tbd_list)
                display_val_result.display_validation_res()
                return

            #logging.info("END: TEST CASE [%s] " % usr_in_cmd.test_case_id)
            elapsed = (time.time() - TestFlowController.start_time)
            logging.info("Execution Time [%s] seconds" % round(elapsed,2))

            #===================================================================
            # if TestFlowController.test_mngr_initr.test_config_cxt.is_result_protection_set:
            #     TestFlowController.get_curr_log_file()
            #     TestFlowController.save_log_sig()
            #===================================================================

        except TestScriptVerificationError as tsve:
            logging.error(tsve)
            raise

        except Exception:
            # instance.__class__ is the exception class
            logging.error('Exception caught!', exc_info=True)
 
        finally:
            if usr_in_cmd.is_testbed_val or usr_in_cmd.is_testcase_val:
                return
            
            TestLogFileSource.log_file_source_obj_list[2].close_log_file(TestLogFileSource.log_file_hdl_list[2])
            
            if TestFlowController.test_mngr_initr.test_config_cxt.is_result_protection_set:
                TestFlowController.get_curr_log_file()
                TestFlowController.save_log_sig()
                TestFlowController.file_busy.stop_logging()
                
            loggers = logging.getLogger()
            for handler in logging.getLogger().handlers:
                handler.close()
                loggers.removeHandler(handler)


    @staticmethod
    def print_config_files_info(file_name, is_test_case_file=False):
        """Prepares the log files by initializing handles first and creating files after.
        """
        if is_test_case_file:
            logging.info("\n %7s Testcase Command File = %s \n" % ("", file_name))
            logging.info("START: TEST CASE [%s] " % file_name)
            
        if file_name == GlobalConfigFiles.init_config_file:
            logging.info("\n %7s Testcase Init File = %s \n" % ("", file_name))  
        
        logging.info("Processing %s file...." % file_name)
        logging.info("---------------------------------------\n")


    @staticmethod
    def get_config_files_list(usr_in_cmd):
        """Prepares the log files by initializing handles first and creating files after.
        """
        test_file_source_facotry_list = []
        
        if usr_in_cmd.prog_name == "AC-11AG" or usr_in_cmd.prog_name == "AC-11B" or usr_in_cmd.prog_name == "AC-11N":
            test_file_source_facotry_list.append(scriptinfo.scriptsource.TestFileSourceFacotry(GlobalConfigFiles.init_config_file, TestFlowController.test_mngr_initr.test_script_mngr.prog_script_folder_path))
            test_file_source_facotry_list.append(scriptinfo.scriptsource.TestFileSourceFacotry(GlobalConfigFiles.init_cmd_file, TestFlowController.test_mngr_initr.test_script_mngr.prog_script_folder_path))
            test_file_source_facotry_list.append(scriptinfo.scriptsource.TestFileSourceFacotry(TestFlowController.test_mngr_initr.test_script_mngr.test_case_file, TestFlowController.test_mngr_initr.test_script_mngr.prog_script_folder_path))
            return test_file_source_facotry_list
        
        if usr_in_cmd.is_testbed_val or usr_in_cmd.is_testcase_val:
            if usr_in_cmd.is_testcase_val:
                test_file_source_facotry_list.append(scriptinfo.scriptsource.TestFileSourceFacotry(GlobalConfigFiles.dut_info_file, TestFlowController.test_mngr_initr.test_script_mngr.prog_script_folder_path))
                test_file_source_facotry_list.append(scriptinfo.scriptsource.TestFileSourceFacotry(GlobalConfigFiles.master_test_info_file, TestFlowController.test_mngr_initr.test_script_mngr.prog_script_folder_path))

            test_file_source_facotry_list.append(scriptinfo.scriptsource.TestFileSourceFacotry(GlobalConfigFiles.init_config_file, TestFlowController.test_mngr_initr.test_script_mngr.prog_script_folder_path))
            test_file_source_facotry_list.append(scriptinfo.scriptsource.TestFileSourceFacotry(GlobalConfigFiles.device_id_file, TestFlowController.test_mngr_initr.test_script_mngr.prog_script_folder_path))
        else:            
            test_file_source_facotry_list.append(scriptinfo.scriptsource.TestFileSourceFacotry(GlobalConfigFiles.dut_info_file, TestFlowController.test_mngr_initr.test_script_mngr.prog_script_folder_path))
            test_file_source_facotry_list.append(scriptinfo.scriptsource.TestFileSourceFacotry(GlobalConfigFiles.master_test_info_file, TestFlowController.test_mngr_initr.test_script_mngr.prog_script_folder_path))
            test_file_source_facotry_list.append(scriptinfo.scriptsource.TestFileSourceFacotry(GlobalConfigFiles.init_config_file, TestFlowController.test_mngr_initr.test_script_mngr.prog_script_folder_path))
            test_file_source_facotry_list.append(scriptinfo.scriptsource.TestFileSourceFacotry(GlobalConfigFiles.init_cmd_file, TestFlowController.test_mngr_initr.test_script_mngr.prog_script_folder_path))
            test_file_source_facotry_list.append(scriptinfo.scriptsource.TestFileSourceFacotry(TestFlowController.test_mngr_initr.test_script_mngr.test_case_file, TestFlowController.test_mngr_initr.test_script_mngr.prog_script_folder_path))

        return test_file_source_facotry_list
    
    
    @staticmethod
    def prepare_log_files(usr_in_cmd):
        """Prepares the log files by initializing handles first and creating files after.
        """
        if usr_in_cmd.is_testbed_val or usr_in_cmd.is_testcase_val:
            TestLogFileSource.log_file_source_obj_list.append(scriptinfo.scriptsource.TestFileSourceFacotry(GlobalConfigFiles.init_config_log_file, "").file_factory_method())
            TestLogFileSource.log_file_source_obj_list[0].create_log_file() # TestLogFileSource.log_file_hdl_list[0]
        else:

            logging.info("\n*** Running Test - %s *** \n" % usr_in_cmd.test_case_id)

            TestLogFileSource.log_file_source_obj_list.append(scriptinfo.scriptsource.TestFileSourceFacotry(GlobalConfigFiles.init_config_log_file, "").file_factory_method())
            TestLogFileSource.log_file_source_obj_list.append(scriptinfo.scriptsource.TestFileSourceFacotry(GlobalConfigFiles.pre_test_log_file, "").file_factory_method())
            TestLogFileSource.log_file_source_obj_list.append(scriptinfo.scriptsource.TestFileSourceFacotry(usr_in_cmd.test_case_id + ".log", "").file_factory_method())
            TestLogFileSource.log_file_source_obj_list.append(scriptinfo.scriptsource.TestFileSourceFacotry(GlobalConfigFiles.html_file, "").file_factory_method())

            TestLogFileSource.log_file_source_obj_list[0].create_log_file() # TestLogFileSource.log_file_hdl_list[0]
            TestLogFileSource.log_file_source_obj_list[1].create_log_file() # TestLogFileSource.log_file_hdl_list[1]

            U = "\n Test ID = [%s] CmdPath = [%s] Prog Name = [%s] initFile =[%s] TBFile =[%s]" % (usr_in_cmd.test_case_id, TestFlowController.test_mngr_initr.test_script_mngr.prog_script_folder_path, usr_in_cmd.prog_name, GlobalConfigFiles.init_config_file, TestFlowController.test_mngr_initr.test_script_mngr.testbed_ap_file)

            TestLogFileSource.log_file_source_obj_list[2].init_logging(GlobalConfigFiles.LOG_LEVEL)
            TestLogFileSource.log_file_source_obj_list[3].create_log_file()

            logging.info("\n Test Info %s" % U)


    @staticmethod
    def check_file_integrity():
        """Checks the integrity of config files and test script files.
        """
        config_file_list = TestFlowController.get_config_file_call_list()
        tc_file_list = TestFlowController.get_tc_file_call_list()

        file_security_obj = ScriptsSecurity()
        for filename in config_file_list:
            # allows the validation of configuration file to fail
            file_security_obj.validate_single_file(GlobalConfigFiles.curr_prog_name, filename)

        for filename in tc_file_list:
            tc_vrf_rslt = file_security_obj.validate_single_file(GlobalConfigFiles.curr_prog_name, filename)
            if not TestFlowController.test_mngr_initr.test_config_cxt.is_edit_script_flag_set:
                if tc_vrf_rslt:
                    raise TestScriptVerificationError("Script file %s verification failed [current mode %s]" % (filename, TestFlowController.test_mngr_initr.test_config_cxt.user_mode))


    @staticmethod
    def get_config_file_call_list():
        """Gets a list of config files associated with current test case.
        """
        config_file_list = []
        config_file_list.append(GlobalConfigFiles.dut_info_file)
        config_file_list.append(GlobalConfigFiles.master_test_info_file)
        config_file_list.append(GlobalConfigFiles.init_config_file)
        config_file_list.append(GlobalConfigFiles.init_cmd_file)

        file_chain_dict = sorted(core.parser.TestScriptParser.sub_file_call_dict.items(), key=itemgetter(1))
        for fp in file_chain_dict:
            #print fp[0]
            curr_parent = fp[0].split(':')[0]
            curr_child = fp[0].split(':')[1]
            curr_indx = fp[0].split(':')[2]
            #print "curr_index=%s" % curr_indx

            if curr_parent == GlobalConfigFiles.init_config_file or curr_parent == GlobalConfigFiles.init_cmd_file:
                if curr_child == GlobalConfigFiles.init_env_file:
                    continue
                config_file_list.append(curr_child)

        return config_file_list


    @staticmethod
    def get_tc_file_call_list():
        """Gets a list of script files associated with current test case.
        """
        file_chain_list = []
        file_chain_dict = sorted(core.parser.TestScriptParser.sub_file_call_dict.items(), key=itemgetter(1))
        for fp in file_chain_dict:
            #print fp[0]
            curr_parent = fp[0].split(':')[0]
            curr_child = fp[0].split(':')[1]
            curr_indx = fp[0].split(':')[2]
            #print "curr_index=%s" % curr_indx
            #if curr_parent in file_chain_list or curr_child in file_chain_list:
            #    continue

            if curr_parent == GlobalConfigFiles.init_config_file or curr_parent == GlobalConfigFiles.init_cmd_file:
                continue

            if curr_parent == curr_child:
                file_chain_list.append(curr_parent)
            else:
                if curr_parent in file_chain_list and not curr_child in file_chain_list:
                    file_chain_list.append(curr_child)
                if not curr_parent in file_chain_list and curr_child in file_chain_list:
                    file_chain_list.append(curr_parent)
                if not curr_parent in file_chain_list and not curr_child in file_chain_list:
                    file_chain_list.append(curr_parent)
                    file_chain_list.append(curr_child)

        return file_chain_list


    @staticmethod
    def get_curr_log_file():
        """Unlocks the current test log file.
        """
        TestFlowController.file_busy = ReadFileBusy()
        TestFlowController.file_busy.write_string_to_file()


    @staticmethod
    def save_log_sig():
        """Saves the signature of current test log file to database.
        """
        log_file_path = TestScriptSymbolTable.get_value_from_sym_tab("$logFullPath", TestScriptSymbolTable.test_script_sym_tab)
        history = historydb.History(GlobalConfigFiles.curr_prog_name, GlobalConfigFiles.curr_tc_name, TestFlowController.test_mngr_initr.test_config_cxt.user_mode, log_file_path)
        history_service = historydb.HistoryService(history)

        sig = TestFlowController.file_busy.get_file_sig()

        #history_service.updateHistoryByLogSig(sig)
        #####################################################
        blob = TestFlowController.file_busy.set_blob_data()
        digest = TestFlowController.file_busy.get_log_digest()
        history_service.updateHistoryByLogOuput(blob, sig, digest)


    @staticmethod
    def get_test_flow_status():
        """Obtains the current test flow status
        """
        if TestFlowController.test_mngr_initr is None:
            return TestFlowController.TEST_FLOW_STATUS_NOTSTART
        else:
            if not TestFlowController.executor_inst.mainExecQ.is_empty():
                return TestFlowController.TEST_FLOW_STATUS_EXECUTING
            else:
                return TestFlowController.TEST_FLOW_STATUS_RUNNING


def main():
    fec = FrontendCli('AC-11AG AC-11B AC-11N HS2 HS2-R2 N P2P PMF TDLS WFD WMM WPA2 WFDS VHT WMMPS NAN VE')
    #sys.argv = ['uwts_ucc.exe', 'WFD', 'WFD-6.1.21B'] #HS2-4.15 HS2-5.6-A
    #sys.argv = ['uwts_ucc.exe', '-p', 'VHT', '-t', 'VHT-5.2.1']
    #sys.argv = ['uwts_ucc.exe', '-p', 'VHT', '-val']
    #sys.argv = ['uwts_ucc.exe', '-p', 'VHT', '-t', 'VHT-5.2.1', '--set-current-usermode', 'matl-mrcl']
    #sys.argv = ['uwts_ucc.exe', '-p', 'VHT', '--set-current-usermode', 'atl']
    #sys.argv = ['uwts_ucc.exe', '-p', 'VHT', '-t', 'VHT-5.2.1', '-val']
    #sys.argv = ['uwts_ucc.exe', '--show-usermode']
    #sys.argv = ['uwts_ucc.exe', '-v']
    #sys.argv = ['uwts_ucc.exe', '--get-current-usermode']
    #sys.argv = ['uwts_ucc.exe', '--set-default-usermode', 'atl']
    #sys.argv = ['uwts_ucc.exe', '--set-current-usermode', 'atl']

    #print sys.argv
     
    check_cmd_result = fec.fec_register_cmd().fec_check_cli_cmd(sys.argv)
    if check_cmd_result is not None and not isinstance(check_cmd_result, argparse.Namespace):
        logging.error("Error in command line parse")
        exit(1)

    GlobalConfigFiles.usr_req_que = UserInteractQueue("REQUEST")
    GlobalConfigFiles.usr_resp_que = UserInteractQueue("RESPONSE")

    output_str = fec.check_instance(sys.argv)
    if output_str != "Start":
        return

    #register the Queue for FrontendCli
    if fec is not None:
        #start the tcp server here after one successful cli command
        fec_server = FrontendCliServer()
        fec_server.register_parent(fec).register_QCB(Cli_Fl_ctrl_req_Q=GlobalConfigFiles.usr_req_que, \
            Cli_Fl_ctrl_resp_Q=GlobalConfigFiles.usr_resp_que)
        fec_server.start()
    else:
        logging.error("Remote command not able to activate")

    if fec.testProgName is not None:
        prog_name = fec.testProgName[0]
        #print "progName : " + prog_name

    if fec.testCaseName is not None:
        script_name = fec.testCaseName[0]
        #print "scriptName : " + script_name 

    Util.get_wts_build_version()
    
    TestFlowController.usr_action_cls = UserRequestAction()
    TestFlowController.usr_input_handle_thr = threading.Thread(target=TestFlowController.usr_action_cls.user_request_dispatcher)
    TestFlowController.usr_input_handle_thr.start()

    fec.handle_cli_cmd(sys.argv)

    TestFlowController.start_time = time.time()
    timeout = 5
    
    while time.time() < TestFlowController.start_time + timeout:
        #print "diff time %s" % (time.time() - start_time)
        if TestFlowController.usr_action_cls.usr_in_cmd is not None:
            #if prog_name == "AC-11AG" or prog_name == "AC-11B" or prog_name == "AC-11N":
            #    TestFlowController.usr_action_cls.usr_in_cmd.prog_name = "WMM-AC"
            #    prog_name = "WMM-AC"
            
            GlobalConfigFiles.init_cmd_file = GlobalConfigFiles.init_cmd_file.replace("##", prog_name)
            GlobalConfigFiles.init_config_file = GlobalConfigFiles.init_config_file.replace("##", prog_name)

            try:
                TestFlowController.start_test_execution_controller(TestFlowController.usr_action_cls.usr_in_cmd)
                if TestFlowController.usr_action_cls.usr_in_cmd.is_testbed_val or TestFlowController.usr_action_cls.usr_in_cmd.is_testcase_val:
                    break
            except TestScriptVerificationError:
                logging.error("Aborting the test....", exc_info=False)
                #logging.error("%s Aborting the test...." % sys.exc_info()[1])
                break
            except:
                logging.error('caught:', exc_info=True)
                break
        else:
            break

    TestFlowController.usr_action_cls.is_running = False
    TestFlowController.usr_input_handle_thr.join()

    if fec_server is not None:
        fec_server.stop_server()
        fec_server.join()


if __name__ == "__main__":
    main()
