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
import random
from operator import itemgetter
from xml.dom.minidom import Node
from scriptinfo.scriptelement import (TestScriptElementType, ScriptReservedWordsElement, ScriptSpecialSymbolElement,
CAPICommandElement, ScriptStringElement, ScriptVariableElement, TestbedDeviceElement, TestFeatureElement, CAPIReturnElement, EndOfLineElement)
import common
from symtable import TestScriptSymbolTable
from scriptinfo.scriptsource import TestFileSourceFacotry
from scanner import TestScriptScanner, LexicaError, SyntaxError
from util.linkedlist import SingleLinkedList
from util.misc import Util



class UndefinedError(Exception):
    """The factory class that creates families of parsers.
    """
    pass



class TestScriptParserFactory(object):
    """The factory class that creates families of parsers.

    Attributes:
        test_script_scanner (object): The object of TestScriptScanner class.

    """
    test_script_scanner = None

    @staticmethod
    def create_parser(file_source, test_mngr_initr, is_xml_file=False):
        """Creates the concrete parser object.

        Args:
            file_to_lookup (str): file name to look up.
        """
        if is_xml_file:
            return XmlFileParser(file_source)

        TestScriptParserFactory.test_script_scanner = TestScriptScanner(file_source)
        return TestScriptParser(TestScriptParserFactory.test_script_scanner, test_mngr_initr)



class XmlFileParser:
    """The XML file parser class.

    Attributes:
        xml_file_source (object): The object of TestXmlFileSource class.
        sll (object): The object of SingleLinkedList class.

    """
    def __init__(self, xml_file_source):
        self.xml_file_source = xml_file_source
        self.sll = None #SingleLinkedList()


    def init_parser(self):
        """Initializes the SingleLinkedList object.
        """
        self.sll = SingleLinkedList()


    def build_sll_from_xml_tree_node(self, node_name, node_value=""):
        """Stores the node name and value on the sll.

        Args:
            node_name (str): The node name.
            node_value (str): The node value.
        """
        self.sll.insert(node_name, node_value.rstrip("\n").strip())


    def parse(self):
        """Parses the DOM tree of XML file.
        """
        try:
            if self.xml_file_source.xml_file_name == common.GlobalConfigFiles.master_test_info_file:
                self.xml_file_source.load_xml_file()
                
                root = self.parse_root_node()
                logging.info("Testplan version=%s" % root)
                tc_node = self.get_test_case_node(common.GlobalConfigFiles.curr_tc_name)
                self.parse_tc_tree_node(tc_node)

        except Exception, e1:
            raise e1


    def parse_root_node(self):
        """Gets the root node.
        """
        return self.xml_file_source.get_root_node_name()


    def get_test_case_node(self, tc_tag):
        """Gets the test case node based on the given test case name tag.

        Args:
            tc_tag (str): The test case name tag.
        """
        nodes = self.xml_file_source.get_nodes_by_tag_name(tc_tag)
        if len(nodes) == 0:
            raise Exception('Test Case ID not exist - %s' % common.GlobalConfigFiles.curr_tc_name)
        if len(nodes) > 1:
            raise Exception('Duplicate Test Case ID - %s' % common.GlobalConfigFiles.curr_tc_name)
        return nodes[0]


    def parse_tc_tree_node(self, tc_node):
        """Parses the test case subtree based on the given node.

        Args:
            tc_node (str): The node whose subtree to be parsed.
        """
        for child in tc_node.childNodes:
            if child.nodeType == Node.ELEMENT_NODE:
                if child.firstChild is None:
                    continue
                if child.firstChild.nodeType == Node.TEXT_NODE:
                    self.build_sll_from_xml_tree_node(child.nodeName, child.firstChild.nodeValue)
                else:
                    self.build_sll_from_xml_tree_node(child.nodeName)
        
                self.parse_tc_tree_node(child)
            elif child.nodeType == Node.TEXT_NODE:
                pass
                


