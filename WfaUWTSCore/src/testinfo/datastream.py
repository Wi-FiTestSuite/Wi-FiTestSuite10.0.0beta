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
import logging
from core.symtable import TestScriptSymbolTable
from scriptinfo.scriptelement import TestScriptElementType


class DataStreamManager(object):
    """The class that manages traffic data streams.

    Attributes:
        ill (object): The object of SingleLinkedList class.
        data_strm (object): The object of DataStream class.
        running_phase (str): The data transfer phase.
        RTPCount (int): The RTP stream number count.
        multicast (int): The multicast flag.
        resultPrinted (int): The flag to indicate if the result should be printed.

    """
    def __init__(self):
        self.ill = None
        self.data_strm = None
        self.running_phase = '1'
        self.RTPCount = 1
        self.multicast = 0
        self.resultPrinted = 0
        self.event = None

    def set_data_strm_info(self):
        """Sets the values in data_strm object.
        """
        self.data_strm = DataStream()

        curr_node = self.ill.head
        while curr_node is not None:
            if curr_node.tag == "TRAFFICSTREAM":
                test_strm_info = (curr_node.data.keys())[0]
                for key in TestScriptElementType.script_reserved_words:
                    if re.search(key, test_strm_info, re.I):
                        if TestScriptElementType.script_reserved_words[key] == TestScriptElementType.MAX_THROUGHPUT:
                            self.data_strm.max_throughput = (curr_node.data.values())[0]
                            TestScriptSymbolTable.insert_sym_tab(test_strm_info, (curr_node.data.values())[0], TestScriptSymbolTable.test_script_sym_tab)
                        if TestScriptElementType.script_reserved_words[key] == TestScriptElementType.PAYLOAD:
                            self.data_strm.payload = (curr_node.data.values())[0]
                            TestScriptSymbolTable.insert_sym_tab(test_strm_info, (curr_node.data.values())[0], TestScriptSymbolTable.test_script_sym_tab)
                        if TestScriptElementType.script_reserved_words[key] == TestScriptElementType.PAYLOAD16K:
                            self.data_strm.payload16k = (curr_node.data.values())[0]
                            TestScriptSymbolTable.insert_sym_tab(test_strm_info, (curr_node.data.values())[0], TestScriptSymbolTable.test_script_sym_tab)
                        if TestScriptElementType.script_reserved_words[key] == TestScriptElementType.STREAM or TestScriptElementType.script_reserved_words[key] == TestScriptElementType.STREAM_TRANS:
                            self.data_strm.stream_percent[test_strm_info] = (curr_node.data.values())[0]
                            percent = (curr_node.data.values())[0]
                            logging.debug("STREAM = %s, Payload = %s Bytes, Percentage = %s %s of Maximum Throughput" %(test_strm_info, self.data_strm.payload, percent, "%"))
                            frameRate = int(self.data_strm.max_throughput) * int(percent)*1250/int(self.data_strm.payload)
                            logging.info("%s %s Frames / second"  % (test_strm_info, frameRate))
                            TestScriptSymbolTable.insert_sym_tab(test_strm_info, "%s" % frameRate, TestScriptSymbolTable.test_script_sym_tab)
                        
                        break
            curr_node = curr_node.next



class DataStream(object):
    """The summary line for a class docstring should fit on one line.

    Attributes:
        max_throughput (str): The maximum throughput value.
        payload (str): The packet's payload value.
        payload16k (str): The payload vlaue for 16k packet.
        stream_percent (dictionary): The percentage that each stream accounts for.
        stream_trans (str): The number of stream transactions.
        streamRecvResultArray (list): A list of receive stream results.
        streamSendResultArray (list): A list of send stream results.
        streamInfoArray (list): A list of stream information.

    """
    def __init__(self):
        self.max_throughput = ""
        self.payload = ""
        self.payload16k = ""
        self.stream_percent = {}
        self.stream_trans = ""
        self.streamRecvResultArray = []
        self.streamSendResultArray = []
        self.streamInfoArray = []



class streamInfo(object):
    """Returns string in formatted stream info.
    """
    def __init__(self, streamID, IPAddress, pairID, direction,
                 trafficClass, frameRate, phase, RTPID):
        self.streamID = streamID
        self.IPAddress = IPAddress
        self.pairID = pairID
        self.direction = direction
        self.trafficClass = trafficClass
        self.frameRate = frameRate
        self.phase = phase
        self.RTPID = RTPID
        self.status = -1
        

    def __str__(self):
        return "%-10s Stream ID = %s , IP Address = %s \n\r%-10s pairID = %s direction = %s \n\r%-10s frameRate =%s \n\r%-10s status =%s  %s" % (' ', self.streamID, self.IPAddress, ' ', self.pairID, self.direction, ' ', self.frameRate, ' ', self.status, self.phase)



class streamResult(object):
    """Returns string in formatted stream result.
    """
    def __init__(self, streamID, IPAddress, rxFrames, txFrames, rxBytes,
                 txBytes, phase):
        self.streamID = streamID
        self.IPAddress = IPAddress
        self.rxFrames = rxFrames
        self.txFrames = txFrames
        self.rxBytes = rxBytes
        self.txBytes = txBytes
        self.phase = phase


    def __str__(self):
        return "%-10s RX   %10s  Bytes   |  TX  %10s   | Stream ID = %s" % (' ', self.rxBytes, self.txBytes, self.streamID)

