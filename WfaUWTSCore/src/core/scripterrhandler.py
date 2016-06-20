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

class ScriptErrorCode:
    IDENTIFIER_UNDEFINED = 0
    INVALID_EXPRESSION = 1
    INVALID_STATEMENT = 2
    INVALID_TYPE = 3
    
    type2str = {
        IDENTIFIER_UNDEFINED: "Undefined identifier",
        INVALID_EXPRESSION: "Invalid expression"
    }
    
    def __init__(self, type_,message,status=0):
        assert type in self.type2str.keys()
        self._type = type_
        self.status = status
        self.message = message
        
    def __repr__(self):
        return "<%s type=%s" % (self.__class__.__name__, self.type2str[self._type].upper())
    
    def getStatus(self):
        return self.status
    
    
    

class TestScriptErrorHandler:
    
    def __init__(self, status, message):
        self.status = status
        self.message = message
        
    
    def flag(self, elmt, errorCode):
        pass
    
    