class TestScriptParser:
    """The test script parser class.

    Attributes:
        qll (object): The object of SingleLinkedList class to store the test case data.
        ill (object): The object of SingleLinkedList class to store the configuration data.
        ignore_if_else (boolean): The indication of skipping subsequence if/else clauses.
        group_tag_name (str): The file name added to indicate the start of sub file calling.
        add_end_flag (boolean): The indicator for adding the END element.
        sub_file_call_dict (dictionary): The dictionary to store the script calling sequence.

    """
    qll = None # for parsing test case script files
    ill = None # unified init file
    ignore_if_else = False
    group_tag_name = ""
    add_end_flag = False
    sub_file_call_dict = {}
    device_alias_list = []

    def __init__(self, test_script_scanner, test_mngr_initr):
        self.test_script_scanner = test_script_scanner
        self.sll = None # for DUTInfo.txt
        self.test_mngr_initr = test_mngr_initr


    def build_sll_from_xml_tree_node(self, key_name, key_value, tag):
        """Constructs the ill or sll node from the given key, value and tag.

        Args:
            key_name (str): The key.
            key_value (str): The value.
            tag (str): The tag.
        """
        if self.test_mngr_initr.test_config_cxt.is_all_init_config_file:
            TestScriptParser.ill.insert(key_name, key_value, tag)
        else:
            self.sll.insert(key_name, key_value, tag)


    def init_parser(self):
        """Initializes the ill, sll, or qll objects.
        """
        if self.test_mngr_initr.test_config_cxt.is_test_case_file or self.test_mngr_initr.test_config_cxt.is_all_init_command_file:
            if TestScriptParser.qll is None:
                TestScriptParser.qll = SingleLinkedList()

            if self.test_mngr_initr.test_config_cxt.is_test_case_file:
                TestScriptParser.qll.insert("MAINSCRIPT", None, "SEPRATROR", TestScriptParser.group_tag_name)

        elif self.test_mngr_initr.test_config_cxt.is_all_init_config_file:
            TestScriptParser.ill = SingleLinkedList()
        else:
            self.sll = SingleLinkedList()


    def parse(self):
        """Parses the test source file through the underlying scanner.
        """
        try:
            while True:
                self.test_script_scanner.next_element()
                self.goal()
                if self.test_script_scanner.next_segment == "EOF":
                    return
        except SyntaxError:
            logging.error('Syntax Error at position:', self.test_script_scanner.test_script_source.current_pos)
            self.test_script_scanner.show_error()
            raise SyntaxError
        except LexicaError:
            logging.error('Lexical Error at position:', self.test_script_scanner.test_script_source.current_pos)
            self.test_script_scanner.show_error()
            raise LexicaError
        except UndefinedError, name:
            logging.error("'%s' Error at position:", name, self.test_script_scanner.test_script_source.current_pos)
            self.test_script_scanner.show_error()
            raise UndefinedError


    def goal(self):
        """Performs the actual parsing work to extract relevant data, and store it on the qll or global data structures.
        """
        if self.test_script_scanner.current_elmt == "":
            return
        
        element_type = self.test_script_scanner.current_elmt.element_type

        # parsing for reserved words
        if isinstance(self.test_script_scanner.current_elmt, ScriptReservedWordsElement):
            self.parse_reserved_words(element_type)

        elif isinstance(self.test_script_scanner.current_elmt, CAPICommandElement):
            if self.test_mngr_initr.test_config_cxt.is_test_case_file or self.test_mngr_initr.test_config_cxt.is_all_init_command_file:
                paramstr = ""
                
                if self.test_script_scanner.current_elmt.segment_text == TestScriptElementType.get_capi_name_from_val(TestScriptElementType.STA_IS_CONNECTED):
                    TestScriptSymbolTable.insert_sym_tab("$IS_CONNECTED", "", TestScriptSymbolTable.capi_cmd_ret_sym_tab)

                #"sta_preset_testparameters"
                if common.GlobalConfigFiles.curr_prog_name == "PMF" and self.test_script_scanner.current_elmt.segment_text == TestScriptElementType.get_capi_name_from_val(TestScriptElementType.TRAFFIC_STOP_PING):
                    if not TestScriptSymbolTable.lookup_sym_tab("$pingResp", TestScriptSymbolTable.capi_cmd_ret_sym_tab):
                        TestScriptSymbolTable.insert_sym_tab("$pingResp", "", TestScriptSymbolTable.capi_cmd_ret_sym_tab)
                
                if self.test_script_scanner.current_elmt.paramstr != "":
                    paramstr = self.replace_capi_variable_by_value(self.test_script_scanner.current_elmt.paramstr)

                TestScriptParser.qll.insert(self.test_script_scanner.current_elmt.segment_text, paramstr, "CAPICOMMAND", TestScriptParser.group_tag_name)
                TestScriptParser.add_end_flag = True
    
        elif isinstance(self.test_script_scanner.current_elmt, TestbedDeviceElement):
            if self.test_mngr_initr.test_config_cxt.is_test_case_file or self.test_mngr_initr.test_config_cxt.is_all_init_command_file:
                TestScriptParser.qll.insert(self.test_script_scanner.current_elmt.segment_text, None, "TESTBEDDEVICE", TestScriptParser.group_tag_name)
                TestScriptParser.add_end_flag = True
            else:
                if self.test_mngr_initr.test_config_cxt.is_all_init_config_file:
                    self.parse_testbed_device_element(self.test_script_scanner.next_segment, self.test_script_scanner.current_elmt.segment_text)

        elif isinstance(self.test_script_scanner.current_elmt, ScriptVariableElement):
            key_name = self.test_script_scanner.current_elmt.segment_text
            key_value = self.test_script_scanner.get_next_segment_value()            
            TestScriptSymbolTable.insert_sym_tab(key_name, key_value, TestScriptSymbolTable.test_script_sym_tab)

        elif isinstance(self.test_script_scanner.current_elmt, TestFeatureElement):
            key_name = self.test_script_scanner.current_elmt.segment_text
            self.test_script_scanner.next_element()
            key_value = self.test_script_scanner.current_elmt.segment_text            
            self.build_sll_from_xml_tree_node(key_name, key_value, "FEATURE")

        elif isinstance(self.test_script_scanner.current_elmt, EndOfLineElement):
            if self.test_mngr_initr.test_config_cxt.is_test_case_file or self.test_mngr_initr.test_config_cxt.is_all_init_command_file:                
                if TestScriptParser.add_end_flag:
                    TestScriptParser.qll.insert(None, None, "END")
                    TestScriptParser.add_end_flag = False

        elif isinstance(self.test_script_scanner.current_elmt, CAPIReturnElement):
            if self.test_script_scanner.current_elmt.segment_text != "DEFAULT":
                TestScriptParser.qll.insert(self.test_script_scanner.current_elmt.segment_text, self.test_script_scanner.current_elmt.paramstr, "CAPIRETVAR", TestScriptParser.group_tag_name)
                TestScriptParser.add_end_flag = True
                for item in self.test_script_scanner.current_elmt.paramstr.split(','):
                    if item.startswith('$'):
                        TestScriptSymbolTable.insert_sym_tab(item, "", TestScriptSymbolTable.capi_cmd_ret_sym_tab)
                        if TestScriptSymbolTable.lookup_sym_tab(item, TestScriptSymbolTable.test_script_sym_tab):
                            TestScriptSymbolTable.delete_key_from_sym_tab(item, TestScriptSymbolTable.test_script_sym_tab)
        else:
            raise SyntaxError


    def replace_capi_variable_by_value(self, paramstr):
        """Replaces the dollar variables with their actual values if possible.

        Args:
            paramstr (str): The parameter string to be replaced.
        """
        for var in paramstr.split(','):
            if var.startswith('$'):
                val = TestScriptSymbolTable.get_value_from_sym_tab(var, TestScriptSymbolTable.test_script_sym_tab)
                if val is not None:
                    val1 = TestScriptSymbolTable.get_value_from_sym_tab(val, TestScriptSymbolTable.test_script_sym_tab)
                    if val1 is not None:
                        paramstr = paramstr.replace(var, val1, 1)
                    else:
                        if TestScriptSymbolTable.lookup_sym_tab(var, TestScriptSymbolTable.capi_cmd_ret_sym_tab) and not TestScriptSymbolTable.lookup_sym_tab(var, TestScriptSymbolTable.test_script_sym_tab):
                            continue                        
                        else:
                            #===================================================
                            # if TestScriptSymbolTable.lookup_sym_tab(var, TestScriptSymbolTable.capi_cmd_ret_sym_tab) and TestScriptSymbolTable.lookup_sym_tab(var, TestScriptSymbolTable.test_script_sym_tab):
                            #     value = TestScriptSymbolTable.get_value_from_sym_tab(var, TestScriptSymbolTable.test_script_sym_tab)
                            #     if value.startswith('$'):
                            #         continue
                            #===================================================
                            paramstr = paramstr.replace(var, val, 1)
            else:
                val = TestScriptSymbolTable.get_value_from_sym_tab(var, TestScriptSymbolTable.test_script_sym_tab)
                if val is not None:
                    if isinstance(val, dict):
                        if "ipaddr" in val:
                            ipaddr = val["ipaddr"]                        
                        paramstr = paramstr.replace(var, ipaddr, 1)
                    else:
                        paramstr = paramstr.replace(var, val, 1)
                
        return paramstr


    def parse_reserved_words(self, element_type):
        """Parses the reserved words based on the current element type.

        Args:
            element_type (object): The object of TestScriptElementType class.
        """
        # "if" keyword
        if element_type == TestScriptElementType.IF:
            if_parser = IfStatementParser(self.test_script_scanner, self.test_mngr_initr)
            if_parser.parse()
        elif element_type == TestScriptElementType.ELSE:
            if TestScriptParser.ignore_if_else and (self.test_mngr_initr.test_config_cxt.is_test_case_file or self.test_mngr_initr.test_config_cxt.is_all_init_command_file):
                TestScriptParser.qll.insert(None, None, "ELSE", TestScriptParser.group_tag_name)
                TestScriptParser.add_end_flag = True
            else:
                self.test_script_scanner.synchronize([TestScriptElementType.get_resv_word_key_from_val(TestScriptElementType.ENDIF)])
        elif element_type == TestScriptElementType.ENDIF:
            if TestScriptParser.ignore_if_else and (self.test_mngr_initr.test_config_cxt.is_test_case_file or self.test_mngr_initr.test_config_cxt.is_all_init_command_file):
                TestScriptParser.ignore_if_else = False
                TestScriptParser.qll.insert(None, None, "ENDIF", TestScriptParser.group_tag_name)
                TestScriptParser.add_end_flag = True
            
        # "define" keyword
        elif element_type == TestScriptElementType.DEFINE:
            define_parser = DefineStatementParser(self.test_script_scanner, self.test_mngr_initr)
            define_parser.parse()
        # "math" keyword
        elif element_type == TestScriptElementType.MATH:
            self.process_math_calc()
        # "ResultCheck" keyword
        elif element_type == TestScriptElementType.RESULT_CHECK:
            self.process_resultcheck()
        # "search" keyword
        elif element_type == TestScriptElementType.SEARCH:
            self.process_search()
        elif element_type == TestScriptElementType.CAT:
            self.process_cat()
        elif element_type == TestScriptElementType.MEXPR:
            self.process_mexpr()
        # "config_multi_subresults" keyword
        elif element_type == TestScriptElementType.CONFIG_MULTI_SUBRESULTS:
            keyword = self.test_script_scanner.current_elmt.segment_text
            self.test_script_scanner.next_element()
            sub_rslt = self.test_script_scanner.current_elmt.segment_text.split(',')
            if len(sub_rslt) == 2:
                num_req = TestScriptSymbolTable.get_value_from_sym_tab(sub_rslt[0], TestScriptSymbolTable.test_script_sym_tab)
                num_chk = TestScriptSymbolTable.get_value_from_sym_tab(sub_rslt[1], TestScriptSymbolTable.test_script_sym_tab)
                TestScriptParser.qll.insert(keyword, {"NUMOFPASSREQ": num_req, "NUMOFCHECK" : num_chk}, "UCCACTION", TestScriptParser.group_tag_name)
                TestScriptParser.add_end_flag = True
            else:
                raise SyntaxError
            self.test_script_scanner.skip_next_segment()
        elif element_type == TestScriptElementType.ECHO or element_type == TestScriptElementType.EXIT or element_type == TestScriptElementType.INFO or element_type == TestScriptElementType.PAUSE or element_type == TestScriptElementType.SLEEP:
            self.process_echo_exit_info_sleep(element_type)
        elif element_type == TestScriptElementType.GETUSERINPUT:
            self.process_get_user_input()
        elif element_type == TestScriptElementType.PINV or element_type == TestScriptElementType.INVP:
            TestScriptParser.qll.insert(self.test_script_scanner.current_elmt.segment_text, None, "UCCACTION", TestScriptParser.group_tag_name)
            TestScriptParser.add_end_flag = True
        elif element_type == TestScriptElementType.RINFO:
            self.process_rinfo()
        elif element_type == TestScriptElementType.RESULT_WMM or element_type == TestScriptElementType.RESULT_WMM1 or element_type == TestScriptElementType.RESULT_WMM2 or \
                element_type == TestScriptElementType.RESULT_IBSS or element_type == TestScriptElementType.CHECKDT4RESULT or element_type == TestScriptElementType.CHECKTHROUGHPUT or \
                element_type == TestScriptElementType.CHECKMCSTHROUGHPUT or element_type == TestScriptElementType.TRANSACTIONTHROUGHPUT:
            self.process_result_var()
        elif element_type == TestScriptElementType.STORETHROUGHPUT:
            self.process_storethroughput()
        elif element_type == TestScriptElementType.APPEND:
            self.process_append()
        elif element_type == TestScriptElementType.PHASE or element_type == TestScriptElementType.SOCKTIMEOUT or element_type == TestScriptElementType.ADD_STA_VERSION_INFO or element_type == TestScriptElementType.ADD_MEDIA_FILE or element_type == TestScriptElementType.MANUAL_CHECK_INFO:
            TestScriptParser.qll.insert(self.test_script_scanner.current_elmt.segment_text, self.test_script_scanner.next_segment, "UCCACTION", TestScriptParser.group_tag_name)
            TestScriptParser.add_end_flag = True
            self.test_script_scanner.skip_next_segment()
        elif element_type == TestScriptElementType.ECHO_INFOWTS:
            self.process_echoIfNoWTS()
        elif element_type == TestScriptElementType.IFNOWTS or element_type == TestScriptElementType.USERINPUT_IFNOWTS:
            self.process_ifNoWTS()
        elif element_type == TestScriptElementType.GENERATE_RANDNUM:
            self.process_random_gen()
        elif element_type == TestScriptElementType.WFA_TEST_COMMANDS or element_type == TestScriptElementType.WFA_TEST_COMMANDS_INIT:
            filename = self.test_script_scanner.get_next_segment_value()
            TestScriptParser.sub_file_call_dict["%s:%s:%s" % (self.test_script_scanner.test_script_source.test_script_source_name, filename, len(TestScriptParser.sub_file_call_dict) + 1)] = len(TestScriptParser.sub_file_call_dict) + 1
            if self.check_in_script_loop():
                TestScriptParser.qll.insert(self.test_script_scanner.current_elmt.segment_text, None, "GOTO", TestScriptParser.group_tag_name)
                TestScriptParser.add_end_flag = True
                TestScriptParser.group_tag_name = ""
                self.test_script_scanner.skip_next_segment()
                return            
            
            txtFileFactory = TestFileSourceFacotry(filename, self.test_mngr_initr.test_script_mngr.prog_script_folder_path)
            txtFileSource = txtFileFactory.file_factory_method()
            txt_parser = TestScriptParserFactory.create_parser(txtFileSource, self.test_mngr_initr)

            TestScriptParser.group_tag_name = filename
            txt_parser.parse()
            TestScriptParser.group_tag_name = ""
            self.test_script_scanner.skip_next_segment()
        elif element_type == TestScriptElementType.DISPLAYNAME:
            alias = self.test_script_scanner.get_next_segment_value()
            self.test_script_scanner.next_element()
            real_name = self.test_script_scanner.next_segment
            self.test_script_scanner.skip_next_segment()
            self.build_sll_from_xml_tree_node(alias, real_name, "DISPLAYNAME")
        elif element_type == TestScriptElementType.STREAM or element_type == TestScriptElementType.PAYLOAD or element_type == TestScriptElementType.STREAM or element_type == TestScriptElementType.PAYLOAD16K or element_type == TestScriptElementType.MAX_THROUGHPUT or element_type == TestScriptElementType.STREAM_TRANS:
            strm_val = self.test_script_scanner.get_next_segment_value()
            self.build_sll_from_xml_tree_node(self.test_script_scanner.current_elmt.segment_text, strm_val, "TRAFFICSTREAM")
            self.test_script_scanner.skip_next_segment()
        elif element_type == TestScriptElementType.SNIFFER_ENABLE:
            self.process_sniffer_enable()
        elif element_type == TestScriptElementType.EXTERNAL_FUNC:
            keyword = self.test_script_scanner.current_elmt.segment_text
            self.test_script_scanner.next_element()
            TestScriptParser.qll.insert(keyword, {"EXTERNALFUNC": self.test_script_scanner.current_elmt.segment_text}, 'FUNCCALLER', TestScriptParser.group_tag_name)
            self.test_script_scanner.skip_next_segment()
        else:
            raise SyntaxError('Unknown element - %s' % self.test_script_scanner.current_elmt.segment_text)


    def process_append(self):
        """Parses the Append keyword.
        """        
        cmd0 = self.test_script_scanner.current_elmt.segment_text
        cmd1 = self.test_script_scanner.next_segment
        self.test_script_scanner.next_element()
        cmd2 = self.test_script_scanner.next_segment
        self.test_script_scanner.next_element()
        cmd3 = self.test_script_scanner.next_segment
        cmd = []

        for item in cmd2.split(" "):
            if TestScriptSymbolTable.lookup_sym_tab(item, TestScriptSymbolTable.test_script_sym_tab):
                cmd.append(TestScriptSymbolTable.get_value_from_sym_tab(item, TestScriptSymbolTable.test_script_sym_tab))
            else:
                cmd.append("$$$")

        common.logging.debug("..append %s = %s %s using %s" % (cmd1, cmd[0] if cmd[0] != "$$$" else cmd2.split(" ")[0], cmd[1] if cmd[1] != "$$$" else cmd2.split(" ")[1], "space" if cmd3 == " " else cmd3))

        if TestScriptSymbolTable.lookup_sym_tab(cmd1, TestScriptSymbolTable.test_script_sym_tab):
            TestScriptSymbolTable.insert_sym_tab(cmd1, "%s%s%s" % (cmd[0], cmd3, cmd[1]), TestScriptSymbolTable.test_script_sym_tab)
        else:
            if not TestScriptSymbolTable.lookup_sym_tab(cmd1, TestScriptSymbolTable.capi_cmd_ret_sym_tab):
                TestScriptSymbolTable.insert_sym_tab(cmd1, "", TestScriptSymbolTable.capi_cmd_ret_sym_tab)
            TestScriptParser.qll.insert(cmd0, {"LISTNAME" : cmd1, "LISTITEM" : {cmd2.split(" ")[0] : cmd[0], cmd2.split(" ")[1] : cmd[1]}, "ITEMDELIMITER" : cmd3}, "UCCACTION", TestScriptParser.group_tag_name)
            TestScriptParser.add_end_flag = True

        self.test_script_scanner.skip_next_segment()


    def process_get_user_input(self):
        """Parses the GetUserInput keyword.
        """        
        cmd0 = self.test_script_scanner.current_elmt.segment_text
        cmdval = self.test_script_scanner.get_next_segment_value()
        
        self.test_script_scanner.next_element()
        cmdvar = self.test_script_scanner.next_segment
        if not TestScriptSymbolTable.lookup_sym_tab(cmdvar, TestScriptSymbolTable.capi_cmd_ret_sym_tab):
            TestScriptSymbolTable.insert_sym_tab(cmdvar, "", TestScriptSymbolTable.capi_cmd_ret_sym_tab)

        TestScriptParser.qll.insert(cmd0, {"MSG" : cmdval, "INPUTVAL" : cmdvar}, "UCCACTION", TestScriptParser.group_tag_name)
        TestScriptParser.add_end_flag = True
        self.test_script_scanner.skip_next_segment()


    def process_sniffer_enable(self):
        """Parses the SnifferEnable keyword.
        """
        snf_val = self.test_script_scanner.get_next_segment_value()
        TestScriptSymbolTable.insert_sym_tab("$SnifferFileName", "%s_%s" % ("SnifferTrace", common.GlobalConfigFiles.curr_tc_name), TestScriptSymbolTable.test_script_sym_tab)
        if snf_val == '1':
            TestScriptSymbolTable.insert_sym_tab("$StartSniffer", "Sniffer-Start.txt", TestScriptSymbolTable.test_script_sym_tab)
            TestScriptSymbolTable.insert_sym_tab("$StopSniffer", "Sniffer-Stop.txt", TestScriptSymbolTable.test_script_sym_tab)
        else:
            TestScriptSymbolTable.insert_sym_tab("$StartSniffer", "Sniffer-Disable.txt", TestScriptSymbolTable.test_script_sym_tab)
            TestScriptSymbolTable.insert_sym_tab("$StopSniffer", "Sniffer-Disable.txt", TestScriptSymbolTable.test_script_sym_tab)

        self.test_script_scanner.skip_next_segment()


    def process_rinfo(self):
        """Parses the Rinfo keyword.
        """
        keyword = self.test_script_scanner.current_elmt.segment_text
        cmd1 = self.test_script_scanner.get_next_segment_value()
        self.test_script_scanner.next_element()
        cmd2 = self.test_script_scanner.next_segment
        if cmd2 == "EOL":
            TestScriptParser.qll.insert(keyword, {"RESULT" : cmd1}, "UCCACTION", TestScriptParser.group_tag_name)
        else:
            TestScriptParser.qll.insert(keyword, {"RESULT" : cmd1, "MSG": cmd2}, "UCCACTION", TestScriptParser.group_tag_name)
            self.test_script_scanner.skip_next_segment()
        TestScriptParser.add_end_flag = True


    def process_echo_exit_info_sleep(self, element_type):
        """Parses the Echo/Exit/Info/Sleep keywords.

        Args:
            element_type (object): The object of TestScriptElementType class.
        """
        ucckey = self.test_script_scanner.current_elmt.segment_text
        uccval = self.test_script_scanner.get_next_segment_value()
        if uccval == "" and TestScriptSymbolTable.lookup_sym_tab(self.test_script_scanner.next_segment, TestScriptSymbolTable.capi_cmd_ret_sym_tab):
            uccval = self.test_script_scanner.next_segment
        else:
            if TestScriptSymbolTable.lookup_sym_tab(self.test_script_scanner.next_segment, TestScriptSymbolTable.test_script_sym_tab):
                uccval = TestScriptSymbolTable.get_value_from_sym_tab(self.test_script_scanner.next_segment, TestScriptSymbolTable.test_script_sym_tab)
                if TestScriptSymbolTable.lookup_sym_tab(uccval, TestScriptSymbolTable.test_script_sym_tab):
                    uccval = TestScriptSymbolTable.get_value_from_sym_tab(uccval, TestScriptSymbolTable.test_script_sym_tab)

        if element_type == TestScriptElementType.SLEEP:
            TestScriptParser.qll.insert(ucckey, uccval, "UCCACTION", TestScriptParser.group_tag_name)
            TestScriptParser.add_end_flag = True
        elif element_type == TestScriptElementType.EXIT:
            if self.test_mngr_initr.test_config_cxt.is_all_init_command_file:
                raise SystemExit(uccval)
        else:
            TestScriptParser.qll.insert(ucckey, {"MSG": uccval}, "UCCACTION", TestScriptParser.group_tag_name)
            TestScriptParser.add_end_flag = True
        self.test_script_scanner.skip_next_segment()


    def process_mexpr(self):
        """Parses the Mexpr keyword.
        """        
        cmd0 = self.test_script_scanner.current_elmt.segment_text
        first_mex_var = self.test_script_scanner.next_segment
        first_mex_var_val = ""
        if TestScriptSymbolTable.lookup_sym_tab(first_mex_var, TestScriptSymbolTable.test_script_sym_tab):
            first_mex_var_val = TestScriptSymbolTable.get_value_from_sym_tab(first_mex_var, TestScriptSymbolTable.test_script_sym_tab)
        else:
            if not TestScriptSymbolTable.lookup_sym_tab(first_mex_var, TestScriptSymbolTable.capi_cmd_ret_sym_tab):
                TestScriptSymbolTable.insert_sym_tab(first_mex_var, "", TestScriptSymbolTable.capi_cmd_ret_sym_tab)

        self.test_script_scanner.next_element()
        second_mex_var = self.test_script_scanner.next_segment

        self.test_script_scanner.next_element()
        third_mex_var = self.test_script_scanner.next_segment
        third_mex_var_val = self.test_script_scanner.get_next_segment_value()

        if second_mex_var == "%":
            if first_mex_var_val != "" and third_mex_var_val != "":
                TestScriptSymbolTable.insert_sym_tab(first_mex_var, (int(first_mex_var_val) * int(third_mex_var_val)) / 100, TestScriptSymbolTable.test_script_sym_tab)
            else:
                if TestScriptElementType.get_element_type(third_mex_var) == "VARIABLE" and not TestScriptSymbolTable.lookup_sym_tab(third_mex_var, TestScriptSymbolTable.capi_cmd_ret_sym_tab):
                    TestScriptSymbolTable.insert_sym_tab(third_mex_var, "", TestScriptSymbolTable.capi_cmd_ret_sym_tab)
                TestScriptParser.qll.insert(cmd0, {"FIRSTVAR" : first_mex_var, "OPERATOR" : second_mex_var, "SECONDVAR" : third_mex_var_val}, "UCCACTION", TestScriptParser.group_tag_name)
                TestScriptParser.add_end_flag = True

        self.test_script_scanner.skip_next_segment()


    def process_resultcheck(self):
        """Parses the Resultcheck keyword.
        """        
        rslt_chk = self.test_script_scanner.next_segment.split(',')

        rslt_var_val = TestScriptSymbolTable.get_value_from_sym_tab(rslt_chk[0], TestScriptSymbolTable.test_script_sym_tab)
        if rslt_var_val:
            final_str = self.test_script_scanner.next_segment.replace(rslt_chk[0], rslt_var_val)
            TestScriptParser.qll.insert(self.test_script_scanner.current_elmt.segment_text, final_str, "RESULTCHECK", TestScriptParser.group_tag_name)
            TestScriptParser.add_end_flag = True
        else:
            rslt_var_val1 = TestScriptSymbolTable.get_value_from_sym_tab(rslt_chk[0], TestScriptSymbolTable.capi_cmd_ret_sym_tab)
            if rslt_var_val1 or rslt_var_val1 == "":
                TestScriptParser.qll.insert(self.test_script_scanner.current_elmt.segment_text, self.test_script_scanner.next_segment, "RESULTCHECK", TestScriptParser.group_tag_name)
                TestScriptParser.add_end_flag = True
            else:
                raise SyntaxError

        self.test_script_scanner.next_element()
        self.test_script_scanner.skip_next_segment()


    def process_cat(self):
        """Parses the Cat keyword.
        """        
        cmd0 = self.test_script_scanner.current_elmt.segment_text
        var = ""
        comma_list = []
        first_cat_var = self.test_script_scanner.next_segment
        self.test_script_scanner.next_element()

        second_cat_var = self.test_script_scanner.next_segment
        varlist = second_cat_var.split(",")

        self.test_script_scanner.next_element()
        third_cat_var = self.test_script_scanner.next_segment

        for v in varlist:
            if TestScriptSymbolTable.lookup_sym_tab(v, TestScriptSymbolTable.test_script_sym_tab):
                second_cat_val = TestScriptSymbolTable.get_value_from_sym_tab(v, TestScriptSymbolTable.test_script_sym_tab)
                if TestScriptSymbolTable.lookup_sym_tab(second_cat_val, TestScriptSymbolTable.test_script_sym_tab):
                    second_cat_val = TestScriptSymbolTable.get_value_from_sym_tab(second_cat_val, TestScriptSymbolTable.test_script_sym_tab)
                if second_cat_val:
                    if var:
                        var = ("%s%s%s" % (var, third_cat_var, v))
                    else:
                        var = ("%s" % (v))
                    comma_list.append(second_cat_val)
                else:
                    comma_list.append(v)
            else:
                if not TestScriptSymbolTable.lookup_sym_tab(v, TestScriptSymbolTable.capi_cmd_ret_sym_tab):
                    TestScriptSymbolTable.insert_sym_tab(v, "", TestScriptSymbolTable.capi_cmd_ret_sym_tab)
        # end of for loop

        if TestScriptSymbolTable.lookup_sym_tab(first_cat_var, TestScriptSymbolTable.test_script_sym_tab):
            TestScriptSymbolTable.insert_sym_tab(first_cat_var, var, TestScriptSymbolTable.test_script_sym_tab)
        else:
            if not TestScriptSymbolTable.lookup_sym_tab(first_cat_var, TestScriptSymbolTable.capi_cmd_ret_sym_tab):
                TestScriptSymbolTable.insert_sym_tab(first_cat_var, "", TestScriptSymbolTable.capi_cmd_ret_sym_tab)
            TestScriptParser.qll.insert(cmd0, {"FIRSTVAR" : first_cat_var, "VARLIST" : ','.join(comma_list), "DELIMITER" : third_cat_var}, "UCCACTION", TestScriptParser.group_tag_name)
            TestScriptParser.add_end_flag = True

        self.test_script_scanner.skip_next_segment()


    def process_storethroughput(self):
        """Parese the Storethroughput keyword.
        """        
        keyword = self.test_script_scanner.current_elmt.segment_text
        st_var1 = self.test_script_scanner.next_segment
        self.test_script_scanner.next_element()

        st_var2 = self.test_script_scanner.next_segment
        cmd = st_var2.split(",")
        cmd2_val = TestScriptSymbolTable.get_value_from_sym_tab(cmd[2], TestScriptSymbolTable.test_script_sym_tab)
        common.logging.debug("Storing the Throughput(Mbps) value of stream %s[%s %s] in %s  duration=%s phase=%s", cmd[0], cmd[3], "%", st_var1, cmd2_val, cmd[1])

        if TestScriptSymbolTable.lookup_sym_tab(cmd[0], TestScriptSymbolTable.capi_cmd_ret_sym_tab) and not TestScriptSymbolTable.lookup_sym_tab(st_var1, TestScriptSymbolTable.capi_cmd_ret_sym_tab):
            TestScriptSymbolTable.insert_sym_tab(st_var1, "", TestScriptSymbolTable.capi_cmd_ret_sym_tab)
        else:
            TestScriptSymbolTable.insert_sym_tab(st_var1, "", TestScriptSymbolTable.test_script_sym_tab)

        TestScriptParser.qll.insert(keyword, {"STOREVAR" : st_var1, "STREAMID" : cmd[0], "PHASE" : cmd[1], "DURATION": cmd2_val, "PERCENTAGE" : cmd[3]}, "TRAFFICSTREAM", TestScriptParser.group_tag_name)
        TestScriptParser.add_end_flag = True
        self.test_script_scanner.skip_next_segment()


    def process_echoIfNoWTS(self):
        """Parses the EchoIfnowts keyword.
        """       
        if TestScriptSymbolTable.get_value_from_sym_tab("$" + TestScriptElementType.WTS_CONTROLAGENT_SUPPORT, TestScriptSymbolTable.test_script_sym_tab) == "0":
            keyword = self.test_script_scanner.current_elmt.segment_text
            if self.test_script_scanner.next_segment.startswith('$'):
                var1 = self.test_script_scanner.next_segment
                var1_val = self.test_script_scanner.get_next_segment_value()
                if var1_val == "" and TestScriptSymbolTable.lookup_sym_tab(var1, TestScriptSymbolTable.capi_cmd_ret_sym_tab):
                    TestScriptParser.qll.insert(keyword, {"MSG" : var1}, "UCCACTION", TestScriptParser.group_tag_name)
                    TestScriptParser.add_end_flag = True
                elif var1_val != "":
                    TestScriptParser.qll.insert(keyword, {"MSG" : var1_val}, "UCCACTION", TestScriptParser.group_tag_name)
                    TestScriptParser.add_end_flag = True
            else:
                TestScriptParser.qll.insert(keyword, {"MSG" : self.test_script_scanner.next_segment}, "UCCACTION", TestScriptParser.group_tag_name)
                TestScriptParser.add_end_flag = True

            self.test_script_scanner.skip_next_segment()
        else:
            self.test_script_scanner.skip_next_segment()
            if isinstance(self.test_script_scanner.current_elmt, ScriptVariableElement):
                if not (TestScriptSymbolTable.lookup_sym_tab(self.test_script_scanner.current_elmt.segment_text, TestScriptSymbolTable.capi_cmd_ret_sym_tab) and TestScriptSymbolTable.lookup_sym_tab(self.test_script_scanner.current_elmt.segment_text, TestScriptSymbolTable.test_script_sym_tab)):
                    raise common.TestConfigError("Not recognized variable - %s" % self.test_script_scanner.current_elmt.segment_text)


    def process_ifNoWTS(self):
        """Parses the Ifnowts keyword.
        """        
        if TestScriptSymbolTable.get_value_from_sym_tab("$" + TestScriptElementType.WTS_CONTROLAGENT_SUPPORT, TestScriptSymbolTable.test_script_sym_tab) == "0":
            keyword = self.test_script_scanner.current_elmt.segment_text
            last_var = ""
            var2 = self.test_script_scanner.next_segment
            self.test_script_scanner.next_element()
            if self.test_script_scanner.next_segment != "EOL":
                var3 = self.test_script_scanner.next_segment
                var3_val = self.test_script_scanner.get_next_segment_value()
                if var3_val == "" and TestScriptSymbolTable.lookup_sym_tab(var3, TestScriptSymbolTable.capi_cmd_ret_sym_tab):
                    last_var = var3
                elif var3_val != "":
                    last_var = var3_val
                TestScriptParser.qll.insert(keyword, {"MSG" : var2, "EXPRVAR" : last_var}, "UCCACTION", TestScriptParser.group_tag_name)
                TestScriptParser.add_end_flag = True
                self.test_script_scanner.skip_next_segment()
            else:
                TestScriptParser.qll.insert(keyword, {"MSG" : var2, "EXPRVAR" : None}, "UCCACTION", TestScriptParser.group_tag_name)
                TestScriptParser.add_end_flag = True
        else:            
            self.test_script_scanner.next_element()
            while self.test_script_scanner.current_elmt.segment_text != "EOL":                
                self.test_script_scanner.next_element()


    def process_random_gen(self):
        """Parses the Random generation keyword.
        """       
        cmd0 = self.test_script_scanner.current_elmt.segment_text
        cmd1 = ""
        self.test_script_scanner.next_element()
        rand_var1 = self.test_script_scanner.current_elmt.segment_text
        if isinstance(self.test_script_scanner.current_elmt, ScriptVariableElement):
            if TestScriptSymbolTable.lookup_sym_tab(rand_var1, TestScriptSymbolTable.test_script_sym_tab):
                if re.search('null', rand_var1):
                    cmd1 = "null"
                else:
                    rand_var1_val = self.test_script_scanner.get_next_segment_value()
                    if rand_var1_val == "":
                        cmd1 = rand_var1.split(" ")
                    else:
                        cmd1 = rand_var1_val.split(" ")
            else:
                if not TestScriptSymbolTable.lookup_sym_tab(rand_var1, TestScriptSymbolTable.capi_cmd_ret_sym_tab):
                    TestScriptSymbolTable.insert_sym_tab(rand_var1, "", TestScriptSymbolTable.capi_cmd_ret_sym_tab)

        self.test_script_scanner.next_element()
        rand_var2 = self.test_script_scanner.current_elmt.segment_text
        if isinstance(self.test_script_scanner.current_elmt, ScriptVariableElement):
            if TestScriptSymbolTable.lookup_sym_tab(rand_var2, TestScriptSymbolTable.test_script_sym_tab):
                TestScriptSymbolTable.insert_sym_tab(rand_var2, "0", TestScriptSymbolTable.test_script_sym_tab)
            else:
                if not TestScriptSymbolTable.lookup_sym_tab(rand_var1, TestScriptSymbolTable.capi_cmd_ret_sym_tab):
                    TestScriptSymbolTable.insert_sym_tab(rand_var1, "", TestScriptSymbolTable.capi_cmd_ret_sym_tab)

        rand_var3 = self.test_script_scanner.next_segment
        rand_var3_val = self.test_script_scanner.get_next_segment_value()
        if rand_var3_val == "":
            cmd3 = int(rand_var3)
        else:
            cmd3 = int(rand_var3_val)

        if cmd1 != "":
            i = 0
            oplist = []

            while True:
                randnum = random.randint(0, 65535)
                for c in cmd1:
                    if isinstance(c, int):
                        if randnum == int(c):
                            del randnum
                            break
                try:
                    oplist.append(randnum)
                    i = i + 1
                except NameError:
                    common.logging.debug("%s Not defined" % randnum)
                if i == cmd3:
                    break

            TestScriptSymbolTable.insert_sym_tab(rand_var2, ' '.join("%d" % x for x in oplist), TestScriptSymbolTable.test_script_sym_tab)
            common.logging.debug(" %s" % TestScriptSymbolTable.get_value_from_sym_tab(rand_var2, TestScriptSymbolTable.test_script_sym_tab))
        else:
            TestScriptParser.qll.insert(cmd0, {"FIRSTVAR" : rand_var1, "RANDVAR" : rand_var2, "RANDMAX" : rand_var3}, "UCCACTION", TestScriptParser.group_tag_name)
            TestScriptParser.add_end_flag = True

        self.test_script_scanner.skip_next_segment()


    def process_result_var(self):
        """Parses the Traffic related keywords.
        """
        value_str = self.test_script_scanner.next_segment
        rslt_list = self.test_script_scanner.next_segment.split(',')
        rslt_list1 = self.test_script_scanner.next_segment.split(',')
        for i, item in enumerate(rslt_list):
            if item.startswith('$'):
                item_val = TestScriptSymbolTable.get_value_from_sym_tab(item, TestScriptSymbolTable.test_script_sym_tab)
                if item_val is not None:
                    rslt_list1[i] = item_val                  

        value_str = ','.join(rslt_list1)
        TestScriptParser.qll.insert(self.test_script_scanner.current_elmt.segment_text, value_str, "STREAMCHECK", TestScriptParser.group_tag_name)
        TestScriptParser.add_end_flag = True
        self.test_script_scanner.next_element()
        self.test_script_scanner.skip_next_segment()


    def process_search(self):
        """Parses the Search keyword.
        """        
        cmd0 = self.test_script_scanner.current_elmt.segment_text
        cmd1 = []
        cmd2 = ""
        first_seg_var = self.test_script_scanner.next_segment
        if TestScriptSymbolTable.lookup_sym_tab(first_seg_var, TestScriptSymbolTable.test_script_sym_tab):
            first_seg_val = TestScriptSymbolTable.get_value_from_sym_tab(first_seg_var, TestScriptSymbolTable.test_script_sym_tab)
            if first_seg_val is not None:
                cmd1 = first_seg_val
        else:
            if not TestScriptSymbolTable.lookup_sym_tab(first_seg_var, TestScriptSymbolTable.capi_cmd_ret_sym_tab):
                TestScriptSymbolTable.insert_sym_tab(first_seg_var, "", TestScriptSymbolTable.capi_cmd_ret_sym_tab)

        self.test_script_scanner.next_element()

        second_seg_var = self.test_script_scanner.next_segment
        if TestScriptSymbolTable.lookup_sym_tab(second_seg_var, TestScriptSymbolTable.test_script_sym_tab):
            second_seg_val = TestScriptSymbolTable.get_value_from_sym_tab(second_seg_var, TestScriptSymbolTable.test_script_sym_tab)
            if second_seg_val is not None:
                cmd2 = second_seg_val
        else:
            TestScriptSymbolTable.insert_sym_tab(second_seg_var, "", TestScriptSymbolTable.capi_cmd_ret_sym_tab)

        self.test_script_scanner.next_element()
        third_seg_var = self.test_script_scanner.next_segment

        if len(cmd1) > 0 and cmd2 != "":
            TestScriptSymbolTable.insert_sym_tab(third_seg_var, "0", TestScriptSymbolTable.test_script_sym_tab)
        else:
            TestScriptSymbolTable.insert_sym_tab(third_seg_var, "", TestScriptSymbolTable.capi_cmd_ret_sym_tab)

        self.test_script_scanner.next_element()

        if self.test_script_scanner.next_segment != "EOL":
            if self.test_script_scanner.next_segment.lower() == "exact" or self.test_script_scanner.next_segment.lower() == "diff":
                if len(cmd1) > 0 and cmd2 != "":
                    if sorted(cmd1) == sorted(cmd2):
                        TestScriptSymbolTable.insert_sym_tab(third_seg_var, "1", TestScriptSymbolTable.test_script_sym_tab)
                    else:
                        if self.test_script_scanner.next_segment.lower() == "diff":                            
                            cmd1_set = set(cmd1)
                            cmd2 = set(cmd2.split(' '))
                            cmd3 = cmd1_set.difference(cmd2)
                            TestScriptSymbolTable.insert_sym_tab(third_seg_var, "%s" %(' '.join(list(cmd3))), TestScriptSymbolTable.test_script_sym_tab)
                else:
                    TestScriptParser.qll.insert(cmd0, {"LISTNAME" : first_seg_var, "SEARCHITEM" : second_seg_var, "SEARCHRESULT" : third_seg_var, "LASTWORD" : self.test_script_scanner.next_segment}, "UCCACTION", TestScriptParser.group_tag_name)
                    TestScriptParser.add_end_flag = True

            if self.test_script_scanner.next_segment.lower() == "substring":
                if len(cmd1) > 0 and cmd2 != "":
                    common.logging.info("Search \"%s\" in \"%s\"" %(cmd2, cmd1))                    
                    if cmd2 in cmd1:
                        TestScriptSymbolTable.insert_sym_tab(third_seg_var, "1", TestScriptSymbolTable.test_script_sym_tab)
                else:
                    TestScriptParser.qll.insert(cmd0, {"LISTNAME" : first_seg_var, "SEARCHITEM" : second_seg_var, "SEARCHRESULT" : third_seg_var, "LASTWORD" : self.test_script_scanner.next_segment}, "UCCACTION", TestScriptParser.group_tag_name)
                    TestScriptParser.add_end_flag = True
                    
            self.test_script_scanner.skip_next_segment()
        else:
            i = 0
            #Check for NULL before comparison
            if len(cmd1) > 0 and cmd2 != "":
                cmd2 = cmd2.split(" ")
                for c in cmd2:
                    common.logging.info("Search \"%s\" in \"%s\"" %(cmd2[i], cmd1))
                    if re.search('%s' % c, cmd1, re.I):
                        TestScriptSymbolTable.insert_sym_tab(cmd3, "1", TestScriptSymbolTable.test_script_sym_tab)
                    i += 1
            else:
                TestScriptParser.qll.insert(cmd0, {"LISTNAME" : first_seg_var, "SEARCHITEM" : second_seg_var, "SEARCHRESULT" : third_seg_var}, "UCCACTION", TestScriptParser.group_tag_name)
                TestScriptParser.add_end_flag = True

        #self.test_script_scanner.skip_next_segment()


    def process_math_calc(self):
        """Parses the Math keyword.
        """        
        keyword = self.test_script_scanner.current_elmt.segment_text
        self.test_script_scanner.next_element()

        if isinstance(self.test_script_scanner.current_elmt, ScriptVariableElement):
            first_var = self.test_script_scanner.current_elmt.segment_text
            first_var_val = TestScriptSymbolTable.get_value_from_sym_tab(first_var, TestScriptSymbolTable.test_script_sym_tab)

            oper_sym = self.test_script_scanner.next_segment
            self.test_script_scanner.next_element()

            third_var = self.test_script_scanner.next_segment
            third_var_val = self.test_script_scanner.get_next_segment_value()
        else:
            raise SyntaxError

        if oper_sym == TestScriptElementType.get_resv_word_key_from_val(TestScriptElementType.RAND):
            #if (not Util.str_to_type(first_var_val) is int) and (not Util.str_to_type(first_var_val) is float):
            #    raise SyntaxError
            varlist = third_var_val.split(":")
            random_index = random.randrange(0, len(varlist))
            TestScriptSymbolTable.insert_sym_tab(first_var, "%s" % int(varlist[random_index]), TestScriptSymbolTable.test_script_sym_tab)
            self.test_script_scanner.next_element()
            return

        if (first_var_val == "" or first_var_val is None) and TestScriptSymbolTable.lookup_sym_tab(first_var, TestScriptSymbolTable.capi_cmd_ret_sym_tab) and third_var_val:
            TestScriptParser.qll.insert(keyword, first_var + oper_sym + third_var_val, "UCCACTION", TestScriptParser.group_tag_name)
            TestScriptParser.add_end_flag = True
            TestScriptSymbolTable.insert_sym_tab(first_var, "", TestScriptSymbolTable.capi_cmd_ret_sym_tab)
        elif (third_var_val == "" or third_var_val is None) and TestScriptSymbolTable.lookup_sym_tab(third_var, TestScriptSymbolTable.capi_cmd_ret_sym_tab) and first_var_val:
            TestScriptParser.qll.insert(keyword, first_var_val + oper_sym + third_var, "UCCACTION", TestScriptParser.group_tag_name)
            TestScriptParser.add_end_flag = True
            TestScriptSymbolTable.insert_sym_tab(third_var, "", TestScriptSymbolTable.capi_cmd_ret_sym_tab)
        elif (first_var_val == "" or first_var_val is None) and (third_var_val == "" or third_var_val is None):
            TestScriptParser.qll.insert(keyword, first_var + oper_sym + third_var, "UCCACTION", TestScriptParser.group_tag_name)
            TestScriptParser.add_end_flag = True
            TestScriptSymbolTable.insert_sym_tab(first_var, "", TestScriptSymbolTable.capi_cmd_ret_sym_tab)
            TestScriptSymbolTable.insert_sym_tab(third_var, "", TestScriptSymbolTable.capi_cmd_ret_sym_tab)
        elif (first_var_val != "" or first_var_val is not None) and (third_var_val != "" or third_var_val is not None):
            if oper_sym == TestScriptElementType.get_spcl_sym_key_from_val(TestScriptElementType.PLUS) or oper_sym == TestScriptElementType.get_spcl_sym_key_from_val(TestScriptElementType.MINUS) \
                or oper_sym == TestScriptElementType.get_spcl_sym_key_from_val(TestScriptElementType.MULTIPLY) or oper_sym == TestScriptElementType.get_spcl_sym_key_from_val(TestScriptElementType.DIVIDE) \
                or oper_sym == TestScriptElementType.get_spcl_sym_key_from_val(TestScriptElementType.MODULO):
                    val = eval(str(first_var_val) + ' ' + oper_sym + ' ' + str(third_var_val))
                    TestScriptSymbolTable.insert_sym_tab(first_var, val, TestScriptSymbolTable.test_script_sym_tab)
            else:
                raise SyntaxError

        self.test_script_scanner.next_element()


    def check_in_script_loop(self):
        """Checks for script calling loop.
        """
        dict1 = sorted(TestScriptParser.sub_file_call_dict.items(), key=itemgetter(1))
        dict2 = sorted(TestScriptParser.sub_file_call_dict.items(), key=itemgetter(1))
        for fp in dict1:            
            curr_parent = fp[0].split(':')[0]
            curr_child = fp[0].split(':')[1]
            for fp1 in dict2:
                if fp[1] == fp1[1]:
                    continue
                else:
                    if curr_parent == fp1[0].split(':')[1] and curr_child == fp1[0].split(':')[0]:
                        return True
        return False


    def parse_testbed_device_element(self, next_elem, segment_text="", dollar_flag=False):
        """Parses the testbed device element.

        Args:
            next_elem (str): The next element text to be parsed.
            segment_text (str): The segment text.
        """
        key_name = segment_text
        key_value = ""
        serial_port_found = False
        
        segment_var_list = next_elem.split(',')
        if not segment_var_list:
            raise SyntaxError
        else:            
            if len(segment_var_list) == 1:
                # check if it is in IP format only
                if Util.is_IPv4_addr(segment_var_list[0]):                    
                    if len(segment_var_list[0].split(' ')) == 2:
                        finalip = segment_var_list[0].split(' ')[0]
                        finalport = segment_var_list[0].split(' ')[1]
                        serial_port_found = True
                    elif len(segment_var_list[0].split(' ')) == 1:
                        finalip = segment_var_list[0]
                    else:
                        raise SyntaxError

                    if Util.is_valid_IPv4_addr(finalip):
                        key_value = finalip # test network ip
                    else:
                        raise SyntaxError
                elif Util.is_MAC_addr(segment_var_list[0]):
                    if Util.is_valid_MAC_addr(segment_var_list[0]):
                        key_value = segment_var_list[0] # test network ip
                    else:
                        raise SyntaxError
                else:
                    key_value = segment_var_list[0]
            
            if re.search("ipaddr=", next_elem, 0) and re.search("port=", next_elem, 0):
                ipaddr = segment_var_list[0].split('=')[1]
                port = segment_var_list[1].split('=')[1]
                if not Util.is_IPv4_addr(ipaddr) and not Util.is_valid_IPv4_addr(ipaddr):
                    raise SyntaxError
                key_value = {"ipaddr": ipaddr, "port" : port} # control network ip and port

            if key_name != "": # for define statement where dollar variable is present
                if serial_port_found:
                    key_value = {"ipaddr": next_elem, "port" : finalport} # control network ip and port
                    TestScriptSymbolTable.insert_sym_tab(key_name, {"ipaddr": next_elem, "port" : finalport}, TestScriptSymbolTable.test_script_sym_tab)
                else:
                    if len(segment_var_list) == 1:
                        TestScriptSymbolTable.insert_sym_tab(key_name, segment_var_list[0], TestScriptSymbolTable.test_script_sym_tab)
                    if len(segment_var_list) == 2:
                        TestScriptSymbolTable.insert_sym_tab(key_name, {"ipaddr": segment_var_list[0], "port" : segment_var_list[1]}, TestScriptSymbolTable.test_script_sym_tab)
                        
            self.test_script_scanner.skip_next_segment()
        
        if dollar_flag:
            key_name = key_name.replace("$", "")
        
        self.build_sll_from_xml_tree_node(key_name, key_value, "TESTBED")



