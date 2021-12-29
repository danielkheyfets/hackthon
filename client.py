import colorama
import struct
import sys
from socket import socket
import socket
from threading import Thread
from colorama import Fore,Back,Style
from select import select
import time
from termios import tcflush, TCIFLUSH


local_ip = '127.0.0.1'
getch = ""
bufferSize = 1024
TeamName = b'Danieliel'
client_start_listening = f'Client started, listening for offer requests...'
ClientReceivedMsg = f'Received offer from {local_ip},attempting to connect...'
server_disconnected_msg = f'Server disconnected, listening for offer requests...'
server_port = ""
events = []
data = ""


def main():
    global getch, server_port, local_ip, events, data
    events = []
    data = ""

    print(client_start_listening)
    while True:
        try:
            #START UDP CONNECTION AN WAITE FORE THE BRUDCUST MESSAGE FROM THE SERVER
            client_udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            client_udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            client_udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            client_udp_socket.bind(('', 13115))
            data, local_ip = client_udp_socket.recvfrom(bufferSize)
            server_port = struct.unpack('I b h', data)[2]
            local_ip=local_ip[0]
        

            if not (data[0:4] == bytes([0xba, 0xdc, 0xcd, 0xab])) or not data[4] == 0x02:
                print(Fore.GREEN+f'Incompatible magic cookie or msg type')
            else:
                print(Fore.RED+f'Received offer from {local_ip},attempting to connect...')
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_tcp_socket:
                        client_tcp_socket.connect((local_ip, server_port))
                        client_tcp_socket.sendall(TeamName)
                        data = client_tcp_socket.recv(bufferSize)
                        print(Fore.BLUE+data.decode())  
                        events, _, _ = select([sys.stdin, client_tcp_socket], [], [], 10)
                        if not events:
                            pass
                        elif events[0] == sys.stdin:
                            getch = sys.stdin.readline()[0]
                            sys.stdin.flush()
                            tcflush(sys.stdin, TCIFLUSH)
                            print(Fore.BLUE+getch)
                            client_tcp_socket.sendall(getch.encode())


                        data = (client_tcp_socket.recv(bufferSize)).decode()
                        print(Fore.BLUE+data)
                        data = (client_tcp_socket.recv(bufferSize)).decode()
                        print(Fore.BLUE+data)
               
                finally:
                    client_tcp_socket.close()
                    time.sleep(5)

        except Exception as e:
            print (e)
        finally: 
            client_udp_socket.close()

def get_ans_from_keybord():
    global getch
    getch = input()
    print("get: " + getch)


if __name__ == '__main__':
    main()
