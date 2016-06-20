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

import os
import time
from StringIO import StringIO
import HTML
import core.parser
from core.symtable import TestScriptSymbolTable
from scriptinfo.scriptelement import TestScriptElementType
import common
#from dbaccess import historydb
from scriptinfo.scriptsource import TestLogFileSource
from features.validation import Validation


class TestConfigContext:
    """The class that stores the test configuration context that some of them come from user input command.

    Attributes:
        is_testbed_validation_set (boolean): Description of `attr1`.
        is_testcase_validation_set (boolean): Description of `attr2`.
        is_asd_mode_set (boolean): Description of `attr2`.
        is_tms_mode_set (boolean): Description of `attr2`.
        is_group_run_set (boolean): Description of `attr2`.
        group_file_name (str): Description of `attr2`.
        is_test_case_file (boolean): Description of `attr2`.
        is_all_init_config_file (boolean): Description of `attr2`.
        is_all_init_command_file (boolean): Description of `attr2`.
        user_mode (str): Description of `attr2`.

    """
    def __init__(self):
        self.is_testbed_validation_set = False
        self.is_testcase_validation_set = False

        self.is_asd_mode_set = False
        self.is_tms_mode_set = False

        self.is_group_run_set = False
        self.group_file_name = ""

        self.is_test_case_file = False
        self.is_all_init_config_file = False
        self.is_all_init_command_file = False

        self.user_mode = ""
        self.is_app_id_set = False
        self.is_script_protection_set = False
        self.is_result_protection_set = False

        self.is_edit_script_flag_set = False
        self.is_testcase_ignored = False



