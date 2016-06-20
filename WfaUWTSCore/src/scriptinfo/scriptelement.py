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
﻿
class ElementTypeError(Exception):
    """The summary line for a class docstring should fit on one line.
    """
    pass



class TestScriptElement:
    """A class of test script element.
    """
    def __init__(self, test_script_source):
        self.element_type = None
        self.test_script_source = test_script_source
        self.line_number = test_script_source.line_number
        self.segment_text = None
        self.segment_value = None

        self.extract()


    # Extract script element
    def extract(self):
        """Extracts the segment text and value from the current segment
        """
        # convert to string
        self.segment_text = str(self.current_segment())
        self.element_type = TestScriptElementType.get_element_type(self.segment_text)
        self.segment_value = None

    
    def current_segment(self):
        """Calls test script source's current_segment() to return the current segment.
        """
        return self.test_script_source.current_segment()

    
    def next_segment(self):
        """Calls test script source's next_segment() to return the next segment.
        """
        return self.test_script_source.next_segment()



class TestFeatureElement(TestScriptElement):
    """A class of test feature element.
    """

    def __init__(self, test_script_source):
        TestScriptElement.__init__(self, test_script_source)


    def extract(self):
        """Extracts the segment text value.
        """
        TestScriptElement.extract(self)



class TestbedDeviceElement(TestScriptElement):
    """A class of testbed device element.
    """

    def __init__(self, test_script_source):
        TestScriptElement.__init__(self, test_script_source)


    def extract(self):
        """Extracts the segment text value.
        """
        TestScriptElement.extract(self)



class CAPICommandElement(TestScriptElement):
    """A class of capi command element.
    """

    def __init__(self, test_script_source):
        self.paramstr = ""
        TestScriptElement.__init__(self, test_script_source)

    def extract(self):
        """Extracts the segment text value.
        """
        TestScriptElement.extract(self)
        element = self.segment_text.split(',')
        # capi command name
        self.segment_text = element[0]
        self.paramstr = ','.join(element[1:]) if len(element) > 1 else ""



class CAPIReturnElement(TestScriptElement):
    """A class of capi return element.
    """

    def __init__(self, test_script_source):
        self.paramstr = ""
        TestScriptElement.__init__(self, test_script_source)

    def extract(self):
        """Extracts the segment text value.
        """
        TestScriptElement.extract(self)
        element = self.segment_text.split(',')
        # capi command name
        self.segment_text = element[0]
        if len(element) == 1:
            self.paramstr = ""
        elif len(element) == 2:
            self.paramstr = element[1]
        elif len(element) > 2:
            self.paramstr = ','.join(element[1:])
        else:
            raise SyntaxError



class EndOfLineElement(TestScriptElement):
    """A class of script end of line element.
    """

    def __init__(self, test_script_source):
        TestScriptElement.__init__(self, test_script_source)

    def extract(self):
        """Extracts the segment text value.
        """
        TestScriptElement.extract(self)



class ScriptReservedWordsElement(TestScriptElement):
    """A class of script reserved element.
    """

    def __init__(self, test_script_source):
        TestScriptElement.__init__(self, test_script_source)

    def extract(self):
        """Extracts the segment text value.
        """
        TestScriptElement.extract(self)



class ScriptSpecialSymbolElement(TestScriptElement):
    """A class of script string element.
    """

    def __init__(self, test_script_source):
        TestScriptElement.__init__(self, test_script_source)

    def extract(self):
        """Extracts the segment text value.
        """
        TestScriptElement.extract(self)



class ScriptStringElement(TestScriptElement):
    """A class of script string element.
    """

    def __init__(self, test_script_source):
        TestScriptElement.__init__(self, test_script_source)

    def extract(self):
        """Extracts the segment text value.
        """
        TestScriptElement.extract(self)



class ScriptVariableElement(TestScriptElement):
    """A class of script variable element.
    """

    def __init__(self, test_script_source):
        TestScriptElement.__init__(self, test_script_source)

    def extract(self):
        """Extracts the segment text value.
        """
        TestScriptElement.extract(self)



class ScriptErrorElement(TestScriptElement):
    """A class of script error element.
    """

    def __init__(self, test_script_source):
        TestScriptElement.__init__(self, test_script_source)

    def extract(self):
        """Extracts the segment text value.
        """
        element = self.current_segment()
        self.segment_text = str(element)



