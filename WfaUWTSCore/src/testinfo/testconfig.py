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
﻿import re
import logging
import common
from core.symtable import TestScriptSymbolTable
from scriptinfo.scriptelement import TestScriptElementType
from scriptinfo.scriptsource import TestLogFileSource


class TestConfigInfoManager:
    """The class that manages test config info.

    Attributes:
        sll (str): The object of SinglyLinkedList class.
        test_config_info (object): The object of TestConfigInfo class.
        test_mngr_initr (object): The object of TestManagerInitializer class.
        decorator (object): The object of Decorator class.
        test_config_func_dict (dictionary): The callback function dictionary.

    """
    def __init__(self, test_config_info, decorator_prog=None):
        self.sll = None
        self.test_config_info = test_config_info
        self.test_mngr_initr = None

        if decorator_prog == None:
            self.decorator = Decorator()
        else:
            self.decorator = decorator_prog
        self.decorator.set_component(test_config_info)

        self.test_config_func_dict = {
            TestConfigInfo.SSID: self.test_config_info.set_test_config_info_SSID,
            TestConfigInfo.CHANNEL: self.test_config_info.set_test_config_info_CHANNEL,
            TestConfigInfo.BAND: self.test_config_info.set_test_config_info_BAND,
            TestConfigInfo.AP: self.test_config_info.set_test_config_info_AP,
            TestConfigInfo.STA: self.decorator.set_test_config_info_STA,
            TestConfigInfo.DUTFILE: self.decorator.set_test_config_info_DUTFILE,
            TestConfigInfo.TESTBEDFILE: self.test_config_info.set_test_config_info_TESTBEDFILE,
            TestConfigInfo.STAFILE: self.test_config_info.set_test_config_info_STAFILE,
            TestConfigInfo.SERVER: self.test_config_info.set_test_config_info_SERVER,
            TestConfigInfo.SUPPLICANT: self.test_config_info.set_test_config_info_SUPPLICANT,
            TestConfigInfo.APCHANNELWIDTH: self.test_config_info.set_test_config_info_APCHANNELWIDTH,
            TestConfigInfo.OPERATINGCHANNEL: self.decorator.set_test_config_info_OPERATINGCHANNEL,
            TestConfigInfo.SERVICEPREF: self.test_config_info.set_test_config_info_SERVICEPREF,
            TestConfigInfo.LISTENCHANNEL: self.test_config_info.set_test_config_info_LISTENCHANNEL,
            TestConfigInfo.INTENTVALUE_DUT: self.test_config_info.set_test_config_info_INTENTVALUE_DUT,
            TestConfigInfo.INTENTVALUE_STA: self.test_config_info.set_test_config_info_INTENTVALUE_STA,
            TestConfigInfo.WPSCONFIG: self.test_config_info.set_test_config_info_WPSCONFIG,
            TestConfigInfo.SUBSRIPTSERVER: self.test_config_info.set_test_config_info_SUBSRIPTSERVER,
            TestConfigInfo.WLANTESTFILE: self.test_config_info.set_test_config_info_WLANTESTFILE,
            TestConfigInfo.SECURITY: self.test_config_info.set_test_config_info_SECURITY,
            TestConfigInfo.PMFCAPABILITY: self.test_config_info.set_test_config_info_PMFCAPABILITY,
            #TestConfigInfo.QUALCOMBINATIONINFO: self.test_config_info.set_test_config_info_QUALCOMBINATIONINFO,
            TestConfigInfo.PERSISTENT: self.test_config_info.set_test_config_info_PERSISTENT,
            TestConfigInfo.SERDISC: self.test_config_info.set_test_config_info_SERDISC,
            TestConfigInfo.THROUGHPUTS: self.test_config_info.set_test_config_info_THROUGHPUTS,
            TestConfigInfo.THROUGHPUTASD: self.test_config_info.set_test_config_info_THROUGHPUTASD,
            TestConfigInfo.WMMSTREAM_THRESHOLD: self.test_config_info.set_test_config_info_WMMSTREAM_THRESHOLD,
            # to do: need to check if the test case is optinal by looking at CheckFlag11n element
            # for VHT, it is checkFeatureFlag
            TestConfigInfo.CHECKFLAG11N: self.test_config_info.set_test_config_info_CHECKFLAG11N
            }


    def exec_callback_func(self, keyword, func_param):
        """Executes the callback function based on the passed-in key.

        Attributes:
            keyword (str): The key of test_config_func_dict.
            func_param (str): The parameter string of the funciton to be invoked.
        """
        ##print keyWord
        if keyword in self.test_config_func_dict:
            self.test_config_func_dict[keyword](func_param)


    def set_test_config_info(self):
        """Sets the test config info.
        """
        curr_node = self.sll.head
        while curr_node is not None:
            # curr_node.data is a dictionary
            for key in curr_node.data:
                self.exec_callback_func(key, curr_node.data[key])
                break
            curr_node = curr_node.next
        #end of while loop
        
        self.test_config_info.set_other_varlist_values()
        self.decorator.set_other_varlist_values()



