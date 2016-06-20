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

class TestConfigService:
    """Constructs domain data objects based on the information on linked list and generates initenv file

    Attributes:
        test_mngr_initr (Optional[int]): The object of TestManagerInitializer class.
    """

    def __init__(self):
        self.test_mngr_initr = None


    def get_test_case_info(self):
        """Gets the list of testbed devices based on the given optional device name and type.

        Args:
            dev_name (Optional[str]): The device name.
            dev_type (Optional[str]): The device type.
        """
        # invoke the methods in TestCase class to obtain the information about the test case
        return self.test_mngr_initr.test_case_mngr.test_case


    def get_test_case_stream_info(self):
        """Gets the list of testbed devices based on the given optional device name and type.

        Args:
            dev_name (Optional[str]): The device name.
            dev_type (Optional[str]): The device type.
        """
        return self.test_mngr_initr.test_data_strm_mngr.data_strm


    def get_test_case_config_info(self):
        """Gets the list of testbed devices based on the given optional device name and type.

        Args:
            dev_name (Optional[str]): The device name.
            dev_type (Optional[str]): The device type.
        """
        return self.test_mngr_initr.test_config_info_mngr.test_config_info


    def get_test_case_device_list(self):
        """Gets the list of testbed devices based on the given optional device name and type.

        Args:
            dev_name (Optional[str]): The device name.
            dev_type (Optional[str]): The device type.
        """
        # read mastertestinfo.xml file and get a list of testbed devices
        return self.test_mngr_initr.test_case_mngr.test_case.testbed_dev_list


    def get_test_case_tbd_list(self, dev_name="", dev_type=""):
        """Gets the list of testbed devices based on the given optional device name and type.

        Args:
            dev_name (Optional[str]): The device name.
            dev_type (Optional[str]): The device type.
        """
        tbd_list = []
        if dev_name == "" and dev_type == "":
            return self.test_mngr_initr.test_case_mngr.test_case.testbed_dev_list

        for tbd in self.test_mngr_initr.test_case_mngr.test_case.testbed_dev_list:
            if dev_name == "" and dev_type != "":
                if tbd.dev_type == dev_type:
                    tbd_list.append(tbd)
            if dev_name != "" and dev_type == "":
                if tbd.dev_name == dev_name:
                    tbd_list.append(tbd)
            if dev_name != "" and dev_type != "":
                if tbd.dev_name == dev_name and tbd.dev_type == dev_type:
                    tbd_list.append(tbd)

        return tbd_list


    def get_test_prog_device_list(self):
        """Gets the list of testbed devices based on the given optional device name and type.

        Args:
            dev_name (Optional[str]): The device name.
            dev_type (Optional[str]): The device type.
        """
        return self.test_mngr_initr.test_prog_mngr.test_prog.testbed_dev_list


    def get_test_prog_tbd_list(self, dev_name="", dev_type=""):
        """Gets the list of testbed devices based on the given optional device name and type.

        Args:
            dev_name (Optional[str]): The device name.
            dev_type (Optional[str]): The device type.
        """
        tbd_list = []
        if dev_name == "" and dev_type == "":
            return self.test_mngr_initr.test_prog_mngr.test_prog.testbed_dev_list

        for tbd in self.test_mngr_initr.test_prog_mngr.test_prog.testbed_dev_list:
            if dev_name == "" and dev_type != "":
                if tbd.dev_type == dev_type:
                    tbd_list.append(tbd)
            if dev_name != "" and dev_type == "":
                if tbd.dev_name == dev_name:
                    tbd_list.append(tbd)
            if dev_name != "" and dev_type != "":
                if tbd.dev_name == dev_name and tbd.dev_type == dev_type:
                    tbd_list.append(tbd)

        return tbd_list


    def get_test_prog_feat_list(self):
        """Gets the list of testbed devices based on the given optional device name and type.

        Args:
            dev_name (Optional[str]): The device name.
            dev_type (Optional[str]): The device type.
        """
        return self.test_mngr_initr.test_prog_mngr.test_prog.feat_list
