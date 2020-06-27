import socket
import select
import random
import os
import subprocess
import shutil 
IP = "127.0.0.1"

PORT = 1234

server_to_port_map = {}

directories_to_be_removed = os.listdir()

print("Clearing previous sessions if any.....")
for d in directories_to_be_removed:
    if os.path.isdir(d):
        print(d,"server removed")
        shutil.rmtree(d)
    else:
        # print("This is a file",d)
        pass
print("Coordinator started....")
while True:

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as coordinator_socket:

        coordinator_socket.bind((IP, PORT))

        coordinator_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        bytesAddressPair = coordinator_socket.recvfrom(1024)

        message = bytesAddressPair[0]

        address = bytesAddressPair[1]

        portMsg = message.decode('utf-8').strip()
        
        # print(portMsg)

        if not portMsg in server_to_port_map:
            while 1:
                num = random.randint(1111,9999)
                if num not in server_to_port_map.values():
                    server_to_port_map[portMsg] = num
                    break
            new_server = subprocess.Popen(["python3", "server.py"] + [str(server_to_port_map[portMsg])])

        # Sending a reply to client
        # print(server_to_port_map[portMsg])

        bytesToSend = bytes(str(server_to_port_map[portMsg]), 'utf-8')

        # bytesToSend = bytesToSend.encocde('utf-8')

        print("Port address ",bytesToSend,"sent to ",address)

        coordinator_socket.sendto(bytesToSend, address)
