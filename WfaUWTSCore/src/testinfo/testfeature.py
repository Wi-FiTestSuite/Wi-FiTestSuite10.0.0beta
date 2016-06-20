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

class TestProgramFeatureManager:
    """The class that manages the test program feature.

    Attributes:
        sll (object): The object of SingleLinkedList class.
        prog_name (str): The program name.
        test_mngr_initr (object): The object of TestManagerInitializer class.

    """
    def __init__(self, prog_name):
        self.sll = None
        self.prog_name = prog_name
        self.test_mngr_initr = None


    def get_feat_obj_val_by_name(self, feat_name):
        """Gets TestProgramFeature object based on the given feature name.

        Args:
            feat_name (str): The feature name to look up.
        """
        for feature in self.test_mngr_initr.test_prog_mngr.test_prog.feat_list:
            if feature.feat_name == feat_name:
                return feature.feat_value
        return None


    def set_test_prog_feat(self):
        """Stores DUT feature info on the linkedlist to domain object of TestProgramFeature class.
        """
        curr_node = self.sll.head
        while curr_node is not None:
            if curr_node.tag == "FEATURE":
                # curr_node.data is a dictionary
                testProgFeat = TestProgramFeature()
                testProgFeat.feat_name = list(curr_node.data.keys())[0]
                testProgFeat.feat_value = list(curr_node.data.values())[0]                
                self.test_mngr_initr.test_prog_mngr.test_prog.feat_list.append(testProgFeat)
                curr_node = curr_node.next


    def get_dut_feat_list(self):
        """Gets the list of DUT features defined in DUTInfo.txt file.
        """
        ret_str = -1
        for feature in self.test_mngr_initr.test_prog_mngr.test_prog.feat_list:
            if ret_str == -1:
                ret_str = "%s,%s%s" % (feature.feat_name, feature.feat_value, '!')
            else:
                ret_str = "%s%s,%s%s" % (ret_str, feature.feat_name, feature.feat_value, '!')

        return ret_str



class TestProgramFeature():
    """The DUT feature class.

    Attributes:
        feat_name (str): The feature name.
        feat_mand_opt (str): The feature is mandatory or optional.
        is_feat_flagged (boolean): Is the feature flagged in the test case?
        feat_value (str): The feature value.

    """
    def __init__(self):
        self.feat_name = None
        self.feat_mand_opt = None
        self.is_feat_flagged = False
        self.feat_value = None