class TestConfigInfo:
    """The summary line for a class docstring should fit on one line.

    Attributes:
        attr1 (str): Description of `attr1`.
        attr2 (Optional[int]): Description of `attr2`.

    """
    SSID = "SSID"
    BAND = "Band"
    CHANNEL = "Channel"
    AP = "AP"
    STA = "STA"
    DUTFILE = "DUTFile"
    TESTBEDFILE = "TestbedFile"
    STAFILE = "STAFile"
    SUPPLICANT = "Supplicant"
    SERVER = "Server"

    THROUGHPUTS = "Throughputs"
    THROUGHPUTASD = "Throughputs_ASD"

    HTFLAG = "HTFlag"
    STA_LEGACY = "STA_LEGACY"
    CHECKFLAG11N = "CheckFlag11n"
    WMMFLAG = "WMMFlag"

    APCHANNELWIDTH = "APChannelWidth"

    CONDITIONALSTEP_DISCREQ = "ConditionalStep-DiscReq"
    CONDITIONALSTEP_PUSLEEP = "ConditionalStep-PUSleep"
    CONDITIONALSTEP_AONLY40 = "ConditionalStep-Aonly-40"
    CONDITIONALSTEP_2SS = "ConditionalStep-2SS"
    CONDITIONALSTEP_3SS = "ConditionalStep-3SS"
    TX_SS = "TX-SS"
    RX_SS = "RX-SS"
    STA_FRAG = "STA_Frag"
    STA_LEGACY_PS = "STA_Legacy_PS"
    STA2_LEGACY_PS = "STA2_Legacy_PS"
    OFFCH = "Offch"
    OFFCHWIDTH = "Offchwidth"
    DUTSUPPORTEDCW = "DUTSupportedCW"
    WMMSTREAM_THRESHOLD = "WMMStreamThreshold"
    SECURITY = "Security"
    PMFCAPABILITY = "PMFCapability"
    SENDER = "sender"
    WFA_TESTER = "WFA_Tester"
    TBAPCONFIGSERVER = "TBAPConfigServer"
    WFA_SNIFFER = "WFA_Sniffer"
    WFA_TEST_CONTROL_AGENT = "WFA_TEST_control_agent"

    #QUALCOMBINATIONINFO = "QualCombinationInfo"
    PERSISTENT = "PERSISTENT"
    SERDISC = "SERDISC"

    OPERATINGCHANNEL = "OperatingChannel"
    SERVICEPREF = "ServicePref"
    LISTENCHANNEL = "ListenChannel"
    INTENTVALUE_DUT = "IntentValue_DUT"
    INTENTVALUE_STA = "IntentValue_STA"
    WPSCONFIG = "WPS_Config"

    SUBSRIPTSERVER = "SubscriptionServer"
    WLANTESTFILE = "WLanTestFile"

    band_mapping_dict = {
        'A/G': "AG",
        'A/G/N': "AGN",
        'G/N': "GN",
        'A/N': "AN",
        'A/B': "AB",
        'A/C': "AC"
        }

    default_band_select_dict = {
        # DUT Mode BG
        "A:BG": "11g",
        "B:BG": "11g",
        "G:BG": "11g",
        "AG:BG": "11g",
        "AB:BG": "11g",

        # DUT Mode A only
        "A:A": "11a",
        "B:A": "11a",
        "G:A": "11a",
        "AG:A": "11a",
        "AB:A": "11a",

        # DUT Mode ABG
        "A:ABG": "11a",
        "B:ABG": "11b",
        "G:ABG": "11g",
        "AG:ABG": "11a",
        "AB:ABG": "11a",

        # DUT Mode b only
        "A:B": "11g",
        "B:B": "11b",
        "G:B": "11g",
        "AG:B": "11g",
        "AB:B": "11b",

        # DUT Mode G only
        "A:G": "11g",
        "B:G": "11g",
        "G:G": "11g",
        "AG:G": "11g",
        "AB:G": "11b",

        # DUT mode A and b only
        "A:AB": "11a",
        "B:AB": "11b",
        "G:AB": "11b",
        "AG:AB": "11b",
        "AB:AB": "11a",

        # DUT mode ABGN
        "A:ABGN": "11a",
        "B:ABGN": "11b",
        "G:ABGN": "11g",
        "AG:ABGN": "11a",
        "AB:ABGN": "11a",
        "AGN:ABGN": "11na",
        "AN:ABGN": "11na",
        "GN:ABGN": "11ng",

        # DUT mode GN
        "A:GN": "11g",
        "B:GN": "11b",
        "G:GN": "11g",
        "AG:GN": "11g",
        "AB:GN": "11b",
        "AGN:GN": "11ng",
        "AN:GN": "11ng",
        "GN:GN": "11ng",

        # DUT mode AN
        "A:AN": "11a",
        "B:AN": "11a",
        "G:AN": "11a",
        "AG:AN": "11a",
        "AB:AN": "11a",
        "AGN:AN": "11na",
        "AN:AN": "11na",
        "GN:AN": "11na",
        "AGN:ABG": "11a",
        "AGN:BG": "11g",
        "AGN:B": "11b",
        "AN:ABG": "11a",
        "AN:BG": "11g",
        "AN:B": "11b",
        "GN:ABG": "11g",
        "GN:BG": "11g",
        "GN:B": "11b",

        # DUT mode AC
        "A:AC": "11a",
        "AN:AC": "11na",
        "AC:AC": "11ac",
        "B:BGNAC": "11b",
        "BG:BGNAC": "11g",
        "BGN:BGNAC": "11ng"
        }


    def __init__(self):
        self.band = ""
        self.ssid = {}
        self.channel = {}

        self.dut_config_file = ""
        self.sta_config_file = ""
        self.testbed_dev_config_file = ""
        self.wlan_test_capi_file = ""
        self.test_progFeatureList = []
        self.testThroughput = None

        self.ap_channel_width = ""
        self.var_list = {}
        self.test_config_info_mngr = None


    def set_value_to_var_list(self, var_name, val_default, set_flag=True):
        """Sets the variable values ot he var_list dictionary.

        Attributes:
            var_name (str): The variable name.
            val_default (str): The variable's default value.
            set_flag (boolean): The flag for setting the default or non-default value.
        """
        cond = self.test_config_info_mngr.sll.search(var_name)
        if cond is not None:
            self.var_list.setdefault(var_name, cond.data[var_name])
        else:
            if set_flag:
                self.var_list.setdefault(var_name, val_default)


    def set_other_varlist_values(self):
        """Sets the variable values to the var_list dictionary.
        """
        self.set_value_to_var_list(self.TX_SS, "", False)        
        self.set_value_to_var_list(self.RX_SS, "", False)        

        self.set_value_to_var_list(self.STA_FRAG, "2346", True)      

        self.set_value_to_var_list(self.STA_LEGACY_PS, "off", True)        

        self.set_value_to_var_list(self.STA2_LEGACY_PS, "off", True)        

        self.set_value_to_var_list(self.HTFLAG, "off", True)        

        self.set_value_to_var_list(self.WMMFLAG, "off", True)


    def set_test_config_info_WMMSTREAM_THRESHOLD(self, tp_tag):
        TestLogFileSource.log_file_source_obj_list[0].write_log_message("\n|\n|\n| Searching WMM Stream Thrshold values for TestID %s" % (common.GlobalConfigFiles.curr_tc_name), TestLogFileSource.log_file_hdl_list[0])
        if tp_tag.strip() == "":
            tp_tag = TestConfigInfo.WMMSTREAM_THRESHOLD
            
        nextNode = self.test_config_info_mngr.sll.get_next_node(tp_tag)
        if nextNode is not None:
            key = nextNode.data.keys()[0]
            length = len(key)
            count = self.test_config_info_mngr.sll.get_num_nodes_with_keyword(tp_tag, key[:(length-1)])
            for num in range(0, len(count)):
                list_item = self.test_config_info_mngr.sll.search_node_by_parent(tp_tag, count[num])
                if list_item is not None:
                    result = list_item.data[count[num]]
                    self.var_list.setdefault(count[num], result)
                    TestLogFileSource.log_file_source_obj_list[0].write_log_message("\n|\n|\n| Found WMM Throughput values -%s-" % (result), TestLogFileSource.log_file_hdl_list[0])


    def set_test_config_info_THROUGHPUTS(self, tp_tag):
        """Sets the test config info for throughput.

        Attributes:
            tp_tag (str): The throughput info.
        """
        tag1 = ""
        result = ""
        TestLogFileSource.log_file_source_obj_list[0].write_log_message("\n|\n|\n| Searching Throughput values for TestID %s" % (common.GlobalConfigFiles.curr_tc_name), TestLogFileSource.log_file_hdl_list[0])

        bnd = self.band
        if bnd == "11a" or bnd == "11na":
            tag1 = "A"
        elif bnd == "11g" or bnd == "11ng":
            tag1 = "G"
        elif bnd == "11b":
            tag1 = "B"
        elif bnd == "11ac":
            tag1 = "AC"

        TestLogFileSource.log_file_source_obj_list[0].write_log_message("Test Running in band -%s-%s- " % (bnd, tag1), TestLogFileSource.log_file_hdl_list[0])
        nextNode = self.test_config_info_mngr.sll.get_next_node(tag1)
        if nextNode is not None:
            key = nextNode.data.keys()[0]
            length = len(key)
            count = self.test_config_info_mngr.sll.get_num_nodes_with_keyword(tag1, key[:(length-1)])            
            for num in range(0, len(count)):                
                list_item = self.test_config_info_mngr.sll.search_node_by_parent(tag1, count[num])

                if list_item is not None:                    
                    result = list_item.data[count[num]]                    
                    self.var_list.setdefault(count[num], result)
                    TestLogFileSource.log_file_source_obj_list[0].write_log_message("\n|\n|\n| Found Throughput values -%s-" % (result), TestLogFileSource.log_file_hdl_list[0])
        
        secNextNode = self.test_config_info_mngr.sll.get_next_node(count[len(count)-1])
        if secNextNode.data.values()[0] != "" and secNextNode is not None:
            key = secNextNode.data.keys()[0]
            length = len(key)
            count1 = self.test_config_info_mngr.sll.get_num_nodes_with_keyword(tag1, key[:(length-1)])            
            for num in range(0, len(count1)):                
                list_item = self.test_config_info_mngr.sll.search_node_by_parent(tag1, count1[num])

                if list_item is not None:                    
                    result1 = list_item.data[count1[num]]                    
                    self.var_list.setdefault(count1[num], result1)
                    TestLogFileSource.log_file_source_obj_list[0].write_log_message("\n|\n|\n| Found Throughput values -%s-" % (result1), TestLogFileSource.log_file_hdl_list[0])


    def set_test_config_info_THROUGHPUTASD(self, tp_tag):
        """Sets the test config info for throughput asd.

        Attributes:
            tp_tag (str): The throughput asd value.
        """
        asd_type = self.test_config_info_mngr.test_mngr_initr.test_feat_mngr.get_feat_obj_val_by_name(TestScriptElementType.get_test_feat_key_from_val(TestScriptElementType.ASD))
        tag1 = ""
        if int(asd_type) > 0:
            TestLogFileSource.log_file_source_obj_list[0].write_log_message("\n|\n|\n| Searching ASD Throughput values for TestID %s" % (common.GlobalConfigFiles.curr_tc_name), TestLogFileSource.log_file_hdl_list[0])

            if asd_type == "1":
                tag1 = "Handsets"
            elif asd_type == "2":
                tag1 = "TV"
            elif asd_type == "3":
                tag1 = "Printer"
            elif asd_type == "4":
                tag1 = "SetTopBox"
            elif asd_type == "5":
                tag1 = "MobileAP"

            TestLogFileSource.log_file_source_obj_list[0].write_log_message("Test Running ASD -%s-%s- " % (asd_type, tag1), TestLogFileSource.log_file_hdl_list[0])

            nextNode = self.test_config_info_mngr.sll.get_next_node(tag1)
            if nextNode is not None:
                key = nextNode.data.keys()[0]
                length = len(key)
                count = self.test_config_info_mngr.sll.get_num_nodes_with_keyword(tag1, key[:(length-1)])
                for num in range(0, len(count)):
                    list_item = self.test_config_info_mngr.sll.search_node_by_parent(tag1, count[num])
                    if list_item is not None:
                        ASDkey = "FrameRate_" + count[num]
                        ASDframerate = self.get_ASD_framerate(list_item.data[count[num]])
                        self.var_list.setdefault(ASDkey, ASDframerate)
                        TestLogFileSource.log_file_source_obj_list[0].write_log_message("\n|\n|\n| Found Throughput values -%s-" % (ASDframerate), TestLogFileSource.log_file_hdl_list[0])
            
            secNextNode = self.test_config_info_mngr.sll.get_next_node(count[len(count)-1])
            if secNextNode.data.values()[0] != "" and secNextNode is not None:
                key = secNextNode.data.keys()[0]
                length = len(key)
                count1 = self.test_config_info_mngr.sll.get_num_nodes_with_keyword(tag1, key[:(length-1)])            
                for num in range(0, len(count1)):                
                    list_item = self.test_config_info_mngr.sll.search_node_by_parent(tag1, count1[num])
    
                    if list_item is not None:                    
                        result1 = list_item.data[count1[num]]                    
                        self.var_list.setdefault(count1[num], result1)
                        TestLogFileSource.log_file_source_obj_list[0].write_log_message("\n|\n|\n| Found Throughput values -%s-" % (result1), TestLogFileSource.log_file_hdl_list[0])


    def get_ASD_framerate(self, ASD_value):
        """Calculates the frame rate based on the passed-in asd value.

        Attributes:
            ASD_value (str): The asd value.
        """
        # The expected traffic is about 30% more than the expected throughput value
        offset = 0.3
        # payload value is 1000, which is hard-coded in the script
        ASD_framerate = ((float(ASD_value) * (1+offset) * 1000000) / (1000 * 8))
        ASD_framerate = "{:.2f}".format(ASD_framerate)
        return ASD_framerate


    def set_test_config_info_PERSISTENT(self, persist_val):
        """Sets the test config info for persistent.

        Attributes:
            persist_val (str): The persistent info.
        """
        if persist_val != "":
            self.var_list.setdefault("PERSISTENT", persist_val)
        else:
            self.var_list.setdefault("PERSISTENT", 0)


    def set_test_config_info_SERDISC(self, ser_disc_val):
        """Sets the test config info for serdisc.

        Attributes:
            ser_disc_val (str): The serdisc info.
        """
        if ser_disc_val != "":
            self.var_list.setdefault("SERDISC", ser_disc_val)
        else:
            self.var_list.setdefault("SERDISC", 0)


    #def set_test_config_info_QUALCOMBINATIONINFO(self, value):
    #    combo = self.test_config_info_mngr.sll.search("QualCombinationInfo")
    #    if combo is not None and combo != "":
    #        result = combo.data["QualCombinationInfo"]
    #        TestLogFileSource.log_file_source_obj_list[0].write_log_message("Combination Info = %s" % combo, TestLogFileSource.log_file_hdl_list[0])
    #        self.var_list.setdefault("QualCombinationInfo", result)


    def set_test_config_info_PMFCAPABILITY(self, pmf_cap):
        """Sets the values of DUT_PMFCap and PMFCap* elements under PMFCapability in MasterTestInfo.xml in PMF program
        """
        list_item = self.test_config_info_mngr.sll.search_node_by_parent("PMFCapability", "DUT_PMFCap")
        if list_item is not None:
            result = list_item.data["DUT_PMFCap"]
            self.var_list.setdefault("DUT_PMFCap", result)

        for num in range(1, 3):
            list_item = self.test_config_info_mngr.sll.search_node_by_parent("PMFCapability", "PMFCap" + str(num))
           
            if list_item is not None:
                result = list_item.data["PMFCap" + str(num)]
                self.var_list.setdefault("PMFCap" + str(num), result)
                TestLogFileSource.log_file_source_obj_list[0].write_log_message("------------Testbed PMF Cap3= %s" % result, TestLogFileSource.log_file_hdl_list[0])


    def set_test_config_info_SECURITY(self, security):
        """Sets the test config info for security.

        Args:
            security (str): The security info.

        """
        dut_type = self.test_config_info_mngr.test_mngr_initr.test_feat_mngr.get_feat_obj_val_by_name(TestScriptElementType.get_test_feat_key_from_val(TestScriptElementType.DUT_TYPE))
        security = TestConfigInfo.SECURITY if security.strip() == "" else security
        list_item = self.test_config_info_mngr.sll.search_node_by_parent(security, "KeyMgmt")
        if list_item is not None:
            result = list_item.data["KeyMgmt"]
        else:
            raise common.TestConfigError("Security/KeyMgmt search returns None")

        if result == "WFA-Ent":
            if dut_type == "WPA2-Personal":
                self.var_list.setdefault("Keymgnt", "%s" % ("WPA2-PSK"))
                self.var_list.setdefault("keymgmttpye", "%s" % ("WPA2"))
            if dut_type == "WPA2-Enterprise":
                self.var_list.setdefault("Keymgnt", result)
                self.var_list.setdefault("keymgmttpye", "%s" % ("WPA2"))
        else:
            self.var_list.setdefault("Keymgnt", "%s-%s" % (result, "PSK"))
            self.var_list.setdefault("keymgmttpye", result)

        list_item = self.test_config_info_mngr.sll.search_node_by_parent(security, "Encryption")
        TestLogFileSource.log_file_source_obj_list[0].write_log_message("------------Security Info= %s" % result, TestLogFileSource.log_file_hdl_list[0])

        if list_item is not None:
            result = list_item.data["Encryption"]
            self.var_list.setdefault("encpType", result)

        list_item = self.test_config_info_mngr.sll.search_node_by_parent(security, "Passphrase")
        TestLogFileSource.log_file_source_obj_list[0].write_log_message("------------Security Info= %s" % result, TestLogFileSource.log_file_hdl_list[0])

        if list_item is not None:
            result = list_item.data["Passphrase"]
            self.var_list.setdefault("passphrase", result)

        TestLogFileSource.log_file_source_obj_list[0].write_log_message("\n|\n|\n| Found Security Info", TestLogFileSource.log_file_hdl_list[0])


    def set_test_config_info_WLANTESTFILE(self, wlan_test_file):
        """Sets the test config info for wlantest file.

        Args:
            wlan_test_file (str): The wlan test file info.

        """
        wlan_test_file = TestConfigInfo.WLANTESTFILE if wlan_test_file.strip() == "" else wlan_test_file
        list_item = self.test_config_info_mngr.sll.search_node_by_parent(wlan_test_file, "_Value")
        if list_item is not None:
            wlan_test_file = list_item.data["_Value"]
        else:
            raise common.TestConfigError("WLanTestFile/_Value search returns None")
        self.wlan_test_capi_file = wlan_test_file


    def set_test_config_info_SUBSRIPTSERVER(self, sub_svr):
        """Sets thet test config info for subscript server.

        Args:
            sub_svr (str): The subscript server.
        """
        eap_name = TestScriptSymbolTable.get_value_from_sym_tab(TestScriptElementType.DUTEAPMETHOD, TestScriptSymbolTable.test_script_sym_tab)
        tls_name = TestScriptElementType.get_test_feat_key_from_val(TestScriptElementType.TLS)

        eap_val = self.test_config_info_mngr.test_mngr_initr.test_feat_mngr.get_feat_obj_val_by_name(eap_name)
        if eap_val is not None and eap_val == tls_name:
            tag = tls_name
        else:
            tag = "Other"

        iCount = 1
        sub_server_name = self.test_config_info_mngr.sll.search_node_by_parent("SubscriptionServer", tag)
        if sub_server_name is not None:
            self.var_list.setdefault("SS%s_control_agent" %(iCount), "wfa_control_agent_%s_osu" % (sub_server_name.data[tag].lower()))
            self.var_list.setdefault("SS%s" % (iCount), "%s" % (sub_server_name.data[tag].lower()))


    def set_test_config_info_WPSCONFIG(self, wps_config):
        """Sets the test config info for wps config.

        Args:
            wps_config (str): The wps config info.
        """
        result = ""
        wps_config_list = ["WPS_Keypad", "WPS_Display", "WPS_PushButton", "WPS_Label"]
        listitem = self.test_config_info_mngr.sll.search("WPS_Config")
        if listitem is not None:
            result = listitem.data["WPS_Config"]
            if result != "":
                wps_type = self.test_config_info_mngr.test_mngr_initr.test_feat_mngr.get_feat_obj_val_by_name(wps_config)
                if wps_type is not None and int(wps_type) != 1:
                    for m in wps_config_list:
                        wps_type1 = self.test_config_info_mngr.test_mngr_initr.test_feat_mngr.get_feat_obj_val_by_name(m)
                        if wps_type1 is not None and int(wps_type1) == 1:
                            result = m
                            break
                else:
                    result = wps_config
            self.var_list.setdefault("DUT_WPS_METHOD", result)


    def set_test_config_info_INTENTVALUE_STA(self, inte_val_sta):
        """Sets the test config info for intent value of sta.

        Args:
            inte_val_sta (str): The intented value info.
        """
        self.var_list.setdefault("INTENT_VAL_STA", inte_val_sta)


    def set_test_config_info_INTENTVALUE_DUT(self, inte_val_dut):
        """Sets the test config info for intent value of dut.

        Args:
            inte_val_dut (str): The intent value info.
        """
        self.var_list.setdefault("INTENT_VAL_DUT", inte_val_dut)


    def set_test_config_info_LISTENCHANNEL(self, lstn_chnl):
        """Sets the test config info for listening channel.

        Args:
            lstn_chnl (str): The listening channel.
        """
        self.var_list.setdefault("LISTEN_CHN", lstn_chnl)


    def set_test_config_info_SERVICEPREF(self, svr_pref):
        """Sets the test config info for service pref.

        Args:
            svr_pref (str): The service pref info.
        """
        self.var_list.setdefault("WfdsTestServicePref", svr_pref)


    def set_test_config_info_OPERATINGCHANNEL(self, oper_chnl):
        """Sets the test config info for operating channel.

        Args:
            oper_chnl (str): The operating channel info.
        """
        self.var_list.setdefault("OPER_CHN", oper_chnl)


    def set_test_config_info_APCHANNELWIDTH(self, ap_chnl_width):
        """Sets the test config info for ap channel width.

        Args:
            ap_chnl_width (str): The ap channel width info.
        """
        self.ap_channel_width = ap_chnl_width
        self.var_list.setdefault("APChannelWidth", self.ap_channel_width)


    def set_test_config_info_CHECKFLAG11N(self, opt_feat_11n):
        """Sets the test config info for checkflag11.

        Args:
            opt_feat_11n (str): The optional feature info of 11n.
        """
        self.test_config_info_mngr.test_mngr_initr.test_case_mngr.test_case.opt_test_feat = opt_feat_11n
        feat_val = self.test_config_info_mngr.test_mngr_initr.test_feat_mngr.get_feat_obj_val_by_name(opt_feat_11n)
        if feat_val is not None and feat_val == 0:
            logging.info("%s not supported by DUT; Skipping the Test. Re-Check the file \"DUTInfo.txt\"" % feat_val)


    def set_test_config_info_SUPPLICANT(self, supp_info):
        """Sets the test config info for supplicant.

        Args:
            supp_info (str): The supplicant info.
        """
        # add supplicant info to the testbed device list at test plan level even though there may be no radius server being used in the test case
        # therefore there is no radius server shown up in the testbed device list at test case level
        for tbd in self.test_config_info_mngr.test_mngr_initr.test_prog_mngr.test_prog.testbed_dev_list:
            if tbd.dev_type == "RADIUSSERVER":
                dut_category = self.test_config_info_mngr.test_mngr_initr.test_feat_mngr.get_feat_obj_val_by_name(TestScriptElementType.get_test_feat_key_from_val(TestScriptElementType.DUT_CATEGORY))
                list_item = self.test_config_info_mngr.sll.search_node_by_parent("DUT", dut_category)
                if list_item is not None:
                    tbd.supplicant = list_item.data[dut_category]
                list_item = self.test_config_info_mngr.sll.search_node_by_parent("STA", dut_category)
                if list_item is not None:
                    tbd.sta_supplicant = list_item.data[dut_category]


    def set_test_config_info_SERVER(self, rad_svr_info):
        """Sets the test config info server.

        Args:
            rad_svr_info (str): The radius server info.
        """
        eap_name = TestScriptSymbolTable.get_value_from_sym_tab(TestScriptElementType.DUTEAPMETHOD, TestScriptSymbolTable.test_script_sym_tab)
        tls_name = TestScriptElementType.get_test_feat_key_from_val(TestScriptElementType.TLS)
        # get DUTEAPMETHOD value from dutinfo.txt file parsing
        eap_val = self.test_config_info_mngr.test_mngr_initr.test_feat_mngr.get_feat_obj_val_by_name(eap_name)
        if eap_val is not None and eap_name == tls_name:
            tag = tls_name
        else:
            tag = "Other"
        server_name = self.test_config_info_mngr.sll.search_node_by_parent("Server", tag)
        if server_name is not None:
            TestScriptSymbolTable.insert_sym_tab("RadiusServerName", server_name.data[tag], TestScriptSymbolTable.test_script_sym_tab)
            self.var_list.setdefault("RadiusServerName", server_name.data[tag])
            # add the radius server device to the device list in TestCase class
            for tbd in self.test_config_info_mngr.test_mngr_initr.test_prog_mngr.test_prog.testbed_dev_list:
                if tbd.dev_type == "RADIUSSERVER" and tbd.dev_name == server_name.data[tag]:
                    #===========================================================
                    # dut_category = self.test_config_info_mngr.test_mngr_initr.test_feat_mngr.get_feat_obj_val_by_name(TestScriptElementType.get_test_feat_key_from_val(TestScriptElementType.DUT_CATEGORY))
                    # list_item = self.test_config_info_mngr.sll.search_node_by_parent("DUT", dut_category)
                    # if list_item is not None:
                    #     tbd.supplicant = list_item.data[dut_category]
                    # list_item = self.test_config_info_mngr.sll.search_node_by_parent("STA", dut_category)
                    # if list_item is not None:
                    #     tbd.sta_supplicant = list_item.data[dut_category]
                    #===========================================================
                    self.test_config_info_mngr.test_mngr_initr.test_case_mngr.test_case.testbed_device_list.append(tbd)
                    break


    def set_test_config_info_AllFiles(self, parent):
        """Sets the test config info for all files.

        Args:
            parent (str): The parent node key.
        """
        result = None

        list_item = self.test_config_info_mngr.sll.search_node_by_parent(parent, "_Value")
        if list_item is not None:            
            result = list_item.data["_Value"]
        else:
            dutType = self.test_config_info_mngr.test_mngr_initr.test_feat_mngr.get_feat_obj_val_by_name(TestScriptElementType.get_test_feat_key_from_val(TestScriptElementType.DUT_TYPE))

            if dutType == "WPA2-Personal":
                list_item = self.test_config_info_mngr.sll.search_node_by_parent(parent, "WPA2-Personal")
                if list_item is not None:
                    result = list_item.data["WPA2-Personal"]
                else:
                    raise common.TestConfigError("DUT Type (WPA2-Personal) value returns None")

            if dutType == "WPA2-Enterprise":
                eapMethod = TestScriptSymbolTable.get_value_from_sym_tab(TestScriptElementType.DUTEAPMETHOD, TestScriptSymbolTable.test_script_sym_tab)
                eapMethodVal = self.test_config_info_mngr.test_mngr_initr.test_feat_mngr.get_feat_obj_val_by_name(TestScriptElementType.get_test_feat_key_from_val(eapMethod))
                if int(eapMethodVal) == 0:
                    raise common.TestConfigError("The EAP method %s not supported in DUTInfo.txt" % eapMethod)

                main_node = self.test_config_info_mngr.sll.search(parent)

                if main_node.next.data.keys()[0] == dutType : 
                    parent_node = main_node.next.next
                elif main_node.next.next.data.keys()[0] == dutType :
                    parent_node = main_node.next.next.next

                curr_node = parent_node.next
                found = False
                while curr_node and found is False:
                    key_list = curr_node.data.keys()
                    key_count = len(key_list)
                    if key_count == 1 and key_list[0] == eapMethod:
                        found = True
                        break
                    else:
                        curr_node = curr_node.next

                if curr_node is not None:
                    result = curr_node.data[eapMethod]
                else:
                    raise common.TestConfigError("DUT Type (WPA2-Enterprise) value returns None")

        if result == "NA":
            dutType = self.test_config_info_mngr.test_mngr_initr.test_feat_mngr.get_feat_obj_val_by_name(TestScriptElementType.get_test_feat_key_from_val(TestScriptElementType.DUT_TYPE))
            TestLogFileSource.log_file_source_obj_list[0].write_log_message("\n The test %s is not applicable for DUT Type %s" % (common.GlobalConfigFiles.curr_tc_name, dutType), TestLogFileSource.log_file_hdl_list[0])
            raise common.TestConfigError("The test %s is not applicable for DUT Type %s" % (common.GlobalConfigFiles.curr_tc_name, dutType))

        return result


    def set_test_config_info_STAFILE(self, sta_file=""):
        """Sets the test config info for sta file.

        Args:
            sta_file (str): The sta file info.
        """
        self.sta_config_file = self.set_test_config_info_AllFiles(TestConfigInfo.STAFILE)


    def set_test_config_info_DUTFILE(self, dut_file=""):
        """Sets the test config info for dut file.

        Args:
            dut_file (str): The dut file info.
        """
        self.dut_config_file = self.set_test_config_info_AllFiles(TestConfigInfo.DUTFILE)
        self.var_list.setdefault("WTSMsg", "")


    def search_sll_by_keyword(self, parentkeyword, childkeyword):
        """Searches the sll for certain node given the parent and child node keys.

        Args:
            parentkeyword (str): The parent node key.
            childkeyword (str): The child node key.
        """
        list_item = self.test_config_info_mngr.sll.search_node_by_parent(parentkeyword, childkeyword)
        if list_item is not None:
            logging.debug(list_item.data[childkeyword])
            return list_item.data[childkeyword]
        return None


    def set_test_config_info_TESTBEDFILE(self, tbd_file=""):
        """Sets the test config infor for testbed file.

        Args:
            tbd_file (str): The testbed file info.
        """
        result = self.search_sll_by_keyword("TestbedFile", "_Value")
        if result is None:            
            dutType = self.test_config_info_mngr.test_mngr_initr.test_feat_mngr.get_feat_obj_val_by_name(TestScriptElementType.get_test_feat_key_from_val(TestScriptElementType.DUT_TYPE))
            result = self.search_sll_by_keyword("TestbedFile", dutType)

        if result == '0':
            result = ""

        if result is not None:
            self.testbed_dev_config_file = result

        if result == "NA":
            TestLogFileSource.log_file_source_obj_list[0].write_log_message("\n The test %s is not applicable for DUT Type %s" % (common.GlobalConfigFiles.curr_tc_name, dutType), TestLogFileSource.log_file_hdl_list[0])
            TestLogFileSource.log_file_source_obj_list[0].write_log_message("\n The test %s is not applicable for DUT Type %s" % (common.GlobalConfigFiles.curr_tc_name, dutType), TestLogFileSource.log_file_hdl_list[0])
            raise common.TestConfigError("The test %s is not applicable for DUT Type %s" % (common.GlobalConfigFiles.curr_tc_name, dutType))
            self.var_list.setdefault("TestNA", "The test %s is not applicable for DUT Type %s" % (common.GlobalConfigFiles.curr_tc_name, dutType))


    def set_test_config_info_SSID(self, ssid):
        """Sets the test config info for ssid.

        Args:
            ssid (str): The ssid info.
        """
        self.ssid["SSID"] = ssid

        iCount = 1
        SSIDs = ssid.split(" ")
        for SSID in SSIDs:
            if len(SSIDs) > 1:
                self.ssid["SSID_%s"%(iCount)] = SSID
                iCount = iCount + 1


    def set_test_config_info_BAND(self, band_info):
        """Sets the test config info for band.

        Args:
            band_info (str): The band info.
        """
        if band_info in TestConfigInfo.band_mapping_dict:
            bandsel = TestConfigInfo.band_mapping_dict[band_info]
        else:
            bandsel = band_info
        dut_band = self.test_config_info_mngr.test_mngr_initr.test_feat_mngr.get_feat_obj_val_by_name(TestScriptElementType.get_test_feat_key_from_val(TestScriptElementType.DUT_BAND))

        try:
            self.band = TestConfigInfo.default_band_select_dict["%s:%s" % (bandsel, dut_band)]
        except KeyError:
            TestLogFileSource.log_file_source_obj_list[0].write_log_message("Invalid band information %s" % bandsel, TestLogFileSource.log_file_hdl_list[0])
            raise KeyError("Invalid band information %s" % bandsel)


    def set_test_config_info_CHANNEL(self, chan_info):
        """Sets the test config info for channel.

        Args:
            chan_info (str): The channel info.
        """
        dut_band = self.test_config_info_mngr.test_mngr_initr.test_feat_mngr.get_feat_obj_val_by_name(TestScriptElementType.get_test_feat_key_from_val(TestScriptElementType.DUT_BAND))
        
        band = -1
        testChannel = []
        channelList = []

        list_item = self.test_config_info_mngr.sll.search("Band")
        if list_item is not None:
            self.set_test_config_info_BAND(list_item.data["Band"])
            band = self.band

        DUTBAND = ("%s" % dut_band).upper()
        chans = chan_info.split(',')
        if chans[0] == "":
            return

        for i in range(0, len(chans)):
            channelList.append(chans[i].split('/'))
            if band != "11a" and band != "11na" and band != "11ac" and band != -1:
                testChannel.append(channelList[i][1])
            elif band != -1:
                testChannel.append(channelList[i][0])

        if band == "11a" or band == "11g":            
            self.var_list.setdefault("STAPHY", "ag")
        elif band == "11b":            
            self.var_list.setdefault("STAPHY", "b")
        elif band == "11na" or band == "11ng":
            TestScriptSymbolTable.insert_sym_tab("STAPHY", "11n", TestScriptSymbolTable.test_script_sym_tab)
            self.var_list.setdefault("STAPHY", "11n")
        elif band == "11ac":
            TestScriptSymbolTable.insert_sym_tab("STAPHY", "11ac", TestScriptSymbolTable.test_script_sym_tab)
            self.var_list.setdefault("STAPHY", "11ac")

        if int(testChannel[0]) > 35:
            if band == "11ac":
                self.var_list.setdefault("APUT_Band", "11ac")
                self.var_list.setdefault("STAUT_Band", "11ac")
                self.var_list.setdefault("Band_Legacy", "11a")
                self.var_list.setdefault("Band_LegacyN", "11na")
            else:
                if DUTBAND == "AN" or DUTBAND == "ABGN":
                    self.var_list.setdefault("APUT_Band", "11na")
                    self.var_list.setdefault("STAUT_Band", "11na")
                    self.var_list.setdefault("Band_Legacy", "11a")
                elif DUTBAND == "A" or DUTBAND == "ABG":
                    self.var_list.setdefault("APUT_Band", "11a")
                    self.var_list.setdefault("STAUT_Band", "11a")
                    self.var_list.setdefault("Band_Legacy", "11a")
        else:
            if DUTBAND == "GN" or DUTBAND == "ABGN":
                self.var_list.setdefault("APUT_Band", "11ng")
                self.var_list.setdefault("STAUT_Band", "11ng")
                self.var_list.setdefault("Band_Legacy", "11g")
            elif DUTBAND == "BG" or DUTBAND == "ABG":
                self.var_list.setdefault("APUT_Band", "11g")
                self.var_list.setdefault("STAUT_Band", "11g")
                self.var_list.setdefault("Band_Legacy", "11g")
            elif DUTBAND == "B":
                self.var_list.setdefault("APUT_Band", "11b")
                self.var_list.setdefault("STAUT_Band", "11b")
                self.var_list.setdefault("Band_Legacy", "11b")

        self.band = band

        iCount = 1
        for chan in testChannel:
            if len(testChannel) > 1:
                self.channel["Channel_%s" % (iCount)] = chan
                iCount = iCount + 1
                self.channel["Channel"] = self.channel["Channel_1"]
            else:
                self.channel["Channel"] = chan


    def set_test_config_info_AP(self, ap_info):
        """Sets the test config info for AP.

        Args:
            ap_info (str): The AP info.
        """
        APs = ap_info.split(',')

        for i, ap in enumerate(APs):
            if ap == "":
                continue

            for tbd in self.test_config_info_mngr.test_mngr_initr.test_prog_mngr.test_prog.testbed_dev_list:
                if tbd.dev_name == ap and tbd.dev_type == "AP":
                    tbd.number = "AP%s" % (i + 1)
                    tbd.state = "On"
                    tbd.num_var_name = "AP%s_control_agent" % (i + 1)
                    tbd.dollar_var_name = "$%sAP" % ap

                    self.test_config_info_mngr.test_mngr_initr.test_case_mngr.test_case.testbed_device_list.append(tbd)
                    break

            if int(self.channel["Channel"]) > 35:
                self.var_list.setdefault("bssid", ("$%sAPMACAddress_5G" % ap))
                self.var_list.setdefault(("AP%sMACAddress" % (i + 1)), ("$%sAPMACAddress_5G" % ap))
                self.var_list.setdefault(("AP%sMACAddress2" % (i + 1)), ("$%sAPMACAddress2_5G" % ap))
                self.var_list.setdefault(("AP%sMACAddress3" % (i + 1)), ("$%sAPMACAddress3_5G" % ap))
            else:
                self.var_list.setdefault("bssid", ("$%sAPMACAddress_24G" % ap))
                self.var_list.setdefault(("AP%sMACAddress" % (i + 1)), ("$%sAPMACAddress_24G" % ap))
                self.var_list.setdefault(("AP%sMACAddress2" % (i + 1)), ("$%sAPMACAddress2_24G" % ap))
                self.var_list.setdefault(("AP%sMACAddress3" % (i + 1)), ("$%sAPMACAddress3_24G" % ap))

            self.var_list.setdefault("AP%s_control_agent" % (i + 1), "wfa_control_agent_%s_ap" % (ap.lower()))
        # end of for loop


    def set_test_config_info_STA(self, sta_info):
        """Sets the test config info for STA.

        Args:
            sta_info (str): The STA info.
        """
        value = ("%s" % sta_info).strip()
        logging.debug(value)

        if not value: return

        STAs = sta_info.split(',')
        for i, sta in enumerate(STAs):
            if sta == "" or sta == "0":
                continue

            for tbd in self.test_config_info_mngr.test_mngr_initr.test_prog_mngr.test_prog.testbed_dev_list:
                if tbd.dev_name == sta and tbd.dev_type == "STA":
                    tbd.number = "STA%s" % (i + 1)
                    tbd.num_var_name = "STA%s_control_agent" % (i + 1)
                    tbd.dollar_var_name = "$%sSTA" % sta

                    self.test_config_info_mngr.test_mngr_initr.test_case_mngr.test_case.testbed_device_list.append(tbd)
                    break

            self.var_list.setdefault("STA%s_control_agent" % (i + 1), "wfa_control_agent_%s_sta" % sta.lower())
            self.var_list.setdefault("STA%s_wireless_ip" % (i + 1), "%s_sta_wireless_ip" % sta.lower())
            self.var_list.setdefault("STA%s_MACAddress" % (i + 1), ("$%sSTAMACAddress" % sta))



