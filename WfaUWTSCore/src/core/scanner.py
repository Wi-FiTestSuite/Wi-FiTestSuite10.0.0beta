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
from scriptinfo.scriptelement import (TestScriptElementType, ScriptSpecialSymbolElement, ScriptReservedWordsElement,
                                      ScriptStringElement, CAPICommandElement, ScriptVariableElement,
                                      TestbedDeviceElement, TestFeatureElement, CAPIReturnElement, EndOfLineElement)

import common
from symtable import TestScriptSymbolTable


class SyntaxError(Exception):
    """The class that manages the traffic data streams.
    """
    pass



class LexicaError(Exception):
    """The class that manages the traffic data streams.
    """
    pass



class TestScriptScanner:
    """The class that manages the traffic data streams.

    Attributes:
        ill (object): Description of `attr1`.
        data_strm (Optional[int]): Description of `attr2`.

    """
    def __init__(self, test_script_source):
        self.test_script_source = test_script_source
        self.current_elmt = ""
        self.next_segment = ""


    def skipWhiteSpace(self):
        """Example of docstring on the __init__ method.

        Args:
            file_to_lookup (str): file name to look up.
        """
        pass


    def synchronize(self, keywordList):
        """Example of docstring on the __init__ method.

        Args:
            file_to_lookup (str): file name to look up.
        """
        while True:
            segment = self.test_script_source.next_segment()
            if segment == "EOF":
                raise SyntaxError("No closing else or endif found")
                #break

            for keyword in keywordList: # else, endif
                if keyword == segment:
                    segment = self.test_script_source.next_segment()
                    return True
        #raise SyntaxError
        return False


    def skip_next_segment(self):
        """Skips the next segment.
        """
        self.test_script_source.next_segment()


    def get_next_segment_value(self):
        """Gets the value of next segment.
        """
        segval = ""
        if TestScriptElementType.get_element_type(self.next_segment) == "VARIABLE":
            segval = TestScriptSymbolTable.get_value_from_sym_tab(self.next_segment, TestScriptSymbolTable.test_script_sym_tab)
            segval = segval if segval else ""
        elif TestScriptElementType.get_element_type(self.next_segment) == "STRING":
            segval = self.next_segment

        return segval


    def extract_element(self):
        """Extracts the element while recognizing its element type.
        """
        self.skipWhiteSpace()
        segment = self.test_script_source.current_segment()
        # special symbols
        if segment in TestScriptElementType.script_special_symbols:
            self.current_elmt = ScriptSpecialSymbolElement(self.test_script_source)
        # reserved words
        elif segment in TestScriptElementType.script_reserved_words:
            self.current_elmt = ScriptReservedWordsElement(self.test_script_source)
        # variable
        elif segment.startswith('$'):
            self.current_elmt = ScriptVariableElement(self.test_script_source)
            if self.test_script_source.current_pos == 0:
                segval = TestScriptSymbolTable.get_value_from_sym_tab(segment, TestScriptSymbolTable.test_script_sym_tab)
                if segval is not None and segval != "":
                    for key in TestScriptElementType.script_testbed_devices:
                        if re.search(key, segval, re.I):
                            self.current_elmt = TestbedDeviceElement(self.test_script_source)
                            self.current_elmt.segment_text = segval
                            self.current_elmt.element_type = TestScriptElementType.get_element_type(segval)
                            break
        else:
            # capi commands
            for cmd in TestScriptElementType.script_capi_commands:
                if re.search(cmd, segment, re.I):                
                    self.current_elmt = CAPICommandElement(self.test_script_source)
                    self.test_script_source.line_attr = "CAPI"

                    self.next_segment = self.test_script_source.next_segment()
                    return self.next_segment

            is_testbed_device_elem = False
            
            # use regular expression to search the testbed device vendor name
            if not self.test_script_source.test_script_source_name == common.GlobalConfigFiles.dut_info_file:
                for key in TestScriptElementType.script_testbed_devices:
                    if re.search(key, segment, re.I):                    
                        # skip the variable such as $DUT_IF which causes it is recognized as testbed DUT
                        if self.test_script_source.current_pos == self.test_script_source.total_num_seg - 1 and key != segment:
                            break

                        self.current_elmt = TestbedDeviceElement(self.test_script_source)
                        is_testbed_device_elem = True
                        break

            if not is_testbed_device_elem:
                # based on the name of the file - DUTInfo.txt, we classify the current element into Feature element
                if self.test_script_source.test_script_source_name == common.GlobalConfigFiles.dut_info_file and (segment in TestScriptElementType.test_feature_key_words):
                    self.current_elmt = TestFeatureElement(self.test_script_source)
                elif segment == "EOL": # for return variable
                    self.current_elmt = EndOfLineElement(self.test_script_source)
                elif self.test_script_source.current_pos == self.test_script_source.total_num_seg - 1 and self.test_script_source.line_attr == "CAPI":
                    self.current_elmt = CAPIReturnElement(self.test_script_source)
                elif segment == "EOF":
                    self.next_segment = "EOF"
                    return
                else:
                    self.current_elmt = ScriptStringElement(self.test_script_source)
                #self.current_elmt = ScriptErrorElement(self.test_script_source)
                #raise LexicaError

        self.next_segment = self.test_script_source.next_segment()
        return self.next_segment


    def current_element(self):
        """Returns the current element of the current line being parsed.
        """
        return self.current_elmt


    def next_element(self):
        """Returns the next element of the current line being parsed.
        """
        return self.extract_element()        


    def show_error(self):
        """Displays the parsing error.
        """
        logging.error('=> ', self.test_script_source.line)
        total_len = 0
        i = 0
        if self.test_script_source.current_pos <= self.test_script_source.total_num_seg:
            if i < self.test_script_source.current_pos - 1:
                total_len = total_len + len(self.test_script_source.line_segments[i])
                i += 1
        else:
            total_len = len(self.test_script_source.line)

        if self.test_script_source.current_pos > 1:
            logging.error('=> ', (' ' * (total_len + 1)) + '^')
        else:
            logging.error('=> ', (' ' * total_len) + '^')
