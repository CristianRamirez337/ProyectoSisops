'''
    Proyecto estacionameinto Sistemas Operativos

    Cristian Aurelio Ramírez Anzaldo A01066337
'''

import socket
import sys
import threading
from time import gmtime, strftime, sleep, time, thread_time_ns


def establish_connection():
    '''
        Function to Establish connection with the client
        Returns: sock.accept() - connection and client address
    '''

    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to the port
    server_address = ('localhost', 8888)
    print('starting up on %s port %s' % server_address)
    sock.bind(server_address)

    # Listen for incoming connections
    sock.listen(1)

    print('waiting for a connection')
    return sock.accept()


def data_processor(message):
    print("Thread says: " + message)


def main():
    ''' Main function of the parking lot system'''

    # --------/ Variables \--------
    # Dictionary to store table data
    server_data_table = {'Time-stamp': [], 'Command': [], 'Server display': [], 'Free': [], 'Occupied': []}

    # Counters
    free_places_var = 50
    occupied_places_var = 0

    # Buffer semaphores
    free_places = threading.Semaphore(value=free_places_var)
    occupied_places = threading.Semaphore(value=occupied_places_var)

    # Establishing connection with the server
    connection, client_address = establish_connection()

    try:
        print('connection from', client_address)

        # Getting time from the processor
        current_time = strftime("%a, %d %b %Y %H:%M:%S 0", gmtime())
        print("Starting time is: " + current_time)



        # Receiving the data
        while True:
            data = connection.recv(256)
            print('server received "%s"' % data.decode('utf-8'))  # data bytes back to str

            if data:
                client_message = data.decode('utf-8')

                t = threading.Thread(target=data_processor, args=(client_message,))
                t.start()

                connection.sendall(b'data received...')

                server_data_table['Time-stamp'].append(client_message[:client_message.find(' ')])
            else:
                print('no data from', client_address)
                connection.close()
                sys.exit()

    finally:
        # Clean up the connection
        print('se fue al finally')
        print(server_data_table)
        connection.close()


if __name__ == '__main__':
    main()