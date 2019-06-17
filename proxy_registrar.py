#!/usr/bin/python3
# -*- coding: utf-8 -*-


import socketserver
import socket
import sys
import os
import json
import time
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
from uaserver import info_log
import uaclient
import random


class XMLHandler(ContentHandler):
    def __init__(self):
        self.lista = []
        self.dic = {'server': ['name', 'ip', 'puerto'],
                    'database': ['path', 'passwdpath'],
                    'log': ['path']}

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

def actualiza_dicc(dicc_cliente):
    Lista_clientes = []
    for clientes in dicc_clientes:
        Expires = int(dicc_clientes[clientes][4])
        Tiempo = int(time.time())
        if Tiempo >= Expires:
            Lista_clientes.append(clientes)
    for No_usuario in List:
        del dicc_cliente[No_usuario]

class ProxyRegistrar(socketserver.DatagramRequestHandler):
   
    dicc_usuario = {}
    NONCE = random.getrandbits(100)
    
    
    def handle(self):
        #actualizacion del dicc por si ha expirado algun cliente
        actualiza_dicc(self.dicc_cliente)

        
        info = line.decode('utf-8')
        if (len(info) >= 2):
            if (info.split()[0].upper() == "REGISTER"):
                direccion = info.split()[1]
                expiracion = int(info.split()[4])
                expires = int(time.time()) + expiracion
                tiempo_expiracion = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(expires))
                info_usuarios["direccion"] = self.client_address[0]
                info_usuarios["expires"] = tiempo_expiracion
                if (expiracion == 0):
                    del self.dicc_usuario[direccion]
                    self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
                    if(len(self.dicc_usuario) != 0):
                        del self.dicc_usuario[direccion]
                        self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
                elif "@" in direccion:
                    self.dicc_usuario[direccion] = info_usuarios
                    self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
                print(self.dicc_usuario)

    def register2json(self):
        file_json = json.dumps(self.dicc_usuario)
        with open("registered.json", "w") as file_json:
            json.dump(self.dicc_usuario, file_json, sort_keys=True, indent=4)

    def json2resgistered(self):
        try:
            file_json = open("registered.json", "r")
            self.dicc_usuario = json.load(file_json)
        except:
            self.dicc_usuario = {}


if __name__ == "__main__":
    try:
        FICHERO = sys.argv[1]
        parser = make_parser()
        cHandler = XMLHandler()
        parser.setContentHandler(cHandler)
        parser.parse(open(FICHERO))
        lista = cHandler.get_tags()
        
        # info fichero XML dentro de las variables
        NOMB_SERVIDOR = lista[0]['server']['name']
        IP_SERVIDOR = lista[0]['server']['ip']
        PUERTO_SERVIDOR = lista[0]['server']['puerto']
        PATH = lista[1]['database']['path']
        PASSWD = lista[1]['database']['passwdpath']
        LOG = lista[2]['log']['path']
    except:
        sys.exit("Usage: python proxy_registrar.py config")
    try:
        enviar = NOM_SERVIDOR + "Listening at port" + PUERTO_SERVIDOR + "..."
        PUERTO = int(PUERTO_SERVIDOR)
        Evento = "Starting..."
        info_log(LOG, Evento, "", "", "")
        IP = "127.0.0.1"
        serv = socketserver.UDPServer((IP, PUERTO), ProxyRegistrar)
        serv.serve_forever()
    except:
        sys.exit("Usage: python proxy_registrar.py config")
