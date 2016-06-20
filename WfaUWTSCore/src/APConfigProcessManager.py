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
import os
import sys
import re
import time
import subprocess
import SocketServer

apconfig_tcp_server = None

class APConfigProcessManager(object):
    
    ROOT_APCONFIG_PATH = "C:\WFASoft\AP_ControlAgent"
    AP_SERVICE_BATCH_FILE = "APService.bat"
    UCC_TEST_BED_CONF = "src\UCCTestbed.conf"
    CURR_NUM_OF_AP = 0
    RECV_NUM_OF_AP = 0
    RECV_PORT_START = 0
    ap_service_shell_pid_list = []
    ap_service_shell_process_list = []
    
    @staticmethod
    def get_ap_num_info(packet):
        pkt_list = packet.split(',')
        APConfigProcessManager.RECV_PORT_START = int(pkt_list[0].split('=')[1])
        APConfigProcessManager.RECV_NUM_OF_AP = int(pkt_list[1].split('=')[1])
        print "received"
    
    @staticmethod
    def run_apconfig_subprocess():
        if APConfigProcessManager.CURR_NUM_OF_AP == 0:
            for i in range(0, APConfigProcessManager.RECV_NUM_OF_AP):
                os.chdir(APConfigProcessManager.ROOT_APCONFIG_PATH)
                APConfigProcessManager.update_port_num(APConfigProcessManager.RECV_PORT_START + i)                
                p = subprocess.Popen(APConfigProcessManager.AP_SERVICE_BATCH_FILE, shell=False, creationflags=subprocess.CREATE_NEW_CONSOLE)
                APConfigProcessManager.ap_service_shell_process_list.append(p)
                APConfigProcessManager.ap_service_shell_pid_list.append(p.pid)
                time.sleep(1)
            APConfigProcessManager.CURR_NUM_OF_AP = APConfigProcessManager.RECV_NUM_OF_AP
        else:
            subtract = APConfigProcessManager.RECV_NUM_OF_AP - APConfigProcessManager.CURR_NUM_OF_AP
            if subtract > 0:
                for i in range(0, subtract):
                    APConfigProcessManager.update_port_num(APConfigProcessManager.RECV_PORT_START + APConfigProcessManager.CURR_NUM_OF_AP)
                    p = subprocess.Popen(APConfigProcessManager.AP_SERVICE_BATCH_FILE, creationflags=subprocess.CREATE_NEW_CONSOLE)
                    APConfigProcessManager.ap_service_shell_process_list.append(p)
                    APConfigProcessManager.ap_service_shell_pid_list.append(p.pid)
                    time.sleep(1)
                APConfigProcessManager.CURR_NUM_OF_AP = APConfigProcessManager.RECV_NUM_OF_AP
            
            
    @staticmethod
    def update_port_num(port):
        if os.path.exists(APConfigProcessManager.UCC_TEST_BED_CONF):
            conf_file = open(APConfigProcessManager.UCC_TEST_BED_CONF, 'r+b')
            file_content = conf_file.read()
            if re.search("ServerPort", file_content, re.IGNORECASE):
                file_content = re.sub(r'ServerPort=\d+', r'ServerPort=%s' % str(port), file_content)
                conf_file.seek(0)
                conf_file.truncate()
                conf_file.write(file_content)
                conf_file.close()
        else:
            raise IOError('%s file not found' % APConfigProcessManager.UCC_TEST_BED_CONF)
        

class TCPHandler(SocketServer.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(2048);
        print "{} wrote:".format(self.client_address[0])
        print self.data
        try:
            APConfigProcessManager.get_ap_num_info(self.data)
            APConfigProcessManager.run_apconfig_subprocess()
            self.request.sendall('status,COMPLETE\r\n')
        except IOError:
            exc_info = sys.exc_info()[1]
            self.request.sendall('status,ERROR,reason,%s\r\n' % exc_info)
            print sys.exc_info()


class APConfigTCPServer(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server = None
    
    def run_server(self):
        self.server = SocketServer.TCPServer(self.host, self.port)
        self.server.serve_forever()


def main():
    global apconfig_tcp_server
    fh = open('nul', 'w')
    
    apconfig_tcp_server = APConfigTCPServer(('', 8800), TCPHandler)
    apconfig_tcp_server.run_server()


def exit_process_manager():
    global apconfig_tcp_server
    
    if apconfig_tcp_server is not None:
        apconfig_tcp_server.server.server_close()    

    for pid in APConfigProcessManager.ap_service_shell_pid_list:
        fh = open('NUL', 'w')
        subprocess.Popen("TASKKILL /F /PID {pid} /T".format(pid=pid), stdout = fh, stderr = fh)
        fh.close()

    
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print "Bye"
    except Exception:
        print sys.exc_info()
    finally:
        print "Done....."
        exit_process_manager()
