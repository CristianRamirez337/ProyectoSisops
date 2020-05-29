import socket
import sys

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = ('localhost', 8080)
print('connecting to %s port %s' % server_address)
sock.connect(server_address)


messages = ['0.00 Apertura 50 2', '1.00 oprimeBoton 1', '49.00 meteTarjeta 1']
try:
    # Send data
    for m in messages:
        print("client sending " + m)
        sock.sendall(m.encode('utf-8'))

        respuesta = sock.recv(256)
        print('client received ' + respuesta.decode('utf-8'))
finally:
    print('closing socket')
    sock.close()



    def main(args):
        return 0


    if __name__ == '__main__':
        import sys

        sys.exit(main(sys.argv))

