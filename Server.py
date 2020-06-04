'''
    Proyecto estacionameinto Sistemas Operativos

    Cristian Aurelio Ramírez Anzaldo A01066337
'''

import socket
import sys
import threading
import queue
from time import gmtime, strftime, sleep, time
from tabulate import tabulate

# GLobal variables
number_exits = 0
number_entries = 0
free_places_var = 0
occupied_places_var = 0
# Dictionary to store table data
server_data_table = {'Time-stamp': [], 'Command': [], 'Server display': [], 'Free': [], 'Occupied': []}


def get_data_command(message, maxsplit):
    '''Elements of the message are obtained from the string and sent back
    message : message from the client
    maxplit : quantity of elements to get from the message'''
    if '/' in message:
        message = message[:message.find('/')].split(' ', maxsplit)
    else:
        message = message.split(' ', maxsplit)
    return message


def server_data_table_modificator(time_stamp, command, server_display, occupied, free):
    ''' Function to modify the dictionary that will be the table
    and it add what is has in the arguments'''
    server_data_table['Time-stamp'].append(time_stamp)
    server_data_table['Command'].append(command)
    server_data_table['Free'].append(free)
    server_data_table['Occupied'].append(occupied)
    server_data_table['Server display'].append(server_display)

def laser_on_s(message):
    pass

def laser_off_s(message):
    pass

def laser_on_e(message):
    '''The car has finished going through the entrance, the number of occupied and free places
    is uupdated as well as the sempahore that guards the door is released. Also, the barrier
    is set to go down and the table is updated'''
    # Getting data from the message ant getting rid of the comments
    [time_stamp, command, number] = get_data_command(message, 2)
    
    # Se suma uno a lugares ocupados y se resta a los disponibles
    sem_mutex_places.acquire()
    global occupied_places_var, free_places_var
    occupied_places_var += 1
    free_places_var -= 1
    sem_mutex_places.release()

    # Modificando la tabla
    sem_mutex_table.acquire()
    server_data_table_modificator(time_stamp, message[message.find(command):], ' ', ' ', ' ')
    server_display = 'Auto termina de pasar E' + number
    server_data_table_modificator(time_stamp, ' ', server_display, occupied_places_var, free_places_var)
    sem_mutex_table.release()

    # Se libera semaforo para que pueda pasar un coche por la misma entrada
    sem_entries_exits[int(number) - 1].release()

    # Modificacion de tabla con semaforo
    sem_mutex_table.acquire()
    server_display = 'Se bajó la barra E' + number
    server_data_table_modificator(float(time_stamp) + 5, ' ', server_display, ' ', ' ')
    sem_mutex_table.release()

def laser_off_e(message):
    '''The car start to enter the parking lot so a semaphore to ensure that only one car
    is going through the entrance, the sempahone is store in a list and the data in the table
    is updated'''
    [time_stamp, command, number] = get_data_command(message, 2)

    # Toma el semaforo de la entrada correspondiente
    sem_entries_exits[int(number) - 1].acquire()

    # Modificacion de la tabla
    sem_mutex_table.acquire()
    server_data_table_modificator(time_stamp, message[message.find(command):], ' ', ' ', ' ')
    server_display = 'Auto comienza a pasar E' + number
    server_data_table_modificator(time_stamp, ' ', server_display, ' ', ' ')
    sem_mutex_table.release()


def mete_tarjeta(message):
    '''It verifies that the client paid the ticket bill, and if not,
    the barrier stays down, otherwise it starts to lift'''

    # Separando el mensaje en valores
    [time_stamp, command, number] = get_data_command(message, 2)
    number = number[:number.find(' ')]
    paid = int(number[number.find(' ') + 1:])

    # Modificacion de la tabla
    sem_mutex_table.acquire()
    server_data_table_modificator(time_stamp, message[message.find(command):], ' ', ' ', ' ')
    server_display = 'Auto quiere salir por salida S' + number
    server_data_table_modificator(time_stamp, ' ', server_display, ' ', ' ')
    sem_mutex_table.release()

    # Verificando si pago el don
    if paid == 1:
        sem_mutex_table.acquire()
        server_display = 'Se levantó la barrera S' + number
        server_data_table_modificator(float(time_stamp) + 5, ' ', server_display, ' ', ' ')
        sem_mutex_table.release()
    else:
        sem_mutex_table.acquire()
        server_display = 'Boleto no pagado en S' + number
        server_data_table_modificator(time_stamp, ' ', server_display, ' ', ' ')
        sem_mutex_table.release()


