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


class TestCaseManager(object):
    """The summary line for a class docstring should fit on one line.
    """

    def __init__(self):        
        self.test_case = None # TestCase(progName, tcName)



    def getTestCaseOne(self):
        """The summary line for a class docstring should fit on one line.
        """
        # Use self.progName and self.tcName as IDs to retrieve all the test cases from database or file
        self.test_case.opt_test_feat = ""
        self.test_case.tc_type = ""

        return self.test_case


    def getTestCaseAll(self):
        """The summary line for a class docstring should fit on one line.
        """
        # Use self.progName as an ID to retrieve all the test cases from database or file
        self.getTestCaseOne()



class TestCase(object):
    """The summary line for a class docstring should fit on one line.

    Attributes:
        attr1 (str): Description of `attr1`.
        attr2 (Optional[int]): Description of `attr2`.

    """
    def __init__(self, prog_name, tc_name):
        self.prog_name = prog_name
        self.tc_name = tc_name
        self.tc_id = None
        self.tc_type = None
        self.opt_test_feat = None
        self.test_case_file = None
        self.testbed_device_list = []


    def isTestCaseMandOrOpt(self):
        """The summary line for a class docstring should fit on one line.
        """
        if self.opt_test_feat is not None:
            return True
        else:
            return False

