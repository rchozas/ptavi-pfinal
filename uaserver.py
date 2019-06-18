#!/usr/bin/python3
# -*- coding: utf-8 -*-

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
                Evento = "Received from "
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
                    Evento = "Send to "
                    info_log(LOG, Evento, RPROXY_IP, RPROXY_PUERTO, enviar)
                elif metodo == "ACK":
                    Evento = "sending RTP "
                    info_log(LOG, Evento, " ", " ", " ")
                    aEjecutar = "./mp32rtp -i " + UAS_IP + "-p" + RTP_AUDIO
                    aEjecutar += " < " + AUDIO
                    print("vamos a ejecutar", aEjecutar)
                    os.system(aEjecutar)
                elif metodo == "BYE":
                    enviar = "SIP/2.0 200 OK\r\n\r\n"
                    self.wfile.write(bytes(enviar, 'utf-8'))
                    Evento = "Send to "
                    info_log(LOG, Evento, RPROXY_IP, RPROXY_PUERTO, enviar)
                elif metodo and metodo not in metodos:
                    enviar = "SIP/2.0 405 Method Not Allowed\r\n\r\n"
                    self.wfile.write(bytes(enviar, 'utf-8'))
                    Evento = "Send to "
                    info_log(LOG, Evento, RPROXY_IP, RPROXY_PUERTO, enviar)
                else:
                    enviar = "SIP/2.0 400 Bad request\r\n\r\n"
                    self.wfile.write(bytes(enviar, 'utf-8'))
                    Evento = "Send to "
                    info_log(LOG, Evento, RPROXY_IP, RPROXY_PUERTO, enviar)
            # Si no hay más líneas salimos del bucle infinito
            if not line:
                break
            


if __name__ == "__main__":

    try:
        FICHERO = sys.argv[1]
        parser = make_parser()
        cHandler = XMLHandler()
        parser.setContentHandler(cHandler)
        parser.parse(open(FICHERO))
        lista = cHandler.get_tags()

        # info fichero XML
        USERNAME = lista[0]['account']['username']
        PASSWD = lista[0]['account']['passwd']
        UAS_IP = lista[1]['uaserver']['ip']
        UAS_PUERTO = lista[1]['uaserver']['puerto']
        RTP_AUDIO = lista[2]['rtpaudio']['puerto']
        RPROXY_IP = lista[3]['regproxy']['ip']
        RPROXY_PUERTO = lista[3]['regproxy']['puerto']
        LOG = lista[4]['log']['path']
        AUDIO = lista[5]['audio']['path']
    except IndexError:
        sys.exit("Usage: python uaserver.py config")
    try:
        puerto = int(UAS_PUERTO)
        serv = socketserver.UDPServer((UAS_IP, puerto), EchoHandler)
        print("Listening...")
        serv.serve_forever()
    except IndexError:
        Evento = "Error... "
        info_log(LOG, Evento, RPROXY_IP, RPROXY_PUERTO, " ")
        sys.exit("Error: The Server is not listening")
