#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Programa cliente que abre un socket a un servidor
"""

import socket
import sys
import os
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
from uaserver import XMLHandler
from uaserver import info_log

if __name__ == "__main__":

    if len(sys.argv) != 4:
        sys.exit("Usage: python uaclient.py config method option")
    try:
        FICHERO = sys.argv[1]
        METHOD = sys.argv[2].upper()
        OPTION = sys.argv[3]

    # FICHERO -config-(fichero de config XML), METHOD (método SIP),
    # OPTION (parámetro opcional según el método utilizado)

    except:
        sys.exit("Usage: python uaclient.py config method option")
    try:
        if os.path.exists(FICHERO) is False:
            sys.exit("El fichero no existe")

        # leer datos del fichero XML mediante el parser
        parser = make_parser()
        cHandler = XMLHandler()
        parser.setContentHandler(cHandler)
        parser.parse(open(FICHERO))
        lista = cHandler.get_tags()

        # info dentro fichero XML
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
        sys.exit("Usage: python uaclient.py config method option")

    # Metodos SIP: REGISTER, INVITE, ACK, BYE
    # BYE (100 Trying, 180 Ringing, 200 OK)
    try:
        Metodos_SIP = ["REGISTER", "INVITE", "BYE"]
        metodo_sip = METHOD + " sip:"
        if METHOD == "REGISTER":
            # Fichero log, escribe evento
            Evento = "Starting ..."
            info_log(LOG, Evento, " ", " ", " ")
            LINE = metodo_sip + USERNAME + ":" + UAS_PUERTO + " SIP/2.0\r\n"
            LINE += "Expires: " + OPTION + "\r\n"
            print(LINE)
        elif METHOD == "INVITE":
            LINE = metodo_sip + OPTION + " SIP/2.0\r\n"
            LINE += "Content-Type: application/sdp\r\n\r\n"
            LINE += "v=0\r\n"
            LINE += "o=" + USERNAME + " " + UAS_IP + "\r\n"
            LINE += "s=sesionactiva\r\n"
            LINE += "t=0\r\n"
            LINE += "m=audio " + RTP_AUDIO + " " + "RTP\r\n"
            print(LINE)
        elif METHOD == "BYE":
            LINE = metodo_sip + OPTION + " SIP/2.0\r\n"
    except:
        sys.exit("Usage: python uaclient.py config method option")

# Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    my_socket.connect((RPROXY_IP, int(RPROXY_PUERTO)))
    my_socket.send(bytes(LINE, 'utf-8') + b"\r\n")
    print("Enviando: ")
    # enviando datos
    my_socket.send(bytes(LINE, 'utf-8') + b"\r\n")
    # informacion que se recibe, decodificando
    data = my_socket.recv(1024)
    info_decode = data.decode('utf-8')
    print(info_decode)

    Evento = " Received from "
    info_log(LOG, Evento, RPROXY_IP, RPROXY_PUERTO, info_decode)
    print("Terminando socket...")

# si recibe las respuestas 100 Trying, 180 Ringing, 200 OK
    r = data.decode('utf-8').split("\r\n\r\n")[0:-1]
    if r == ["SIP/2.0 100 Trying", "SIP/2.0 180 Ringing", "SIP/2.0 200 OK"]:
        LINEACK = "ACK sip:" + LOGIN + IP + " SIP/2.0\r\n"
        print("Enviando: " + LINEACK)
        my_socket.send(bytes(LINE, 'utf-8') + b'\r\n')
        data = my_socket.recv(1024)

# finalizando el socket, evento fin
print("Terminando el socket")
my_socket.close()
Evento = " Finishing."
info_log(LOG, Evento, " ", " ", " ")
print("Fin.")
