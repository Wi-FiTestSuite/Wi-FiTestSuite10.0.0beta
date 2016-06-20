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
import re
from scriptinfo.scriptelement import TestScriptElementType
from core.symtable import TestScriptSymbolTable


class TestbedDeviceManager:
    """The class that manages testbed device info.

    Attributes:
        ill (object): The object of SingleLinkedList class.
        prog_name (str): The program name.
        test_mngr_initr (object): The object of TestManagerInitializer class.

    """
    def __init__(self, prog_name):
        self.ill = None
        self.prog_name = prog_name
        self.test_mngr_initr = None
        self.num_of_aps_capi = 0

    def create_testbed_device_instance(self, dev_name_info, hint):
        """Creates the instance of testbed device specified by the input parameters.

        Args:
            dev_name_info (str): The name of testbed device.
            hint (str): The type of testbed device.
        """
        testbed_dev = None
        if hint == "AP":
            testbed_dev = TestBedAP(self.prog_name)
            testbed_dev.dev_name = dev_name_info
            testbed_dev.dev_type = "AP"
        if hint == "STA":
            testbed_dev = TestBedSTA(self.prog_name)
            testbed_dev.dev_name = dev_name_info
            testbed_dev.dev_type = "STA"
        if hint == "DUT":
            testbed_dev = DUT(self.prog_name)
            testbed_dev.dev_name = dev_name_info
            testbed_dev.dev_type = "DUT"
        if hint == "SNIFFER":
            testbed_dev = Sniffer(self.prog_name)
            testbed_dev.dev_name = dev_name_info
            testbed_dev.dev_type = "SNIFFER"
        if hint == "PCENDPOINT":
            testbed_dev = PCEndpoint(self.prog_name)
            testbed_dev.dev_name = dev_name_info
            testbed_dev.dev_type = "PCENDPOINT"
        if hint == "APCONFIG":
            testbed_dev = APConfig(self.prog_name)
            testbed_dev.dev_name = dev_name_info
            testbed_dev.dev_type = "APCONFIG"
        if hint == "RADIUSSERVER":
            testbed_dev = RadiusServer(self.prog_name)
            testbed_dev.dev_name = dev_name_info
            testbed_dev.dev_type = "RADIUSSERVER"
        if hint == "OSUSERVER":
            testbed_dev = OSUServer(self.prog_name)
            testbed_dev.dev_name = dev_name_info
            testbed_dev.dev_type = "OSUSERVER"
        if hint == "ATTENUATOR":
            testbed_dev = Attenuator(self.prog_name)
            testbed_dev.dev_name = dev_name_info
            testbed_dev.dev_type = "ATTENUATOR"
        if hint == "POWERSWITCH":
            testbed_dev = PowerSwitch(self.prog_name)
            testbed_dev.dev_name = dev_name_info
            testbed_dev.dev_type = "POWERSWITCH"
        if hint == "WFAEMT":
            testbed_dev = WFAEMT(self.prog_name)
            testbed_dev.dev_name = dev_name_info
            testbed_dev.dev_type = "WFAEMT"
        return testbed_dev


    def check_testbed_device_list(self, dev_name):
        """Checks if the device name is in the testbed device list.

        Args:
            dev_name (str): The name of device to be checked.
        """
        for tbd in self.test_mngr_initr.test_prog_mngr.test_prog.testbed_dev_list:
            if tbd.dev_name == dev_name:
                return tbd
        return None


    def set_rs_eap_cred(self):
        """Sets the device's radius server EAP credential info.
        """
        for tbd in self.test_mngr_initr.test_prog_mngr.test_prog.testbed_dev_list:
            if tbd.dev_type == "RADIUSSERVER":                
                for eap_name in self.test_mngr_initr.test_configurator.eap_method_list:
                    rseapcred = RadiusServerEAPCredential()
                    eap_value = ""
                    if eap_name == TestScriptElementType.TLS:
                        eap_value = TestScriptSymbolTable.get_value_from_sym_tab("$trustedRootCACertName", TestScriptSymbolTable.test_script_sym_tab)
                        rseapcred.root_cert_name = eap_value if eap_value else ""
                        eap_value = TestScriptSymbolTable.get_value_from_sym_tab("$clientCertificateName", TestScriptSymbolTable.test_script_sym_tab)
                        rseapcred.cli_cert_name = eap_value if eap_value else ""
                        eap_value = TestScriptSymbolTable.get_value_from_sym_tab("$TLSUserName", TestScriptSymbolTable.test_script_sym_tab)
                        rseapcred.tls_username = eap_value if eap_value else ""

                    if eap_name == TestScriptElementType.PEAP0:
                        eap_value = TestScriptSymbolTable.get_value_from_sym_tab("$PUserName", TestScriptSymbolTable.test_script_sym_tab)
                        rseapcred.username = eap_value if eap_value else ""
                        eap_value = TestScriptSymbolTable.get_value_from_sym_tab("$PPassword", TestScriptSymbolTable.test_script_sym_tab)
                        rseapcred.password = eap_value if eap_value else ""

                    if eap_name == TestScriptElementType.PEAP1:
                        eap_value = TestScriptSymbolTable.get_value_from_sym_tab("$P1UserName", TestScriptSymbolTable.test_script_sym_tab)
                        rseapcred.username = eap_value if eap_value else ""
                        eap_value = TestScriptSymbolTable.get_value_from_sym_tab("$P1Password", TestScriptSymbolTable.test_script_sym_tab)
                        rseapcred.password = eap_value if eap_value else ""

                    if eap_name == TestScriptElementType.TTLS or eap_name == TestScriptElementType.FAST or eap_name == TestScriptElementType.SIM or eap_name == TestScriptElementType.AKA or eap_name == TestScriptElementType.AKA_PRIME or eap_name == TestScriptElementType.PWD:
                        if eap_name == TestScriptElementType.FAST:
                            eap_value = TestScriptSymbolTable.get_value_from_sym_tab("$FASTGTCUserName", TestScriptSymbolTable.test_script_sym_tab)
                            rseapcred.gtc_username = eap_value if eap_value else ""
                            eap_value = TestScriptSymbolTable.get_value_from_sym_tab("$FASTGTCPassword", TestScriptSymbolTable.test_script_sym_tab)
                            rseapcred.gtc_password = eap_value if eap_value else ""
                        if eap_name == TestScriptElementType.AKA_PRIME:
                            eap_value = TestScriptSymbolTable.get_value_from_sym_tab("$AKA\'WrongUserName", TestScriptSymbolTable.test_script_sym_tab)
                            rseapcred.wrong_username = eap_value if eap_value else ""
                        if eap_name == TestScriptElementType.PWD:
                            eap_value = TestScriptSymbolTable.get_value_from_sym_tab("$PWDWrongUserName", TestScriptSymbolTable.test_script_sym_tab)
                            rseapcred.wrong_username = eap_value if eap_value else ""

                        eap_value = TestScriptSymbolTable.get_value_from_sym_tab("$" + eap_name + "UserName", TestScriptSymbolTable.test_script_sym_tab)
                        rseapcred.username = eap_value if eap_value else ""
                        eap_value = TestScriptSymbolTable.get_value_from_sym_tab("$" + eap_name + "Password", TestScriptSymbolTable.test_script_sym_tab)
                        rseapcred.password = eap_value if eap_value else ""

                    tbd.rs_eap_cred_list.append(rseapcred)


    def set_rad_svr_dev(self, dev_info_str, curr_node):
        """Sets the radius server device info.

        Args:
            dev_info_str (str): The string that includes device name and other device info.
            curr_node (node): The node object of SingleLinkedList class.
        """
        for tbd in self.test_mngr_initr.test_prog_mngr.test_prog.testbed_dev_list:
            indx = dev_info_str.find(tbd.dev_name)
            indx1 = indx + len(tbd.dev_name)

            if indx != -1 and tbd.dev_type == "RADIUSSERVER":
                if dev_info_str[indx1:] == "IPAddress":
                    tbd.testipaddr = (curr_node.data.values())[0]
                if dev_info_str[indx1:] == "Port":
                    tbd.testport = (curr_node.data.values())[0]
                if dev_info_str[indx1:] == "SharedSecret":
                    tbd.shared_secret = (curr_node.data.values())[0]
                break


    def set_osu_svr_dev(self, dev_info_str, curr_node):
        """Sets the OSU server device info.

        Args:
            dev_info_str (str): The string that includes device name and other device info.
            curr_node (node): The node object of SingleLinkedList class.
        """
        for tbd in self.test_mngr_initr.test_prog_mngr.test_prog.testbed_dev_list:
            indx = dev_info_str.find(tbd.dev_name)
            indx1 = indx + len(tbd.dev_name)

            if indx != -1 and tbd.dev_type == "OSUSERVER":
                if dev_info_str[indx1:] == "_osu":
                    tbd.ctrlipaddr = ((curr_node.data.values())[0])["ipaddr"]
                    tbd.ctrlport = ((curr_node.data.values())[0])["port"]
                    tbd.alias = dev_info_str
                break


    def set_atten_dev(self, dev_info_str, curr_node):
        """Sets the attenuator device info.

        Args:
            dev_info_str (str): The string that includes device name and other device info.
            curr_node (node): The node object of SingleLinkedList class.
        """
        indx = dev_info_str.upper().find("ATTEN")

        if indx != -1:
            tbd = self.check_testbed_device_list("ATTENUATOR")
            if tbd is None:
                tbd = self.create_testbed_device_instance("WFA_ATTEN", "ATTENUATOR")
                self.test_mngr_initr.test_prog_mngr.test_prog.testbed_dev_list.append(tbd)

                tbd.ctrlipaddr = ((curr_node.data.values())[0])["ipaddr"]
                tbd.ctrlport = ((curr_node.data.values())[0])["port"]
                tbd.alias = dev_info_str
                return


    def set_testbed_ap_sta_dev(self, dev_info_str, curr_node, dev_type, flag=""):
        """Sets the testbed AP or STA info.

        Args:
            dev_info_str (str): The string that includes device name and other device info.
            curr_node (node): The node object of SingleLinkedList class.
            dev_type (str): AP or STA.
            flag (str): Indication of underlying variable format.
        """
        for tbd in self.test_mngr_initr.test_prog_mngr.test_prog.testbed_dev_list:
            indx = -1
            if tbd.dev_type == dev_type:
                if flag == "NOTVAR":
                    indx = dev_info_str.lower().find(tbd.dev_name.lower())
                    indx1 = indx + len(tbd.dev_name)
                else:
                    indx = dev_info_str.find(tbd.dev_name + tbd.dev_type)
                    indx1 = indx + len(tbd.dev_name + tbd.dev_type)

                if indx != -1:
                    if tbd.dev_type == "STA":
                        if dev_info_str[indx1:] == "_sta_wireless_ip":
                            tbd.testipaddr = (curr_node.data.values())[0]
                            break
                        if dev_info_str[indx1:] == "_sta_wireless_ipv6":
                            tbd.testipaddr_ipv6 = (curr_node.data.values())[0]
                            break
                        if dev_info_str[indx1:] == "_sta":
                            tbd.ctrlipaddr = ((curr_node.data.values())[0])["ipaddr"]
                            tbd.ctrlport = ((curr_node.data.values())[0])["port"]
                            if flag == "NOTVAR":
                                tbd.alias = dev_info_str
                            break

                    if tbd.dev_type == "AP":
                        if dev_info_str[indx1:] == "_ap":
                            tbd.ctrlipaddr = ((curr_node.data.values())[0])["ipaddr"]
                            tbd.ctrlport = ((curr_node.data.values())[0])["port"]
                            tbd.is_emd_ctrl_agt = True
                            if flag == "NOTVAR":
                                tbd.alias = dev_info_str
                            break
                        if dev_info_str[indx1:] == "IPAddress":
                            tbd.testipaddr = (curr_node.data.values())[0]
                            break
                        if dev_info_str[indx1:] == "UserName":
                            tbd.username = (curr_node.data.values())[0]
                            break
                        if dev_info_str[indx1:] == "Password":
                            tbd.password = (curr_node.data.values())[0]
                            break
                        if dev_info_str[indx1:] == "HostName":
                            tbd.hostname = (curr_node.data.values())[0]
                            break
                        if dev_info_str[indx1:] == "PowerSwitchPort":
                            tbd.pwrswtport = (curr_node.data.values())[0]
                            break
                        if dev_info_str[indx1:] == "SerialPortIPAddress":
                            if "ipaddr" in (curr_node.data.values())[0] and "port" in (curr_node.data.values())[0]:
                                tbd.serialserverip = ((curr_node.data.values())[0])["ipaddr"]
                                tbd.serialserverport = ((curr_node.data.values())[0])["port"]
                            else:
                                tbd.serialserverip = (curr_node.data.values())[0]
                            break
                        if dev_info_str[indx1:] == "MACAddress_24G":
                            tbd.macaddr_24g = (curr_node.data.values())[0]
                            break
                        if dev_info_str[indx1:] == "MACAddress2_24G":
                            tbd.macaddr_24g_1 = (curr_node.data.values())[0]
                            break
                        if dev_info_str[indx1:] == "MACAddress_5G":
                            tbd.macaddr_5g = (curr_node.data.values())[0]
                            break
                        if dev_info_str[indx1:] == "MACAddress2_5G":
                            tbd.macaddr_5g_1 = (curr_node.data.values())[0]
                            break

                    if dev_info_str[indx1:] == "MACAddress":
                        tbd.macaddr = (curr_node.data.values())[0]
                        break


    def set_sniffer_dev(self, dev_info_str, curr_node):
        """Sets the sniffer device info.

        Args:
            dev_info_str (str): The string that includes device name and other device info.
            curr_node (node): The node object of SingleLinkedList class.
        """
        tbd = self.check_testbed_device_list(dev_info_str)
        if tbd is None:
            tbd = self.create_testbed_device_instance(dev_info_str, "SNIFFER")
            self.test_mngr_initr.test_prog_mngr.test_prog.testbed_dev_list.append(tbd)

        tbd.ctrlipaddr = ((curr_node.data.values())[0])["ipaddr"]
        tbd.ctrlport = ((curr_node.data.values())[0])["port"]
        tbd.alias = dev_info_str


    def set_apconfig_dev(self, dev_info_str, curr_node):
        """Sets the APConfig device info.

        Args:
            dev_info_str (str): The string that includes device name and other device info.
            curr_node (node): The node object of SingleLinkedList class.
        """
        tbd = self.check_testbed_device_list("APConfig")
        if tbd is None:
            tbd = self.create_testbed_device_instance("APConfig", "APCONFIG")
            self.test_mngr_initr.test_prog_mngr.test_prog.testbed_dev_list.append(tbd)

        tbd.alias = dev_info_str
        tbd.ctrlipaddr = ((curr_node.data.values())[0])["ipaddr"]
        tbd.ctrlport = ((curr_node.data.values())[0])["port"]


    def set_pce_dev(self, dev_info_str, curr_node):
        """Sets the PCEndpoint device info.

        Args:
            dev_info_str (str): The string that includes device name and other device info.
            curr_node (node): The node object of SingleLinkedList class.
        """
        tbd = self.check_testbed_device_list("PCEndpoint")
        if tbd is None:
            tbd = self.create_testbed_device_instance("PCEndpoint", "PCENDPOINT")
            self.test_mngr_initr.test_prog_mngr.test_prog.testbed_dev_list.append(tbd)

        if dev_info_str == "wfa_console_ctrl":
            tbd.ctrlipaddr = ((curr_node.data.values())[0])["ipaddr"]
            tbd.ctrlport = ((curr_node.data.values())[0])["port"]
            tbd.alias = dev_info_str

        if dev_info_str == "wfa_console_tg":
            tbd.testipaddr = (curr_node.data.values())[0]


    def set_wfa_emt_dev(self, dev_info_str, curr_node, flag=""):
        """Sets the WFA EMT device info.

        Args:
            dev_info_str (str): The string that includes device name and other device info.
            curr_node (node): The node object of SingleLinkedList class.
        """
        indx = dev_info_str.upper().find("WFAEMT")

        if indx != -1 or flag == "NOTVAR":
            tbd = self.check_testbed_device_list("WFAEMT")
            if tbd is None:
                tbd = self.create_testbed_device_instance("WFAEMT", "WFAEMT")
                self.test_mngr_initr.test_prog_mngr.test_prog.testbed_dev_list.append(tbd)

            if flag == "NOTVAR":
                tbd.ctrlipaddr = ((curr_node.data.values())[0])["ipaddr"]
                tbd.ctrlport = ((curr_node.data.values())[0])["port"]
                tbd.alias = dev_info_str
                return

            indx = indx + len("WFAEMT")
            if dev_info_str[indx:] == "APIPAddress":
                tbd.testipaddr = (curr_node.data.values())[0]

            if dev_info_str[indx:] == "WirlessIP":
                tbd.wlipaddr = (curr_node.data.values())[0]

            if dev_info_str[indx:] == "Iface":
                tbd.testifname = (curr_node.data.values())[0]


    def set_pwr_swt_dev(self, dev_info_str, curr_node):
        """Sets the power switch device info.

        Args:
            dev_info_str (str): The string that includes device name and other device info.
            curr_node (node): The node object of SingleLinkedList class.
        """
        indx = dev_info_str.find("PowerSwitch")

        if indx != -1:
            tbd = self.check_testbed_device_list("PowerSwitch")
            if tbd is None:
                tbd = self.create_testbed_device_instance("PowerSwitch", "POWERSWITCH")
                self.test_mngr_initr.test_prog_mngr.test_prog.testbed_dev_list.append(tbd)
                tbd.alias = "PowerSwitch"
                
            indx = indx + len("PowerSwitch")
            if dev_info_str[indx:] == "IPAddress":
                tbd.ctrlipaddr = (curr_node.data.values())[0]
            if dev_info_str[indx:] == "UserName":
                tbd.username = (curr_node.data.values())[0]
            if dev_info_str[indx:] == "Password":
                tbd.password = (curr_node.data.values())[0]
            if dev_info_str[indx:] == "HostName":
                tbd.hostname = (curr_node.data.values())[0]


    def set_dut_dev(self, dev_info_str, curr_node, flag=""):
        """Sets the DUT device info.

        Args:
            dev_info_str (str): The string that includes device name and other device info.
            curr_node (node): The node object of SingleLinkedList class.
            flag (str): Indication of underlying variable format.
        """
        indx = -1
        indx1 = -1

        if re.search("Dut", dev_info_str, 0):
            indx = dev_info_str.find("Dut")

        if re.search("APUT", dev_info_str, 0):
            indx1 = dev_info_str.find("APUT")

        if indx != -1 or indx1 != -1 or flag == "NOTVAR":
            tbd = self.check_testbed_device_list("DUT")
            if tbd is None:
                tbd = self.create_testbed_device_instance("DUT", "DUT")
                self.test_mngr_initr.test_prog_mngr.test_prog.testbed_dev_list.append(tbd)

            if flag == "NOTVAR":
                if dev_info_str == "wfa_control_agent_dut":
                    tbd.ctrlipaddr = ((curr_node.data.values())[0])["ipaddr"]
                    tbd.ctrlport = ((curr_node.data.values())[0])["port"]
                    tbd.alias = dev_info_str
                if dev_info_str == "dut_wireless_ip":
                    tbd.testipaddr = (curr_node.data.values())[0]
                if dev_info_str == "dut_wireless_ipv6":
                    tbd.testipaddr_ipv6 = (curr_node.data.values())[0]
                return

            indx = indx + len("Dut")
            if dev_info_str[indx:] == "MacAddress_24G":
                tbd.macaddr_24g = (curr_node.data.values())[0]
            if dev_info_str[indx:] == "MacAddress_24G_1":
                tbd.macaddr_24g_1 = (curr_node.data.values())[0]
            if dev_info_str[indx:] == "MacAddress_5G":
                tbd.macaddr_5g = (curr_node.data.values())[0]
            if dev_info_str[indx:] == "MacAddress_5G_1":
                tbd.macaddr_5g_1 = (curr_node.data.values())[0]
            if dev_info_str[indx:] == "MacAddress":
                tbd.macaddr = (curr_node.data.values())[0]
            if dev_info_str[indx:] == "_Name":
                tbd.dev_name = (curr_node.data.values())[0]

            if indx1 != -1:
                indx1 = indx1 + len("APUT")
                if dev_info_str[indx1:] == "PowerSwitchPort":
                    tbd.pwrswtport = (curr_node.data.values())[0]
                if dev_info_str[indx1:] == "_uname":
                    tbd.username = (curr_node.data.values())[0]
                if dev_info_str[indx1:] == "_pword":
                    tbd.password = (curr_node.data.values())[0]
                if dev_info_str[indx1:] == "_hostname":
                    tbd.hostname = (curr_node.data.values())[0]


    def set_testbed_device(self):
        """Sets the testbed device info.
        """
        curr_node = self.ill.head
        while curr_node is not None:
            if curr_node.tag == "TESTBED":
                # curr_node.data is a dictionary                
                dev_info_str = (curr_node.data.keys())[0]

                for key in TestScriptElementType.script_testbed_devices:

                    searchObj = re.search(key, dev_info_str, re.I)
                    if searchObj:
                        if TestScriptElementType.script_testbed_devices[key] == TestScriptElementType.WFA_DUT:
                            self.set_dut_dev(dev_info_str, curr_node)
                        elif TestScriptElementType.script_testbed_devices[key] == TestScriptElementType.WFA_CONTROL_AGENT_DUT:
                            self.set_dut_dev(dev_info_str, curr_node, "NOTVAR")
                        elif TestScriptElementType.script_testbed_devices[key] == TestScriptElementType.WFA_CONTROL_AGENT_STA or TestScriptElementType.script_testbed_devices[key] == TestScriptElementType.WFA_CONTROL_AGENT_AP:
                            if TestScriptElementType.script_testbed_devices[key] == TestScriptElementType.WFA_CONTROL_AGENT_STA:
                                self.set_testbed_ap_sta_dev(dev_info_str, curr_node, "STA", "NOTVAR")
                            else:
                                self.set_testbed_ap_sta_dev(dev_info_str, curr_node, "AP", "NOTVAR")
                        elif TestScriptElementType.script_testbed_devices[key] == TestScriptElementType.WFA_TESTBEDSTA or TestScriptElementType.script_testbed_devices[key] == TestScriptElementType.WFA_TESTBEDAP:
                            if TestScriptElementType.script_testbed_devices[key] == TestScriptElementType.WFA_TESTBEDSTA:
                                self.set_testbed_ap_sta_dev(dev_info_str, curr_node, "STA", "")
                            else:
                                self.set_testbed_ap_sta_dev(dev_info_str, curr_node, "AP", "")
                        elif TestScriptElementType.script_testbed_devices[key] == TestScriptElementType.WFAEMT:
                            self.set_wfa_emt_dev(dev_info_str, curr_node)
                        elif TestScriptElementType.script_testbed_devices[key] == TestScriptElementType.WFA_EMT_CONTROL_AGNET:
                            self.set_wfa_emt_dev(dev_info_str, curr_node, "NOTVAR")
                        elif TestScriptElementType.script_testbed_devices[key] == TestScriptElementType.POWERSWITCH:
                            self.set_pwr_swt_dev(dev_info_str, curr_node)
                        elif TestScriptElementType.script_testbed_devices[key] == TestScriptElementType.WFA_APCONFIGSERVER:
                            self.set_apconfig_dev(dev_info_str, curr_node)
                        elif TestScriptElementType.script_testbed_devices[key] == TestScriptElementType.WFA_PCEDNPOINT:
                            self.set_pce_dev(dev_info_str, curr_node)
                        elif TestScriptElementType.script_testbed_devices[key] == TestScriptElementType.WFA_SNIFFER:
                            self.set_sniffer_dev(dev_info_str, curr_node)
                        elif TestScriptElementType.script_testbed_devices[key] == TestScriptElementType.WFA_RADIUSSERVER:
                            self.set_rad_svr_dev(dev_info_str, curr_node)
                        elif TestScriptElementType.script_testbed_devices[key] == TestScriptElementType.WFA_CONTROL_AGENT_OSUSERVER:
                            self.set_osu_svr_dev(dev_info_str, curr_node)
                        elif TestScriptElementType.script_testbed_devices[key] == TestScriptElementType.WFA_ATTENUATOR:
                            self.set_atten_dev(dev_info_str, curr_node)
                        else:
                            raise SyntaxError
                        break
            if curr_node.tag == "DISPLAYNAME":
                for tbd in self.test_mngr_initr.test_prog_mngr.test_prog.testbed_dev_list:
                    if tbd.alias == (curr_node.data.keys())[0]:
                        tbd.displayname = (curr_node.data.values())[0]
                        break

            curr_node = curr_node.next

        