def recoge_tarjeta(message):
    '''Function to indicate that the client
    has taken the card To enter the parking lot'''
    # Separando el mensaje en valores
    [time_stamp, command, number] = get_data_command(message, 2)

    sem_mutex_table.acquire()
    server_data_table_modificator(time_stamp, message[message.find(command):], ' ', ' ', ' ')
    server_display = 'Se empieza a levantar la barrera E' + number
    server_data_table_modificator(time_stamp, ' ', server_display, ' ', ' ')
    sem_mutex_table.release()

    sem_mutex_table.acquire()
    server_display = 'Se levantó la barrera E' + number
    server_data_table_modificator(float(time_stamp) + 5, ' ', server_display, ' ', ' ')
    sem_mutex_table.release()

    

def oprime_botom_thread(message):
    '''Thread to handle what happen with the function oprime boton from
    the client'''
    [time_stamp, command, number] = get_data_command(message, 2)

    sem_mutex_table.acquire()
    server_data_table_modificator(time_stamp, message[message.find(command):], ' ', occupied_places_var, free_places_var)
    server_display = ('Se comienza a imprimir tarjeta por E' + str(number))
    server_data_table_modificator(time_stamp, ' ', server_display, ' ', ' ')
    sem_mutex_table.release()

    #sleep(5)

    sem_mutex_table.acquire()
    server_display = 'Se imprimió tarjeta. ' + strftime("%a, %d %b %Y %H:%M:%S 0", gmtime())
    server_data_table_modificator(float(time_stamp) + 5, ' ', server_display, ' ', ' ')
    sem_mutex_table.release()


def oprime_boton(message):
    '''If there is an available place it will print a card with the OS hour, otherwise
    it will display: No hay lugar, espere un poco y vuelva a imprimir boton. It start
    a thread if there available places'''

    [time_stamp, command, number] = get_data_command(message, 2)

    if int(number) <= number_entries and int(number_entries) > 0:
        if sem_free_places.acquire(timeout=1):

            boton_thread = threading.Thread(target=oprime_botom_thread, args=(message,))
            boton_thread.start()
        else:
            print("No hay lugar, espere un poco y vuelva a presionar el boton")
    else:
        print("Número de puerta inexistente o incorrecto")


def abrir_cerrar(message):
    ''' The purpose of this function is to check if the meesage from the client
    is to open the parking lot and start executing orders or ignore them while it
    is not open yet. if it is the instruction to oppen data is added to the table
    en the free places semaphore value is set. If the command is cerrar, return false.'''

    [time_stamp, command] = get_data_command(message, 1)
    global free_places_var, server_data_table, occupied_places_var, number_entries, number_exits
    if 'apertura' in command.lower():
        [time_stamp, command, number, entries, exits] = get_data_command(message, 4)
        server_data_table['Time-stamp'].append(time_stamp)
        server_data_table['Command'].append(message[message.find(command):])
        server_data_table['Free'].append(number)
        server_data_table['Occupied'].append(0)
        number_entries = int(entries)
        number_exits = int(exits)
        server_data_table['Server display'].append('Se abre un estacionamiento de ' + number + ' lugares, ' + entries + ' puertas de entrada y ' + exits + ' de salida')
        free_places_var = int(number)
        
        return True

    elif 'cierre' in command.lower():
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

    [time_stamp, command, number] = get_data_command(message, 2)

    functions[command.lower()](message)


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


''' +++++++++++++| Main function of the parking lot system |+++++++++++++'''
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
                    sem_entries_exits = []
                    for i in range(number_entries):
                        sem_entries_exits.append(threading.Semaphore())
                    for i in range(number_exits):
                        sem_entries_exits.append(threading.Semaphore())

            connection.sendall(b'data received...')
        # else:
        #     print('no data from', client_address)
        #     connection.close()
        #     sys.exit()


finally:
    # Clean up the connection
    print('se fue al finally')
    connection.close()