class IfStatementParser(TestScriptParser):
    """The class that manages the traffic data streams.

    Attributes:
        test_script_scanner (object): The oject of TestScriptScanner class.
        test_mngr_initr (object): The object of TestManagerInitializer class.

    """
    def __init__(self, test_script_scanner, test_mngr_initr):        
        self.test_script_scanner = test_script_scanner
        self.test_mngr_initr = test_mngr_initr

    def parse(self):
        """Initializes the test environment including domain object managers

        Args:
            usr_in_cmd (object): The object of TestManagerInitializer class.
        """
        self.test_script_scanner.next_element()
        expr_parser = ExpressionStatementParser(self.test_script_scanner, self.test_mngr_initr)
        b = expr_parser.parse()
        if not b: # b = False skip the statements in between if and else
            if not self.test_script_scanner.synchronize([TestScriptElementType.get_resv_word_key_from_val(TestScriptElementType.ELSE), TestScriptElementType.get_resv_word_key_from_val(TestScriptElementType.ENDIF)]):
                raise SyntaxError



class ExpressionStatementParser(TestScriptParser):
    """The expression statement parser class.

    Attributes:
        test_script_scanner (object): The oject of TestScriptScanner class.
        test_mngr_initr (object): The object of TestManagerInitializer class.

    """
    def __init__(self, test_script_scanner, test_mngr_initr):        
        self.test_script_scanner = test_script_scanner
        self.test_mngr_initr = test_mngr_initr


    def parse(self):
        """Parses the expression statement.
        """
        if_eval_str = ""
        temp_logic_result = False
        final_logic_result_list = []
        is_capi_ret_var_found = False
        final_result_str = ""

        element_type = self.test_script_scanner.current_elmt.element_type
            
        while self.test_script_scanner.next_segment != "EOL":
            value1 = None
            if isinstance(self.test_script_scanner.current_elmt, ScriptVariableElement) or isinstance(self.test_script_scanner.current_elmt, ScriptStringElement) or isinstance(self.test_script_scanner.current_elmt, TestbedDeviceElement):
                if TestScriptSymbolTable.lookup_sym_tab(self.test_script_scanner.current_elmt.segment_text, TestScriptSymbolTable.capi_cmd_ret_sym_tab) and (self.test_mngr_initr.test_config_cxt.is_test_case_file or self.test_mngr_initr.test_config_cxt.is_all_init_command_file):                
                    if_eval_str = if_eval_str + self.test_script_scanner.current_elmt.segment_text + self.test_script_scanner.next_segment

                    is_capi_ret_var_found = True                    
                    self.test_script_scanner.next_element()
                    
                    if_eval_str = if_eval_str + self.test_script_scanner.next_segment

                    self.test_script_scanner.next_element()

                    if self.test_script_scanner.next_segment == TestScriptElementType.get_resv_word_key_from_val(TestScriptElementType.AND) or self.test_script_scanner.next_segment == TestScriptElementType.get_resv_word_key_from_val(TestScriptElementType.OR):
                        if_eval_str = if_eval_str + ' ' + self.test_script_scanner.next_segment + ' '
                        self.test_script_scanner.next_element()
                        self.test_script_scanner.next_element()
                    continue
                
                value1 = TestScriptSymbolTable.get_value_from_sym_tab(self.test_script_scanner.current_elmt.segment_text, TestScriptSymbolTable.test_script_sym_tab)
                if value1 is None:
                    # for those dollar variables that are used in AllInitConfig.txt file before they are present in the initEnv file which is generated after parsing AllInitConfig file
                    if self.test_mngr_initr.test_config_cxt.is_all_init_config_file:
                        no_dollar_var = self.test_script_scanner.current_elmt.segment_text.replace("$", "")
                        if no_dollar_var in self.test_mngr_initr.test_config_info_mngr.test_config_info.var_list:
                            value1 = self.test_mngr_initr.test_config_info_mngr.test_config_info.var_list[no_dollar_var]
                        else:
                            raise common.TestConfigError("Value of %s doesn't exist and returns None" % self.test_script_scanner.current_elmt.segment_text)
                    else:
                        if isinstance(self.test_script_scanner.current_elmt, ScriptStringElement):
                            value1 = self.test_script_scanner.current_elmt.segment_text
                        else:
                            raise common.TestConfigError("Value of %s doesn't exist and returns None" % self.test_script_scanner.current_elmt.segment_text)

            if isinstance(self.test_script_scanner.current_elmt, ScriptStringElement):                
                if Util.str_to_type(self.test_script_scanner.current_elmt.segment_text) is int:                
                    value1 = float(self.test_script_scanner.current_elmt.segment_text)
                elif element_type == "STRING":
                    value1 = "%s" % self.test_script_scanner.current_elmt.segment_text
                else:
                    raise common.TestConfigError("Unrecognized element %s" % self.test_script_scanner.current_elmt.segment_text)

            temp_logic_result = self.parse_binary_operator(value1)
            final_logic_result_list.append(temp_logic_result)

            if self.test_script_scanner.next_segment == TestScriptElementType.get_resv_word_key_from_val(TestScriptElementType.AND) or self.test_script_scanner.next_segment == TestScriptElementType.get_resv_word_key_from_val(TestScriptElementType.OR):                
                final_result_str1 = ""
                if self.test_script_scanner.next_segment == TestScriptElementType.get_resv_word_key_from_val(TestScriptElementType.AND):
                    for result in final_logic_result_list:
                        final_result_str1 = final_result_str1 + ' ' + str(result)

                    ret1 = eval(final_result_str1)
                    if not ret1:
                        return ret1
                
                final_logic_result_list.append(self.test_script_scanner.next_segment)
                self.test_script_scanner.next_element()
                self.test_script_scanner.next_element()
                continue            
        # end of while loop

        if is_capi_ret_var_found:
            if_eval_str = if_eval_str.strip()
            TestScriptParser.qll.insert(if_eval_str, None, "IFCOND")
            TestScriptParser.add_end_flag = True
            TestScriptParser.ignore_if_else = True
            return True

        for result in final_logic_result_list:
            final_result_str = final_result_str + ' ' + str(result)

        ret = eval(final_result_str)
        return ret


    def parse_binary_operator(self, value1):
        """Parses the binary operation.

        Args:
            value1 (str): The first value to be compared.
        """
        self.test_script_scanner.next_element()
        element_type = self.test_script_scanner.current_elmt.element_type

        if isinstance(self.test_script_scanner.current_elmt, ScriptSpecialSymbolElement):
            if element_type == "EQ" or element_type == "NE" or element_type == "LT" or element_type == "LE" or element_type == "GT" or element_type == "GE":
                self.test_script_scanner.next_element()
                #element_type1 = self.test_script_scanner.current_elmt.element_type
                if isinstance(self.test_script_scanner.current_elmt, ScriptVariableElement) or isinstance(self.test_script_scanner.current_elmt, TestbedDeviceElement):
                    value2 = TestScriptSymbolTable.get_value_from_sym_tab(self.test_script_scanner.current_elmt.segment_text, TestScriptSymbolTable.test_script_sym_tab)
                elif isinstance(self.test_script_scanner.current_elmt, ScriptStringElement):
                    value2 = self.test_script_scanner.current_elmt.segment_text
                
                if isinstance(value1, dict) and isinstance(value2, dict):
                    if element_type == "EQ":
                        return True if cmp(value1, value2) == 0 else False
                    if element_type == "NE":
                        return False if cmp(value1, value2) == 0 else True
                    
                if Util.str_to_type(value1) is float or Util.str_to_type(value1) is int:
                    value1 = float(value1)
                elif Util.str_to_type(value1) is str:
                    value1 = "%s" % value1
                
                if Util.str_to_type(value2) is float or Util.str_to_type(value2) is int:
                    value2 = float(value2)
                else:
                    value2 = "%s" % value2

                if element_type == "EQ":
                    return value1 == value2
                elif element_type == "NE":
                    return value1 != value2
                elif element_type == "LT":
                    return value1 < value2
                elif element_type == "LE":
                    return value1 <= value2
                elif element_type == "GT":
                    return value1 > value2
                elif element_type == "GE":
                    return value1 >= value2
        else:
            raise UndefinedError



