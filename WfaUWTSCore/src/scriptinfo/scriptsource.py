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
﻿import os
import time
import sys
import re
import logging
from xml.dom import minidom
from xml.parsers.expat import ExpatError
from xml.dom.minidom import Node

from util.misc import Util
from common import GlobalConfigFiles, TestConfigError
from core.symtable import TestScriptSymbolTable
from security.filelocker import FileLocker

import json
import logging.config


class TestFileManager:
    """A thread class to handle user requests passed in through front end controller.

    Attributes:
        test_mngr_initr (object): The object of TestManagerInitializer class.
        is_running (boolean): The while loop stops when it is False.
        req_msg_hdlr_dict (dictionary): Store the mappings of user command to its handling function
    """

    def __init__(self, prog_name):
        self.prog_name = prog_name
        self.prog_script_list_file = None
        self.prog_script_folder_path = None
        self.test_case_file = None
        self.testbed_ap_file = None

    
    def get_script_folder_info(self, file_to_lookup):
        """Example of docstring on the __init__ method.

        Args:
            file_to_lookup (str): file name to look up.
        """
        self.prog_script_folder_path = self.read_map_file(file_to_lookup, "%s_CMD_PATH" % self.prog_name, '=')
        self.prog_script_list_file = self.read_map_file(file_to_lookup, "%s_TEST_LIST" % self.prog_name, '=')
        self.testbed_ap_file = self.read_map_file(file_to_lookup, "%s_TESTBED_AP" % self.prog_name, '=')


    def get_real_test_case_file(self, tc_name):
        """Gets real test case name that will be executed.

        Args:
            tc_name (str): test case name.

        """
        self.test_case_file = self.read_map_file(GlobalConfigFiles.config_root + self.prog_script_list_file, tc_name, '!', 2)
        if self.test_case_file == "":
            raise TestConfigError("No test case file found for test ID - %s" % tc_name)


    def get_test_case_id_type(self, tc_list_file):
        """Example of docstring on the __init__ method.

        Args:
            tc_list_file (str): Description of `param1`.
        """
        tc_info_dict = {}
        if not os.path.exists(tc_list_file):
            logging.error("File not found -%s- " % tc_list_file)
            return None

        file_to_read = open(tc_list_file, 'r')

        for l in file_to_read.readlines():
            if not l:
                break

            l = l.rstrip()
            line = l.split('#')
            if line[0] == '':
                continue

            line_segs = line[0].split('!')

            if len(line_segs) == 4:
                tc_info_dict[line_segs[0]] = [line_segs[2], line_segs[3]]

        file_to_read.close()
        return tc_info_dict


    def read_map_file(self, file_name, pattern, delim, n=1):
        """Searches the file for certain string based on the specified pattern, delimiter and position.

        Args:
            file_name (str): The file to be searched.
            pattern (str): The search pattern string.
            delim (str): The delimiter character.
            n (int): The search position.
        """
        ret_string = ""

        if not os.path.exists(file_name):
            logging.error("File not found -%s- " % file_name)
            return ret_string

        file_to_read = open(file_name, 'r')

        for l in file_to_read.readlines():
            if not l:
                break

            line = l.split('#')
            if line[0] == '':
                continue

            line_segs = line[0].split(delim)

            if pattern in line_segs:
                ret_string = line_segs[line_segs.index(pattern)+n].strip()
                break

        file_to_read.close()
        return ret_string



class TestFileSourceFacotry:
    """The parent factory class for handling the creation of different format of source file object.

    Attributes:
        file_name (str): The file name.
        file_path (str): The file path.
        file_type (str): The file type.

    """
    def __init__(self, file_name, file_path):
        self.file_name = file_name
        self.file_path = file_path
        self.file_type = None


    def file_factory_method(self):
        """Creates different source file object based on the file extension and calling subclass's factory methods.
        """
        if self.file_name.endswith('.xml'):
            self.file_type = "XML"
            xml_file_src_factory = TestXmlFileSourceFactory(self.file_name, self.file_path)
            return xml_file_src_factory.file_factory_method()
        elif self.file_name.endswith('.log') or self.file_name.endswith('.html'):
            self.file_type = "LOG"
            log_file_src_factory = TestLogFileSourceFactory(self.file_name, self.file_path)
            return log_file_src_factory.file_factory_method()
        else:
            self.file_type = "TXT"
            test_script_src_factory = TestScriptSourceFactory(self.file_name, self.file_path)
            return test_script_src_factory.file_factory_method()        



class TestScriptSourceFactory(TestFileSourceFacotry):
    """The child factory class to create TestScriptSource object.
    """
    def file_factory_method(self):
        return TestScriptSource(self.file_name, self.file_path)



class TestXmlFileSourceFactory(TestFileSourceFacotry):
    """The child factory class to create TestXmlFileSource object.
    """
    def file_factory_method(self):
        return TestXmlFileSource(self.file_name, self.file_path)