class TestbedDevice:
    """The class of testbed device.

    Attributes:
        prog_name (str): The program name.
        dev_name (str): The device name.
        ctrlipaddr (str): The control network IP address.
        ctrlsubnet (str): The control network subnet.
        ctrlport (str): The control network port.
        testipaddr (str): The test network IP address.
        testsubnet (str): The test network subnet.
        testport (str): The test network port.
        testipaddr_ipv6 (str): The test network IPv6 address.
        ctrlifname (str): The control network interface name.
        testifname (str): The test network interface name.
        macaddr (str): The MAC address.
        hostname (str): The host name.
        osver (str): The os version.
        firmver (str): The firmware version.
        prodmodel (str): The product model number.
        drvver (str): The driver version.
        wtsver (str): The WTS version.
        alias (str): The alias name.
        displayname (str): The name displayed on console.

    """
    def __init__(self, prog_name):
        self.prog_name = prog_name
        self.dev_name = ""

        self.ctrlipaddr = ""
        self.ctrlsubnet = ""
        self.ctrlport = ""

        self.testipaddr = ""
        self.testsubnet = ""
        self.testport = ""
        self.testipaddr_ipv6 = ""

        self.ctrlifname = ""
        self.testifname = ""

        self.macaddr = ""

        self.hostname = ""
        self.osver = ""
        self.firmver = ""
        self.prodmodel = ""
        self.drvver = ""
        self.wtsver = ""

        # addition for Validation info(ca_get_version & device_get_info)
        self.ca_version = ""
        self.model = ""
        self.vendor = ""
        self.sw_version = ""
        self.validation_dict = {}
        ####################
        self.alias = ""
        self.displayname = ""
        # a dictionary storing the wireless configuration information
        self.config_dict = {}
        self.config_state = "Unconfigured"