class Decorator(TestConfigInfo):
    """Attaches additional functionalities to the parent class dynamically.

    Attributes:
        test_config_info (object): Description of `attr1`.

    """
    def __init__(self):
        self.test_config_info = None


    def set_component(self, test_config_info):
        """Sets the component variable.

        Args:
            test_config_info (object): The object of TestConfigInfo class.
        """
        self.test_config_info = test_config_info


    def set_test_config_info_STA(self, sta_info):
        """Sets the test config info for STA.

        Args:
            sta_info (str): The STA info.
        """
        if not self.test_config_info is None:
            self.test_config_info.set_test_config_info_STA(sta_info)


    def set_test_config_info_AP(self, ap_info):
        """Sets the test config info for AP.

        Args:
            ap_info (str): The AP info.
        """
        if not self.test_config_info is None:
            self.test_config_info.set_test_config_info_AP(ap_info)


    def set_other_varlist_values(self):
        """Sets values to program specific variables and stores in var_list dictionary.
        """
        if not self.test_config_info is None:
            self.test_config_info.set_other_varlist_values()


    def set_test_config_info_OPERATINGCHANNEL(self, oper_chnl):
        """Gets real test case name that will be executed.

        Args:
            tc_name (str): test case name.
        """
        if not self.test_config_info is None:
            self.test_config_info.set_test_config_info_OPERATINGCHANNEL(oper_chnl)


    def set_test_config_info_DUTFILE(self, dut_file=""):
        """Gets real test case name that will be executed.

        Args:
            tc_name (str): test case name.
        """
        if not self.test_config_info is None:
            self.test_config_info.set_test_config_info_DUTFILE(dut_file="")



