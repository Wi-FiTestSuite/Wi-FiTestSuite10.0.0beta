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
from testcase import TestCase


class TestProgramManager:
    """The class that manages the test program class.

    Attributes:
        attr1 (str): Description of `attr1`.
        attr2 (Optional[int]): Description of `attr2`.

    """
    def __init__(self, prog_name):
        self.test_prog = TestProgram(prog_name)



class TestProgram:
    """The class that contains the test program info.

    Attributes:
        prog_name (str): Description of `attr1`.
        test_plan_ver (Optional[int]): Description of `attr2`.
        feat_list (list): The program feature list.
        testbed_dev_list (list): The program testbed device list.
        tc_list (list): The program's test case list.
        is_tp_prog (boolean): The flag to indicate the throughput related program.

    """
    def __init__(self, prog_name):
        self.prog_name = prog_name
        self.test_plan_ver = None
        self.feat_list = []
        self.testbed_dev_list = []
        self.tc_list = self.tcListFactoryMethod()
        self.is_tp_prog = False

    def set_prog_info(self):
        if (self.prog_name == "N" 
            or self.prog_name == "VHT" 
            or self.prog_name == "WMMPS"
            or self.prog_name =="TDLS"
            or self.prog_name == "VE"):
            self.is_tp_prog = True

    def featListFactoryMethod(self):
        return {}

    def tcListFactoryMethod(self):
        return []



    def getTestProgName(self):
        return self.prog_name

    def setTestProgName(self, prog_name):
        self.prog_name = prog_name

    def getTCList(self):

        return self.tc_list

    def addTCInfoToList(self, tcInfo):
        if isinstance(tcInfo, TestCase):
            self.tc_list.append(tcInfo)

    def removeTcInfoFromList(self, tcName):
        for x in self.tc_list:
            if x.tcName == tcName:
                self.tc_list.remove(x)

    def addFeatInfoToList(self, featInfo):
        if isinstance(featInfo, TestFeature):
            self.feat_list.append(featInfo)

    def removeFeatInfoFromList(self, feat_name):
        for x in self.feat_list:
            if x.feat_name == feat_name:
                self.feat_list.remove(x)

    progName = property(getTestProgName, setTestProgName, None, None)



class TestProgram_11n(TestProgram):
    """A concrete program which contains a feature list."""
    def featListFactoryMethod(self):
        return self.feat_list

    def tcListFactoryMethod(self):
        # to do: get the list of test cases from database or external file

        self.tc_list = [] # list of testcase objects
        return self.tc_list


class TestProgram_P2P(TestProgram):
    pass

class TestProgram_VHT(TestProgram):
    pass


class TestFeature:

    def __init__(self, feat_name):
        self.feat_name = feat_name
        self.testProgSupported = None

    pass

