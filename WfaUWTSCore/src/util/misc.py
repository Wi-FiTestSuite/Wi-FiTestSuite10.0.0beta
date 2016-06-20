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
import re
import os
from ctypes import windll
from common import GlobalConfigFiles


class Util(object):
    """The class that manages the traffic data streams.

    Attributes:
        ill (object): Description of `attr1`.
        data_strm (Optional[int]): Description of `attr2`.

    """
    STD_INPUT_HANDLE = -10
    STD_OUTPUT_HANDLE = -11
    STD_ERROR_HANDLE = -12

    FOREGROUND_BLUE = 0x01 # text color contains blue.
    FOREGROUND_GREEN = 0x02 # text color contains green.
    FOREGROUND_RED = 0x04 # text color contains red.
    FOREGROUND_INTENSITY = 0x08 # text color is intensified.

    #Define extra colours
    FOREGROUND_WHITE = FOREGROUND_RED | FOREGROUND_BLUE | FOREGROUND_GREEN
    FOREGROUND_YELLOW = FOREGROUND_RED | FOREGROUND_GREEN
    FOREGROUND_CYAN = FOREGROUND_BLUE | FOREGROUND_GREEN
    FOREGROUND_MAGENTA = FOREGROUND_RED | FOREGROUND_BLUE
    #FOREGROUND_WHITE = FOREGROUND_GREEN | FOREGROUND_RED --> this is yellow.

    BACKGROUND_BLUE = 0x10 # background color contains blue.
    BACKGROUND_GREEN = 0x20 # background color contains green.
    BACKGROUND_RED = 0x40 # background color contains red.
    BACKGROUND_INTENSITY = 0x80 # background color is intensified.

    BACKGROUND_WHITE = BACKGROUND_RED | BACKGROUND_BLUE | BACKGROUND_GREEN
    BACKGROUND_YELLOW = BACKGROUND_RED | BACKGROUND_GREEN
    BACKGROUND_CYAN = BACKGROUND_BLUE | BACKGROUND_GREEN
    BACKGROUND_MAGENTA = BACKGROUND_RED | BACKGROUND_BLUE

    std_out_handle = windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)


    @staticmethod
    def dump(self, obj):
        """
        dump either dict or list
        """
        if type(obj) == dict:
            for key, val in obj.items():
                if hasattr(val, '__iter__'):
                    print key
                    self.dump(val)
                else:
                    print '%s : %s' % (key, val)
        elif type(obj) == list:
            for val in obj:
                if hasattr(val, '__iter__'):
                    self.dump(val)
                else:
                    print val
        else:
            print obj


    @staticmethod
    def str_to_type(s):
        """Checks the str type.

        Args:
            s (str): The string to be checked.
        """
        try:
            float(s)
            #if "." not in s:
            if str(s).find('.') == -1:
                return int
            return float
        except ValueError:
            value = s.upper()
            if value == "TRUE" or value == "FALSE":
                return bool
            return type(s)


    @staticmethod
    def is_MAC_addr(string):
        """Checks if the passed-in string is in the MAC format.

        Args:
            string (str): The string to be checked.
        """
        if not re.match(r'(..):(..):(..):(..):(..):(..)', string):
            return False

        return True


    @staticmethod
    def is_valid_MAC_addr(string):
        """Checks if the passed-in string is a valid MAC address.

        Args:
            string (str): The string to be checked.
        """
        hexdigits = '0123456789abcdefABCDEF'
        string = string.split(':')
        for num in string:
            for char in num:
                if char not in hexdigits:
                    return False
        return True


    @staticmethod
    def is_IPv4_addr(string):
        """Checks if the passed-in string is in the IPv4 format.

        Args:
            string (str): The string to be checked.
        """
        if not re.match(r'(\d+)\.(\d+)\.(\d+)\.(\d+)', string):
            return False

        return True


    @staticmethod
    def is_valid_IPv4_addr(string):
        """Checks if the passed-in string is a valid IPv4 address.

        Args:
            string (str): The string to be checked.
        """
        string = string.split('.')
        for num in string:
            if not num.isdigit():
                return False
                if (int(num) < 0) or (int(num) > 255):
                    return False
        return True


    @staticmethod
    def set_color(color, handle=std_out_handle):
        """Sets the console font color (color) -> BOOL

        Args:
            color (str): The color to be set.
            handle (object): The handle to direct the output.

        Example: set_color(FOREGROUND_GREEN | FOREGROUND_INTENSITY)
        """
        handle = windll.kernel32.GetStdHandle(Util.STD_OUTPUT_HANDLE)
        setRslt = windll.kernel32.SetConsoleTextAttribute(handle, color)
        return setRslt
    
    
    @staticmethod
    def get_wts_build_version():
        """Gets the wts version string from the version.txt file
        """
        version_file = "version.txt"
        version = ""
        build = ""
        package_name = ""
        sw_version = ""
        if os.path.exists("../" + version_file):
            with open("../" + version_file) as f:
                for line in f:
                    str = line.split(':')
                    if re.search(r"Version", str[0]):
                        version = str[1].strip()
                    if re.search(r"Build", str[0]):
                        build = str[1].strip()
                    if re.search(r"Package Name", str[0]):
                        package_name = str[1].strip()
            #sw_version = package_name + "_" + version + "_" + build
            sw_version = package_name
        
        GlobalConfigFiles.VERSION = sw_version
        return sw_version