class Decorator_PMF(Decorator):
    """The decorator class for PMF.
    """
    def __init__(self):
        Decorator.__init__(self)


    def set_other_varlist_values(self):
        """Sets values to program specific variables and stores in var_list dictionary.
        """
        self.test_config_info.var_list.setdefault("TBAPConfigServer", "TestbedAPConfigServer")
        self.test_config_info.var_list.setdefault("WFA_Sniffer", self.test_config_info.WFA_SNIFFER.lower())
        self.test_config_info.var_list.setdefault("WFA_TEST_control_agent", "wfa_test_control_agent")

        for tc in self.test_config_info.test_config_info_mngr.test_mngr_initr.test_prog_mngr.test_prog.tc_list:
            if tc.tc_id == common.GlobalConfigFiles.curr_tc_name and tc.tc_type == "APUT":            
                self.test_config_info.var_list.setdefault("sender", "sta")
                break
            if tc.tc_id == common.GlobalConfigFiles.curr_tc_name and tc.tc_type == "STAUT":
                self.test_config_info.var_list.setdefault("sender", "ap")
                break

        list_item = self.test_config_info.test_config_info_mngr.sll.search("WFA_Tester")
        if list_item is not None:
            self.test_config_info.var_list.setdefault("WFA_Tester", list_item.data["WFA_Tester"])



