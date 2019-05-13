#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Clase (y programa principal) para un servidor de eco en UDP simple
"""

import socketserver
import socket
import sys
import os
import os.path
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import time

# clase XMLHandler siguiendo el esquema de etiquetas de la practica 3.
# para manejar el fichero de configuracion XML


class XMLHandler(ContentHandler):

    def __init__(self):
        self.lista = []
        self.dic = {'account': ['username', 'passwd'],
                    'uaserver': ['ip', 'puerto'],
                    'rtpaudio': ['puerto'],
                    'regproxy': ['ip', 'puerto'],
                    'log': ['path'],
                    'audio': ['path']}

    def startElement(self, name, attrs):
        """
        starElement almacena las etiquetas, los atributos y su contenido.
        """
        if name in self.dic:
            dicc = {}
            for atributo in self.dic[name]:
                dicc[atributo] = attrs.get(atributo, "")
                dic_final = {name: dicc}
            self.lista.append(dic_final)

    def get_tags(self):
        """
        Devuelve las etiquetas, atributos y el contenido.
        """
        return self.lista


def info_log(archivo, evento, ip, puerto, linea):
    fichero = open(archivo, "a")
    tiempo = time.strftime("%Y%m%d%H%M%S", time.gmtime(time.time()))
    if evento != "Starting..." and evento != "Finishing.":
        port = str(puerto)
        info = tiempo + " " + evento + ip + ":" + port + ": " + linea + "\r\n"
    elif evento == "Error":
        info = tiempo + " " + evento + ": Server is not listening in the port"
        info += ip + ":" + "puerto" + puerto + "\r\n"
    else:
        info = tiempo + " " + evento + "\r\n"
    fichero.write(info)
    fichero.close()


if len(sys.argv) != 4:
    sys.exit("Usage: python uaserver.py config")
try:
    IP = sys.argv[1]
    PUERTO = int(sys.argv[2])
    FICHERO = sys.argv[3]
    if not os.path.exists(FICHERO):
        sys.exit("Usage: python uaserver.py config")
except:
    sys.exit("Usage: python uaserver.py config")


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
                # Fichero log, escribe evento
                Evento = "Received from"
                info_log(LOG, Evento, RPROXY_IP, RPROXY_PUERTO, line.decode('utf-8'))
                if metodo == "INVITE":
                    enviar = b"SIP/2.0 100 Trying\r\n\r\n"
                    enviar += b"SIP/2.0 180 Ringing\r\n\r\n"
                    enviar += b"SIP/2.0 200 OK\r\n\r\n"
                    enviar += "Content-Type: application/sdp\r\n\r\n"
                    enviar += "v=0\r\n"
                    enviar += "o=" + USERNAME + " " + UAS_IP + "\r\n"
                    enviar += "s=sesionactiva\r\n"
                    enviar += "t=0\r\n"
                    enviar += "m=audio" + RTP_AUDIO + " " + "RTP\r\n\r\n"
                    # envio de respuesta
                    self.wfile.write(bytes(enviar, 'utf-8'))
                    # Fichero log, escribe evento
                    Evento = "Send to"
                    info_log(LOG, Evento, RPROXY_IP, RPROXY_PUERTO, enviar)
                elif metodo == "ACK":
                    Evento = "sending RTP"
                    info_log(LOG, Evento, " ", " ", " ")
                    aEjecutar = "./mp32rtp -i 127.0.0.1 -p 23032 < " + FICHERO
                    print("vamos a ejecutar", aEjecutar)
                    os.system(aEjecutar)
                elif metodo == "BYE":
                    enviar = "SIP/2.0 200 OK\r\n\r\n"
                    self.wfile.write(bytes(enviar, 'utf-8'))
                    Evento = "Send to"
                    info_log(LOG, Evento, RPROXY_IP, RPROXY_PUERTO, enviar)
                elif metodo and metodo not in metodos:
                    enviar = "SIP/2.0 405 Method Not Allowed\r\n\r\n"
                    self.wfile.write(bytes(enviar, 'utf-8')
                    Evento ="Send to"
                    info_log(LOG, Evento, RPROXY_IP, RPROXY_PUERTO, enviar)
                else:
                    enviar = "SIP/2.0 400 Bad request\r\n\r\n"
                    self.wfile.write(bytes(enviar, 'utf-8'))
                    Evento = "Send to"
                    info_log(LOG, Evento, RPROXY_IP, RPROXY_PUERTO, enviar)
            else:
                break

            # Si no hay más líneas salimos del bucle infinito
            if not line:
                break
            # print(line.decode('utf-8'))


if __name__ == "__main__":
    # Creamos servidor de eco y escuchamos
    serv = socketserver.UDPServer((IP, PUERTO), EchoHandler)
    print("Listening...")
    serv.serve_forever()