class DUT(TestbedDevice):
    """The class of DUT device.

    Attributes:
        band (str): The band info.

    """
    def __init__(self, prog_name):
        TestbedDevice.__init__(self, prog_name)
        self.band = ""
        self.dev_type = "DUT"

        self.username = ""
        self.password = ""
        self.hostname = ""
        self.pwrswtport = ""
        self.state = ""
        self.macaddr_24g = ""
        self.macaddr_5g = ""
        self.macaddr_24g_1 = ""
        self.macaddr_5g_1 = ""
        self.is_emd_ctrl_agt = False



class TestBedSTA(TestbedDevice):
    """The class of testbed STA device.

    Attributes:
        number (str): The STA device number.
        dollar_var_name (str): The dollar variable name representing the device.
        num_var_name (str): The STA device variable name and number.

    """
    def __init__(self, prog_name):
        TestbedDevice.__init__(self, prog_name)
        self.dev_type = "STA"
        self.number = ""
        self.dollar_var_name = ""
        self.num_var_name = ""



class TestBedAP(TestbedDevice):
    """The class of testbed AP device.

    Attributes:
        username (str): The user name.
        password (str): The password.
        hostname (str): The host name.
        pwrswtport (str): The power switch port.
        state (str): The power on/off state.
        number (str): The power switch port number.
        serialserverip (str): The serial server IP.
        serialserverport (str): The serail server port.
        dollar_var_name (str): The dollar variable name of AP.
        num_var_name (str): The number variable name of AP.
        macaddr_24g (str): The 2.4G MAC address.
        macaddr_5g (str): The 5G MAC address.
        is_emd_ctrl_agt (boolean): The flag to indicate the embedded control agent.

    """
    def __init__(self, prog_name):
        TestbedDevice.__init__(self, prog_name)
        self.username = ""
        self.password = ""
        self.hostname = ""
        self.pwrswtport = ""
        self.state = ""
        self.number = ""
        self.serialserverip = ""
        self.serialserverport = ""
        self.dev_type = "AP"
        self.dollar_var_name = ""
        self.num_var_name = ""
        self.macaddr_24g = ""
        self.macaddr_5g = ""
        self.macaddr_24g_1 = ""
        self.macaddr_5g_1 = ""
        self.is_emd_ctrl_agt = False