class Decorator_VE(Decorator):
    """The decorator class for VE.
    """
    def __init__(self):
        Decorator.__init__(self)


    def set_other_varlist_values(self):
        """Sets values to program specific variables and stores in var_list dictionary.
        """
        self.test_config_info.var_list.setdefault("BSS_Trans_Query_Support", self.test_config_info.test_config_info_mngr.test_mngr_initr.test_feat_mngr.get_feat_obj_val_by_name(TestScriptElementType.get_test_feat_key_from_val(TestScriptElementType.BSS_TRANS_QUERY_SUPPORT)))
        self.test_config_info.var_list.setdefault("TSM_Support", self.test_config_info.test_config_info_mngr.test_mngr_initr.test_feat_mngr.get_feat_obj_val_by_name(TestScriptElementType.get_test_feat_key_from_val(TestScriptElementType.TSM_SUPPORT)))



class Decorator_N(Decorator):
    """The decorator class for N.
    """
    def __init__(self):
        Decorator.__init__(self)


    def set_other_varlist_values(self):
        """Sets values to program specific variables and stores in var_list dictionary.
        """
        self.test_config_info.var_list.setdefault("ChannelWidth_Value", self.test_config_info.test_config_info_mngr.test_mngr_initr.test_feat_mngr.get_feat_obj_val_by_name(TestScriptElementType.get_test_feat_key_from_val(TestScriptElementType.SUPPORTED_CHANNEL_WIDTH)))
        self.test_config_info.var_list.setdefault("GreenField_Value", self.test_config_info.test_config_info_mngr.test_mngr_initr.test_feat_mngr.get_feat_obj_val_by_name(TestScriptElementType.get_test_feat_key_from_val(TestScriptElementType.GREENFIELD)))
        self.test_config_info.var_list.setdefault("SGI20_Value", self.test_config_info.test_config_info_mngr.test_mngr_initr.test_feat_mngr.get_feat_obj_val_by_name(TestScriptElementType.get_test_feat_key_from_val(TestScriptElementType.SGI20)))
        self.test_config_info.var_list.setdefault("SGI40_Value", self.test_config_info.test_config_info_mngr.test_mngr_initr.test_feat_mngr.get_feat_obj_val_by_name(TestScriptElementType.get_test_feat_key_from_val(TestScriptElementType.SGI40)))
        self.test_config_info.var_list.setdefault("MCS_Set_Value", self.test_config_info.test_config_info_mngr.test_mngr_initr.test_feat_mngr.get_feat_obj_val_by_name(TestScriptElementType.get_test_feat_key_from_val(TestScriptElementType.STREAMS)))
        self.test_config_info.var_list.setdefault("MCS32_Value", self.test_config_info.test_config_info_mngr.test_mngr_initr.test_feat_mngr.get_feat_obj_val_by_name(TestScriptElementType.get_test_feat_key_from_val(TestScriptElementType.MCS32)))
        self.test_config_info.var_list.setdefault("STBC_RX_Value", self.test_config_info.test_config_info_mngr.test_mngr_initr.test_feat_mngr.get_feat_obj_val_by_name(TestScriptElementType.get_test_feat_key_from_val(TestScriptElementType.STBC_RX)))
        self.test_config_info.var_list.setdefault("STBC_TX_Value", self.test_config_info.test_config_info_mngr.test_mngr_initr.test_feat_mngr.get_feat_obj_val_by_name(TestScriptElementType.get_test_feat_key_from_val(TestScriptElementType.STBC_TX)))

        self.test_config_info.var_list.setdefault("STAUT_PM", self.test_config_info.test_config_info_mngr.test_mngr_initr.test_feat_mngr.get_feat_obj_val_by_name(TestScriptElementType.get_test_feat_key_from_val(TestScriptElementType.STAUT_PM)))
        self.test_config_info.var_list.setdefault("Streams", "%sSS" % self.test_config_info.test_config_info_mngr.test_mngr_initr.test_feat_mngr.get_feat_obj_val_by_name(TestScriptElementType.get_test_feat_key_from_val(TestScriptElementType.STREAMS)))
        self.test_config_info.var_list.setdefault("Open_Mode", self.test_config_info.test_config_info_mngr.test_mngr_initr.test_feat_mngr.get_feat_obj_val_by_name(TestScriptElementType.get_test_feat_key_from_val(TestScriptElementType.OPEN_MODE)))
        self.test_config_info.var_list.setdefault("Mixedmode_WPA2WPA", self.test_config_info.test_config_info_mngr.test_mngr_initr.test_feat_mngr.get_feat_obj_val_by_name(TestScriptElementType.get_test_feat_key_from_val(TestScriptElementType.MIXEDMODE_WPA2WPA)))
        self.test_config_info.var_list.setdefault("PMF_OOB", self.test_config_info.test_config_info_mngr.test_mngr_initr.test_feat_mngr.get_feat_obj_val_by_name(TestScriptElementType.get_test_feat_key_from_val(TestScriptElementType.PMF_OOB)))
        self.test_config_info.var_list.setdefault("ASD", self.test_config_info.test_config_info_mngr.test_mngr_initr.test_feat_mngr.get_feat_obj_val_by_name(TestScriptElementType.get_test_feat_key_from_val(TestScriptElementType.ASD)))

        cond = self.test_config_info.test_config_info_mngr.sll.search(self.test_config_info.CONDITIONALSTEP_AONLY40)
        if cond is not None:
            suptBandWidth = self.test_config_info.test_config_info_mngr.test_mngr_initr.test_feat_mngr.get_feat_obj_val_by_name(TestScriptElementType.get_test_feat_key_from_val(TestScriptElementType.SUPPORTED_CHANNEL_WIDTH))
            dut_band = self.test_config_info.test_config_info_mngr.test_mngr_initr.test_feat_mngr.get_feat_obj_val_by_name(TestScriptElementType.get_test_feat_key_from_val(TestScriptElementType.DUT_BAND))
            if re.search('A', dut_band) and suptBandWidth == "40":
                self.test_config_info.var_list.setdefault(self.test_config_info.CONDITIONALSTEP_AONLY40, cond.data.values()[0])
            else:
                self.test_config_info.var_list.setdefault(self.test_config_info.CONDITIONALSTEP_AONLY40, "DoNothing.txt")

        cond = self.test_config_info.test_config_info_mngr.sll.search(self.test_config_info.CONDITIONALSTEP_2SS)
        if cond is not None:
            streams = self.test_config_info.test_config_info_mngr.test_mngr_initr.test_feat_mngr.get_feat_obj_val_by_name(TestScriptElementType.get_test_feat_key_from_val(TestScriptElementType.STREAMS))
            if streams == "3" or streams == "2":
                self.test_config_info.var_list.setdefault(self.test_config_info.CONDITIONALSTEP_2SS, cond.data.values()[0])
            else:
                self.test_config_info.var_list.setdefault(self.test_config_info.CONDITIONALSTEP_2SS, "DoNothing.txt")

        cond = self.test_config_info.test_config_info_mngr.sll.search(self.test_config_info.CONDITIONALSTEP_3SS)
        if cond is not None:
            streams = self.test_config_info.test_config_info_mngr.test_mngr_initr.test_feat_mngr.get_feat_obj_val_by_name(TestScriptElementType.get_test_feat_key_from_val(TestScriptElementType.STREAMS))
            if streams == "3":
                self.test_config_info.var_list.setdefault(self.test_config_info.CONDITIONALSTEP_3SS, cond.data.values()[0])
            else:
                self.test_config_info.var_list.setdefault(self.test_config_info.CONDITIONALSTEP_3SS, "DoNothing.txt")

        suptChnlWidth = self.test_config_info.test_config_info_mngr.test_mngr_initr.test_feat_mngr.get_feat_obj_val_by_name(TestScriptElementType.get_test_feat_key_from_val(TestScriptElementType.SUPPORTED_CHANNEL_WIDTH))
        self.test_config_info.var_list.setdefault(self.test_config_info.DUTSUPPORTEDCW, suptChnlWidth)



