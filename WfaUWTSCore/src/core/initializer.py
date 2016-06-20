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
import re
from testinfo.testprogram import TestProgramManager
import testinfo.testbeddevice

from testinfo.datastream import DataStreamManager
from testinfo.testcase import TestCaseManager, TestCase
from testinfo.testfeature import TestProgramFeatureManager
from testinfo.testconfig import (TestConfigInfoManager, TestConfigInfo, Decorator_N, Decorator_TDLS, Decorator_HS2R2, Decorator_WFD, Decorator_P2P, Decorator_HS2,
                                            Decorator_WFDS, Decorator_WMMPS, Decorator_NAN, Decorator_VE, Decorator_PMF)

from core.configurator import TestConfigurator, TestConfigContext
from scriptinfo.scriptsource import TestFileManager
from core.configservice import TestConfigService
import common



class TestManagerInitializer(object):
    """The class that contains all class managers.

    Attributes:
        prog_name (str): The test program name.
        tc_name (str): The test case name.
        test_prog_mngr (object): The object of test program manager class.
        test_case_mngr (object): The object of test case manager class.
        testbed_dev_mngr (object): The object of testbed device manager class.
        test_feat_mngr (object): The object of test feature manager class.
        test_data_strm_mngr (object): The object of test data stream manager class.
        test_config_info_mngr (object): The object of test config info manager class.
        test_script_mngr (object): The object of test script manager class.
        test_config_cxt (object): The object of test config context class.
        test_configurator (object): The object of test configurator class.
        test_config_service (object): The object of test config service class.
        test_config_info_class_list (list): The test config infor class list.
        testbed_dev_file_dict (dictionary): The testbed device file dictionary.

    """
    def __init__(self, prog_name, tc_name):
        self.prog_name = prog_name
        self.tc_name = tc_name

        self.test_prog_mngr = None
        self.test_case_mngr = None
        self.testbed_dev_mngr = None
        self.test_feat_mngr = None
        self.test_data_strm_mngr = None
        self.test_config_info_mngr = None
        self.test_config_info_class_list = [Decorator_N, Decorator_TDLS, Decorator_HS2R2, Decorator_WFD, Decorator_P2P, Decorator_HS2,
                                            Decorator_WFDS, Decorator_WMMPS, Decorator_NAN, Decorator_VE, Decorator_PMF]

        self.test_script_mngr = None
        self.test_config_cxt = None
        self.test_configurator = None
        self.test_config_service = None

        self.testbed_dev_file_dict = {
            "N": [common.GlobalConfigFiles.testbed_ap_names, common.GlobalConfigFiles.testbed_sta_names, common.GlobalConfigFiles.radius_server_names],
            "VHT": [common.GlobalConfigFiles.testbed_ap_names, common.GlobalConfigFiles.testbed_sta_names, common.GlobalConfigFiles.radius_server_names],
            "P2P": [common.GlobalConfigFiles.testbed_sta_names, common.GlobalConfigFiles.testbed_ap_names],
            "PMF": [common.GlobalConfigFiles.testbed_ap_names, common.GlobalConfigFiles.testbed_sta_names, common.GlobalConfigFiles.radius_server_names],
            "WFD": [common.GlobalConfigFiles.testbed_sta_names, common.GlobalConfigFiles.testbed_ap_names],
            "WFDS": [common.GlobalConfigFiles.testbed_sta_names],
            "WMMPS": [common.GlobalConfigFiles.testbed_ap_names, common.GlobalConfigFiles.testbed_sta_names],
            "HS2-R2": [common.GlobalConfigFiles.testbed_ap_names, common.GlobalConfigFiles.testbed_sta_names, common.GlobalConfigFiles.radius_server_names, common.GlobalConfigFiles.osu_server_names],
            "NAN": [common.GlobalConfigFiles.testbed_sta_names],
            "TDLS": [common.GlobalConfigFiles.testbed_ap_names, common.GlobalConfigFiles.testbed_sta_names],
            "Voice-Ent": [common.GlobalConfigFiles.testbed_ap_names, common.GlobalConfigFiles.testbed_sta_names, common.GlobalConfigFiles.radius_server_names],
            "AC-11AG": [common.GlobalConfigFiles.testbed_sta_names],
            "AC-11B": [common.GlobalConfigFiles.testbed_sta_names],
            "AC-11N": [common.GlobalConfigFiles.testbed_sta_names]
            }


    def init_test_manager(self):
        """Initializes the various class managers.
        """
        found_decorator = False
        self.test_prog_mngr = TestProgramManager(self.prog_name)
        self.test_prog_mngr.test_prog.set_prog_info()

        self.testbed_dev_mngr = testinfo.testbeddevice.TestbedDeviceManager(self.prog_name)
        self.test_feat_mngr = TestProgramFeatureManager(self.prog_name)

        self.test_data_strm_mngr = DataStreamManager()

        test_config_info = TestConfigInfo()
        # search class name in test_config_info_class_list and initialize it if some class is found
        for index, test_config_info_cls in enumerate(self.test_config_info_class_list):
            if test_config_info_cls.__name__.find(self.prog_name.replace("-", "")) >= 0:
                found_decorator = True
                test_config_info_cls = self.test_config_info_class_list[index]()
                self.test_config_info_mngr = TestConfigInfoManager(test_config_info, test_config_info_cls)
                break
        if not found_decorator:
            self.test_config_info_mngr = TestConfigInfoManager(test_config_info)
        test_config_info.test_config_info_mngr = self.test_config_info_mngr

        self.test_case_mngr = TestCaseManager()

        # assume tc_name is the same as fileName at this point
        self.test_script_mngr = TestFileManager(self.prog_name)
        self.test_script_mngr.get_script_folder_info(common.GlobalConfigFiles.uwts_ucc_file)

        if self.test_config_cxt.is_testcase_ignored: return

        self.test_script_mngr.get_real_test_case_file(self.tc_name)


    def init_test_case(self):
        """Initializes the test case object of TestCase class.
        """
        self.test_case_mngr.test_case = TestCase(self.prog_name, self.test_script_mngr.test_case_file)
        self.test_case_mngr.test_case.tc_id = self.tc_name
        for tc in self.test_prog_mngr.test_prog.tc_list:
            if tc.tc_name == self.test_script_mngr.test_case_file:
                self.test_case_mngr.test_case.tc_type = tc.tc_type
                break


    def init_test_config_context(self, usr_in_cmd):
        """Initializes the test config context object based on the user input command parameter.

        Args:
            usr_in_cmd (object): The object of UserCommand class.
        """
        self.test_config_cxt = TestConfigContext()
        self.test_config_cxt.user_mode = usr_in_cmd.user_mode
        self.test_config_cxt.is_group_run_set = usr_in_cmd.is_group_run
        self.test_config_cxt.group_file_name = usr_in_cmd.group_file_name
        self.test_config_cxt.is_testbed_validation_set = usr_in_cmd.is_testbed_val
        self.test_config_cxt.is_testcase_validation_set = usr_in_cmd.is_testcase_val
        if usr_in_cmd.is_testbed_val and usr_in_cmd.test_case_id == "":
            self.test_config_cxt.is_testcase_ignored = True

        self.test_configurator = TestConfigurator(self.prog_name, self.tc_name, self.test_config_cxt)
        self.test_config_service = TestConfigService()


    def init_testbed_device(self):
        """Initializes the lists of testbed device and test case of the underlying program.
        """
        testbed_names_file_path_list = []

        if self.prog_name in self.testbed_dev_file_dict:
            for fp in self.testbed_dev_file_dict[self.prog_name]:
                testbed_names_file_path_list.append(self.test_script_mngr.prog_script_folder_path + "\\" + fp)

        for testbed_name_file in testbed_names_file_path_list:
            if os.path.exists(testbed_name_file):
                tbd_file = open(testbed_name_file, 'r')
                for item in tbd_file.readlines():
                    if item == '':
                        continue
                    tbd_name = item.rstrip("\n")
                    tbd_type = ""
                    if re.search(common.GlobalConfigFiles.testbed_ap_names, testbed_name_file):
                        tbd_type = "AP"
                    elif re.search(common.GlobalConfigFiles.testbed_sta_names, testbed_name_file):
                        tbd_type = "STA"
                    elif re.search(common.GlobalConfigFiles.radius_server_names, testbed_name_file):
                        tbd_type = "RADIUSSERVER"
                    elif re.search(common.GlobalConfigFiles.osu_server_names, testbed_name_file):
                        tbd_type = "OSUSERVER"

                    testbed_device = self.testbed_dev_mngr.create_testbed_device_instance(tbd_name, tbd_type)
                    testbed_device.prog_name = self.prog_name
                    self.test_prog_mngr.test_prog.testbed_dev_list.append(testbed_device)
                if tbd_file:
                    tbd_file.close()
            else:
                raise OSError(testbed_name_file + " not exists")

        if self.test_config_cxt.is_testcase_ignored: return

        test_list_file = common.GlobalConfigFiles.config_root + self.test_script_mngr.prog_script_list_file
        tc_info_dict = self.test_script_mngr.get_test_case_id_type(test_list_file)
        for tc_id in tc_info_dict:
            test_case = TestCase(self.prog_name, (tc_info_dict[tc_id])[0])
            test_case.tc_id = tc_id
            test_case.tc_type = (tc_info_dict[tc_id])[1]
            self.test_prog_mngr.test_prog.tc_list.append(test_case)
