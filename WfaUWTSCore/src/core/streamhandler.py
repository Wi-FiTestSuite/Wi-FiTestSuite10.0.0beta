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

import logging
import sys


from common import GlobalConfigFiles
from util.misc import Util
from core.symtable import TestScriptSymbolTable
from testinfo.datastream import streamInfo, streamResult
from scriptinfo.scriptsource import TestFileManager


class StreamHandler(object):
    """
    handle stream related part
    """

    def __init__(self, test_mngr_initr=None):
        self.test_mngr_initr = test_mngr_initr
        self.ProgName = test_mngr_initr.prog_name
        self.DisplayNameTable = {}
        #self.streamSendResultArray = test_mngr_initr.test_data_strm_mngr.data_strm.streamSendResultArray
        #self.streamRecvResultArray = test_mngr_initr.test_data_strm_mngr.data_strm.streamRecvResultArray
        #self.streamInfoArray = test_mngr_initr.test_data_strm_mngr.data_strm.streamInfoArray

    @property
    def multicast(self):
        return self.test_mngr_initr.test_data_strm_mngr.multicast

    @multicast.setter
    def multicast(self, value):
        self.test_mngr_initr.test_data_strm_mngr.multicast = value

    @property
    def running_phase(self):
        return self.test_mngr_initr.test_data_strm_mngr.running_phase

    @running_phase.setter
    def running_phase(self, value):
        self.test_mngr_initr.test_data_strm_mngr.running_phase = value

    @property
    def RTPCount(self):
        return self.test_mngr_initr.test_data_strm_mngr.RTPCount

    @RTPCount.setter
    def RTPCount(self, value):
        self.test_mngr_initr.test_data_strm_mngr.RTPCount = value

    @property
    def resultPrinted(self):
        return self.test_mngr_initr.test_data_strm_mngr.resultPrinted

    @resultPrinted.setter
    def resultPrinted(self, value):
        self.test_mngr_initr.test_data_strm_mngr.resultPrinted = value


    def add_streamInfo(self, streamInfoClass):
        self.test_mngr_initr.test_data_strm_mngr.data_strm.streamInfoArray.append(streamInfoClass)

    def processStreamResults(self, command):
        """process stream results..."""

        #=======================================================================
        # if self.test_mngr_initr.test_data_strm_mngr.resultPrinted == 1:
        #     return
        #=======================================================================
        
        ret = 'NONE'
        
        if self.test_mngr_initr.test_data_strm_mngr.resultPrinted == 0:
            if self.ProgName == "P2P":
                logging.debug("skip if program is P2P")
                return
    
            checkWPA2 = TestScriptSymbolTable.lookup_sym_tab("WPA2Test", TestScriptSymbolTable.capi_cmd_ret_sym_tab)
    
            if checkWPA2 == True:
                logging.debug("WPA2 Results")
                self.printStreamResults_WPA2()
            else:
                self.printStreamResults_WMM()

        cmdFilter = command.split('!')
        logging.debug("stream handler : %s" % cmdFilter[0])

        if cmdFilter[0].lower() == 'checkthroughput':
            ret = self.process_CheckThroughput(cmdFilter[1], 0)

        elif cmdFilter[0].lower() == 'checkmcsthroughput':
            ret = self.process_CheckMCSThroughput(cmdFilter[1])

        elif cmdFilter[0].lower() == 'checkdt4result':
            ret = self.process_CheckDT4(cmdFilter[1])

        elif cmdFilter[0].lower() == 'resultwmm':
            ret = self.process_passFailWMM(cmdFilter[1], 0)

        elif cmdFilter[0].lower() == 'resultwmm_1':
            ret = self.process_passFailWMM(cmdFilter[1], 1)

        elif cmdFilter[0].lower() == 'resultwmm_2':
            ret = self.process_passFailWMM(cmdFilter[1], 2)

        elif cmdFilter[0].lower() == 'resultibss':
            ret = self.process_passFailIBSS(cmdFilter[1])

        elif cmdFilter[0].lower() == 'transactionthroughput':
            ret = self.process_CheckThroughput(cmdFilter[1], 1)

        return ret


    def printStreamResults_WPA2(self):
        """Prints stream results of WPA2"""
        maxRTP = 1
        Util.set_color(Util.FOREGROUND_WHITE)

        if not self.test_mngr_initr.test_data_strm_mngr.data_strm.streamSendResultArray:
            self.test_mngr_initr.test_data_strm_mngr.resultPrinted = 0
        else:
            self.test_mngr_initr.test_data_strm_mngr.resultPrinted = 1
        logging.info("\n\r %-7s --------------------STREAM RESULTS-----------------------" % "")

        for tbd in self.test_mngr_initr.test_prog_mngr.test_prog.testbed_dev_list:
            self.DisplayNameTable.setdefault(tbd.ctrlipaddr, tbd.displayname)

        for s in self.test_mngr_initr.test_data_strm_mngr.data_strm.streamSendResultArray:
            sDisplayAddress = s.IPAddress
            if s.IPAddress in self.DisplayNameTable:
                sDisplayAddress = self.DisplayNameTable[s.IPAddress]
            for r in self.test_mngr_initr.test_data_strm_mngr.data_strm.streamInfoArray:
                if r.streamID == s.streamID and r.IPAddress == s.IPAddress and r.phase == s.phase:
                    recv_id = r.pairID
                    trafficClass = r.trafficClass
                    phase = r.phase
                    break
            for p in self.test_mngr_initr.test_data_strm_mngr.data_strm.streamRecvResultArray:
                pDisplayAddress = p.IPAddress
                if p.IPAddress in self.DisplayNameTable:
                    pDisplayAddress = self.DisplayNameTable[p.IPAddress]
                if p.streamID == recv_id and p.phase == s.phase:
                    logging.info("\n\r %-7s -----  %s --> %s -----" %
                                 ("", sDisplayAddress, pDisplayAddress))
                    logging.info("\n%s" % s)
                    if maxRTP < int(r.RTPID):
                        maxRTP = int(r.RTPID)
                    logging.info("\n%s" % p)
                    break
        Util.set_color(Util.FOREGROUND_INTENSITY)

    def printStreamResults_WMM(self):
        """Prints stream results of WMM"""
        summaryList = {}
        summaryStreamDisplay = {}
        maxRTP = 1
        i = 1

        if not self.test_mngr_initr.test_data_strm_mngr.data_strm.streamSendResultArray:
            self.test_mngr_initr.test_data_strm_mngr.resultPrinted = 0
        else:
            self.test_mngr_initr.test_data_strm_mngr.resultPrinted = 1

        for tbd in self.test_mngr_initr.test_prog_mngr.test_prog.testbed_dev_list:
            self.DisplayNameTable.setdefault(tbd.ctrlipaddr, tbd.displayname)

        logging.info("\n\r %-7s --------------------STREAM RESULTS-----------------------" % "")

        for s in self.test_mngr_initr.test_data_strm_mngr.data_strm.streamSendResultArray:
            sDisplayAddress = s.IPAddress
            if s.IPAddress in self.DisplayNameTable:
                sDisplayAddress = self.DisplayNameTable[s.IPAddress]
            for r in self.test_mngr_initr.test_data_strm_mngr.data_strm.streamInfoArray:
                if r.streamID == s.streamID and r.IPAddress == s.IPAddress and r.phase == s.phase:
                    recv_id = r.pairID
                    trafficClass = r.trafficClass
                    phase = r.phase
                    break
            for p in self.test_mngr_initr.test_data_strm_mngr.data_strm.streamRecvResultArray:
                pDisplayAddress = p.IPAddress
                if p.IPAddress in self.DisplayNameTable:
                    pDisplayAddress = self.DisplayNameTable[p.IPAddress]
                if p.streamID == recv_id and p.phase == s.phase:
                    logging.info("\n\r %-7s ----- RTP_%s-%s ( %s --> %s ) PHASE  = %s -----" %("", r.RTPID, trafficClass, sDisplayAddress, pDisplayAddress, p.phase))
                    logging.info("\n%s" % s)
                    summaryList.setdefault("%s:%s"%(int(r.RTPID), int(phase)), p.rxBytes)
                    summaryStreamDisplay.setdefault("%s:%s" % (int(r.RTPID), int(phase)), "RTP%-1s_%-10s [%s-->%s]" % (r.RTPID, trafficClass, sDisplayAddress, pDisplayAddress))
                    if maxRTP < int(r.RTPID):
                        maxRTP = int(r.RTPID)
                    logging.info("\n%s" % p)
                    break
        Util.set_color(Util.FOREGROUND_WHITE)
        logging.info("--------------------------SUMMARY----------------------------------")
        logging.info(" %46s %10s | %10s" % ("|", "Phase1 (Bytes)", "Phase2 (Bytes)"))
        logging.info("-------------------------------------------------------------------")
        while i <= maxRTP:
            str1 = ""
            str2 = ""
            stremDisplay = ""
            if "%s:%s"%(i, "1") in summaryList:
                str1 = summaryList["%s:%s" % (i, "1")]
                stremDisplay = summaryStreamDisplay["%s:%s"%(i, "1")]
            if "%s:%s"%(i, "2") in summaryList:
                str2 = summaryList["%s:%s" % (i, "2")]
                stremDisplay = summaryStreamDisplay["%s:%s"%(i, "2")]

            logging.info("\n%6s %-43s %5s %10s | %10s" % (" ", stremDisplay, "|", str1, str2))
            i = i + 1
        Util.set_color(Util.FOREGROUND_INTENSITY)


    def process_passFailWMM(self, line, case):
        """Determines pass or fail for WMM based on two phases result and what is expected"""
        try:
            cmd = line.split(',')
            P1 = -1
            P2 = -1

            id = cmd[0]
            id1 = cmd[1]
            expectedVal = cmd[2]
            #print "wmm stream ids and expectedval:%s***%s***%s" % (id,id1,expectedVal)
            for p in self.test_mngr_initr.test_data_strm_mngr.data_strm.streamRecvResultArray:
                #print "in for loop ---> p.streamID / p.phase / p.rxBytes :" + str(p.streamID) +'/'+  p.phase + '/' + str(p.rxBytes)
                if p.streamID == id and int(p.phase) == 1:#int(self.running_phase):
                    P1 = p.rxBytes
                elif p.streamID == id1 and int(p.phase) == 2:#int(self.running_phase):
                    P2 = p.rxBytes

            if (int(P2) <= 0) or (int(P1) <= 0):
                actual = -1
            else:
                actual = (float(P2) / float(P1)) * 100

            if case == 0:
                if actual > long(expectedVal):
                    Util.set_color(Util.FOREGROUND_GREEN | Util.FOREGROUND_INTENSITY)
                    result = cmd[3]
                else:
                    Util.set_color(Util.FOREGROUND_RED | Util.FOREGROUND_INTENSITY)
                    result = cmd[4]

                logging.info("\n       ----------------RESULT---------------------------\n")
                logging.info("%s Phase 1 = %s Bytes | %s Phase 2 = %s Bytes " %(cmd[5], P1, cmd[5], P2))
                logging.info("Expected  > %s %s" % (expectedVal, "%"))
                logging.info("Actual -  %6.6s %s" % (actual, "%"))
                logging.info("TEST RESULT ---> %s" % result)
                logging.info("\n       ------------------------------------------------")

            elif case == 1:
                if actual <= long(expectedVal):
                    Util.set_color(Util.FOREGROUND_GREEN | Util.FOREGROUND_INTENSITY)
                    result = cmd[3]
                else:
                    Util.set_color(Util.FOREGROUND_RED | Util.FOREGROUND_INTENSITY)
                    result = cmd[4]

                logging.info("\n       ----------------RESULT---------------------------\n")
                logging.info("Expected  <= %s %s" % (expectedVal, "%"))
                logging.info("Actual -  %6.6s %s" % (actual, "%"))
                logging.info("TEST RESULT ---> %s" % result)
                logging.info("\n       ------------------------------------------------")
            elif case == 2:
                if actual >= long(expectedVal):
                    Util.set_color(Util.FOREGROUND_GREEN | Util.FOREGROUND_INTENSITY)
                    result = cmd[3]
                else:
                    Util.set_color(Util.FOREGROUND_RED | Util.FOREGROUND_INTENSITY)
                    result = cmd[4]

                logging.info("\n       ----------------RESULT---------------------------\n")
                logging.info("Expected  >= %s %s" % (expectedVal, "%"))
                logging.info("Actual -  %6.6s %s" % (actual, "%"))
                logging.info("TEST RESULT ---> %s" % result)
                logging.info("\n       ------------------------------------------------")

            Util.set_color(Util.FOREGROUND_WHITE)
            
            return result

        except:
            exc_info = sys.exc_info()
            logging.error('Invalid Pass/Fail Formula - %s' % exc_info[1])

    def process_passFailIBSS(self, line):
        """Determines pass or fail for IBSS based on results and what is expected"""
        try:
            cmd = line.split(',')
            P1 = -1
            id = cmd[0]

            logging.debug("Processing PASS/FAIL...")
            for p in self.test_mngr_initr.test_data_strm_mngr.data_strm.streamRecvResultArray:
                if p.streamID == id:
                    P1 = p.rxBytes
                    break
            logging.info(" Received = %s Bytes Duration = %s Seconds Expected = %s Mbps " % (P1, cmd[2], cmd[1]))
            logging.debug(" B = %s B1 = %s" % (((long(P1) / 10000)), ((float(cmd[1]) * 125000))))
            if int(P1) <= 0:
                actual = -1
            else:
                actual = ((float(P1) * 8)) / (1000000 * int(cmd[2]))

            logging.info("Expected = %s Mbps  Received =%s Mbps" % (cmd[1], actual))
            if float(actual) >= float(cmd[1]):
                result = cmd[3]
            else:
                result = cmd[4]
            
            return result

        except:
            exc_info = sys.exc_info()
            logging.error('Invalid Pass/Fail Formula - %s' % exc_info[1])

    def process_CheckThroughput(self, line, Trans):
        """Determines throughput and prints the results and expected to logs"""
        try:
            cmd = line.split(',')

            duration = cmd[2]
            expected = cmd[3]
            id = cmd[0]


            P1 = -1
            logging.debug("Processing Throughput Check...")
            if Trans:
                for p in self.test_mngr_initr.test_data_strm_mngr.data_strm.streamSendResultArray:
                    if p.streamID == id and int(p.phase) == int(cmd[1]):
                        P1 = p.rxBytes
                        break
            else:
                for p in self.test_mngr_initr.test_data_strm_mngr.data_strm.streamRecvResultArray:
                    if p.streamID == id and int(p.phase) == int(cmd[1]):
                        P1 = p.rxBytes
                        if not P1:
                            P1 = -1
                        break

            if int(P1) <= 0:
                actual = -1
            else:
                actual = ((float(P1) * 8))/(1000000 * int(duration))

            if float(actual) >= float(expected):
                result = cmd[4]
            else:
                result = cmd[5]
            
            Util.set_color(Util.FOREGROUND_YELLOW | Util.FOREGROUND_INTENSITY)
            logging.debug(" Received = %s Bytes Duration = %s Seconds Expected = %s Mbps " % (P1, duration, expected))
            logging.info("\n Expected >= %s Mbps Actual = %s Mbps" % (expected, actual))
            
            if 'PASS' in result:
                Util.set_color(Util.FOREGROUND_GREEN | Util.FOREGROUND_INTENSITY)
                logging.info ("CHECK %s" % result)
                result = 'PASS'
            else :
                Util.set_color(Util.FOREGROUND_RED | Util.FOREGROUND_INTENSITY)
                logging.info ("CHECK %s" % result)
                result = 'FAIL'

            Util.set_color(Util.FOREGROUND_WHITE)
            return result
            
        except:
            exc_info = sys.exc_info()
            logging.error('Invalid Pass/Fail Formula - %s' % exc_info[1])

    def process_CheckMCSThroughput(self, line):
        """Determines MCS throughput and prints the results and expected to logs"""
        try:
            cmd = line.split(',')
            logging.debug("process_CheckMCSThroughput")
            logging.debug("-%s-%s-%s-%s-%s" % (cmd[0], cmd[1], cmd[2], cmd[3], cmd[4]))

            TX = -1
            RX1 = -1
            RX2 = -1

            logging.debug("Processing Throughput Check...")
            for p in self.test_mngr_initr.test_data_strm_mngr.data_strm.streamSendResultArray:
                if p.streamID ==  cmd[1] and int(p.phase) == int(cmd[0]):
                    TX = long(p.txBytes)
                    break
            for p in self.test_mngr_initr.test_data_strm_mngr.data_strm.streamRecvResultArray:
                if p.streamID == cmd[2] and int(p.phase) == int(cmd[0]):
                    RX1 = long(p.rxBytes)
                if p.streamID == cmd[3] and int(p.phase) == int(cmd[0]):
                    RX2 = long(p.rxBytes)

            logging.debug("-%s-%s-%s-%s" % (TX, RX1, RX2, cmd[4]))
            TX = (long(TX)* (float(cmd[4])/100))
            actual = -1
            if int(TX) <= 0:
                actual = -1
            else:
                if RX1 > TX and RX2 > TX:
                    actual = 1

            if float(actual) > 0:
                result = cmd[5]
            else:
                result = cmd[6]

            logging.info("\n MCS Expected %s bytes, actual %s bytes and %s bytes" % (TX, RX1, RX2))
            
            return result
        except:
            exc_info = sys.exc_info()
            logging.error('Invalid Pass/Fail Formula - %s' % exc_info[1])

    def process_CheckDT4(self, line):
        """Determines amount of DT4 packets and prints the results and expected to logs"""
        try:
            cmd = line.split(',')
            logging.debug("process_Check DT4 Results")
            logging.debug("-%s-%s-%s-%s-%s-%s" % (cmd[0], cmd[1], TestScriptSymbolTable.get_value_from_sym_tab(cmd[1], TestScriptSymbolTable.capi_cmd_ret_sym_tab), cmd[2], cmd[3], cmd[4]))
            RX = -1

            id = cmd[1]
            for p in self.test_mngr_initr.test_data_strm_mngr.data_strm.streamSendResultArray:
                if p.streamID == id and int(p.phase) == int(cmd[0]):
                    RX = long(p.rxFrames)

            logging.debug("-%s-%s" % (RX, cmd[2]))

            actual = -1
            if long(RX) > long(cmd[2]):
                actual = 1

            if float(actual) > 0:
                result = cmd[3]
            else:
                result = cmd[4]

            logging.info("\n DT4 Expected > %s packets, actual %s packets" % (cmd[2], RX))

            return result
        except:
            exc_info = sys.exc_info()
            logging.error('Invalid Pass/Fail Formula - %s' % exc_info[1])