class TestLogFileSourceFactory(TestFileSourceFacotry):
    """The child factory class to create TestLogFileSource object.
    """
    def file_factory_method(self):
        return TestLogFileSource(self.file_name, self.file_path)



class TestFileSource:
    """The dummy parent class of different source file subclasses.
    """
    def __init__(self):
        pass



class TestLogFileSource(TestFileSource):
    """The child class of log source file.

    Attributes:
        log_file_hdl_list (list): The list of log file handles.
        log_file_source_obj_list (list): The list of log file objects.

        file_name (str): The file name.
        file_path (str): The file path.

    """
    log_file_hdl_list = []
    log_file_source_obj_list = []


    def __init__(self, file_name, file_path):
        self.file_name = file_name
        self.file_path = file_path


    def init_logging(self, log_level):
        """Initializes loggers and assign them to corresponding log files.

        Args:
            log_level (str): The logging level to be set.
        """
        p = self.file_name.replace(".log", "").split('\\')
        #resultCollectionFile = open("TestResults", "a")
        for s in p:
            t_file_name = s

        tms_time_stamp = time.strftime("%b-%d-%Y__%H-%M-%S", time.localtime())
        directory = "./log/%s_%s" % (t_file_name.rstrip(".txt"), tms_time_stamp)
        #tmsLogLocation = directory
        os.makedirs(directory)

        TestScriptSymbolTable.insert_sym_tab("$logDir", directory.replace("log/", ""), TestScriptSymbolTable.test_script_sym_tab)

        os.system("echo %s > p" % directory)

        fname = "%s/log_%s.log" % (directory, t_file_name.rstrip(".txt"))
        TestScriptSymbolTable.insert_sym_tab("$logFullPath", fname, TestScriptSymbolTable.test_script_sym_tab)

        fname_sniffer = "%s/sniffer_log_%s.log" % (directory, t_file_name.rstrip(".txt"))

        logging.getLogger().handlers = []
        
        #tmsPacket.TestCaseId = tFileName.rstrip(".txt")
        #tmsPacket.LogFileName = fname

        self.create_log_file(fname_sniffer, ("SNIFFER CHECKS LOG - Testcase: %s \n\n" % t_file_name.rstrip(".txt")), 'a')
        
        color_stream = None
        if os.path.exists(GlobalConfigFiles.logging_config_file):
            with open(GlobalConfigFiles.logging_config_file, 'r') as f:
                config = json.load(f)
                file_handler = config['handlers']['file_handler']
                file_handler['filename'] = fname
                logging.config.dictConfig(config)
                
                file_lock = FileLocker()
                file_lock.add_logger()
        else:
            file_lock = FileLocker()
            file_lock.add_logger()
        
            fh = logging.FileHandler(fname, mode='w')
            #fh.setLevel(logging.DEBUG)
            fh.setLevel(logging.INFO)
        
            #a Handler which writes INFO messages or higher to the sys.stderr
            console = logging.StreamHandler()
            console.setLevel(logging.INFO)
    
            # set a format which is simpler for console use
            formatter = logging.Formatter('%(levelname)-8s %(message)s')
            formatter1 = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
            # tell the handler to use this format
            console.setFormatter(formatter)
            fh.setFormatter(formatter1)
            
            logging.getLogger().addHandler(console)
            logging.getLogger().addHandler(fh)            
            
        Util.set_color(Util.FOREGROUND_INTENSITY, color_stream)        

        #tmsPacket.getTestID(GlobalConfigFiles.VERSION)
        
        logging.info("###########################################################\n")
        logging.info("UWTS Version [%s]",GlobalConfigFiles.VERSION)
        logging.info('Logging started in file - %s' % (fname))


    def create_log_file(self, file_name="", msg="", permission='w'):
        """Creates a log file with the name and permission specified, also message if available

        Args:
            file_name (object): Optional.
            msg (object): Optional. The message that is going to written to the log file.
            permission (object): The permission, default is write.
        """
        if file_name:
            log_file_hdl = open(file_name, permission)
        else:
            log_file_hdl = open(self.file_name, permission)
        TestLogFileSource.log_file_hdl_list.append(log_file_hdl)
        if msg:
            log_file_hdl.write("%s\n" % msg)


    def write_log_message(self, msg, file_hdl, log_fmt='INITLOG'):
        """Writes to the log file associated with the given file handle and format

        Args:
            file_hdl (object): The file handle.
            log_fmt (object): The log format.
        """
        if log_fmt == 'INITLOG':
            file_hdl.write("\n %s - %s" % (time.strftime("%H-%M-%S_%b-%d-%y", time.localtime()), msg))
            file_hdl.flush()
        if log_fmt == 'SNIFFERLOG':
            file_hdl.write("%s | %s \n" % (time.strftime("%b:%d:%Y-%H:%M:%S", time.localtime()), msg))


    def close_log_file(self, file_hdl):
        """Closes the log file associated to the given file handle

        Args:
            file_hdl (object): The file handle.
        """
        for hdl in TestLogFileSource.log_file_hdl_list:
            if hdl == file_hdl:
                file_hdl.close()
                return