class Decorator_WFD(Decorator):
    """The decorator class for WFD.
    """
    def __init__(self):
        Decorator.__init__(self)


    def set_test_config_info_DUTFILE(self, dut_file=""):
        """Sets configuration info of DUT file specific to WFD.

        Args:
            dut_file (str): DUT file name.
        """
        wts_support = self.test_config_info.test_config_info_mngr.test_mngr_initr.test_feat_mngr.get_feat_obj_val_by_name(TestScriptElementType.get_test_feat_key_from_val(TestScriptElementType.WTSSUPPORT))

        if int(wts_support) == 0:
            self.dut_config_file = "NoWTSSupportMsg.txt"
            self.test_config_info.var_list.setdefault("WTSMsg", "Configure DUT for Testcase = -- %s --" % common.GlobalConfigFiles.curr_tc_name)
            self.test_config_info.var_list.setdefault("DUT_WTS_VERSION", "NA")
        else:
            self.test_config_info.set_test_config_info_DUTFILE(dut_file)


    def set_other_varlist_values(self):
        """Sets values to program specific variables and stores in var_list dictionary.
        """
        self.test_config_info.set_value_to_var_list(self.test_config_info.PERSISTENT, "0", True)
        self.test_config_info.set_value_to_var_list(self.test_config_info.SERDISC, "0", True)


    def set_test_config_info_OPERATINGCHANNEL(self, oper_chnl):
        """Sets the operating channel to var_list dictionary.

        Args:
            oper_chnl (str): The operating channel info.
        """
        test_oper_channel = []
        oper_channel1 = []
        band = -1
        dut_band = self.test_config_info.test_config_info_mngr.test_mngr_initr.test_feat_mngr.get_feat_obj_val_by_name(TestScriptElementType.get_test_feat_key_from_val(TestScriptElementType.DUT_BAND))

        list_item = self.test_config_info.test_config_info_mngr.sll.search("Band")
        if list_item is not None:
            self.test_config_info.set_test_config_info_BAND(list_item.data["Band"])
            band = self.test_config_info.band

        operChannel1 = oper_chnl.split(',')
        if operChannel1[0] == "":
            return
        
        for chan in range(0, len(operChannel1)):
            oper_channel1.append(operChannel1[chan].split("/"))
            TestLogFileSource.log_file_source_obj_list[0].write_log_message("Test case Operating Channel %s %s" % (oper_channel1[chan][0], oper_channel1[chan][1]), TestLogFileSource.log_file_hdl_list[0])

            if band != "11a" and band != "11na" and band != -1:
                test_oper_channel.append(oper_channel1[chan][1])
            elif band != -1:
                test_oper_channel.append(oper_channel1[chan][0])
            if band == -1:
                self.test_config_info.var_list.setdefault("TestNA", "Invalid Band. DUT Capable Band is [%s] and Test requires [%s]" % (dut_band, band))

        TestLogFileSource.log_file_source_obj_list[0].write_log_message("Test execution in %s Band and Operating Channel %s" % (band, test_oper_channel), TestLogFileSource.log_file_hdl_list[0])

        self.test_config_info.band = band

        i_count = 1
        for chan in test_oper_channel:
            if len(test_oper_channel) > 1:
                self.test_config_info.var_list.setdefault("OPER_CHN_%s"%(i_count), chan)
                i_count = i_count + 1
                self.test_config_info.var_list.setdefault("OPER_CHN", self.test_config_info.var_list["OPER_CHN_1"])
            else:
                self.test_config_info.var_list.setdefault("OPER_CHN", chan)