class Sniffer(TestbedDevice):
    """The class of sniffer device.
    """
    def __init__(self, prog_name):
        TestbedDevice.__init__(self, prog_name)
        self.dev_type = "SNIFFER"



class PCEndpoint(TestbedDevice):
    """The class of PCEndpoint device.
    """
    def __init__(self, prog_name):
        TestbedDevice.__init__(self, prog_name)
        self.dev_type = "PCENDPOINT"



class APConfig(TestbedDevice):
    """The class of APConfig device.
    """
    def __init__(self, prog_name):
        TestbedDevice.__init__(self, prog_name)
        self.dev_type = "APCONFIG"



class WFAEMT(TestbedDevice):
    """The class of WFA EMT device.

    Attributes:
        wlipaddr (str): The wireless IP address.

    """
    def __init__(self, prog_name):
        TestbedDevice.__init__(self, prog_name)
        self.wlipaddr = ""
        self.dev_type = "WFAEMT"



class PowerSwitch(TestbedDevice):
    """The class of power switch.

    Attributes:
        username (str): The user name.
        password (str): The password.

    """
    def __init__(self, prog_name):
        TestbedDevice.__init__(self, prog_name)
        self.username = ""
        self.password = ""
        self.dev_type = "POWERSWITCH"



class RadiusServer(TestbedDevice):
    """The class of radius server.

    Attributes:
        shared_secret (str): The shared secret.
        supplicant (str): The supplicant.
        sta_supplicant (str): The supplicant that STA uses.
        eap_method (str): The EAP method used.
        rs_eap_cred_list (list): The list of radius server credentials.

    """
    def __init__(self, prog_name):
        TestbedDevice.__init__(self, prog_name)
        self.shared_secret = ""
        self.supplicant = ""
        self.sta_supplicant = ""
        self.eap_method = ""
        self.rs_eap_cred_list = []
        self.dev_type = "RADIUSSERVER"



class RadiusServerEAPCredential:
    """The Radius Server EAP method credential class.

    Attributes:
        root_cert_name (str): The root certificate name.
        cli_cert_name (str): The client certificate name.
        tls_username (str): The TLS method user name.
        username (str): The user name
        password (str): The password.
        gtc_username (str): The GTC user name.
        gtc_password (str): The GTC password.
        wrong_username (str): Incorrect user name to use.

    """
    def __init__(self):
        self.root_cert_name = ""
        self.cli_cert_name = ""
        self.tls_username = ""

        self.username = ""
        self.password = ""
        self.gtc_username = ""
        self.gtc_password = ""
        self.wrong_username = ""



class OSUServer(TestbedDevice):
    """The class of OSU server device.
    """
    def __init__(self, prog_name):
        TestbedDevice.__init__(self, prog_name)
        self.dev_type = "OSUSERVER"



class Attenuator(TestbedDevice):
    """The class of attenuator device.
    """
    def __init__(self, prog_name):
        TestbedDevice.__init__(self, prog_name)
        self.dev_type = "ATTENUATOR"