class DefineStatementParser(TestScriptParser):
    """The Define statement parser class.

    Attributes:
        test_script_scanner (object): The oject of TestScriptScanner class.
        test_mngr_initr (object): The object of TestManagerInitializer class.

    """
    def __init__(self, test_script_scanner, test_mngr_initr):        
        self.test_script_scanner = test_script_scanner
        self.test_mngr_initr = test_mngr_initr


    def parse(self):
        """Parses the line with Define keyword.
        """
        device_alias_found = False
        # Get the element after DEFINE
        self.test_script_scanner.next_element()
        key = self.test_script_scanner.current_elmt.segment_text
        
        if self.test_mngr_initr.test_config_cxt.is_all_init_config_file and self.test_script_scanner.test_script_source.test_script_source_name != common.GlobalConfigFiles.init_env_file:
            #if self.test_script_scanner.test_script_source.test_script_source_name == common.GlobalConfigFiles.init_env_file:
            #    return
                       
            if isinstance(self.test_script_scanner.current_elmt, TestbedDeviceElement):                
                return self.parse_testbed_device_element(self.test_script_scanner.next_segment, self.test_script_scanner.current_elmt.segment_text)

            if isinstance(self.test_script_scanner.current_elmt, ScriptVariableElement):
                value = self.test_script_scanner.next_segment
                if TestScriptSymbolTable.lookup_sym_tab(self.test_script_scanner.next_segment, TestScriptSymbolTable.test_script_sym_tab):
                    value = TestScriptSymbolTable.get_value_from_sym_tab(self.test_script_scanner.next_segment, TestScriptSymbolTable.test_script_sym_tab)

                #define!$AP1!Marvell11nAP!                
                for tbd in self.test_mngr_initr.test_prog_mngr.test_prog.testbed_dev_list:
                    if tbd.dev_name in value:
                        for key2 in TestScriptElementType.script_testbed_devices:
                            if re.search(key2, value, re.I):
                                TestScriptParser.device_alias_list.append(self.test_script_scanner.current_elmt.segment_text)
                                device_alias_found = True
                                break                                    
                        break
                    
                if not device_alias_found:
                    for item in TestScriptParser.device_alias_list:
                        if item in self.test_script_scanner.current_elmt.segment_text:
                            item_val = TestScriptSymbolTable.get_value_from_sym_tab(item, TestScriptSymbolTable.test_script_sym_tab)
                            dev_val = self.test_script_scanner.current_elmt.segment_text.replace(item, item_val)
                            TestScriptSymbolTable.insert_sym_tab(self.test_script_scanner.current_elmt.segment_text, value, TestScriptSymbolTable.test_script_sym_tab)
                            return self.parse_testbed_device_element(value, dev_val)                            
                
                    no_dollar_var = self.test_script_scanner.current_elmt.segment_text.replace("$", "")
                    for key1 in TestScriptElementType.script_testbed_devices:
                        if re.search(key1, no_dollar_var, re.I):                  
                            return self.parse_testbed_device_element(value, self.test_script_scanner.current_elmt.segment_text, True)

        if self.test_mngr_initr.test_config_cxt.is_test_case_file:
            if isinstance(self.test_script_scanner.current_elmt, ScriptReservedWordsElement):
                keyword = self.test_script_scanner.current_elmt.segment_text
                self.test_script_scanner.next_element()
                keyvalue = self.test_script_scanner.current_elmt.segment_text
                TestScriptParser.qll.insert(keyword, keyvalue, "UCCINTERNALVAR", TestScriptParser.group_tag_name)
                TestScriptParser.add_end_flag = True
                return
            
            if TestScriptParser.ignore_if_else:
                keyword = self.test_script_scanner.current_elmt.segment_text
                self.test_script_scanner.next_element()
                keyvalue = self.test_script_scanner.current_elmt.segment_text
                
                # redefine occurs and delete the previous define
                if TestScriptSymbolTable.lookup_sym_tab(keyvalue, TestScriptSymbolTable.capi_cmd_ret_sym_tab):
                    if TestScriptSymbolTable.lookup_sym_tab(keyword, TestScriptSymbolTable.test_script_sym_tab):
                        TestScriptSymbolTable.delete_key_from_sym_tab(keyword, TestScriptSymbolTable.test_script_sym_tab)
                    if TestScriptSymbolTable.lookup_sym_tab(keyvalue, TestScriptSymbolTable.test_script_sym_tab):
                        TestScriptSymbolTable.delete_key_from_sym_tab(keyvalue, TestScriptSymbolTable.test_script_sym_tab)
                    TestScriptSymbolTable.insert_sym_tab(keyword, keyvalue, TestScriptSymbolTable.capi_cmd_ret_sym_tab)
                    
                if TestScriptSymbolTable.lookup_sym_tab(keyword, TestScriptSymbolTable.test_script_sym_tab):
                    TestScriptSymbolTable.insert_sym_tab(keyword, keyvalue, TestScriptSymbolTable.test_script_sym_tab)
                    
                TestScriptParser.qll.insert(keyword, keyvalue, "UCCDEFINEVAR", TestScriptParser.group_tag_name)
                TestScriptParser.add_end_flag = True
                return
            
            if isinstance(self.test_script_scanner.current_elmt, ScriptVariableElement):
                if TestScriptSymbolTable.lookup_sym_tab(self.test_script_scanner.next_segment, TestScriptSymbolTable.capi_cmd_ret_sym_tab):
                    
                    #redefine occurs and delete the previous define
                    if TestScriptSymbolTable.lookup_sym_tab(self.test_script_scanner.next_segment, TestScriptSymbolTable.test_script_sym_tab):
                        TestScriptSymbolTable.delete_key_from_sym_tab(self.test_script_scanner.next_segment, TestScriptSymbolTable.test_script_sym_tab)
                    if TestScriptSymbolTable.lookup_sym_tab(self.test_script_scanner.current_elmt.segment_text, TestScriptSymbolTable.test_script_sym_tab):
                        TestScriptSymbolTable.delete_key_from_sym_tab(self.test_script_scanner.current_elmt.segment_text, TestScriptSymbolTable.test_script_sym_tab)
                
                    keyword = self.test_script_scanner.current_elmt.segment_text
                    self.test_script_scanner.next_element()
                    keyvalue = self.test_script_scanner.current_elmt.segment_text
                    TestScriptSymbolTable.insert_sym_tab(keyword, keyvalue, TestScriptSymbolTable.capi_cmd_ret_sym_tab)
                    TestScriptParser.qll.insert(keyword, keyvalue, "UCCDEFINEVAR", TestScriptParser.group_tag_name)
                    TestScriptParser.add_end_flag = True
                    return

        # Get the value of the element from symbol table - test_script_sym_tab
        self.test_script_scanner.next_element()
        element_type = self.test_script_scanner.current_elmt.element_type
        
        if element_type == "VARIABLE":
            if TestScriptSymbolTable.lookup_sym_tab(self.test_script_scanner.current_elmt.segment_text, TestScriptSymbolTable.test_script_sym_tab):
                value = TestScriptSymbolTable.get_value_from_sym_tab(self.test_script_scanner.current_elmt.segment_text, TestScriptSymbolTable.test_script_sym_tab)
            else:
                value = self.test_script_scanner.current_elmt.segment_text
        else:            
            if element_type == "STRING":
                value = self.test_script_scanner.current_elmt.segment_text
            else:                
                value = self.test_script_scanner.current_elmt.segment_text

        TestScriptSymbolTable.insert_sym_tab(key, value, TestScriptSymbolTable.test_script_sym_tab)

