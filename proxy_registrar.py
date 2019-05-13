#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Clase (y programa principal) para un servidor de eco en UDP simple
"""

import socketserver
import sys
import json
import time
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import uaclient


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


class SIPRegisterHandler(socketserver.DatagramRequestHandler):
    """
    Echo server class
    """

    dicc_usuario = {}

    def handle(self):

        info_usuarios = {}

        IP = self.client_address[0]
        print("IP cliente: ", IP)
        PORT = self.client_address[1]
        print("Puerto: ", str(PORT))
        line = self.rfile.read()

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

    PORT = int(sys.argv[1])
    serv = socketserver.UDPServer(('', PORT), SIPRegisterHandler)
    print("Lanzando servidor UDP de eco...")
    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        print("Finalizado servidor")
