import socket
import select
import errno
import sys
import time
import re
HEADER_LENGTH = 10

COORD_IP = "127.0.0.1"

COORD_PORT = 1234

my_username = input("Username: ")

re1 = "[E|e]xit"
re2 = "[Q|q]uit"
re3 = "[B|b]ye.*"

def talk_with_ss(recv_port):

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    client_socket.connect((COORD_IP, recv_port))

    client_socket.setblocking(False)
    
    username = my_username.encode('utf-8')
    
    username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')
    
    client_socket.send(username_header + username)

    clientlogs = my_username+".txt"
    client_logs = open(f"./{recv_port}/{my_username}_logs.txt","w")

    while True:
 
        message = input(f'{my_username} > ')
        client_logs.write(f'Me > '+message+"\n")
        if message:

            # Encode message to bytes, prepare header and convert to bytes, like for username above, then send
            if re.compile("(%s|%s|%s)" % (re1, re2, re3)).findall(message):
                sys.exit()
            message = message.encode('utf-8')
            message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
            client_socket.send(message_header + message)

        try:
            # Now we want to loop over received messages (there might be more than one) and print them
            while True:

                # Receive our "header" containing username length, it's size is defined and constant
                username_header = client_socket.recv(HEADER_LENGTH)

                # If we received no data, server gracefully closed a connection, for example using socket.close() or socket.shutdown(socket.SHUT_RDWR)
                if not len(username_header):
                    sprint = 'Connection closed by the server'
                    print(sprint)
                    client_logs.write(sprint+"\n")
                    break

                # Convert header to int value
                username_length = int(username_header.decode('utf-8').strip())

                # Receive and decode username
                username = client_socket.recv(username_length).decode('utf-8')

                # Now do the same for message (as we received username, we received whole message, there's no need to check if it has any length)
                message_header = client_socket.recv(HEADER_LENGTH)
                message_length = int(message_header.decode('utf-8').strip())
                message = client_socket.recv(message_length).decode('utf-8')

                # Print message
                sprint = f'{username} connected to {recv_port} > {message}'
                print(sprint)
                client_logs.write(sprint+"\n")

            break

        except IOError as e:
            # This is normal on non blocking connections - when there are no incoming data error is going to be raised
            # Some operating systems will indicate that using AGAIN, and some using WOULDBLOCK error code
            # We are going to check for both - if one of them - that's expected, means no incoming data, continue as normal
            # If we got different error code - something happened
            if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                print('Reading error: {}'.format(str(e)))
                break

            # We just did not receive anything
            continue

        except Exception as e:
            # Any other exception - something happened, exit
            print('Reading error: '.format(str(e)))
            break

    client_socket.close()
    client_logs.close()

while True:

    session_name = input("Enter a session name : ")

    session_name = session_name.encode('utf-8')

    client_coordinator_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    client_coordinator_socket.sendto(session_name,(COORD_IP, COORD_PORT))

    recv_port = client_coordinator_socket.recvfrom(1024)[0]

    recv_port = int(recv_port.decode('utf-8').strip())

    print("Received port from coordinator : ",recv_port)

    time.sleep(1)
    
    talk_with_ss(recv_port)

    client_coordinator_socket.close()


    
