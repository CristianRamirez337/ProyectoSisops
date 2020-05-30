'''
    Proyecto estacionameinto Sistemas Operativos

    Cristian Aurelio Ramírez Anzaldo A01066337
'''

import socket
import sys
import threading
import queue
from time import gmtime, strftime, sleep, time, thread_time_ns
from tabulate import tabulate

# GLobal variables
number_exits = 0
number_entries = 0
free_places_var = 0
occupied_places_var = 0
# Dictionary to store table data
server_data_table = {'Time-stamp': [], 'Command': [], 'Server display': [], 'Free': [], 'Occupied': []}

def get_data_command(message):
    time_stamp = message[:message.find(' ')]
    command = message[(message.find(time_stamp) + len(time_stamp) + 1): message.find(' ', (
            message.find(time_stamp) + len(time_stamp) + 1))]
    number = message[(message.find(command) + len(command) + 1):]
    if command == 'Cierr':
        command = 'Cierre'
    return time_stamp, command, number


def cierre(message):
    pass

def laser_on_s(message):
    pass

def laser_off_s(message):
    pass

def laser_on_e(message):
    pass

def laser_off_e(message):
    pass

def mete_tarjeta(message):
    pass

def recoge_tarjeta(message):
    pass

def server_data_table_modificator(time_stamp, command, server_display, occupied, free):
    server_data_table['Time-stamp'].append(time_stamp)
    server_data_table['Command'].append(command)
    server_data_table['Free'].append(free)
    server_data_table['Occupied'].append(occupied)
    server_data_table['Server display'].append(server_display)

def oprime_botom_thread(message):
    [time_stamp, command, number] = get_data_command(message)

    sem_mutex_table.acquire()
    server_display = ' '
    server_data_table_modificator(time_stamp, message[message.find(command):], server_display, occupied_places_var, free_places_var)
    server_display = ('Se comienza a imprimir tarjeta por E' + str(number))
    print("NUMBER IS")
    print(number)
    server_data_table_modificator(time_stamp, ' ', server_display, ' ', ' ')
    sem_mutex_table.release()

    #sleep(5)

    sem_mutex_table.acquire()
    server_display = 'Se imprimió tarjeta. ' + strftime("%a, %d %b %Y %H:%M:%S 0", gmtime())
    server_data_table_modificator(float(time_stamp) + 5, ' ', server_display, ' ', ' ')
    sem_mutex_table.release()


def oprime_boton(message):
    '''If there is an available place it will print a card with the SO hour, otherwise
    it will display: No hay lugar, espere un poco y vuelva a imprimir boton'''

    [time_stamp, command, number] = get_data_command(message)

    if sem_free_places.acquire(timeout=1):

        boton_thread = threading.Thread(target=oprime_botom_thread, args=(message,))
        boton_thread.start()
    else:
        print("No hay lugar, espere un poco y vuelva a presionar el boton")

    pass


def abrir_cerrar(message):
    ''' The purpose of this function is to check if the meesage from the client
    is to open the parking lot and start executing orders or ignore them while it
    is not open yet. if it is the instruction to oppen data is added to the table
    en the free places semaphore value is set. If the command is cerrar, return false.'''

    [time_stamp, command, number] = get_data_command(message)
    global free_places_var, server_data_table, occupied_places_var
    if 'Apertura' in command:
        server_data_table['Time-stamp'].append(time_stamp)
        server_data_table['Command'].append(message[message.find(command):])
        server_data_table['Free'].append(int(number[:number.find(' ')]))
        server_data_table['Occupied'].append(0)
        number_entries = message[(message.find(number) + len(number) + 1) : message.find(' ', (
            message.find(number) + len(number) + 1))]
        number_exits = message[(message.find(number_entries) + len(number_entries) + 1) : ]
        server_data_table['Server display'].append('Se abre un estacionamiento de ' + number + ' lugares, ' + number_entries + ' puertas de entrada y ' + number_exits + ' de salida')
        free_places_var = int(number[:number.find(' ')])
        # Buffer semaphores

        return True

    elif 'Cierre' in command:
        server_data_table['Time-stamp'].append(time_stamp)
        server_data_table['Command'].append(message[message.find(command):])
        server_data_table['Free'].append(free_places_var)
        server_data_table['Occupied'].append(occupied_places_var)

        # PRINT TABLE HERE
        print("Parking lot has been closed")
        print(tabulate(server_data_table, headers=['Time-stamp', 'Command', 'Server display', 'Free', 'Occupied']))
        sys.exit()
        #return False

    else:
        return False


def data_processor(message):
    '''
    Function to process every message received by the client
    '''
    global server_data_table
    # Function dictionary
    functions = {'cierre': abrir_cerrar, 'oprimeboton': oprime_boton, 'recogetarjeta': recoge_tarjeta,
                 'metetarjeta': mete_tarjeta, 'laseroffe': laser_off_e, 'laserone': laser_on_e,
                 'laseroffs': laser_off_s, 'laserons': laser_on_s}

    [time_stamp, command, number] = get_data_command(message)

    functions[command.lower()](message)

    # command = (message[(message.find(time_stamp) + len(time_stamp) + 1): message.find(' ', (
    #             message.find(time_stamp) + len(time_stamp) + 1))]).lower()
    # functions[command](message)
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



''' Main function of the parking lot system'''

# --------/ Variables \--------
sem_mutex_table = threading.Semaphore(value=1)
sem_mutex_places = threading.Semaphore(value=1)

# Establishing connection with the server
connection, client_address = establish_connection()


try:
    print('connection from', client_address)

    # Getting time from the processor
    current_time = strftime("%a, %d %b %Y %H:%M:%S 0", gmtime())
    print("Starting time is: " + current_time)
    parking_open = False


    # Receiving the data
    while True:
        data = connection.recv(256)
        print('server received "%s"' % data.decode('utf-8'))  # data bytes back to str

        if data:

            client_message = data.decode('utf-8')

            if parking_open:

                data_processor(client_message)

            else:
                parking_open = abrir_cerrar(client_message)
                if parking_open:
                    sem_free_places = threading.Semaphore(value=free_places_var)
                    sem_occupied_places = threading.Semaphore(value=occupied_places_var)

            connection.sendall(b'data received...')
        # else:
        #     print('no data from', client_address)
        #     connection.close()
        #     sys.exit()


finally:
    # Clean up the connection
    print('se fue al finally')
    connection.close()