class TestScriptElementType:
    """A class that defines all the elements contained in test script files.
    """

    ####################################
    # Reserved words
    ####################################
    # "if"
    IF = "IF"
    # "else"
    ELSE = "ELSE"
    # "endif"
    ENDIF = "ENDIF"
    # "or"
    OR = "OR"
    # "and"
    AND = "AND"
    # "math"
    MATH = "MATH"
    # "rand"
    RAND = "RAND"
    # "_dnb_"
    DNB = "DNB"
    # "_inv"
    PINV = "_INV"
    # "inv_"
    INVP = "INV_"
    # "exit"
    EXIT = "EXIT"
    # "sleep"
    SLEEP = "SLEEP"
    # "r_info"
    RINFO = "R_INFO"
    # "define"
    DEFINE = "DEFINE"
    # "echo"
    ECHO = "ECHO"
    # "wfa_test_commands"
    WFA_TEST_COMMANDS = "WFA_TEST_COMMANDS"
    # "info"
    INFO = "INFO"
    # "wfa_test_commands_init"
    WFA_TEST_COMMANDS_INIT = "WFA_TEST_COMMANDS_INIT"
    # "pause"
    PAUSE = "PAUSE"
    # "getuserinput"
    GETUSERINPUT = "GETUSERINPUT"

    # "DisplayName"
    DISPLAYNAME = "DISPLAYNAME"
    # sniffer_enable
    SNIFFER_ENABLE = "SNIFFER_ENABLE"
    # "stream"
    STREAM = "STREAM"
    # "max_throughput"
    MAX_THROUGHPUT = "MAX_THROUGHPUT"
    # "payload"
    PAYLOAD = "PAYLOAD"
    PAYLOAD16K = "PAYLOAD16K"
    # "stream_trans"
    STREAM_TRANS = "STREAM_TRANS"
    # "ResultCheck"
    RESULT_CHECK = "RESULT_CHECK"
    # "search"
    SEARCH = "SEARCH"
    # "cat"
    CAT = "CAT"
    # "mexpr"
    MEXPR = "MEXPR"

    # "echo_IfNoWTS"
    ECHO_INFOWTS = "ECHO_INFOWTS"
    # "IfNoWTS"
    IFNOWTS = "IFNOWTS"
    # "UserInput_IfNoWTS"
    USERINPUT_IFNOWTS = "USERINPUT_IFNOWTS"
    # "generate_randnum"
    GENERATE_RANDNUM = "GENERATE_RANDNUM"

    # "Phase"
    PHASE = "PHASE"
    # "StoreThroughput"
    STORETHROUGHPUT = "STORETHROUGHPUT"
    # "resultwmm"
    RESULT_WMM = "RESULT_WMM"
    # "resultwmm_1"
    RESULT_WMM1 = "RESULT_WMM1"
    # "resultwmm_2"
    RESULT_WMM2 = "RESULT_WMM2"
    # "resultIBSS"
    RESULT_IBSS = "RESULT_IBSS"

    # "CheckThroughput"
    CHECKTHROUGHPUT = "CHECKTHROUGHPUT"
    # "CheckMCSThroughput"
    CHECKMCSTHROUGHPUT = "CHECKMCSTHROUGHPUT"
    # "CheckDT4Result"
    CHECKDT4RESULT = "CHECKDT4RESULT"
    # "TransactionThroughput"
    TRANSACTIONTHROUGHPUT = "TRANSACTIONTHROUGHPUT"

    # "manual_check_info"
    MANUAL_CHECK_INFO = "MANUAL_CHECK_INFO"
    # "add_media_file"
    ADD_MEDIA_FILE = "ADD_MEDIA_FILE"

    #"AddSTAVersionInfo"
    ADD_STA_VERSION_INFO = "ADD_STA_VERSION_INFO"

    SOCKTIMEOUT = "SOCKTIMEOUT"

    PING_INTERNAL_CHECK = "PING_INTERNAL_CHECK"

    APPEND = "APPEND"

    CONFIG_MULTI_SUBRESULTS = "CONFIG_MULTI_SUBRESULTS"

    EXTERNAL_FUNC = "EXTERNAL_FUNC"

    ####################################
    # Special symbols
    ####################################
    # "+"
    PLUS = "ADD"
    # "-"
    MINUS = "SUBTRACT"
    # "*"
    MULTIPLY = "MULTIPLY"
    # "/"
    DIVIDE = "DIVIDE"
    # "%"
    MODULO = "MODULO"
    # "="
    EQUALS = "EQ"
    # "<>"
    NOT_EQUALS = "NE"
    # "<"
    LESS_THAN = "LT"
    # "<="
    LESS_EQUALS = "LE"
    # ">="
    GREATER_EQUALS = "GE"
    # ">"
    GREATER_THAN = "GT"

    ####################################
    # Reserved CAPIs
    ####################################
    # "traffic_agent_send"
    TRAFFIC_AGENT_SEND = "TRAFFIC_AGENT_SEND"
    # "traffic_agent_receive_stop"
    TRAFFIC_AGENT_RECEIVE_STOP = "TRAFFIC_AGENT_RECEIVE_STOP"
    # "traffic_send_ping"
    TRAFFIC_SEND_PING = "TRAFFIC_SEND_PING"
    TRAFFIC_AGENT_RESET = "TRAFFIC_AGENT_RESET"
    TRAFFIC_STOP_PING = "TRAFFIC_STOP_PING"
    TRAFFIC_AGENT_CONFIG = "TRAFFIC_AGENT_CONFIG"
    TRAFFIC_AGENT_RECEIVE_START = "TRAFFIC_AGENT_RECEIVE_START"


    AP_SET_WIRELESS = "AP_SET_WIRELESS"
    AP_SET_SECURITY = "AP_SET_SECURITY"
    AP_CONFIG_COMMIT = "AP_CONFIG_COMMIT"
    AP_CA_VERSION = "AP_CA_VERSION"
    AP_SET_11N_WIRELESS = "AP_SET_11N_WIRELESS"
    AP_SET_PMF = "AP_SET_PMF"
    AP_SET_APQOS = "AP_SET_APQOS"
    AP_SET_STAQOS = "AP_SET_STAQOS"
    AP_SET_RADIUS = "AP_SET_RADIUS"
    AP_REBOOT = "AP_REBOOT"
    AP_RESET_DEFAULT = "AP_RESET_DEFAULT"
    AP_GET_INFO = "AP_GET_INFO"
    AP_DEAUTH_STA = "AP_DEAUTH_STA"
    AP_GET_MAC_ADDRESS = "AP_GET_MAC_ADDRESS"
    AP_SET_HS2 = "AP_SET_HS2"
    AP_SET_RRM = "AP_SET_RRM"
    AP_SEND_ADDBA_REQ = "AP_SEND_ADDBA_REQ"
    AP_SET_11D = "AP_SET_11D"
    AP_SET_11H = "AP_SET_11H"
    AP_SET_RRM = "AP_SET_RRM"

    SNIFFER_CHECK_P2P_NOA_WMMPS_RETRIGGER = "SNIFFER_CHECK_P2P_NOA_WMMPS_RETRIGGER"
    #sniffer_check_p2p_NoA_start_time
    SNIFFER_CHECK_P2P_NOA_START_TIME = "SNIFFER_CHECK_P2P_NOA_START_TIME"
    SNIFFER_CHECK_P2P_NOA_DURATION = "SNIFFER_CHECK_P2P_NOA_DURATION"
    # sniffer_check_p2p_opps_go
    SNIFFER_CHECK_P2P_OPPS_GO = "SNIFFER_CHECK_P2P_OPPS_GO"
    SNIFFER_CHECK_P2P_OPPS_CLIENT = "SNIFFER_CHECK_P2P_OPPS_CLIENT"
    SNIFFER_GET_FIELD_VALUE = "SNIFFER_GET_FIELD_VALUE"
    SNIFFER_CONTROL_FIELD_CHECK = "SNIFFER_CONTROL_FIELD_CHECK"
    SNIFFER_CONTROL_START = "SNIFFER_CONTROL_START"
    # "sniffer_control_stop"
    SNIFFER_CONTROL_STOP = "SNIFFER_CONTROL_STOP"
    SNIFFER_FRAME_CHECK = "SNIFFER_FRAME_CHECK"
    # "sniffer_check_pmk_id"
    SNIFFER_CHECK_PMK_ID = "SNIFFER_CHECK_PMK_ID"
    SNIFFER_CONTROL_FILTER_CAPTURE = "SNIFFER_CONTROL_FILTER_CAPTURE"
    SNIFFER_GET_INFO = "SNIFFER_GET_INFO"
    SNIFFER_INJECT_FRAME = "SNIFFER_INJECT_FRAME"
    SNIFFER_CLEAR_COUNTERS = "SNIFFER_CLEAR_COUNTERS"
    SNIFFER_CONTROL_CAPTURE_DECRYPT = "SNIFFER_CONTROL_CAPTURE_DECRYPT"
    SNIFFER_CONTROL_UPLOAD = "SNIFFER_CONTROL_UPLOAD"
    WFA_AV_CAPTURE = "WFA_AV_CAPTURE"
    SNIFFER_MEDIA_CHECK = "SNIFFER_MEDIA_CHECK"
    WFA_MERGE_TRACE = "WFA_MERGE_TRACE"
    WFA_WFDS_GENERATE_HASH = "WFA_WFDS_GENERATE_HASH"
    SNIFFER_STREAM_CHECK = "SNIFFER_STREAM_CHECK"
    SNIFFER_CONTROL_SUBTASK = "SNIFFER_CONTROL_SUBTASK"
    SNIFFER_FETCH_FILE = "SNIFFER_FETCH_FILE"
    SNIFFER_DECRYPT_TRACE = "SNIFFER_DECRYPT_TRACE"
    SNIFFER_CHECK_TIME_DIFFERENCE = "SNIFFER_CHECK_TIME_DIFFERENCE"
    SNIFFER_CHECK_DSCV_WINDOW = "SNIFFER_CHECK_DSCV_WINDOW"
    WFA_SNIFFER_CHECK_RETRY = "WFA_SNIFFER_CHECK_RETRY"
    
    CA_GET_VERSION = "CA_GET_VERSION"
    DEVICE_GET_INFO = "DEVICE_GET_INFO"
    DEVICE_LIST_INTERFACES = "DEVICE_LIST_INTERFACES"
    # "sta_is_connected"
    STA_IS_CONNECTED = "STA_IS_CONNECTED"
    STA_DISCONNECT = "STA_DISCONNECT"
    STA_ASSOCIATE = "STA_ASSOCIATE"
    STA_GET_BSSID = "STA_GET_BSSID"
    STA_GET_IP_CONFIG = "STA_GET_IP_CONFIG"
    STA_PRESET_TESTPARAMETERS = "STA_PRESET_TESTPARAMETERS"
    STA_GET_INFO = "STA_GET_INFO"
    STA_SET_ENCRYPTION = "STA_SET_ENCRYPTION"
    STA_SET_IP_CONFIG = "STA_SET_IP_CONFIG"
    STA_GET_MAC_ADDRESS = "STA_GET_MAC_ADDRESS"
    STA_VERIFY_IP_CONNECTION = "STA_VERIFY_IP_CONNECTION"
    STA_SET_PSK = "STA_SET_PSK"
    STA_SET_EAPTLS = "STA_SET_EAPTLS"
    STA_SET_EAPTTLS = "STA_SET_EAPTTLS"
    STA_SET_EAPSIM = "STA_SET_EAPSIM"
    STA_SET_PEAP = "STA_SET_PEAP"
    STA_SET_EAPFAST = "STA_SET_EAPFAST"
    STA_SET_EAPAKA = "STA_SET_EAPAKA"
    STA_SET_UAPSD = "STA_SET_UAPSD"
    STA_SET_IBSS = "STA_SET_IBSS"
    STA_SET_MODE = "STA_SET_MODE"
    STA_SET_WMM = "STA_SET_WMM"
    STA_UP_LOAD = "STA_UP_LOAD"
    STA_SET_SYSTIME = "STA_SET_SYSTIME"
    STA_SET_11N = "STA_SET_11N"
    STA_SET_RIFS_TEST = "STA_SET_RIFS_TEST"
    STA_SET_WIRELESS = "STA_SET_WIRELESS"
    STA_SEND_ADDBA = "STA_SEND_ADDBA"
    STA_SEND_COEXIST_MGMT = "STA_SEND_COEXIST_MGMT"
    STA_GET_P2P_DEV_ADDRESS = "STA_GET_P2P_DEV_ADDRESS"
    STA_SET_P2P = "STA_SET_P2P"
    STA_START_AUTONOMOUS_GO = "STA_START_AUTONOMOUS_GO"
    STA_P2P_CONNECT = "STA_P2P_CONNECT"
    STA_P2P_START_GROUP_FORMATION = "STA_P2P_START_GROUP_FORMATION"
    STA_P2P_DISSOLVE = "STA_P2P_DISSOLVE"
    STA_SEND_P2P_INVITATION_REQ = "STA_SEND_P2P_INVITATION_REQ"
    STA_ACCEPT_P2P_INVITATION_REQ = "STA_ACCEPT_P2P_INVITATION_REQ"
    STA_SEND_P2P_PROVISION_DIS_REQ = "STA_SEND_P2P_PROVISION_DIS_REQ"
    STA_SET_WPS_PBC = "STA_SET_WPS_PBC"
    STA_WPS_READ_PIN = "STA_WPS_READ_PIN"
    STA_WPS_READ_LABEL = "STA_WPS_READ_LABEL"
    STA_WPS_ENTER_PIN = "STA_WPS_ENTER_PIN"
    STA_GET_PSK = "STA_GET_PSK"
    STA_P2P_RESET = "STA_P2P_RESET"
    STA_GET_P2P_IP_CONFIG = "STA_GET_P2P_IP_CONFIG"
    STA_SEND_P2P_PRESENCE_REQ = "STA_SEND_P2P_PRESENCE_REQ"
    STA_SET_SLEEP = "STA_SET_SLEEP"
    STA_SET_OPPORTUNISTIC_PS = "STA_SET_OPPORTUNISTIC_PS"
    STA_SEND_SERVICE_DISCOVERY_REQ = "STA_SEND_SERVICE_DISCOVERY_REQ"
    STA_ADD_ARP_TABLE_ENTRY = "STA_ADD_ARP_TABLE_ENTRY"
    STA_BLOCK_ICMP_RESPONSE = "STA_BLOCK_ICMP_RESPONSE"
    STA_SET_SECURITY = "STA_SET_SECURITY"
    STA_SET_MACADDR = "STA_SET_MACADDR"
    STA_RESET_DEFAULT = "STA_RESET_DEFAULT"
    STA_RESET_PARM = "STA_RESET_PARM"
    STA_SET_RFEATURE = "STA_SET_RFEATURE"
    STA_SET_RADIO = "STA_SET_RADIO"
    DEV_SEND_FRAME = "DEV_SEND_FRAME"
    STA_HS2_ASSOCIATE = "STA_HS2_ASSOCIATE"
    STA_BSSID_POOL = "STA_BSSID_POOL"
    STA_ADD_CREDENTIAL = "STA_ADD_CREDENTIAL"
    START_WFD_CONNECTION = "START_WFD_CONNECTION"
    CONNECT_GO_START_WFD = "CONNECT_GO_START_WFD"
    STA_GENERATE_EVENT = "STA_GENERATE_EVENT"
    REINVOKE_WFD_SESSION = "REINVOKE_WFD_SESSION"
    STA_GET_PARAMETER = "STA_GET_PARAMETER"
    STA_SET_POWER_SAVE = "STA_SET_POWER_SAVE"
    STA_EXEC_ACTION = "STA_EXEC_ACTION"
    STA_INVOKE_COMMAND = "STA_INVOKE_COMMAND"
    STA_MANAGE_SERVICE = "STA_MANAGE_SERVICE"
    STA_GET_EVENT_DETAILS = "STA_GET_EVENT_DETAILS"
    STA_POLICY_UPDATE = "STA_POLICY_UPDATE"
    STA_SET_PWRSAVE = "STA_SET_PWRSAVE"
    STA_SCAN = "STA_SCAN"
    STA_GET_EVENTS = "STA_GET_EVENTS"
    STA_NFC_ACTION = "STA_NFC_ACTION"
    STA_REASSOCIATE = "STA_REASSOCIATE"
    STA_REASSOC = "STA_REASSOC"
    STA_OSU = "STA_OSU"

    SERVER_RESET_DEFAULT = "SERVER_RESET_DEFAULT"
    SERVER_REQUEST_STATUS = "SERVER_REQUEST_STATUS"
    SERVER_SET_PARAMETER = "SERVER_SET_PARAMETER"
    SERVER_GET_INFO = "SERVER_GET_INFO"
    SERVER_CA_GET_VERSION = "SERVER_CA_GET_VERSION"
    
    WFA_ACA_GET = "WFA_ACA_GET"
    WFA_ACA_SET = "WFA_ACA_SET"
    WFA_ACA_ACT = "WFA_ACA_ACT"

    WFAEMT_CONFIG_NAV = "WFAEMT_CONFIG_NAV"
    WFAEMT_START_TEST = "WFAEMT_START_TEST"
    WFAEMT_STOP_TEST = "WFAEMT_STOP_TEST"
    WFAEMT_START_STAUT_MIC_TEST = "WFAEMT_START_STAUT_MIC_TEST"
    WFAEMT_STOP_STAUT_MIC_TEST = "WFAEMT_STOP_STAUT_MIC_TEST"
    WFAEMT_CONFIG_STAUT_MIC = "WFAEMT_CONFIG_STAUT_MIC"
    
    ACCESSPOINT = "ACCESSPOINT"
    POWER_SWITCH = "POWER_SWITCH"
    POWER_SWITCH_CTRL = "POWER_SWITCH_CTRL"


    ####################################
    # Testbed device element
    ####################################
    # "wfa_control_agent_sta"
    WFA_CONTROL_AGENT_STA = "WFA_CONTROL_AGENT_STA"
    # "wfa_control_agent_ap"
    WFA_CONTROL_AGENT_AP = "WFA_CONTROL_AGENT_AP"
    # "wfa_control_agent_dut"
    WFA_CONTROL_AGENT_DUT = "WFA_CONTROL_AGENT_DUT"
    
    WFA_DUT = "WFA_DUT"
    WFA_PCEDNPOINT = "WFA_PCEDNPOINT"

    # "wfa_sniffer"
    WFA_SNIFFER = "WFA_SNIFFER"

    WFA_RADIUSSERVER = "WFA_RADIUSSERVER"

    WFA_CONTROL_AGENT_OSUSERVER = "WFA_CONTROL_AGENT_OSUSERVER"

    WFA_TESTBEDAP = "WFA_TESTBEDAP"
    WFA_TESTBEDSTA = "WFA_TESTBEDSTA"

    # PowerSwitch
    POWERSWITCH = "POWERSWITCH"
    # TestbedAPConfigServer
    WFA_APCONFIGSERVER = "WFA_APCONFIGSERVER"
    # WFAEMTAP
    WFAEMT = "WFAEMT"

    WFA_ATTENUATOR = "WFA_ATTENUATOR"
    
    # wfa_wfaemt_control_agent
    WFA_EMT_CONTROL_AGNET = "WFA_EMT_CONTROL_AGNET"

    ####################################
    # DUT feature element
    ####################################
    TLS = "TLS"
    TTLS = "TTLS"
    PEAP0 = "PEAP0"
    PEAP1 = "PEAP1"
    FAST = "FAST"
    SIM = "SIM"
    AKA = "AKA"
    AKA_PRIME = "AKA\'"
    PWD = "PWD"
    DUT_TYPE = "DUT_TYPE"
    DUT_BAND = "DUT_BAND"
    DUT_CATEGORY = "DUT_CATEGORY"
    WEP = "WEP"
    PRE_AUTH = "PRE_AUTH"
    _11H = "11H"
    SUPPORTED_CHANNEL_WIDTH = "SupportedChannelWidth"
    STREAMS = "STREAMS"
    GREENFIELD = "GREENFIELD"
    SGI20 = "SGI20"
    SGI40 = "SGI40"
    RIFS_TX = "RIFS_TX"
    COEXISTENCE_2040 = "COEXISTENCE_2040"
    STBC_RX = "STBC_RX"
    STBC_TX = "STBC_TX"
    MCS32 = "MCS32"
    WTSSUPPORT = "WTSSUPPORT"
    OBSS = "OBSS"
    AMPDU_TX = "AMPDU_TX"
    AP_CONCURRENT = "AP_CONCURRENT"
    _11D = "11D"
    STAUT_PM = "STAUT_PM"
    OPEN_MODE = "OPEN_MODE"
    MIXEDMODE_WPA2WPA = "MIXEDMODE_WPA2WPA"
    PMF_OOB = "PMF_OOB"
    DUTEAPMETHOD = "DUTEAPMethod"
    WTS_CONTROLAGENT_SUPPORT = "WTS_ControlAgent_Support"
    ASD = "ASD"
    TDLSDISCREQ = "TDLSDISCREQ"
    PUSLEEPSTA = "PUSLEEPSTA"

    BSS_TRANS_QUERY_SUPPORT = "BSS_TRANS_QUERY_SUPPORT"
    TSM_SUPPORT = "TSM_SUPPORT"
    NFC_INTERFACE_FLAG = "NFC_INTERFACE_FLAG"
    NFC_SUPPORT_FLAG = "NFC_SUPPORT_FLAG"
    P2P_WMM_PS = "P2P_WMM_PS"
    P2P_11N_MULTI_STREAM_SUPPORT = "P2P_11N_MULTI_STREAM_SUPPORT"
    P2P_GO_OPPORTUNISTIC_PS_SUPPORT = "P2P_GO_OPPORTUNISTIC_PS_SUPPORT"
    P2P_GO_NOTICE_OF_ABSENCE_SUPPORT = "P2P_GO_NOTICE_OF_ABSENCE_SUPPORT"
    P2P_INTRA_BSS_BIT_CONF_SUPPORT = "P2P_INTRA_BSS_BIT_CONF_SUPPORT"
    P2P_GO_MULTI_CLIENT_SUPPORT = "P2P_GO_MULTI_CLIENT_SUPPORT"
    P2P_MANAGED_SUPPORT = "P2P_MANAGED_SUPPORT"
    P2P_SERVICE_DISCOVERY_SUPPORT = "P2P_SERVICE_DISCOVERY_SUPPORT"
    P2P_DISCOVERABILITY_EXCHANGE_SUPPORT = "P2P_DISCOVERABILITY_EXCHANGE_SUPPORT"
    P2P_EXTENDED_LISTEN_TIMING_SUPPORT = "P2P_EXTENDED_LISTEN_TIMING_SUPPORT"
    P2P_DUAL_BAND_SUPPORT = "P2P_DUAL_BAND_SUPPORT"
    P2P_PERSISTENT_GROUP_SUPPORT = "P2P_PERSISTENT_GROUP_SUPPORT"
    P2P_INVITATION_USER_CONF = "P2P_INVITATION_USER_CONF"
    P2P_INVITATION_PROCEDURE_SUPPORT = "P2P_INVITATION_PROCEDURE_SUPPORT"
    P2P_CROSS_CONNECTION_BIT_CONF_SUPPORT = "P2P_CROSS_CONNECTION_BIT_CONF_SUPPORT"
    P2P_MULTI_CHANNEL_CONCURRENCY_SUPPORT = "P2P_MULTI_CHANNEL_CONCURRENCY_SUPPORT"
    P2P_CONCURRENCY_SUPPORT = "P2P_CONCURRENCY_SUPPORT"
    P2P_GO_INTENT_VALUE_CONFIGURATION = "P2P_GO_INTENT_VALUE_CONFIGURATION"
    WPS_LABEL = "WPS_LABEL"
    WPS_KEYPAD = "WPS_KEYPAD"
    WPS_DISPLAY = "WPS_DISPLAY"
    WPS_PUSHBUTTON = "WPS_PUSHBUTTON"
    INTERNAL_BATTERY_POWERED = "INTERNAL_BATTERY_POWERED"
    MOBILE_AP = "MOBILE_AP"
    RX_LDPC = "RX_LDPC"
    TX_LDPC = "TX_LDPC"
    TX_SU_BEAMFORMEE = "TX_SU_BEAMFORMEE"
    TX_SU_BEAMFORMER = "TX_SU_BEAMFORMER"
    RX_AMPDU_OF_AMSDU = "RX_A-MPDU_OF_A-MSDU"
    RX_MSC_8_9 = "RX_MSC_8-9"
    SGI80 = "SGI80"
    SGI80_RX = "SGI80_RX"
    DUAL_BAND = "DUAL_BAND"
    TPC_CHANNEL_SWITCH = "TPC_CHANNEL_SWITCH"
    CHANNEL_SWITCH = "CHANNEL_SWITCH"
    TPC_SUPPORT = "TPC_SUPPORT"
    COUNTRY_CODE = "COUNTRY_CODE"
    SPECTRUM_MANAGEMENT_BIT = "SPECTRUM_MANAGEMENT_BIT"
    DUTOOBPASSPHRASE = "DUTOOBPASSPHRASE"
    DUTOOBSECURITY = "DUTOOBSECURITY"
    DUTOOBSSID = "DUTOOBSSID"
    HS2_APUT_EXTERNAL_FILTERING = "HS2_APUT_EXTERNAL_FILTERING"
    HS2_APUT_INBUILT_FILTERING = "HS2_APUT_INBUILT_FILTERING"
    HS2_APUT_EXTERNAL_ANQP_SERVER = "HS2_APUT_EXTERNAL_ANQP_SERVER"
    HS2_APUT_4FRAME_GAS = "HS2_APUT_4FRAME_GAS"
    #HS2_APUT_OPCLASS_INDICATION = "HS2_APUT_OPCLASS_INDICATION"
    HS2_STAUT_HREALM_QUERY = "HS2_STAUT_HREALM_QUERY"
    HS2_STAUT_KEYPAD = "HS2_STAUT_KEYPAD"
    HS2_STAUT_DISPLAY = "HS2_STAUT_DISPLAY"
    HS2_STAUT_IPV6 = "HS2_STAUT_IPV6"
    HS2_STAUT_SIM = "HS2_STAUT_SIM"

    HS2_STAUT_CERT_RETRIEVAL = "HS2_STAUT_CERT_RETRIEVAL"
    HS2_STAUT_PRSMO_RETRIEVAL = "HS2_STAUT_PRSMO_RETRIEVAL"
    HS2_STAUT_OPCLASS_INDICATION = "HS2_STAUT_OPCLASS_INDICATION"
    HS2_STAUT_HREALM_QUERY = "HS2_STAUT_HREALM_QUERY"
    HS2_STAUT_STATIC_IPV6 = "HS2_STAUT_STATIC_IPV6"
    HS2_STAUT_STATIC_IPV4 = "HS2_STAUT_STATIC_IPV4"
    HS2_NETWORK_SELECTION = "HS2_NETWORK_SELECTION"
    HS2_INDICATION_UI = "HS2_INDICATION_UI"
    HS2_STAUT_IPV6 = "HS2_STAUT_IPV6"
    HS2_DUTTYPE = "HS2_DUTTYPE"

    SCAN_TIME = "SCAN_TIME"
    PERIODICITY = "PERIODICITY"
    MAXATTENLVL = "MAXATTENLVL"
    A_ATTNLVL = "A_ATTNLVL"
    NAN_FURTHERAVAILATTR = "NAN_FURTHERAVAILATTR"
    AUTO_FOLLOWUP = "AUTO_FOLLOWUP"
    DB_CLOSE_PROX = "DB_CLOSE_PROX"
    SERVICE_NAME = "SERVICE_NAME"
    DUTMATCHFILTER = "DUTMATCHFILTER"
    NAN_PASSIVESUBSCRIBE = "NAN_PASSIVESUBSCRIBE"
    NAN_ACTIVESUBSCRIBE = "NAN_ACTIVESUBSCRIBE"
    NAN_SOLICITEDPUBLISH = "NAN_SOLICITEDPUBLISH"
    NAN_UNSOLICITEDPUBLISH = "NAN_UNSOLICITEDPUBLISH"
    OPER_CHN_5G = "OPER_CHN_5G"

    PMF_SHA1SHA256_SUPPORT = "PMF_SHA1SHA256_SUPPORT"
    PMF_BCAST_DISCONNECT_SUPPORT = "PMF_BCAST_DISCONNECT_SUPPORT"
    PMF_UNICAST_DISCONNECT_SUPPORT = "PMF_UNICAST_DISCONNECT_SUPPORT"
    PMF_REQUIRED_SUPPORT = "PMF_REQUIRED_SUPPORT"
    WPA = "WPA"
    PUAPSDSLEEPSTA_SUPPORT = "PUAPSDSLEEPSTA_SUPPORT"
    DISCOVERYREQUEST_SUPPORT = "DISCOVERYREQUEST_SUPPORT"

    WFD_OPTIONAL_VIDEO_LIST = "WFD_OPTIONAL_VIDEO_LIST"
    WFD_VIDEOFORMAT3 = "WFD_VIDEOFORMAT3"
    WFD_VIDEOFORMAT2 = "WFD_VIDEOFORMAT2"
    WFD_VIDEOFORMAT1 = "WFD_VIDEOFORMAT1"
    WFD_AV_FORMAT_CHANGE_SUPPORT = "WFD_AV_FORMAT_CHANGE_SUPPORT"
    WFD_VIDEOAUDIO_ENCRYPTION = "WFD_VIDEOAUDIO_ENCRYPTION"
    WFD_VIDEOONLY_ENCRPTION = "WFD_VIDEOONLY_ENCRPTION"
    WFD_HDCP_VERSION = "WFD_HDCP_VERSION"
    WFD_HDCP_SUPPORT = "WFD_HDCP_SUPPORT"
    AUTO_M15REQ = "AUTO_M15REQ"
    AUTO_M14REQ = "AUTO_M14REQ"
    WFD_UIBC_OOB = "WFD_UIBC_OOB"
    WFD_UIBC_HID_M4REQ = "WFD_UIBC_HID_M4REQ"
    WFD_UIBC_GEN_M4REQ = "WFD_UIBC_GEN_M4REQ"
    WFD_UIBC_USBKEYBOARD = "WFD_UIBC_USBKEYBOARD"
    WFD_UIBC_USBMOUSE = "WFD_UIBC_USBMOUSE"
    WFD_UIBC_KEYBOARD = "WFD_UIBC_KEYBOARD"
    WFD_UIBCMOUSE = "WFD_UIBCMOUSE"
    WFD_UIBC_HID_SUPPORT = "WFD_UIBC_HID_SUPPORT"
    WFD_UIBC_GEN_SUPPORT = "WFD_UIBC_GEN_SUPPORT"
    WFD_OPTIONAL_VIDEO_MODE_SUPPORT = "WFD_OPTIONAL_VIDEO_MODE_SUPPORT"
    WFD_STANDBY_SUPPORT = "WFD_STANDBY_SUPPORT"
    WFD_EDID_SUPPORT = "WFD_EDID_SUPPORT"
    WFD_I2C_SUPPORT = "WFD_I2C_SUPPORT"
    WFD_PERFERRED_DISPAY_MODE_SUPPORT = "WFD_PERFERRED_DISPAY_MODE_SUPPORT"
    WFD_FRAME_RECOVERY_SUPPORT = "WFD_FRAME_RECOVERY_SUPPORT"
    WFD_FRAME_SKIPPING_SUPPORT = "WFD_FRAME_SKIPPING_SUPPORT"
    WFD_CONCURRENCY_SUPPORT = "WFD_CONCURRENCY_SUPPORT"
    WFD_PERSISTENT_SUPPORT = "WFD_PERSISTENT_SUPPORT"
    WFD_SERVICE_DISCOVERY_SUPPORT = "WFD_SERVICE_DISCOVERY_SUPPORT"
    WFD_PROV_DISCOVERY_SUPPORT = "WFD_PROV_DISCOVERY_SUPPORT"
    WFD_PC_SCHEME = "WFD_PC_SCHEME"
    WFD_TDLS_SUPPORT = "WFD_TDLS_SUPPORT"
    WFD_5GHZ_SUPPORT = "WFD_5GHZ_SUPPORT"
    WFD_DUTTYPE = "WFD_DUTTYPE"

    DUTSPECIFICOPENPORTS = "DUTSPECIFICOPENPORTS"
    MULTIPLE_SERVICE_ADVERTISE = "MULTIPLE_SERVICE_ADVERTISE"
    ENABLE_SERVICE_INFO = "ENABLE_SERVICE_INFO"
    ENABLE = "ENABLE"
    PRINT_SERVICE_INFO = "PRINT_SERVICE_INFO"
    PRINT = "PRINT"
    DISPLAY_SERVICE_INFO = "DISPLAY_SERVICE_INFO"
    DISPLAY = "DISPLAY"
    PLAY_SERVICE_INFO = "PLAY_SERVICE_INFO"
    PLAY = "PLAY"
    SEND_SERVICE_INFO = "SEND_SERVICE_INFO"
    SEND = "SEND"
    WPS_DEFAULT_PIN = "WPS_DEFAULT_PIN"

    #########################################################################
    test_feature_key_words = {
        "WTS_ControlAgent_Support": WTS_CONTROLAGENT_SUPPORT,
        "TLS": TLS,
        "TTLS": TTLS,
        "PEAP0": PEAP0,
        "PEAP1": PEAP1,
        "SIM": SIM,
        "FAST": FAST,
        "AKA": AKA,
        "AKA\'": AKA_PRIME,
        "PWD": PWD,
        "DUTType": DUT_TYPE,
        "DUTBand": DUT_BAND,
        "DUTCategory": DUT_CATEGORY,
        "WEP": WEP,
        "PreAuth": PRE_AUTH,
        "11h": _11H,
        "11d": _11D,
        "SupportedChannelWidth": SUPPORTED_CHANNEL_WIDTH,
        "Streams": STREAMS,
        "Greenfield": GREENFIELD,
        "SGI20": SGI20,
        "SGI40": SGI40,
        "RIFS_TX": RIFS_TX,
        "Coexistence_2040": COEXISTENCE_2040,
        "STBC_RX": STBC_RX,
        "STBC_TX": STBC_TX,
        "MCS32": MCS32,
        "WTS_ControlAgent_Support": WTSSUPPORT,
        "OBSS": OBSS,
        "AMPDU_TX": AMPDU_TX,
        "AP_Concurrent": AP_CONCURRENT,
        "STAUT_PM": STAUT_PM,
        "Open_Mode": OPEN_MODE,
        "Mixedmode_WPA2WPA": MIXEDMODE_WPA2WPA,
        "PMF_OOB": PMF_OOB,
        "ASD": ASD,
        "TDLSDiscReq": TDLSDISCREQ,
        "PUSleepSTA": PUSLEEPSTA,
        "BSS_Trans_Query_Support": BSS_TRANS_QUERY_SUPPORT,
        "TSM_Support": TSM_SUPPORT,
        ##############################
        "NFC_Interface_Flag": NFC_INTERFACE_FLAG,
        "NFC_Support_Flag": NFC_SUPPORT_FLAG,
        "P2P_WMM_PS": P2P_WMM_PS,
        "P2P_11n_Multi_Stream_Support": P2P_11N_MULTI_STREAM_SUPPORT,
        "P2P_GO_Opportunistic_PS_Support": P2P_GO_OPPORTUNISTIC_PS_SUPPORT,
        "P2P_GO_Notice_of_Absence_Support": P2P_GO_NOTICE_OF_ABSENCE_SUPPORT,
        "P2P_Intra_BSS_Bit_Conf_Support": P2P_INTRA_BSS_BIT_CONF_SUPPORT,
        "P2P_GO_Multi_Client_Support": P2P_GO_MULTI_CLIENT_SUPPORT,
        "P2P_Managed_Support": P2P_MANAGED_SUPPORT,
        "P2P_Service_Discovery_Support": P2P_SERVICE_DISCOVERY_SUPPORT,
        "P2P_Discoverability_Exchange_Support": P2P_DISCOVERABILITY_EXCHANGE_SUPPORT,
        "P2P_Extended_Listen_Timing_Support": P2P_EXTENDED_LISTEN_TIMING_SUPPORT,
        "P2P_Dual_Band_Support": P2P_DUAL_BAND_SUPPORT,
        "P2P_Persistent_Group_Support": P2P_PERSISTENT_GROUP_SUPPORT,
        "P2P_Invitation_User_Conf": P2P_INVITATION_USER_CONF,
        "P2P_Invitation_Procedure_Support": P2P_INVITATION_PROCEDURE_SUPPORT,
        "P2P_Cross_Connection_Bit_Conf_Support": P2P_CROSS_CONNECTION_BIT_CONF_SUPPORT,
        "P2P_Multi_Channel_Concurrency_Support": P2P_MULTI_CHANNEL_CONCURRENCY_SUPPORT,
        "P2P_Concurrency_Support": P2P_CONCURRENCY_SUPPORT,
        "P2P_GO_Intent_Value_Configuration": P2P_GO_INTENT_VALUE_CONFIGURATION,
        "WPS_Label": WPS_LABEL,
        "WPS_Keypad": WPS_KEYPAD,
        "WPS_Display": WPS_DISPLAY,
        "WPS_PushButton": WPS_PUSHBUTTON,
        ############################################
        "Internal_Battery_Powered": INTERNAL_BATTERY_POWERED,
        "Mobile_AP": MOBILE_AP,

        "RX_LDPC": RX_LDPC,
        "Tx_LDPC": TX_LDPC,
        "Tx_SU_beamformee": TX_SU_BEAMFORMEE,
        "Tx_SU_beamformer": TX_SU_BEAMFORMER,
        "Rx_A-MPDU_of_A-MSDU": RX_AMPDU_OF_AMSDU,
        "Rx_MCS_8-9": RX_MSC_8_9,
        "SGI80": SGI80,
        "SGI80_RX": SGI80_RX,
        "Dual_band": DUAL_BAND,
        "TPC_Channel_Switch": TPC_CHANNEL_SWITCH,
        "Channel_Switch": CHANNEL_SWITCH,
        "TPC_Support": TPC_SUPPORT,
        "Country_Code": COUNTRY_CODE,
        "Spectrum_Management_Bit": SPECTRUM_MANAGEMENT_BIT,
        "DUTOOBPassPhrase": DUTOOBPASSPHRASE,
        "DUTOOBSecurity": DUTOOBSECURITY,
        "DUTOOBSSID": DUTOOBSSID,
        ########################
        "HS2_APUT_External_Filtering": HS2_APUT_EXTERNAL_FILTERING,
        "HS2_APUT_Inbuilt_Filtering": HS2_APUT_INBUILT_FILTERING,
        "HS2_APUT_External_ANQP_Server": HS2_APUT_EXTERNAL_ANQP_SERVER,
        "HS2_APUT_4Frame_GAS": HS2_APUT_4FRAME_GAS,
        #"HS2_STAUT_Opclass_Indication": HS2_APUT_OPCLASS_INDICATION,
        #"HS2_STAUT_Hrealm_Query": HS2_STAUT_HREALM_QUERY,
        "HS2_STAUT_Keypad": HS2_STAUT_KEYPAD,
        "HS2_STAUT_Display": HS2_STAUT_DISPLAY,
        #"HS2_STAUT_IPv6": HS2_STAUT_IPV6,
        "HS2_STAUT_SIM": HS2_STAUT_SIM,
        ###############################
        "HS2_STAUT_Cert_Retrieval": HS2_STAUT_CERT_RETRIEVAL,
        "HS2_STAUT_PPSMO_Retrieval": HS2_STAUT_PRSMO_RETRIEVAL,
        "HS2_STAUT_Opclass_Indication": HS2_STAUT_OPCLASS_INDICATION,
        "HS2_STAUT_Hrealm_Query": HS2_STAUT_HREALM_QUERY,
        "HS2_STAUT_STATIC_IPv6": HS2_STAUT_STATIC_IPV6,
        "HS2_STAUT_STATIC_IPv4": HS2_STAUT_STATIC_IPV4,
        "HS2_Network_Selection": HS2_NETWORK_SELECTION,
        "HS2_Indication_UI": HS2_INDICATION_UI,
        "HS2_STAUT_IPv6": HS2_STAUT_IPV6,
        "HS2_DUTTYPE": HS2_DUTTYPE,
        #############################
        "scan_time": SCAN_TIME,
        "periodicity": PERIODICITY,
        "maxattenlvl": MAXATTENLVL,
        "A_AttnLvl": A_ATTNLVL,
        "NAN_FurtherAvailAttr": NAN_FURTHERAVAILATTR,
        "auto_followup": AUTO_FOLLOWUP,
        "dB_CLOSE_PROX": DB_CLOSE_PROX,
        "service_name": SERVICE_NAME,
        "dutMatchfilter": DUTMATCHFILTER,
        "NAN_PassiveSubscribe": NAN_PASSIVESUBSCRIBE,
        "NAN_ActiveSubscribe": NAN_ACTIVESUBSCRIBE,
        "NAN_SolicitedPublish": NAN_SOLICITEDPUBLISH,
        "NAN_UnsolicitedPublish": NAN_UNSOLICITEDPUBLISH,
        "OPER_CHN_5G": OPER_CHN_5G,
        ##############################3
        "PMF_SHA1SHA256_Support": PMF_SHA1SHA256_SUPPORT,
        "PMF_BCAST_DISCONNECT_Support": PMF_BCAST_DISCONNECT_SUPPORT,
        "PMF_UNICAST_DISCONNECT_Support": PMF_UNICAST_DISCONNECT_SUPPORT,
        "PMF_REQUIRED_Support": PMF_REQUIRED_SUPPORT,
        ############################
        "WPA": WPA,
        "PUAPSDSleepSTA_Support": PUAPSDSLEEPSTA_SUPPORT,
        "DiscoveryRequest_Support": DISCOVERYREQUEST_SUPPORT,
        ############################

        "WFD_OPTIONAL_VIDEO_LIST": WFD_OPTIONAL_VIDEO_LIST,
        "WFD_VideoFormat3": WFD_VIDEOFORMAT3,
        "WFD_VideoFormat2": WFD_VIDEOFORMAT2,
        "WFD_VideoFormat1": WFD_VIDEOFORMAT1,
        "WFD_AV_Format_Change_Support": WFD_AV_FORMAT_CHANGE_SUPPORT,
        "WFD_VideoAudioEncryption": WFD_VIDEOAUDIO_ENCRYPTION,
        "WFD_VideoOnlyEncryption": WFD_VIDEOONLY_ENCRPTION,
        "WFD_HDCP_Version": WFD_HDCP_VERSION,
        "WFD_HDCP_Support": WFD_HDCP_SUPPORT,
        "auto_M15Req": AUTO_M15REQ,
        "auto_M14Req": AUTO_M14REQ,
        "WFD_UIBC_OOB": WFD_UIBC_OOB,
        "WFD_UIBC_HID_M4Req": WFD_UIBC_HID_M4REQ,
        "WFD_UIBC_Gen_M4Req": WFD_UIBC_GEN_M4REQ,
        "WFD_UIBCUSBKeyboard": WFD_UIBC_USBKEYBOARD,
        "WFD_UIBCUSBMouse": WFD_UIBC_USBMOUSE,
        "WFD_UIBCKeyboard": WFD_UIBC_KEYBOARD,
        "WFD_UIBCMouse": WFD_UIBCMOUSE,
        "WFD_UIBC_HID_Support": WFD_UIBC_HID_SUPPORT,
        "WFD_UIBC_Gen_Support": WFD_UIBC_GEN_SUPPORT,
        "WFD_Optional_Video_Mode_Support": WFD_OPTIONAL_VIDEO_MODE_SUPPORT,
        "WFD_Standby_Support": WFD_STANDBY_SUPPORT,
        "WFD_EDID_Support": WFD_EDID_SUPPORT,
        "WFD_I2C_Support": WFD_I2C_SUPPORT,
        "WFD_Preferred_Display_Mode_Support": WFD_PERFERRED_DISPAY_MODE_SUPPORT,
        "WFD_Frame_Recovery_Support": WFD_FRAME_RECOVERY_SUPPORT,
        "WFD_Frame_Skipping_Support": WFD_FRAME_SKIPPING_SUPPORT,
        "WFD_Concurrency_Support": WFD_CONCURRENCY_SUPPORT,
        "WFD_Persistent_Support": WFD_PERSISTENT_SUPPORT,
        "WFD_Service_Discovery_Support": WFD_SERVICE_DISCOVERY_SUPPORT,
        "WFD_Prov_Discovery_Support": WFD_PROV_DISCOVERY_SUPPORT,
        "WFD_PC_Scheme": WFD_PC_SCHEME,
        "WFD_TDLS_Support": WFD_TDLS_SUPPORT,
        "WFD_5GHz_Support": WFD_5GHZ_SUPPORT,
        "WFD_DUTTYPE": WFD_DUTTYPE,
        #########################
        "DutSpecificOpenPorts": DUTSPECIFICOPENPORTS,
        "multiple_service_advertise": MULTIPLE_SERVICE_ADVERTISE,
        "enable_service_info": ENABLE_SERVICE_INFO,
        "enable": ENABLE,
        "print_service_info": PRINT_SERVICE_INFO,
        "print": PRINT,
        "display_service_info": DISPLAY_SERVICE_INFO,
        "display": DISPLAY,
        "play_service_info": PLAY_SERVICE_INFO,
        "play": PLAY,
        "send_service_info": SEND_SERVICE_INFO,
        "send": SEND,
        "WPS_DefaultPin": WPS_DEFAULT_PIN

    }

    # Reserved words
    script_reserved_words = {
        "if": IF,
        "else": ELSE,
        "endif": ENDIF,
        "or": OR,
        "and": AND,
        "define": DEFINE,
        "rand": RAND,
        "wfa_test_commands_init": WFA_TEST_COMMANDS_INIT,
        "wfa_test_commands": WFA_TEST_COMMANDS,
        "r_info": RINFO,
        "info": INFO,
        "echo": ECHO,
        "getuserinput": GETUSERINPUT,
        "pause": PAUSE,
        "sleep": SLEEP,
        "_inv": PINV,
        "inv_": INVP,
        "DisplayName": DISPLAYNAME,
        "payloadValue": PAYLOAD,
        "payloadValue16K": PAYLOAD16K,
        "stream1": STREAM,
        "stream2": STREAM,
        "stream3": STREAM,
        "stream_trans": STREAM_TRANS,
        "max_throughput": MAX_THROUGHPUT,
        "sniffer_enable": SNIFFER_ENABLE,
        "exit": EXIT,
        "ResultCheck": RESULT_CHECK,
        "search": SEARCH,
        "cat": CAT,
        "math": MATH,
        "mexpr": MEXPR,
        "echo_IfNoWTS": ECHO_INFOWTS,
        "echoIfNoWTS": ECHO_INFOWTS,
        "ifNoWTS": IFNOWTS,
        "IfNoWTS": IFNOWTS,
        "IfNOWTS": IFNOWTS,
        "UserInput_IfNoWTS": USERINPUT_IFNOWTS,
        "UserInput_IfNOWTS": USERINPUT_IFNOWTS,
        "generate_randnum": GENERATE_RANDNUM,
        "Phase": PHASE,
        "StoreThroughput": STORETHROUGHPUT,
        "ResultWMM": RESULT_WMM,
        "ResultWMM_1": RESULT_WMM1,
        "ResultWMM_2": RESULT_WMM2,
        "ResultIBSS": RESULT_IBSS,
        "CheckThroughput": CHECKTHROUGHPUT,
        "CheckMCSThroughput": CHECKMCSTHROUGHPUT,
        "CheckDT4Result": CHECKDT4RESULT,
        "TransactionThroughput": TRANSACTIONTHROUGHPUT,
        "manual_check_info": MANUAL_CHECK_INFO,
        "add_media_file": ADD_MEDIA_FILE,
        "AddSTAVersionInfo": ADD_STA_VERSION_INFO,
        "socktimeout": SOCKTIMEOUT,
        "PingInternalChk": PING_INTERNAL_CHECK,
        "append": APPEND,
        "config_multi_subresults": CONFIG_MULTI_SUBRESULTS,
        "ExternalFunc": EXTERNAL_FUNC
    }

    # Special symbols
    script_special_symbols = {
        "+": PLUS,
        "-": MINUS,
        "*": MULTIPLY,
        "/": DIVIDE,
        "%": MODULO,
        "=": EQUALS,
        "<>": NOT_EQUALS,
        "<": LESS_THAN,
        "<=": LESS_EQUALS,
        ">": GREATER_THAN,
        ">=": GREATER_EQUALS
    }

    script_capi_commands = {
        "traffic_agent_send": TRAFFIC_AGENT_SEND,
        "traffic_send_ping": TRAFFIC_SEND_PING,
        "traffic_stop_ping": TRAFFIC_STOP_PING,
        "traffic_agent_reset": TRAFFIC_AGENT_RESET,
        "traffic_agent_receive_stop": TRAFFIC_AGENT_RECEIVE_STOP,
        "traffic_agent_config": TRAFFIC_AGENT_CONFIG,
        "traffic_agent_receive_start": TRAFFIC_AGENT_RECEIVE_START,

        "ap_set_wireless": AP_SET_WIRELESS,
        "ap_set_security": AP_SET_SECURITY,
        "ap_config_commit": AP_CONFIG_COMMIT,
        "ap_ca_version": AP_CA_VERSION,
        "ap_set_11n_wireless": AP_SET_11N_WIRELESS,
        "ap_set_pmf": AP_SET_PMF,
        "ap_set_apqos": AP_SET_APQOS,
        "ap_set_staqos": AP_SET_STAQOS,
        "ap_set_radius": AP_SET_RADIUS,
        "ap_reboot": AP_REBOOT,
        "ap_reset_default": AP_RESET_DEFAULT,
        "ap_get_info": AP_GET_INFO,
        "ap_deauth_sta": AP_DEAUTH_STA,
        "ap_get_mac_address": AP_GET_MAC_ADDRESS,
        "ap_set_hs2": AP_SET_HS2,
        "ap_set_rpm": AP_SET_RRM,
        "ap_send_addba_req": AP_SEND_ADDBA_REQ,
        "ap_set_11d": AP_SET_11D,
        "ap_set_11h": AP_SET_11H,
        "ap_set_rrm": AP_SET_RRM,

        "ca_get_version": CA_GET_VERSION,
        "device_get_info": DEVICE_GET_INFO,
        "device_list_interfaces": DEVICE_LIST_INTERFACES,
        "sta_preset_testparameters": STA_PRESET_TESTPARAMETERS,
        "sta_get_info": STA_GET_INFO,
        "sta_set_encryption": STA_SET_ENCRYPTION,
        "sta_set_ip_config": STA_SET_IP_CONFIG,
        "sta_associate": STA_ASSOCIATE,
        "sta_is_connected": STA_IS_CONNECTED,
        "sta_get_bssid": STA_GET_BSSID,
        "sta_get_ip_config": STA_GET_IP_CONFIG,
        "sta_disconnect": STA_DISCONNECT,
        "sta_get_mac_address": STA_GET_MAC_ADDRESS,
        "sta_verify_ip_connection": STA_VERIFY_IP_CONNECTION,
        "sta_set_psk": STA_SET_PSK,
        "sta_set_eaptls": STA_SET_EAPTLS,
        "sta_set_eapttls": STA_SET_EAPTTLS,
        "sta_set_eapsim": STA_SET_EAPSIM,
        "sta_set_peap": STA_SET_PEAP,
        "sta_set_eapfast": STA_SET_EAPFAST,
        "sta_set_eapaka": STA_SET_EAPAKA,
        "sta_set_uapsd":STA_SET_UAPSD,
        "sta_set_ibss": STA_SET_IBSS,
        "sta_set_mode": STA_SET_MODE,
        "sta_set_wmm": STA_SET_WMM,
        "sta_up_load": STA_UP_LOAD,
        "sta_set_systime": STA_SET_SYSTIME,
        "sta_set_11n": STA_SET_11N,
        "sta_set_rifs_test": STA_SET_RIFS_TEST,
        "sta_set_wireless": STA_SET_WIRELESS,
        "sta_send_addba": STA_SEND_ADDBA,
        "sta_send_coexist_mgmt": STA_SEND_COEXIST_MGMT,
        "sta_get_p2p_dev_address": STA_GET_P2P_DEV_ADDRESS,
        "sta_set_p2P": STA_SET_P2P,
        "sta_start_autonomous_go": STA_START_AUTONOMOUS_GO,
        "sta_p2p_connect": STA_P2P_CONNECT,
        "sta_p2p_start_group_formation": STA_P2P_START_GROUP_FORMATION,
        "sta_p2p_dissolve": STA_P2P_DISSOLVE,
        "sta_send_p2p_invitation_req": STA_SEND_P2P_INVITATION_REQ,
        "sta_accept_p2p_invitation_req": STA_ACCEPT_P2P_INVITATION_REQ,
        "sta_send_p2p_provision_dis_req": STA_SEND_P2P_PROVISION_DIS_REQ,
        "sta_set_wps_pbc": STA_SET_WPS_PBC,
        "sta_wps_read_pin": STA_WPS_READ_PIN,
        "sta_wps_read_label": STA_WPS_READ_LABEL,
        "sta_wps_enter_pin": STA_WPS_ENTER_PIN,
        "sta_get_psk": STA_GET_PSK,
        "sta_p2p_reset": STA_P2P_RESET,
        "sta_get_p2p_ip_config": STA_GET_P2P_IP_CONFIG,
        "sta_send_p2p_presence_req": STA_SEND_P2P_PRESENCE_REQ,
        "sta_set_sleep": STA_SET_SLEEP,
        "sta_set_opportunistic_ps": STA_SET_OPPORTUNISTIC_PS,
        "sta_send_service_discovery_req": STA_SEND_SERVICE_DISCOVERY_REQ,
        "sta_add_arp_table_entry": STA_ADD_ARP_TABLE_ENTRY,
        "sta_block_icmp_response": STA_BLOCK_ICMP_RESPONSE,
        "sta_set_security": STA_SET_SECURITY,
        "sta_set_macaddr": STA_SET_MACADDR,
        "sta_reset_default": STA_RESET_DEFAULT,
        "sta_reset_parm": STA_RESET_PARM,
        "sta_set_rfeature": STA_SET_RFEATURE,
        "sta_set_radio": STA_SET_RADIO,
        "dev_send_frame": DEV_SEND_FRAME,
        "sta_hs2_associate": STA_HS2_ASSOCIATE,
        "sta_bssid_pool": STA_BSSID_POOL,
        "sta_add_credential": STA_ADD_CREDENTIAL,
        "start_wfd_connection": START_WFD_CONNECTION,
        "connect_go_start_wfd": CONNECT_GO_START_WFD,
        "sta_generate_event": STA_GENERATE_EVENT,
        "reinvoke_wfd_session": REINVOKE_WFD_SESSION,
        "sta_get_parameter": STA_GET_PARAMETER,
        "sta_set_power_save": STA_SET_POWER_SAVE,
        "sta_exec_action": STA_EXEC_ACTION,
        "sta_invoke_command": STA_INVOKE_COMMAND,
        "sta_manage_service": STA_MANAGE_SERVICE,
        "sta_get_event_details": STA_GET_EVENT_DETAILS,
        "sta_policy_update": STA_POLICY_UPDATE,
        "sta_set_pwrsave": STA_SET_PWRSAVE,
        "sta_scan": STA_SCAN,
        "sta_get_events": STA_GET_EVENTS,
        "sta_nfc_action": STA_NFC_ACTION,
        "sta_reassociate": STA_REASSOCIATE,
        "sta_reassoc": STA_REASSOC,
        "sta_osu": STA_OSU,

        "wfa_merge_trace": WFA_MERGE_TRACE,
        "sniffer_media_check": SNIFFER_MEDIA_CHECK,
        "wfa_av_capture": WFA_AV_CAPTURE,
        "sniffer_control_upload": SNIFFER_CONTROL_UPLOAD,
        "sniffer_clear_counters": SNIFFER_CLEAR_COUNTERS,
        "sniffer_check_p2p_NoA_wmmps_retrigger": SNIFFER_CHECK_P2P_NOA_WMMPS_RETRIGGER,
        "sniffer_check_p2p_NoA_start_time": SNIFFER_CHECK_P2P_NOA_START_TIME,
        "sniffer_check_p2p_NoA_duration": SNIFFER_CHECK_P2P_NOA_DURATION,
        "sniffer_check_p2p_opps_go": SNIFFER_CHECK_P2P_OPPS_GO,
        "sniffer_check_p2p_opps_client": SNIFFER_CHECK_P2P_OPPS_CLIENT,
        "sniffer_get_field_value": SNIFFER_GET_FIELD_VALUE,
        "sniffer_inject_frame": SNIFFER_INJECT_FRAME,
        "sniffer_get_info": SNIFFER_GET_INFO,
        "sniffer_control_field_check": SNIFFER_CONTROL_FIELD_CHECK,
        "sniffer_frame_check": SNIFFER_FRAME_CHECK,
        "sniffer_control_stop": SNIFFER_CONTROL_STOP,
        "sniffer_control_start": SNIFFER_CONTROL_START,
        "sniffer_check_pmk_id": SNIFFER_CHECK_PMK_ID,
        "\w*sniffer_control_filter_capture": SNIFFER_CONTROL_FILTER_CAPTURE,
        "\w*sniffer_control_capture_decrypt": SNIFFER_CONTROL_CAPTURE_DECRYPT,
        "wfa_wfds_generate_hash": WFA_WFDS_GENERATE_HASH,
        "\w*sniffer_stream_check": SNIFFER_STREAM_CHECK,
        "sniffer_control_subtask": SNIFFER_CONTROL_SUBTASK,
        "sniffer_fetch_file": SNIFFER_FETCH_FILE,
        "sniffer_decrypt_trace": SNIFFER_DECRYPT_TRACE,
        "sniffer_check_time_difference": SNIFFER_CHECK_TIME_DIFFERENCE,
        "sniffer_check_Dscv_Window": SNIFFER_CHECK_DSCV_WINDOW,
        "wfa_sniffer_check_retry": WFA_SNIFFER_CHECK_RETRY,

        "server_reset_default": SERVER_RESET_DEFAULT,
        "server_set_parameter": SERVER_SET_PARAMETER,
        "server_get_info": SERVER_GET_INFO,
        "server_request_status": SERVER_REQUEST_STATUS,
        "server_ca_get_version": SERVER_CA_GET_VERSION,
    
        "wfa_aca_get": WFA_ACA_GET,
        "wfa_aca_set": WFA_ACA_SET,
        "wfa_aca_act": WFA_ACA_ACT,
        
        "wfaemt_config_nav": WFAEMT_CONFIG_NAV,
        "wfaemt_start_nav_test": WFAEMT_START_TEST,
        "wfaemt_stop_nav_test": WFAEMT_STOP_TEST,
        "wfaemt_start_staut_mic_test": WFAEMT_START_STAUT_MIC_TEST,
        "wfaemt_stop_staut_mic_test": WFAEMT_STOP_STAUT_MIC_TEST,
        "wfaemt_config_staut_mic": WFAEMT_CONFIG_STAUT_MIC,
        "AccessPoint": ACCESSPOINT,
        "^PowerSwitch,\w+": POWER_SWITCH,
        "power_switch_ctrl": POWER_SWITCH_CTRL
    }

    script_testbed_devices = {
        "wfa_control_agent_[^PCE]\w+_sta": WFA_CONTROL_AGENT_STA,
        "\w+_sta_wireless_ip": WFA_CONTROL_AGENT_STA,
        
        # WMM-AC testbed device
        "control_agent_testbed_sta[1-3]": WFA_CONTROL_AGENT_STA,
        "control_agent_testbed_sta[1-3]_tspec": WFA_CONTROL_AGENT_STA,
        "^testbed_sta[1-3]\w*": WFA_TESTBEDSTA,
        
        "wfa_control_agent_\w+_ap": WFA_CONTROL_AGENT_AP,

        "wfa_control_agent_dut": WFA_CONTROL_AGENT_DUT,
        "dut_wireless_ip": WFA_CONTROL_AGENT_DUT,
        "(?!dut_wireless_ip)Dut\w+": WFA_DUT,
        "APUT_\w+": WFA_DUT,

        "wfa_control_agent_atten": WFA_ATTENUATOR,

        "wfa_console_tg": WFA_PCEDNPOINT,
        "wfa_console_ctrl": WFA_PCEDNPOINT,
        "wfa_control_agent_PCE1_sta": WFA_PCEDNPOINT,
        "wfa_control_agent_PCE2_sta": WFA_PCEDNPOINT,
        "wfa_control_agent_PCE3_sta": WFA_PCEDNPOINT,

        "wfa_sniffer\d*": WFA_SNIFFER,

        "wfa_control_agent_\w+_osu": WFA_CONTROL_AGENT_OSUSERVER,

        "HostAPD\w*": WFA_RADIUSSERVER,
        "Microsoft\w*": WFA_RADIUSSERVER,
        "Radiator\w*": WFA_RADIUSSERVER,
        "RS\d+\w*": WFA_RADIUSSERVER,
        "RADIUS\d+\w*": WFA_RADIUSSERVER,

        "^PowerSwitch\w+": POWERSWITCH,
        "TestbedAPConfigServer": WFA_APCONFIGSERVER,

        "^WFAEMT\w+": WFAEMT,
        "wfa_wfaemt_control_agent": WFA_EMT_CONTROL_AGNET,

        "^Atheros\w*AP\w*": WFA_TESTBEDAP,
        "^Broadcom\w*AP\w*": WFA_TESTBEDAP,
        "^Marvell\w*AP\w*": WFA_TESTBEDAP,
        "^Ralink\w*AP\w*": WFA_TESTBEDAP,
        "^Realtek\w*AP\w*": WFA_TESTBEDAP,
        "^Ericsson\w*AP\w*": WFA_TESTBEDAP,
        "^Cisco\w*AP\w*": WFA_TESTBEDAP,
        "^Qualcomm\w*AP\w*": WFA_TESTBEDAP,
        "^Aruba\w*AP\w*": WFA_TESTBEDAP,

        "^Atheros[^_]*STA\w*": WFA_TESTBEDSTA,
        "^Broadcom[^_]*STA\w*": WFA_TESTBEDSTA,
        "^Marvell[^_]*STA\w*": WFA_TESTBEDSTA,
        "^Ralink[^_]*STA\w*": WFA_TESTBEDSTA,
        "^Intel[^_]*STA\w*": WFA_TESTBEDSTA,
        "^Mediatek[^_]*STA\w*": WFA_TESTBEDSTA,
        "^Qualcomm[^_]*STA\w*": WFA_TESTBEDSTA,
        "^Epson[^_]*STA\w*": WFA_TESTBEDSTA,        
        "^Realtek[^_]*STA\w*": WFA_TESTBEDSTA
    }


    @staticmethod
    def get_spcl_sym_key_from_val(val_name):
        """Gets the entry key from script_special_symbols dictionary based on the value.

        Args:
            val_name (str): The entry value.
        """
        for spcl_sym_item in TestScriptElementType.script_special_symbols:
            if TestScriptElementType.script_special_symbols[spcl_sym_item] == val_name:
                return spcl_sym_item

    @staticmethod
    def get_resv_word_key_from_val(val_name):
        """Gets the entry key from script_reserved_words dictionary based on the value.

        Args:
            val_name (str): The entry value.
        """
        for resv_item in TestScriptElementType.script_reserved_words:
            if TestScriptElementType.script_reserved_words[resv_item] == val_name:
                return resv_item


    @staticmethod
    def get_test_feat_key_from_val(val_name):
        """Gets the test feature key from test_feature_key_words dictionary based on the value.

        Args:
            val_name (str): The value of entry.
        """
        for feat_item in TestScriptElementType.test_feature_key_words:
            if TestScriptElementType.test_feature_key_words[feat_item] == val_name:
                return feat_item


    @staticmethod
    def get_capi_name_from_val(val_name):
        """Gets the capi name from the script_capi_commands dictionary based on the value.

        Args:
            val_name (str): The value of the dictionary entry.
        """
        for capi_item in TestScriptElementType.script_capi_commands:
            if TestScriptElementType.script_capi_commands[capi_item] == val_name:
                return capi_item


    @staticmethod
    def get_element_type(text):
        """Gets the element type based on its text.

        Args:
            text (str): The object of UserInputCommand class.
        """
        if text.startswith('$'):
            return "VARIABLE"
        
        elif text in TestScriptElementType.script_special_symbols.keys():
            return TestScriptElementType.script_special_symbols[text]

        elif text in TestScriptElementType.script_reserved_words.keys():
            return TestScriptElementType.script_reserved_words[text]

        elif text in TestScriptElementType.script_capi_commands.keys():
            return TestScriptElementType.script_capi_commands[text]

        elif text in TestScriptElementType.test_feature_key_words.keys():
            return TestScriptElementType.test_feature_key_words[text]
        # move the STRING type check for <text> to the end to make sure it can be recognized as other types first
        elif isinstance(text, str):
            return "STRING"

        else:
            raise ElementTypeError