class Decorator_TDLS(Decorator):
    """The decorator class for TDLS.
    """
    def __init__(self):
        Decorator.__init__(self)


    def set_test_config_info_STA(self, sta_info):
        """Sets test config info for stations specific to TDLS.

        Args:
            sta_info (str): The STA info.
        """
        self.test_config_info.set_test_config_info_STA(sta_info)
        value = ("%s" % sta_info).strip()
        if not value: return

        STAs = sta_info.split(',')
        for i, sta in enumerate(STAs):
            if sta == "":
                continue
            self.test_config_info.var_list.setdefault("STA%s_wireless_ip2" % (i + 1), "%s_sta_wireless_ip2" % sta.lower())
            self.test_config_info.var_list.setdefault("STA%s_wireless_ip3" % (i + 1), "%s_sta_wireless_ip3" % sta.lower())


    def set_other_varlist_values(self):
        """Sets values to program specific variables and stores in var_list dictionary.
        """
        cond = self.test_config_info.test_config_info_mngr.sll.search(self.test_config_info.CONDITIONALSTEP_DISCREQ)
        if cond is not None:
            TDLSDiscReq = self.test_config_info.test_config_info_mngr.test_mngr_initr.test_feat_mngr.get_feat_obj_val_by_name(TestScriptElementType.get_test_feat_key_from_val(TestScriptElementType.TDLSDISCREQ))
            if TDLSDiscReq == "1":
                self.test_config_info.var_list.setdefault(self.test_config_info.CONDITIONALSTEP_DISCREQ, cond.data.values()[0])
            else:
                self.test_config_info.var_list.setdefault(self.test_config_info.CONDITIONALSTEP_DISCREQ, "DoNothing.txt")

        cond = self.test_config_info.test_config_info_mngr.sll.search(self.test_config_info.CONDITIONALSTEP_PUSLEEP)
        if cond is not None:
            PUSleepSTA = self.test_config_info.test_config_info_mngr.test_mngr_initr.test_feat_mngr.get_feat_obj_val_by_name(TestScriptElementType.get_test_feat_key_from_val(TestScriptElementType.PUSLEEPSTA))
            if PUSleepSTA == "1":
                self.test_config_info.var_list.setdefault(self.test_config_info.CONDITIONALSTEP_PUSLEEP, cond.data.values()[0])
            else:
                self.test_config_info.var_list.setdefault(self.test_config_info.CONDITIONALSTEP_PUSLEEP, "DoNothing.txt")

        self.test_config_info.set_value_to_var_list(self.test_config_info.OFFCH, "44", True)
        #cond = self.test_config_info.test_config_info_mngr.sll.search(self.test_config_info.OFFCH)
        #if cond is not None:
        #    self.test_config_info.var_list.setdefault(self.test_config_info.OFFCH, cond)
        #else:
        #    self.test_config_info.var_list.setdefault(self.test_config_info.OFFCH, "44")
        self.test_config_info.set_value_to_var_list(self.test_config_info.OFFCHWIDTH, "20", True)
        #cond = self.test_config_info.test_config_info_mngr.sll.search(self.test_config_info.OFFCHWIDTH)
        #if cond is not None:
        #    self.test_config_info.var_list.setdefault(self.test_config_info.OFFCHWIDTH, cond)
        #else:
        #    self.test_config_info.var_list.setdefault(self.test_config_info.OFFCHWIDTH, "20")

        suptChnlWidth = self.test_config_info.test_config_info_mngr.test_mngr_initr.test_feat_mngr.get_feat_obj_val_by_name(TestScriptElementType.get_test_feat_key_from_val(TestScriptElementType.SUPPORTED_CHANNEL_WIDTH))
        self.test_config_info.var_list.setdefault(self.test_config_info.DUTSUPPORTEDCW, suptChnlWidth)

        self.test_config_info.set_value_to_var_list(self.test_config_info.WMMSTREAM_THRESHOLD, "", False)
        #cond = self.test_config_info.test_config_info_mngr.sll.search(self.test_config_info.WMMSTREAM_THRESHOLD)
        #if cond is not None:
        #    self.test_config_info.var_list.setdefault(self.test_config_info.WMMSTREAM_THRESHOLD, cond)