class TestConfigurator:
    """Constructs domain data objects based on the information on linked list and generates initenv file

    Attributes:
        prog_name (str): Description of `attr1`.
        tc_name (str): Description of `attr2`.
        test_config_cxt (Optional[int]): Description of `attr2`.
        eap_method_list (Optional[int]): Description of `attr2`.
        test_mngr_initr (Optional[int]): Description of `attr2`.
        eap_file_path (Optional[int]): Description of `attr2`.

    """
    def __init__(self, prog_name, tc_name, test_config_cxt):
        self.prog_name = prog_name
        self.tc_name = tc_name

        self.test_case = None
        self.testbed_device = None
        self.test_config_cxt = test_config_cxt
        self.eap_method_list = []
        self.test_mngr_initr = None
        self.eap_file_path = None


    def configure(self, test_mngr_initr, file_parser):
        """Moves all test related information from linkedlist to domain data objects.

        Attributes:
            test_mngr_initr (object): The object of TestManagerInitializer class.
            file_parser (object): The object of XMLFileParser class or TestScriptParser class.
        """
        self.test_mngr_initr = test_mngr_initr

        file_parser.init_parser()
        file_parser.parse() # parse the data into data structure

        if isinstance(file_parser, core.parser.XmlFileParser):
            test_mngr_initr.test_config_info_mngr.sll = file_parser.sll
            test_mngr_initr.test_config_info_mngr.test_mngr_initr = test_mngr_initr
            test_mngr_initr.test_config_info_mngr.set_test_config_info()

            if self.test_config_cxt.is_testbed_validation_set or self.test_config_cxt.is_testcase_validation_set:
                return

            self.generate_feat_html_file()
            ###output = self.create_init_env_file()
            ##bufferStr = output.getvalue()

            ##history = historyService.History(self.prog_name, self.tc_name)
            ##history_service = historyService.HistoryService(history)
            ##history_service.updateHistoryByInitEnv(bufferStr)
            ###output.close()

            ##raw_input("Writing InitEnv file to database completed, press return to exit.")
            ##sys.exit(0)

        if isinstance(file_parser, core.parser.TestScriptParser):
            if self.test_config_cxt.is_test_case_file or self.test_config_cxt.is_all_init_config_file:
                test_mngr_initr.test_config_service.test_mngr_initr = test_mngr_initr

            if file_parser.test_script_scanner.test_script_source.test_script_source_name == common.GlobalConfigFiles.dut_info_file:
                test_mngr_initr.test_feat_mngr.sll = file_parser.sll
                test_mngr_initr.test_feat_mngr.test_mngr_initr = test_mngr_initr
                test_mngr_initr.test_feat_mngr.set_test_prog_feat()

                if self.is_eap_method_list_file_exist():
                    self.load_eap_method_list()
                self.set_other_dut_info()
                TestLogFileSource.log_file_source_obj_list[0].write_log_message("Input Files - \n MasterTestInfo = %s \n DUTInfoFile =%s \n" %(common.GlobalConfigFiles.master_test_info_file, common.GlobalConfigFiles.dut_info_file), TestLogFileSource.log_file_hdl_list[0])

            if file_parser.test_script_scanner.test_script_source.test_script_source_name == common.GlobalConfigFiles.init_config_file:
                test_mngr_initr.testbed_dev_mngr.ill = file_parser.ill
                test_mngr_initr.testbed_dev_mngr.test_mngr_initr = test_mngr_initr
                test_mngr_initr.testbed_dev_mngr.set_testbed_device()
                test_mngr_initr.testbed_dev_mngr.set_rs_eap_cred()

                if test_mngr_initr.test_prog_mngr.test_prog.is_tp_prog:
                    test_mngr_initr.test_data_strm_mngr.ill = file_parser.ill
                    test_mngr_initr.test_data_strm_mngr.set_data_strm_info()

                if self.test_config_cxt.is_testbed_validation_set or self.test_config_cxt.is_testcase_validation_set:
                    self.create_device_id_file()
                    return

                output = self.create_init_env_file()
                output.close()

    def create_device_id_file(self):
        device_id_file_path = self.test_mngr_initr.test_script_mngr.prog_script_folder_path + "\\" + common.GlobalConfigFiles.device_id_file
        device_id_file = open(device_id_file_path, 'w')
        device_id_file.write("# This is an auto generated file  - %s \n# For test program - %s\n#DO NOT modify this file manually \n\n" %(time.strftime("%b-%d-%y_%H:%M:%S", time.localtime()), self.prog_name))
        val = Validation()
        val_data = val.get_validation_routines(self.prog_name)

        testbed_device_list = []
        if self.test_config_cxt.is_testbed_validation_set:
            testbed_device_list = self.test_mngr_initr.test_prog_mngr.test_prog.testbed_dev_list
        if self.test_config_cxt.is_testcase_validation_set:
            testbed_device_list = self.test_mngr_initr.test_case_mngr.test_case.testbed_device_list

        for tbd_name, v_cmd_data in val_data.items():
            cmd_type = v_cmd_data['command'].get('command_type').lower()
            for tbd in testbed_device_list:
                # assume the tbd_name always uses the format of wfa_control_agent_**
                true_dev_name = tbd_name.replace('wfa_control_agent_', '').lower()
                if tbd_name.endswith('_sta') and tbd.dev_type == "STA":
                    true_sta_name = true_dev_name.replace('_sta', '')
                    if tbd.dev_name.lower() == true_sta_name:
                        if tbd.ctrlipaddr != '':
                            if cmd_type == 'capi':
                                cmd_list = v_cmd_data['command'].get('command').split('\n')
                                for cmd in cmd_list:
                                    if tbd.alias.lower() == tbd_name.lower():
                                        device_id_file.write('\n%s!%s\n' % (tbd_name, cmd))
                                    else:
                                        device_id_file.write('\n%s!%s\n' % (tbd.dev_name + 'STA', cmd))
                            elif cmd_type == 'external':
                                func_name = v_cmd_data['command'].get('command')
                                if tbd.alias.lower() == tbd_name.lower():
                                    device_id_file.write('\n%s!ExternalFunc!%s!DEFAULT\n' % (tbd_name, func_name))
                                else:
                                    device_id_file.write('\n%s!ExternalFunc!%s!DEFAULT\n' % (tbd.dev_name + 'STA', func_name))
                        else:
                            TestLogFileSource.log_file_source_obj_list[0].write_log_message("Device %s IP address not exist" % tbd.dev_name, TestLogFileSource.log_file_hdl_list[0])
                if tbd_name.endswith('_ap') and tbd.dev_type == "AP":
                    true_ap_name = true_dev_name.replace('_ap', '')
                    if tbd.dev_name.lower() == true_ap_name:
                        if cmd_type == 'external':
                            func_name = v_cmd_data['command'].get('command')
                            if tbd.alias.lower() == tbd_name.lower():
                                device_id_file.write('\n%s!ExternalFunc!%s!DEFAULT\n' % (tbd_name, func_name))
                            else:
                                device_id_file.write('\n%s!ExternalFunc!%s!DEFAULT\n' % (tbd.dev_name + 'AP', func_name))
                        elif cmd_type == 'capi':
                            cmd_list = v_cmd_data['command'].get('command').split('\n')
                            #self.test_mngr_initr.testbed_dev_mngr.num_of_aps_capi = len(cmd_list)
                            for cmd in cmd_list:
                                if tbd.alias.lower() == tbd_name.lower():
                                    device_id_file.write('\n%s!%s\n' % (tbd_name, cmd))
                                else:
                                    device_id_file.write('\n%s!%s\n' % (tbd.dev_name + 'AP', cmd))
                if tbd_name == 'wfa_sniffer' and tbd.dev_type == "SNIFFER":
                    if cmd_type == 'external':
                        func_name = v_cmd_data['command'].get('command')
                        if tbd.alias.lower() == tbd_name.lower():
                            device_id_file.write('\n%s!ExternalFunc!%s!DEFAULT\n' % (tbd_name, func_name))
                        else:
                            device_id_file.write('\n%s!ExternalFunc!%s!DEFAULT\n' % (tbd.dev_name, func_name))
                    elif cmd_type == 'capi':
                        cmd_list = v_cmd_data['command'].get('command').split('\n')
                        for cmd in cmd_list:
                            if tbd.alias.lower() == tbd_name.lower():
                                device_id_file.write('\n%s!%s\n' % (tbd_name, cmd))
                            else:
                                device_id_file.write('\n%s!%s\n' % (tbd.dev_name, cmd))
        device_id_file.close()


    def create_init_env_file(self):
        """Generates the initenv.txt file with defined configuraiton variables.
        """
        output = StringIO()

        init_env_file_path = self.test_mngr_initr.test_script_mngr.prog_script_folder_path + "\\" + common.GlobalConfigFiles.init_env_file
        ucc_init_file = open(init_env_file_path, 'w')
        ucc_init_file.write("# This is an auto generated file  - %s \n# For test case - %s\n#DO NOT modify this file manually \n\n" %(time.strftime("%b-%d-%y_%H:%M:%S", time.localtime()), self.tc_name))
        output.write("# This is an auto generated file  - %s \n# For test case - %s\n#DO NOT modify this file manually \n\n" %(time.strftime("%b-%d-%y_%H:%M:%S", time.localtime()), self.tc_name))

        ucc_init_file.write("\ndefine!$tcID!%s!\n" % (self.tc_name))
        output.write("\ndefine!$tcID!%s!\n" % (self.tc_name))

        ucc_init_file.write(self.format_env_variables())
        output.write(self.format_env_variables())

        i = 0
        for tbd in self.test_mngr_initr.test_case_mngr.test_case.testbed_device_list:
            if tbd.dev_type == "AP":
                i += 1

        for p in self.test_mngr_initr.test_prog_mngr.test_prog.testbed_dev_list:
            if p.dev_type == "AP":## and p.number != "":
                if p.number == "":
                    i += 1
                    p.number = "AP%s" % i
                    p.state = "off"
                ucc_init_file.write(self.format_testbed_ap(p))
                output.write(self.format_testbed_ap(p))
            if p.dev_type == "RADIUSSERVER":
                rsName = TestScriptSymbolTable.get_value_from_sym_tab("RadiusServerName", TestScriptSymbolTable.test_script_sym_tab)
                #if rsName != '0' and rsName is not None:
                if rsName is not None:
                    if rsName == p.dev_name or rsName == '0':
                        ucc_init_file.write(self.format_radius_server(p))
                        output.write(self.format_radius_server(p))
                         
        #Writing other variables
        for var in self.test_mngr_initr.test_config_info_mngr.test_config_info.var_list:
            ucc_init_file.write("\ndefine!$%s!%s!\n"%(var, self.test_mngr_initr.test_config_info_mngr.test_config_info.var_list[var]))
            output.write("\ndefine!$%s!%s!\n"%(var, self.test_mngr_initr.test_config_info_mngr.test_config_info.var_list[var]))

        ucc_init_file.write("#EOF")
        output.write("#EOF")

        ucc_init_file.close()
        return output


    def format_radius_server(self, rs):
        """Formats the variables in RadiusServer testbed device objects for output.

        Attributes:
            rs (object): The RadiusServer testbed device object.
        """
        return "\n\ndefine!$RADIUSIPAddress!%s!\ndefine!$RADIUSPort!%s!\ndefine!$RADIUSSharedSecret!%s!\ndefine!$SupplicantName!%s!\ndefine!$STASupplicantName!%s!\n" % \
            (rs.testipaddr, rs.testport, rs.shared_secret, rs.supplicant, rs.sta_supplicant)


    def format_testbed_ap(self, ap):
        """Formats the variables in AP testbed device objects for output.

        Attributes:
            ap (object): The AP testbed device object.
        """
        value = None
        if TestScriptSymbolTable.lookup_sym_tab("$" + ap.number, TestScriptSymbolTable.test_script_sym_tab):
            value = TestScriptSymbolTable.get_value_from_sym_tab("$" + ap.number, TestScriptSymbolTable.test_script_sym_tab)
        # define!$AP1!Marvell11nAP!
        return "\n\ndefine!$%s!%s!\ndefine!$%sPowerSwitchPort!%s!\ndefine!$%sState!%s!\ndefine!$%sIPAddress!%s!\n" % \
            (ap.number, value if value else ap.dev_name, ap.number, ap.pwrswtport, ap.number, ap.state, ap.number, (ap.ctrlipaddr if ap.is_emd_ctrl_agt else ap.testipaddr))


    def format_env_variables(self):
        """Outputs variables per the specified format.
        """
        TSTA = []
        sta_count = 0
        for tbd in self.test_mngr_initr.test_prog_mngr.test_prog.testbed_dev_list:
            if tbd.dev_type == "STA" and tbd.number == "STA" + ("%s" % (sta_count + 1)):
                TSTA.append(tbd.dev_name)
                sta_count += 1

        return "define!$Channel!%s!\ndefine!$Channel_1!%s!\ndefine!$Channel_2!%s!\ndefine!$Channel_3!%s!\ndefine!$Band!%s!\ndefine!$SSID!%s!\ndefine!$SSID_1!%s!\ndefine!$SSID_2!%s!\ndefine!$SSID_3!%s!\ndefine!$STA1!%s!\ndefine!$STA2!%s!\ndefine!$STA3!%s!\ndefine!$TestbedConfigCAPIFile!%s!\ndefine!$DUTConfigCAPIFile!%s!\ndefine!$STAConfigCAPIFile!%s!\ndefine!$WLANTestCAPIFile!%s!\n" % \
                ("" if not "Channel" in self.test_mngr_initr.test_config_info_mngr.test_config_info.channel else self.test_mngr_initr.test_config_info_mngr.test_config_info.channel["Channel"],
                 "" if not "Channel_1" in self.test_mngr_initr.test_config_info_mngr.test_config_info.channel else self.test_mngr_initr.test_config_info_mngr.test_config_info.channel["Channel_1"],
                 "" if not "Channel_2" in self.test_mngr_initr.test_config_info_mngr.test_config_info.channel else self.test_mngr_initr.test_config_info_mngr.test_config_info.channel["Channel_2"],
                 "" if not "Channel_3" in self.test_mngr_initr.test_config_info_mngr.test_config_info.channel else self.test_mngr_initr.test_config_info_mngr.test_config_info.channel["Channel_3"],
                 self.test_mngr_initr.test_config_info_mngr.test_config_info.band,
                 "" if not "SSID" in self.test_mngr_initr.test_config_info_mngr.test_config_info.ssid else self.test_mngr_initr.test_config_info_mngr.test_config_info.ssid["SSID"],
                 "" if not "SSID_1" in self.test_mngr_initr.test_config_info_mngr.test_config_info.ssid else self.test_mngr_initr.test_config_info_mngr.test_config_info.ssid["SSID_1"],
                 "" if not "SSID_2" in self.test_mngr_initr.test_config_info_mngr.test_config_info.ssid else self.test_mngr_initr.test_config_info_mngr.test_config_info.ssid["SSID_2"],
                 "" if not "SSID_3" in self.test_mngr_initr.test_config_info_mngr.test_config_info.ssid else self.test_mngr_initr.test_config_info_mngr.test_config_info.ssid["SSID_3"],
                 TSTA[0] if len(TSTA) == 1 else "",
                 TSTA[1] if len(TSTA) == 2 else "",
                 TSTA[2] if len(TSTA) == 3 else "",
                 self.test_mngr_initr.test_config_info_mngr.test_config_info.testbed_dev_config_file,
                 self.test_mngr_initr.test_config_info_mngr.test_config_info.dut_config_file,
                 self.test_mngr_initr.test_config_info_mngr.test_config_info.sta_config_file,
                 self.test_mngr_initr.test_config_info_mngr.test_config_info.wlan_test_capi_file)


    def is_eap_method_list_file_exist(self):
        """Checks if the EAP method list file exists.
        """
        self.eap_file_path = self.test_mngr_initr.test_script_mngr.prog_script_folder_path + "\\" + common.GlobalConfigFiles.eap_method_listFile
        if os.path.exists(self.eap_file_path):
            return True
        else:
            return False


    def load_eap_method_list(self):
        """Loads EAP method list from file system.
        """
        eap_file = open(self.eap_file_path, 'r')
        for item in eap_file.readlines():
            eap_name = item.rstrip("\n")
            if item.startswith('#'):
                continue
            self.eap_method_list.append(eap_name)
        if eap_file:
            eap_file.close()


    def set_other_dut_info(self):
        """Sets other DUT related information into var_list dictionary.
        """
        if self.is_eap_method_list_file_exist():
            ttls_name = TestScriptElementType.get_test_feat_key_from_val(TestScriptElementType.TTLS)
            TestScriptSymbolTable.insert_sym_tab("DUTEAPMethod", ttls_name, TestScriptSymbolTable.test_script_sym_tab)
            found_eap_method = False
            for eap in self.eap_method_list:
                if found_eap_method:
                    break
                for feature in self.test_mngr_initr.test_prog_mngr.test_prog.feat_list:
                    if feature.feat_name == eap and int(feature.feat_value) == 1:
                        TestScriptSymbolTable.insert_sym_tab("DUTEAPMethod", eap, TestScriptSymbolTable.test_script_sym_tab)
                        found_eap_method = True
                        break

        if "N-4.2" in common.GlobalConfigFiles.curr_tc_name or "N-ExA" in common.GlobalConfigFiles.curr_tc_name:
            self.test_mngr_initr.test_config_info_mngr.test_config_info.var_list.setdefault("APUT_state", "on")

        if "N-5.2" in common.GlobalConfigFiles.curr_tc_name or "N-5.3" in common.GlobalConfigFiles.curr_tc_name or "N-ExS" in common.GlobalConfigFiles.curr_tc_name:
            self.test_mngr_initr.test_config_info_mngr.test_config_info.var_list.setdefault("APUT_state", "off")


    def generate_feat_html_file(self):
        """Generates a html DUT feature file while loading DUT features into var_list dictionary.
        """
        if self.prog_name == "P2P" or self.prog_name == "TDLS" or self.prog_name == "PMF" or self.prog_name == "HS2" or self.prog_name == "WFD" \
            or self.prog_name == "WFDS" or self.prog_name == "VHT" or self.prog_name == "HS2-R2" or self.prog_name == "WMMPS" or self.prog_name == "NAN":
            #fFile = self.test_mngr_initr.test_script_mngr.create_log_file(AllImports.GlobalConfigFiles.html_file, 'w')
            T = HTML.Table(col_width=['70%', '30%'])
            R1 = HTML.TableRow(cells=['Optional Feature', 'DUT Support'], bgcolor="Gray", header="True")
            T.rows.append(R1)

            if self.prog_name == "P2P" or self.prog_name == "TDLS" or self.prog_name == "HS2" or self.prog_name == "WFD" or self.prog_name == "WFDS" or self.prog_name == "HS2-R2" or self.prog_name == "NAN":
                p2p_var_list = self.test_mngr_initr.test_feat_mngr.get_dut_feat_list()
                if p2p_var_list != -1:
                    p2p_var_list = p2p_var_list.split('!')
                    TestLogFileSource.log_file_source_obj_list[0].write_log_message("P2P Supported Features = %s" % p2p_var_list, TestLogFileSource.log_file_hdl_list[0])
                    for var in p2p_var_list:
                        if var != "":
                            v = var.split(',')
                            self.test_mngr_initr.test_config_info_mngr.test_config_info.var_list.setdefault(v[0], v[1])
                            feat_supt = self.test_mngr_initr.test_config_info_mngr.sll.search(v[0])
                            if feat_supt is not None:
                                TestLogFileSource.log_file_source_obj_list[0].write_log_message("%s-%s" % (feat_supt, v[1]), TestLogFileSource.log_file_hdl_list[0])
                                if feat_supt != v[1]:
                                    TestLogFileSource.log_file_source_obj_list[0].write_log_message("DUT does not support the feature", TestLogFileSource.log_file_hdl_list[0])
                                    self.test_mngr_initr.test_config_info_mngr.test_config_info.var_list.setdefault("TestNA", "DUT does not support the feature")

                            if v[1] == "0":
                                dis = "No"
                            elif v[1] == "1":
                                dis = "Yes"
                            else:
                                dis = v[1]
                            if "DUT_" not in v[0]:
                                T.rows.append([v[0], dis])
            else:
                prog_var_list = self.test_mngr_initr.test_feat_mngr.get_dut_feat_list()
                if prog_var_list != -1:
                    prog_var_list = prog_var_list.split('!')
                    TestLogFileSource.log_file_source_obj_list[0].write_log_message("%s Supported Features = %s" % (self.prog_name, prog_var_list), TestLogFileSource.log_file_hdl_list[0])
                    check_feat_flag = self.test_mngr_initr.test_config_info_mngr.sll.search("check_feat_flag")
                    #self.test_config_info_mngr.test_mngr_initr.test_case_mngr.test_case.opt_test_feat
                    TestLogFileSource.log_file_source_obj_list[0].write_log_message("check_feat_flag = %s" % check_feat_flag, TestLogFileSource.log_file_hdl_list[0])
                    for var in prog_var_list:
                        if var != "":
                            v = var.split(',')
                            self.test_mngr_initr.test_config_info_mngr.test_config_info.var_list.setdefault(v[0], v[1])
                            feat_supt = self.test_mngr_initr.test_config_info_mngr.sll.search(v[0])
                            #LogMsg("Feature Support = %s" % feat_supt)
                            if check_feat_flag == v[0]:
                                TestLogFileSource.log_file_source_obj_list[0].write_log_message("%s-%s"%(check_feat_flag, v[1]), TestLogFileSource.log_file_hdl_list[0])
                                if v[1] != "1":
                                    TestLogFileSource.log_file_source_obj_list[0].write_log_message("DUT does not support the feature", TestLogFileSource.log_file_hdl_list[0])
                                    self.test_mngr_initr.test_config_info_mngr.test_config_info.var_list.setdefault("TestNA", "DUT does not support the feature")

                            if v[1] == "0":
                                dis = "No"
                            elif v[1] == "1":
                                dis = "Yes"
                            else:
                                dis = v[1]
                            if "DUT_" not in v[0]:
                                T.rows.append([v[0], dis])
            html_code = str(T)
            TestLogFileSource.log_file_source_obj_list[3].write_log_message(html_code, TestLogFileSource.log_file_hdl_list[3])
            TestLogFileSource.log_file_source_obj_list[3].write_log_message('<p>', TestLogFileSource.log_file_hdl_list[3])
            TestLogFileSource.log_file_source_obj_list[3].close_log_file(TestLogFileSource.log_file_hdl_list[3])
            #fFile.write(html_code)
            #fFile.write('<p>')
