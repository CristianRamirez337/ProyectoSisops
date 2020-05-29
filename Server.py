'''
    Proyecto estacionameinto Sistemas Operativos

    Cristian Aurelio Ramírez Anzaldo A01066337
'''

import socket
import sys
import threading
from time import gmtime, strftime, sleep, time, thread_time_ns


def cierre():
    pass

def laser_on_s():
    pass

def laser_off_s():
    pass

def laser_on_e():
    pass

def laser_off_e():
    pass

def mete_tarjeta():
    pass

def recoge_tarjeta():
    pass

def oprime_boton():
    pass

def apertura(message):
    print("in function apertura: " + message)


def data_processor(message, server_data_table):
    '''
    Multi-threading operation
    For every input data from the client a thread is created
    and its information is manipulated in this function
    '''

    # Function dictionary
    functions = {'apertura': apertura, 'oprimeBoton': oprime_boton,
                 'recogeTarjeta': recoge_tarjeta, 'meteTarjeta': mete_tarjeta}
    functions2 = {'laserOffE': laser_off_e, 'laserOnE': laser_on_e, 'laserOffS': laser_off_s,
                  'laserOnS': laser_on_s, 'cierre': cierre}
    functions = {**functions, **functions2}

    time_stamp = message[:message.find(' ')]
    #
    command = (message[(message.find(time_stamp) + len(time_stamp) + 1) : message.find(' ', (message.find(time_stamp) + len(time_stamp) + 1))]).lower()
    functions[command](message)
    # command_thread = threading.Thread(target=functions[command.lower()], args=(message,))
    # command_thread.start()



def establish_connection():
    '''
        Function to Establish connection with the client
        Returns: sock.accept() - connection and client address
    '''

    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to the port
    server_address = ('localhost', 8080)
    print('starting up on %s port %s' % server_address)
    sock.bind(server_address)

    # Listen for incoming connections
    sock.listen(1)

    print('waiting for a connection')
    return sock.accept()


def main():
    ''' Main function of the parking lot system'''

    # --------/ Variables \--------
    # Dictionary to store table data
    server_data_table = {'Time-stamp': [], 'Command': [], 'Server display': [], 'Free': [], 'Occupied': []}

    # Counters
    free_places_var = 50
    occupied_places_var = 0

    # Buffer semaphores
    sem_free_places = threading.Semaphore(value=free_places_var)
    sem_occupied_places = threading.Semaphore(value=occupied_places_var)
    sem_mutex_table = threading.Semaphore(value=1)

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

                data_processor(client_message, server_data_table)

                connection.sendall(b'data received...')

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