class TestXmlFileSource(TestFileSource):
    """The child class of XML source file.

    Attributes:
        xml_file_name (str): The xml file name.
        xml_file_path (str): The xml file path.
        doc (object): The XML file doc node.

    """
    def __init__(self, xml_file_name, xml_file_path):
        self.xml_file_path = xml_file_path
        self.xml_file_name = xml_file_name
        self.doc = None


    def load_xml_file(self):
        """Loads the xml file.
        """
        try:
            self.doc = minidom.parse(self.xml_file_path + "\\" + self.xml_file_name)
        except ExpatError, e:
            raise e


    def get_nodes_by_tag_name(self, tag_name):
        """Gets the node based on the tag name.

        Args:
            tag_name (str): The XML tag name.
        """
        nodes = self.doc.getElementsByTagName(tag_name)
        return nodes


    def get_node_val_by_node_name(self, node, node_name):
        """Gets the node's value by its name.

        Args:
            node_name (str): The XML node name.
        """
        if node.nodeName == node_name:
            return node.nodeValue


    def get_node_val_by_node_obj(self, node):
        """Gets the value of the node.

        Args:
            node (Node): The node for retrieving value from if exists.
        """
        numOfChildNodes = node.childNodes
        if len(numOfChildNodes) == 0 or len(numOfChildNodes) > 1:
            return None
        if len(numOfChildNodes) == 1 and node.nodeType == Node.TEXT_NODE:
            return node.nodeValue


    def find_child_node_by_node_name(self, parent, name):
        """Finds the child node by its name and parent node.

        Args:
            parent (Node): The parent node.
            name (str): The child node name.
        """
        for node in parent.childNodes:
            if node.nodeType == node.ELEMENT_NODE and node.nodeName == name:
                return node
        return None


    def get_root_node_name(self):
        """Gets the root node name.
        """
        return self.doc.childNodes[0].nodeName



class TestScriptSource(TestFileSource):
    """The child class of test script file.

    Attributes:
        line_number (int): The line number.
        test_script_source_name (str): The test script file name.
        test_script_file_path (str): The test script file path.
        test_script_file_hdl (str): The test script file handle.
        line (object): The line in test script file.
        current_pos (int): The current index of line_segments.
        total_num_seg (int): Total number of segments.
        line_segments (list): The list to store the splitted segments.
        line_attr (str): The attribute of the line.

    """
    def __init__(self, file_name, file_path):
        self.line_number = 0
        self.test_script_source_name = file_name
        self.test_script_file_path = file_path
        self.test_script_file_hdl = None
        self.line = None
        self.current_pos = -1
        self.total_num_seg = 0
        self.line_segments = None
        self.line_attr = None
        self.open_test_script_file()


    def open_test_script_file(self):
        """Opens test script file associated with the file path and name
        """
        if self.test_script_source_name == '':
            raise Exception("Empty file name detected")

        fullFileName = self.test_script_file_path + "\\" + self.test_script_source_name

        if os.path.exists(fullFileName):
            self.test_script_file_hdl = open(fullFileName, 'r')
        else:
            raise OSError(fullFileName + " not exists")


    def read_test_script_line(self):
        """Reads a line of script file while skipping comment or blank lines and splits it into segment list by ! delimiter.
        """
        self.line = self.test_script_file_hdl.readline()

        if not self.line:
            return

        self.line = self.line.strip()
        self.line_number += 1

        # skip comment lines
        while self.line.startswith('#') or self.line == '':
            self.line = self.test_script_file_hdl.readline()
            if not self.line:
                return
            self.line = self.line.strip()
            self.line_number += 1

        logging.debug("current line=%s" % self.line)
        
        self.line_segments = self.line.split('!')
        for idx, seg in enumerate(self.line_segments):
            if seg == '' and idx == len(self.line_segments) - 1:
                self.line_segments.pop(idx)

        self.total_num_seg = len(self.line_segments)


    def close_test_script(self, fileHandle):
        """Closes test script file associated to the given file handle.

        Args:
            file_hdl (object): The file handle.
        """
        if fileHandle:
            fileHandle.close()


    def current_segment(self):
        """Return the every first item of the segment after split by !
        """
        if self.current_pos == -1:
            self.read_test_script_line()
            return self.next_segment()
        elif not self.line:
            self.current_pos = -1
            self.close_test_script(self.test_script_file_hdl)
            return "EOF"
        elif self.current_pos == self.total_num_seg:
            return "EOL"
        elif self.current_pos > self.total_num_seg:
            self.line_attr = None
            self.current_pos = -1
            self.read_test_script_line()            
            return self.next_segment()
        else:
            return self.line_segments[self.current_pos]


    def next_segment(self):
        """Returns next segment in the segment list.
        """
        self.current_pos += 1
        return self.current_segment()

