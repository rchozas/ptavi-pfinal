#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Clase (y programa principal) para un servidor de eco en UDP simple
"""

import socketserver
import sys
import os
import os.path

# partiendo de la práctica 6

if len(sys.argv) != 4:
    sys.exit("Usage: python server.py IP port audio_file")
try:
    IP = sys.argv[1]
    PUERTO = int(sys.argv[2])
    FICHERO = sys.argv[3]
    if not os.path.exists(FICHERO):
        sys.exit('Usage: python server.py IP port audio_file')
except:
    sys.exit('Usage: python server.py IP port audio_file')


class EchoHandler(socketserver.DatagramRequestHandler):
    """
    Echo server class
    """

    def handle(self):
        # Escribe dirección y puerto del cliente (de tupla client_address)

        while 1:
            # Leyendo línea a línea lo que nos envía el cliente
            line = self.rfile.read()
            metodos = ["INVITE", "ACK", "BYE"]
            metodo = line.decode('utf-8').split(' ')[0]
            if len(line.decode('utf-8')) >= 2:
                if metodo == "INVITE":
                    enviar = b"SIP/2.0 100 Trying\r\n\r\n"
                    enviar += b"SIP/2.0 180 Ringing\r\n\r\n"
                    enviar += b"SIP/2.0 200 OK\r\n\r\n"
                    self.wfile.write(enviar)
                elif metodo == "ACK":
                    aEjecutar = "./mp32rtp -i 127.0.0.1 -p 23032 < " + FICHERO
                    print("vamos a ejecutar", aEjecutar)
                    os.system(aEjecutar)
                elif metodo == "BYE":
                    enviar = b"SIP/2.0 200 OK\r\n\r\n"
                    self.wfile.write(enviar)
                elif metodo and metodo not in metodos:
                    enviar = b"SIP/2.0 405 Method Not Allowed\r\n\r\n"
                    self.wfile.write(enviar)
                else:
                    self.wfile.write(b"SIP/2.0 400 Bad request\r\n\r\n")
            else:
                break

            # Si no hay más líneas salimos del bucle infinito
            if not line:
                break
            print(line.decode('utf-8'))

if __name__ == "__main__":
    # Creamos servidor de eco y escuchamos
    serv = socketserver.UDPServer((IP, PUERTO), EchoHandler)
    print("Listening...")
    serv.serve_forever()
