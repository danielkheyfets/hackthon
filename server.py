import colorama
import selectors
import socket
import struct
from threading import Thread
from datetime import datetime, timedelta, time
import random
import time
from select import select
from colorama import Fore,Back,Style

colorama.init()
active_clients = []
localIP = "127.0.0.1"
server_port = 6995
destination_port = 13115
bufferSize = 1024
random_question = " "
answer = ""
winner_group_name = " "
msg_type = 0x02
magic_cookie = 0xabcddcba
isBrodcusLive=True



def main():
    global isBrodcusLive, x , group1_name, group2_name, random_question, active_clients
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
        try:
            tcp_socket.bind(('', server_port))
            while True:
                isBrodcusLive=True
                broadcastThread = Thread(target=send_broadcast)
                broadcastThread.start()   #start the broadcast thread
                print(Fore.BLUE+f'Server started, listening on IP address {localIP}')
                tcp_socket.listen() 
                accept_client_connection(tcp_socket) #take the broadcast connections
                conn1 = active_clients[0][0]
                conn2 = active_clients[1][0]
                group1_name = (conn1.recv(bufferSize)).decode()
                group2_name = (conn2.recv(bufferSize)).decode()
                print (Fore.RED+"group1_name:  " + group1_name)
                print(Fore.RED+"group2_name:  " + group2_name)
                broadcastThread.join()


                time.sleep(10) # start the game after 10 sec
                question, answer = get_random_question_and_answer()
                question_msg = f"""Welcome to Quick Maths!!!\nPlayer 1: {group1_name}\nPlayer 2: {group2_name}\n==\nPlease answer the following question as fast as you can:\nHow much is {question}?"""
                sendMessageToClients(question_msg)
                events, _, _ = select([conn1, conn2], [], [], 10) #wait until get ans wait only 10 sec
                if events:
                    if events[0] == conn1:
                            group1_answer = (conn1.recv(bufferSize)).decode()
                            print(Fore.RED+"group_1 answer: " + str(group1_answer) + " The real answer: " + str(answer))
                            winner=checkGroupAns(group1_answer,answer,group1_name,group2_name)

                    else:
                            group2_answer = (conn2.recv(bufferSize)).decode()
                            print(Fore.RED+"group_2 answer: " + str(group2_answer) + " The real answer: " + str(answer))
                            winner=checkGroupAns(group2_answer,answer,group2_name,group1_name)

                    game_over_msg = f"""Game over!\nThe correct answer was {answer}!\nCongratulations to the winner: {winner} """ 
                    sendMessageToClients(game_over_msg)
                else:
                    print("not event")
                    game_over_msg = f"""Game over! \nTime out, Nobody won """
                    sendMessageToClients(game_over_msg)
                game_over = f"""Game over, sending out offer requests... """
                sendMessageToClients(game_over)
                closeConnectionWithClients()
        except Exception as e:
            print(e)
            

        finally:
            closeConnectionWithClients()
            tcp_socket.close()


#in this function we accept the clients that want to connect us until we get 2 clients
def accept_client_connection(tcp_socket):
    global active_clients
    global isBrodcusLive
    while len(active_clients) < 2:
        conn, address = tcp_socket.accept()
        active_clients.append((conn, address))
        print('Connected by', address)
    isBrodcusLive=False
    


def sendMessageToClients(msg):
    global active_client
    for i in range(len(active_clients)):
        con=active_clients[i][0]
        con.sendall(msg.encode())


#this func send a broadcast 
def send_broadcast():
    global isBrodcusLive
    server_udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    server_udp_socket.settimeout(0.2)
    broadcast_msg = struct.pack('I b h', magic_cookie, msg_type, server_port)
    while isBrodcusLive:
        server_udp_socket.sendto(broadcast_msg, ('<broadcast>', destination_port))
        time.sleep(1)
    server_udp_socket.close()


def closeConnectionWithClients():
    global active_clients
    for i in range(len(active_clients)):
        con=active_clients[i][0]
        con.close()
        print(i)
    active_clients=[]



#in this func we chel if the ans of the group is equal to the actual answer
def checkGroupAns(group_ans,real_ans,theGroupIsAnswered,OtherGroup):
    try:
        if int(group_ans)== real_ans:
            print(Fore.YELLOW+"the winner :" + theGroupIsAnswered)
            winner = theGroupIsAnswered
            
        else:
            print(Fore.YELLOW+"the winner :" + OtherGroup)
            winner = OtherGroup
        return winner
    except:
        print(Fore.YELLOW+"the winner :" + OtherGroup)
        return OtherGroup
    


def get_random_question_and_answer():
    Dict = {'1+1': 2, '1+2': 3, '1+3': 4}
    return random.choice(list(Dict.items()))


if __name__ == '__main__':
    main()
