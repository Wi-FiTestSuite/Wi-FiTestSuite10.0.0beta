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
﻿from Queue import Queue
import time
import logging
from dbaccess import commondb

class TestConfigError(Exception):
    """The summary line for a class docstring should fit on one line.
    """
    pass



class TestScriptVerificationError(Exception):
    """The summary line for a class docstring should fit on one line.
    """
    pass



_gcfdb = commondb.CommonDB(r'..\db\common.db3')
GlobalConfigFiles = _gcfdb.get_common_config_files()
GlobalConfigFiles.LOG_LEVEL = logging.INFO
_gcfdb.close()



class UserInteractQueueItem:
    """The summary line for a class docstring should fit on one line.

    Attributes:
        attr1 (str): Description of `attr1`.
        attr2 (Optional[int]): Description of `attr2`.

    """
    def __init__(self):
        self.cmd = None
        self.src = ""
        self.dest = ""
        self.itemId = 0



class UserInteractQueue:
    """The summary line for a class docstring should fit on one line.

    Attributes:
        attr1 (str): Description of `attr1`.
        attr2 (Optional[int]): Description of `attr2`.

    """
    def __init__(self, direction="REQUEST"):
        self.que = Queue()
        self.direction = direction # OR RESPONSE


    def enqueue(self, queItem):
        """Gets the current user mode

        Args:
            item (**args): The set of parameters passed-in.
        """
        if self.direction == "REQUEST":
            queItem.itemId = int(time.time())

        self.que.put(queItem)


    def dequeue(self):
        """Gets the current user mode

        Args:
            item (**args): The set of parameters passed-in.
        """
        if not self.que.empty():
            return self.que.get()
        else:
            return None


    def clearqueue(self):
        """Gets the current user mode

        Args:
            item (**args): The set of parameters passed-in.
        """
        self.que.queue.clear()



class UserCommand:
    """The summary line for a class docstring should fit on one line.

    Attributes:
        attr1 (str): Description of `attr1`.
        attr2 (Optional[int]): Description of `attr2`.

    """
    GET_DEFAULT_USER_MODE = "GET_DEFAULT_USER_MODE"
    GET_CURRENT_USER_MODE = "GET_CURRENT_USER_MODE"
    SET_DEFAULT_USER_MODE = "SET_DEFAULT_USER_MODE"
    SET_CURRENT_USER_MODE = "SET_CURRENT_USER_MODE"
    SHOW_USER_MODE = "SHOW_USER_MODE"
    STOP_TEST_RUN = "STOP_TEST_RUN"
    SHOW_WTS_VERSION = "SHOW_WTS_VERSION"

    COMPLETE = "COMPLETE"
    INVALID = "INVALID"
    ERROR = "ERROR"
    UNKNOWN = "UNKNOWN"

    def __init__(self):
        self.status = UserCommand.UNKNOWN
        self.result = ""
        self.err_msg = ""



class TestExecutionCommand(UserCommand):
    """The summary line for a class docstring should fit on one line.

    Attributes:
        attr1 (str): Description of `attr1`.
        attr2 (Optional[int]): Description of `attr2`.

    """
    def __init__(self):
        UserCommand.__init__(self)
        self.prog_name = ""
        self.test_case_id = ""
        self.is_group_run = False
        self.group_file_name = ""
        self.user_mode = "PreCert"
        self.log_level = '0'

        self.is_testbed_val = False
        self.is_testcase_val = False



class UserQueryCommand(UserCommand):
    """The summary line for a class docstring should fit on one line.

    Attributes:
        attr1 (str): Description of `attr1`.
        attr2 (Optional[int]): Description of `attr2`.

    """
    def __init__(self):
        UserCommand.__init__(self)
        self.cmd_name = ""
        self.mode = ""