class Decorator_HS2R2(Decorator):
    """The decorator class for HS2R2.
    """
    def __init__(self):
        Decorator.__init__(self)


    def set_other_varlist_values(self):
        """Sets values to program specific variables and stores in var_list dictionary.
        """
        self.test_config_info.var_list.setdefault("SS1", "")


    def set_test_config_info_STA(self, sta_info):
        """Gets real test case name that will be executed.

        Args:
            tc_name (str): test case name.
        """
        value = ("%s" % sta_info).strip()
        if not value: return
        self.test_config_info.set_test_config_info_STA(sta_info)
        STAs = sta_info.split(',')
        for i, sta in enumerate(STAs):
            if sta == "":
                continue
            self.test_config_info.var_list.setdefault("STA%s_wireless_ipv6" % (i + 1), "%s_sta_wireless_ipv6" % sta.lower())


    def set_test_config_info_DUTFILE(self, dut_file=""):
        """Sets configuration info of DUT file specific to HS2R2.

        Args:
            dut_file (str): DUT file name.
        """
        wts_support = self.test_config_info.test_config_info_mngr.test_mngr_initr.test_feat_mngr.get_feat_obj_val_by_name(TestScriptElementType.get_test_feat_key_from_val(TestScriptElementType.WTSSUPPORT))

        if int(wts_support) == 0:
            self.dut_config_file = "NoWTSSupportMsg.txt"
            self.test_config_info.var_list.setdefault("WTSMsg", "Configure DUT for Testcase = -- %s --" % common.GlobalConfigFiles.curr_tc_name)
            self.test_config_info.var_list.setdefault("DUT_WTS_VERSION", "NA")
        else:
            self.test_config_info.set_test_config_info_DUTFILE(dut_file)



class Decorator_HS2(Decorator):
    """The decorator class for HS2.
    """
    def __init__(self):
        Decorator.__init__(self)


    def set_test_config_info_DUTFILE(self, dut_file=""):
        """Sets configuration info of DUT file specific to HS2.

        Args:
            dut_file (str): DUT file name.
        """
        wts_support = self.test_config_info.test_config_info_mngr.test_mngr_initr.test_feat_mngr.get_feat_obj_val_by_name(TestScriptElementType.get_test_feat_key_from_val(TestScriptElementType.WTSSUPPORT))

        if int(wts_support) == 0:
            self.dut_config_file = "NoWTSSupportMsg.txt"
            self.test_config_info.var_list.setdefault("WTSMsg", "Configure DUT for Testcase = -- %s --" % common.GlobalConfigFiles.curr_tc_name)
            self.test_config_info.var_list.setdefault("DUT_WTS_VERSION", "NA")
        else:
            self.test_config_info.set_test_config_info_DUTFILE(dut_file)



class Decorator_WFDS(Decorator):
    """The decorator class for WFDS.
    """
    def __init__(self):
        Decorator.__init__(self)


    def set_test_config_info_DUTFILE(self, dut_file=""):
        """Sets configuration info of DUT file specific to WFDS.

        Args:
            dut_file (str): DUT file name.
        """
        wts_support = self.test_config_info.test_config_info_mngr.test_mngr_initr.test_feat_mngr.get_feat_obj_val_by_name(TestScriptElementType.get_test_feat_key_from_val(TestScriptElementType.WTSSUPPORT))

        if int(wts_support) == 0:
            self.dut_config_file = "NoWTSSupportMsg.txt"
            self.test_config_info.var_list.setdefault("WTSMsg", "Configure DUT for Testcase = -- %s --" % common.GlobalConfigFiles.curr_tc_name)
            self.test_config_info.var_list.setdefault("DUT_WTS_VERSION", "NA")
        else:
            self.test_config_info.set_test_config_info_DUTFILE(dut_file)



class Decorator_P2P(Decorator):
    """The decorator class for P2P.
    """
    def __init__(self):
        Decorator.__init__(self)


    def set_test_config_info_DUTFILE(self, dut_file=""):
        """Sets configuration info of DUT file specific to P2P.

        Args:
            dut_file (str): DUT file name.
        """
        wts_support = self.test_config_info.test_config_info_mngr.test_mngr_initr.test_feat_mngr.get_feat_obj_val_by_name(TestScriptElementType.get_test_feat_key_from_val(TestScriptElementType.WTSSUPPORT))

        if int(wts_support) == 0:
            self.dut_config_file = "NoWTSSupportMsg.txt"
            self.test_config_info.var_list.setdefault("WTSMsg", "Configure DUT for Testcase = -- %s --" % common.GlobalConfigFiles.curr_tc_name)
            self.test_config_info.var_list.setdefault("DUT_WTS_VERSION", "NA")
        else:
            self.test_config_info.set_test_config_info_DUTFILE(dut_file)


    def set_other_varlist_values(self):
        """Sets configuration info of other variables specific to P2P."""
        self.test_config_info.set_value_to_var_list(self.test_config_info.PERSISTENT, "0", True)
        self.test_config_info.set_value_to_var_list(self.test_config_info.SERDISC, "0", True)



class Decorator_WMMPS(Decorator):
    """The decorator class for WMMPS.
    """
    def __init__(self):
        Decorator.__init__(self)


    def set_test_config_info_DUTFILE(self, dut_file=""):
        """Sets configuration info of DUT file specific to WMMPS.

        Args:
            dut_file (str): DUT file name.
        """
        wts_support = self.test_config_info.test_config_info_mngr.test_mngr_initr.test_feat_mngr.get_feat_obj_val_by_name(TestScriptElementType.get_test_feat_key_from_val(TestScriptElementType.WTSSUPPORT))

        if int(wts_support) == 0:
            self.dut_config_file = "NoWTSSupportMsg.txt"
            self.test_config_info.var_list.setdefault("WTSMsg", "Configure DUT for Testcase = -- %s --" % common.GlobalConfigFiles.curr_tc_name)
            self.test_config_info.var_list.setdefault("DUT_WTS_VERSION", "NA")
        else:
            self.test_config_info.set_test_config_info_DUTFILE(dut_file)



class Decorator_NAN(Decorator):
    """The decorator class for NAN.
    """
    def __init__(self):
        Decorator.__init__(self)


    def set_test_config_info_DUTFILE(self, dut_file=""):
        """Sets configuration info of DUT file specific to NAN.

        Args:
            dut_file (str): DUT file name.
        """
        wts_support = self.test_config_info.test_config_info_mngr.test_mngr_initr.test_feat_mngr.get_feat_obj_val_by_name(TestScriptElementType.get_test_feat_key_from_val(TestScriptElementType.WTSSUPPORT))

        if int(wts_support) == 0:
            self.dut_config_file = "NoWTSSupportMsg.txt"
            self.test_config_info.var_list.setdefault("WTSMsg", "Configure DUT for Testcase = -- %s --" % common.GlobalConfigFiles.curr_tc_name)
            self.test_config_info.var_list.setdefault("DUT_WTS_VERSION", "NA")
        else:
            self.test_config_info.set_test_config_info_DUTFILE(dut_file)

