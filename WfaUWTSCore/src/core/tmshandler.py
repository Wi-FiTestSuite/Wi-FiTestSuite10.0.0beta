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

""" TMS processor """

import logging
import json
import os
import re
import string
import sys
import xml.dom.minidom
from xml.dom.minidom import Node
from difflib import SequenceMatcher
from common import GlobalConfigFiles
from scriptinfo.scriptsource import TestFileManager



#TMS response packet
class TMSProcessor(object):
    """ TMS class """
    #Init variables
    def __init__(self, TestResult="N/A", Mode="Sigma", DutParticipantName="Unknown", PrimaryTestbedParticipantName="Unknown"):
        self.TmsEventId = ""
        self.Mode = Mode
        self.Dut = {'company':"", 'model':"", 'firmware':"", 'Category' : "", 'VendorDeviceId' : ""}
        self.PrimaryTestbed = {'company':"", 'model':"", 'firmware':"", 'Category' : "", 'VendorDeviceId' : ""}
        self.SupplementalTestbeds = []
        self.TestResult = TestResult
        self.TimeStamp = ""
        self.LogFileName = ""
        self.ProgramName = GlobalConfigFiles.curr_prog_name
        self.TestCaseId = GlobalConfigFiles.curr_tc_name
        self.DutParticipantName = DutParticipantName
        self.PrimaryTestbedParticipantName = PrimaryTestbedParticipantName

    def __str__(self):
        return("\n Test Event ID = [%s] Prog Name = [%s] Test Case = [%s] Dut Name =[%s] Model Number =[%s] Test Result =[%s]", self.TmsEventId, self.ProgramName, self.TestCaseId, self.DutParticipantName, self.self.Dut.get('model'), self.TestResult)

    #func to get class to dict
    def asDict(self):
        return self.__dict__

    def Search_MasterTestInfo(self, testID, tag):
        """
        Finds the value of given tag in master XML file of Testcase Info (from InitEnv)

        Parameters
        ----------
        testID : str
        tag : tuple of str

        Returns
        -------
        Tag Value (as per XML file) : str
        """
        result = ""

        try:
            #print "search master test info"
            testFileMngr = TestFileManager(GlobalConfigFiles.curr_prog_name)
            testFileMngr.get_script_folder_info(GlobalConfigFiles.uwts_ucc_file)  
        
            path = testFileMngr.prog_script_folder_path + "\\" + GlobalConfigFiles.master_test_info_file
            

            #print "path : " + path
            doc = xml.dom.minidom.parse(path)
            #print "after parse xml...."
            if doc.getElementsByTagName(self.TestCaseId) is not None:
                
                for node in doc.getElementsByTagName(self.TestCaseId):
                    L = node.getElementsByTagName(tag)
                    if L is not None:
                        for node2 in L:
                            if node2.childNodes is not None:
                                for node3 in node2.childNodes:
                                    if node3.nodeType == Node.TEXT_NODE:
                                        result = node3.nodeValue
                                        break

        except Exception:
            logging.debug("Unexpected error:", sys.exc_info())

        return result

    def writeTMSJson(self):
        """Write JSON for TMS -> grep log file and look for Version Info"""


        jsonFname = "tms_%s.json" % (self.TestCaseId)
        try:
            primaryTB = self.Search_MasterTestInfo(self.TestCaseId, "PrimaryTestbed")
        except Exception:
            #exception
            primaryTB = "n/a"
            #print "Unexpected exception:", sys.exc_info()[0]

        BulkStorageServer = ""

        tmsPATH = GlobalConfigFiles.tmsConfigPath
        if os.path.isfile(tmsPATH):

            with open(tmsPATH, "r") as f:

                for line in f:
                    if re.search(r"TmsEventId=", line):
                        pos = line.index('=') + 1
                        data = line[pos:].rstrip('\r\n')
                        self.TmsEventId = data

                    if re.search(r"TestbedParticipantName=", line):
                        pos = line.index('=') + 1
                        data = line[pos:].rstrip('\r\n')
                        if primaryTB != "":
                            self.PrimaryTestbedParticipantName = data
                        else:
                            self.PrimaryTestbedParticipantName = ""

                    if re.search(r"DutParticipantName=", line):
                        pos = line.index('=') + 1
                        data = line[pos:].rstrip('\r\n')
                        self.DutParticipantName = data

                    if re.search(r"BulkStorageServer=", line):
                        pos = line.index('=') + 1
                        data = line[pos:].rstrip('\r\n')
                        BulkStorageServer = data

        if self.Dut.get('VendorDeviceId') != "":
            if self.PrimaryTestbed.get('VendorDeviceId') != "":
                self.LogFileName = BulkStorageServer + "/" + self.TmsEventId + "/" + self.Dut.get('VendorDeviceId') + "/" + self.PrimaryTestbed.get('VendorDeviceId') + "/" + self.TestCaseId + "/" + self.TimeStamp + ".zip"
            else:
                self.LogFileName = BulkStorageServer + "/" + self.TmsEventId + "/" + self.Dut.get('VendorDeviceId') + "/" + self.TestCaseId + "/" + self.TimeStamp + ".zip"
        else:
            self.LogFileName = BulkStorageServer + "/" + self.TmsEventId + "/" + self.TestCaseId + "/" + self.TimeStamp + ".zip"


        tmsFile = open(jsonFname, "w")
        tmsDict = self.asDict()

        if primaryTB == "":
            try:
                del tmsDict['PrimaryTestbed']
                del tmsDict['PrimaryTestbedParticipantName']
                del tmsDict['SupplementalTestbeds']
            except Exception:
                #logging.info("primaryTB not found")
                logging.debug("primaryTB not found")

        else:
            try:
                line = self.Search_MasterTestInfo(self.TestCaseId, "TB_LIST")
                tb_list = line.split(',')
                if len(tb_list) <= 1:
                    del tmsDict['SupplementalTestbeds']
            except Exception:
                #logging.debug("SupplimentalTestbeds not found")
                logging.debug("SupplimentalTestbeds not found")


        TmsFinalResult = {"TmsTestResult" : tmsDict}
        json.dump(TmsFinalResult, tmsFile, indent=4)
        tmsFile.close()


    #func to get device_get_info capi resonse
    def setDutDeviceInfo(self, response):
        category = self.Search_MasterTestInfo(self.TestCaseId, "DUT_CAT")
        dutName = ""
        dutModel = ""
        dutVersion = ""


        specials = "$#&*()[]{};:,//<>?/\/|`~=+"
        trans = string.maketrans(specials, '.'*len(specials))

        try:
            if re.search(r"vendor", response):
                posVendor = response.index('vendor,') + 7
                data = response[posVendor:]
                data = data.lstrip()
                try:
                    posSym = data.index(',')
                    tempStr = data[:posSym]
                    dutName = tempStr.translate(trans)
                except Exception:
                    dutName = data.rstrip('\n')
                    dutName = tempStr.translate(trans)

            if re.search(r"model", response):
                posVendor = response.index('model,') + 6
                data = response[posVendor:]
                data = data.lstrip()
                try:
                    posSym = data.index(',')
                    tempStr = data[:posSym]
                    dutModel = tempStr.translate(trans)
                except Exception:
                    dutModel = data.rstrip('\n')
                    dutModel = dutModel.translate(trans)

            if re.search(r"version", response):
                posVendor = response.index('version,') + 8
                data = response[posVendor:]
                data = data.lstrip()
                try:
                    posSym = data.index(',')
                    tempStr = data[:posSym]
                    dutVersion = tempStr.translate(trans)
                except Exception:
                    dutVersion = data.rstrip('\n')
                    dutVersion = dutVersion.translate(trans)

        except Exception:
            #logging.info("couldn't create device info...")
            logging.debug("couldn't create device info...")


        self.Dut['company'] = dutName.replace(" ", ".")
        self.Dut['model'] = dutModel.replace(" ", ".")
        self.Dut['firmware'] = dutVersion.replace(" ", ".")
        self.Dut['Category'] = category.replace(" ", ".")
        self.Dut['VendorDeviceId'] = dutName.replace(" ", ".") + "_" +  dutModel.replace(" ", ".")

    def setTestbedInfo(self, displayname, response):
        """To get device_get_info CAPI response"""
        primaryTB = ""
        try:
            primaryTB = self.Search_MasterTestInfo(self.TestCaseId, "PrimaryTestbed")
            line = self.Search_MasterTestInfo(self.TestCaseId, "TB_LIST")
            if line == "":
                line = self.Search_MasterTestInfo(self.TestCaseId, "STA")

            tb_list = line.split(',')

            catline = self.Search_MasterTestInfo(self.TestCaseId, "TB_CAT")
            if catline == "":
                catline = self.Search_MasterTestInfo(self.TestCaseId, "STA_CAT")

            tb_category = catline.split(',')
        except Exception:
            #logging.info("self.Search_MasterTestInfo error")
            logging.debug("self.Search_MasterTestInfo error")

        #if there is no primary testbed then no need to create json..
        if primaryTB == "":
            #logging.info("no primary testbed info found")
            logging.debug("no primary testbed info found")
            return
        #number of Stations and number of category should be matched..
        if len(tb_list) != len(tb_category):
            #logging.info("num TB_LIST and TB_CAT doesn't match")
            logging.debug("num TB_LIST and TB_CAT doesn't match")
            return
        if len(tb_list) == 0:
            #logging.info("num -- 0 ")
            logging.debug("num -- 0")
            return

        category = ""
        primaryFlag = 0

        try:
            for index in range(len(tb_list)):

                str1 = tb_list[index].lower()
                str2 = displayname.lower()
                s = SequenceMatcher(None, str1, str2)
                str3 = primaryTB.lower()

                if s.ratio() >= 0.90:
                    category = tb_category[index]
                    if str1 == str3:
                        primaryFlag = 1

        except Exception:
            #logging.info("error - sequence matcher...")
            logging.debug("error - sequence matcher...")

        #if there is no match, then skip
        if category == "":
            return
        companyTestBed = ""
        modelTestBed = ""
        firmwareTestBed = ""

        specials = "$#&*()[]{};:,//<>?/\/|`~=+"
        trans = string.maketrans(specials, '.' * len(specials))

        if re.search(r"status,COMPLETE", response):
            if re.search(r"vendor", response):
                posVendor = response.index('vendor,') + 7
                data = response[posVendor:]
                data = data.lstrip()
                try:
                    posSym = data.index(',')
                    tempStr = data[:posSym]
                    companyTestBed = tempStr.translate(trans)
                except Exception:
                    companyTestBed = data.rstrip('\n')
                    companyTestBed = companyTestBed.translate(trans)

            if re.search(r"model", response):
                posVendor = response.index('model,') + 6
                data = response[posVendor:]
                data = data.lstrip()
                try:
                    posSym = data.index(',')
                    tempStr = data[:posSym]
                    modelTestBed = tempStr.translate(trans)
                except Exception:
                    modelTestBed = data.rstrip('\n')
                    modelTestBed = modelTestBed.translate(trans)

            if re.search(r"version", response):
                posVendor = response.index('version,') + 8
                data = response[posVendor:]
                data = data.lstrip()
                try:
                    posSym = data.index(',')
                    tempStr = data[:posSym]
                    firmwareTestBed = tempStr.translate(trans)
                except Exception:
                    firmwareTestBed = data.rstrip('\n')
                    firmwareTestBed = firmwareTestBed.translate(trans)



            companyTestBed = companyTestBed.replace(" ", ".")
            modelTestBed = modelTestBed.replace(" ", ".")
            firmwareTestBed = firmwareTestBed.replace(" ", ".")

            if primaryFlag == 1:
                self.PrimaryTestbed['company'] = companyTestBed
                self.PrimaryTestbed['model'] = modelTestBed
                self.PrimaryTestbed['firmware'] = firmwareTestBed
                self.PrimaryTestbed['Category'] = category
                self.PrimaryTestbed['VendorDeviceId'] = companyTestBed + "_" +  modelTestBed

            else:
                self.SupplementalTestbeds.append({'company':companyTestBed, 'model':modelTestBed, 'firmware':firmwareTestBed, 'Category' : category, 'VendorDeviceId' : companyTestBed + "_" +  modelTestBed})
