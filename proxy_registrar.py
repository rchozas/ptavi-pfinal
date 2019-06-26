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
        
        

# abrir el socket, lo configuramos y lo atamos a un servidor/puerto
def abrir_socket(path, ip, puerto, linea):

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
        my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        my_socket.connect((ip, int(puerto)))
        my_socket.send(bytes(linea, 'utf-8') + b"\r\n")
        Puerto = str(puerto)
        Evento = "send to"
        decodificar = linea.decode('utf-8')
        info_log(LOG, Evento, ip, Puerto, decodificar)
        
def registro_usuarios(dicc_clientes, cliente):

    # comprobacion de usuario registrado
    if cliente not in dicc_clientes.keys():
        info = "0"
    else:
        info = dicc_clientes[cliente]
    return info

def actualiza_dicc(dicc_clientes):
    Lista_clientes = []
    for cliente in dicc_clientes:
        Expires = int(dicc_clientes[cliente][3])
        Tiempo = int(time.time())
        if Tiempo >= Expires:
            Lista_clientes.append(cliente)
    for No_usuario in Lista_clientes:
        del dicc_clientes[No_usuario]


class ProxyRegistrarHandler(socketserver.DatagramRequestHandler):

    dicc_clientes = {}
    NONCE = random.getrandbits(100)

    def handle(self):
        # actualizacion del dicc por si ha expirado algun cliente
        
        actualiza_dicc(self.dicc_clientes)        
        #IP = self.client_address[0]        
        #PUERTO = self.client_address[1]        

        while 1:
            # Leyendo línea a línea lo que nos envía el cliente
            linea = self.rfile.read()
            print(linea)
            metodo = linea.decode('utf-8').split(' ')[0].upper()
            metodos = ["REGISTER", "INVITE", "ACK", "BYE"]
            IP = self.client_address[0]
            PUERTO = self.client_address[1]

            Evento = "Received from"
            info_log(LOG, Evento, IP, PUERTO, linea.decode('utf-8'))
            if len(linea.decode('utf-8')) >= 2:
                if metodo == "REGISTER":
                    lista = linea.decode('utf-8').split('\r\n')
                    
                    cliente = lista[0].split(':')[1]
                    
                    puertoua = lista[0].split(':')[1].split(' ')[0]
                    if len(lista) == 4:
                        enviar = "SIP/2.0 401 Unauthorized\r\n"
                        enviar += "WWW Authenticate: Digest nonce="
                        enviar += str(self.NONCE)
                        enviar += "\r\n\r\n"
                        print(enviar)
                        self.wfile.write(bytes(enviar, 'utf-8'))
                        print("Enviamos: " + enviar)
                        Evento = "Send to "
                        info_log(LOG, Evento, IP, PUERTO, enviar)
                elif metodo == "INVITE":
                    direcc = linea.decode('utf-8').split(" ")[1]
                    User = direcc.split(":")[1]
                    u_registrado = registro_usuarios(self.dicc_clientes, User)
                    if u_registrado == "0":
                        enviar = "SIP/2.0 404 User Not Found\r\n\r\n"
                        Evento = "Send to "
                        info_log(LOG, Evento, IP, PUERTO, enviar)
                        self.wfile.write(bytes(enviar, 'utf-8'))
                        ####
                    else:
                        IP_registrado= u_resgistrado[0]
                        PUERTO_registrado= int(u_registrado[1])
                elif metodo == "ACK":
                    direcc = linea.decode('utf-8').split(" ")[1]
                    User = direcc.split(":")[1]
                    u_registrado = registro_usuarios(self.dicc_clientes, User)
                    if u_registrado == "0":
                        enviar = "SIP/2.0 404 User Not Found\r\n\r\n"
                        Evento = "Send to "
                        info_log(LOG, Evento, IP, PUERTO, enviar)
                        self.wfile.write(bytes(enviar, 'utf-8'))
                    else:
                        IP_registrado= u_resgistrado[0]
                        PUERTO_registrado= int(u_registrado[1])
                        abrir_socket(LOG, IP_registrado, PUERTO_registrado, linea)
                elif metodo == "BYE":
                    direcc = linea.decode('utf-8').split(" ")[1]
                    User = direcc.split(":")[1]
                    u_registrado = registro_usuarios(self.dicc_clientes, User)
                    if u_registrado == "0":
                        enviar = "SIP/2.0 404 User Not Found\r\n\r\n"
                        Evento = "Send to "
                        info_log(LOG, Evento, IP, PUERTO, enviar)
                        self.wfile.write(bytes(enviar, 'utf-8'))
                    else:
                        IP_registrado= u_resgistrado[0]
                        PUERTO_registrado= int(u_registrado[1])
                elif metodo and metodo not in metodos:
                    enviar = "SIP/2.0 405 Method Not Allowed\r\n\r\n"
                    self.wfile.write(bytes(enviar, 'utf-8'))
                    Evento = "Send to "
                    info_log(LOG, Evento, IP, PUERTO, enviar)
                else:
                    enviar = "SIP/2.0 400 Bad request\r\n\r\n"
                    self.wfile.write(bytes(enviar, 'utf-8'))
                    Evento = "Send to "
                    info_log(LOG, Evento, IP, PUERTO, enviar)
            else:
                break
                
    def register2json(self):
        with open("registered.json", "w") as file_json:
            json.dump(self.dicc_usuarios, file_json, sort_keys=True, indent=4)

    def json2resgistered(self):
        with open("registered.json", "r") as datos_fichero:
            self.dicc_usuarios = json.load(datos_fichero)
       
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
        
        fichero = open(PATH, "a")
        Linea = "Usuario\tIP\tPuerto\t" + "Fecha de Registro\t"
        Linea += "Tiempo de expiracion\r\n"       
        fichero.write(Linea)
        fichero.close()
        
    except:
        sys.exit("Usage: python proxy_registrar.py config")
    try: 
        enviar = NOMB_SERVIDOR + " Listening at port " + PUERTO_SERVIDOR + "..."
        print(enviar)        
        PUERTO1= int(PUERTO_SERVIDOR)
        Evento = "Starting..."        
        info_log(LOG, Evento, "", "", "")
        IP = "127.0.0.1"
        serv = socketserver.UDPServer((IP, PUERTO1), ProxyRegistrarHandler)
        serv.serve_forever()
    except:
        sys.exit("Usage: Error")
        
