'''
    Proyecto estacionamiento Sistemas Operativos

    Cristian Aurelio Ramírez Anzaldo A01066337
'''

import socket
import sys
import time

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = ('localhost', 8888)
print('starting up on %s port %s' % server_address)
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)

print('waiting for a connection')
connection, client_address = sock.accept()

try:
    print('connection from', client_address)

    # Receiving the data
    while True:
        data = connection.recv(256)
        print('server received "%s"' % data.decode('utf-8'))  # data bytes back to str
        if data:
            print('sending answer back to the client')

            connection.sendall(b'va de regreso...' + data)  # b converts str to
            # bytes
        else:
            print('no data from', client_address)
            connection.close()
            sys.exit()

finally:
    # Clean up the connection
    print('se fue al finally')
    connection.close()