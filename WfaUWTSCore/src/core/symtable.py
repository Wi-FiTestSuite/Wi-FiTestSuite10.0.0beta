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

class TestScriptSymbolTable(object):
    """The class that manages the global dictionary data structures.

    Attributes:
        test_script_sym_tab (dictionary): The dictionary to store parsing time variables in the scripts.
        capi_cmd_ret_sym_tab (dictionary): The dictionary to store execution time variables in the scripts.
        test_result_tab (dictionary): The dictionary to store test results variables in the scripts.

    """
    test_script_sym_tab = {"ifCondBit" : True, "socktimeout" : 600, "iDNB" : 0, "testRunning" : 0, "threadCount" : 0}
    capi_cmd_ret_sym_tab = {}
    test_result_tab = {'total_count' : 0, 'pass_count' : 0, 'fail_count' : 0, 'num_of_pass_required' : 0, 'conditional_chk_flag' : 0}


    @staticmethod
    def lookup_sym_tab(key, which_table):
        """Looks up the dictioary for a key.

        Args:
            key (str): The entry key.
            which_table (dictionary): The dictionary to look up.
        """
        if key in which_table:
            return True
        else:
            return False


    @staticmethod
    def get_value_from_sym_tab(key, which_table):
        """Gets the entry value from the dictionary based on the given key.

        Args:
            key (str): The entry key.
            which_table (dictionary): The dictionary to get the entry from.
        """
        if TestScriptSymbolTable.lookup_sym_tab(key, which_table):
            return which_table[key]
        else:
            return None


    @staticmethod
    def insert_sym_tab(key, value, which_table):
        """Inserts the entry into the dictionary based on the given key.

        Args:
            key (str): The entry key.
            which_table (dictionary): The dictionary to insert the entry into.
        """
        which_table[key] = value


    @staticmethod
    def delete_key_from_sym_tab(key, which_table):
        """Deletes the entry from the dictionary based on the given key.

        Args:
            key (str): The entry key.
            which_table (dictionary): The dictionary to delete the entry from.
        """
        if key in which_table:
            del which_table[key]
        else:
            raise KeyError
