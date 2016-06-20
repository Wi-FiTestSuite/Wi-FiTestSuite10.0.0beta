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


import validation
import texttable as tt
from pprint import pprint
from util import misc
from util.misc import Util

def display_validation_res():
    vr = validation.get_validation_results_handle()
    
    for i in vr:
        tab = tt.Texttable()
        header = [i.get_name()," "]
        if not i.overall:
            #print('failed')
            misc.Util.set_color(Util.FOREGROUND_RED | Util.FOREGROUND_INTENSITY)
        list_a = i.create_report()
        tab.add_rows(list_a)
        tab.set_cols_align(['l', 'l'])
        tab.set_cols_valign(['m','m'])
        tab.set_chars(['-','|','+','~'])
        tab.header(header)
        s = tab.draw()
        print(s)
        misc.Util.set_color(Util.FOREGROUND_WHITE)
        print ("\n\n")
