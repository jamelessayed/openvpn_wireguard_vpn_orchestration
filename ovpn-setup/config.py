import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EASYRSA_DIR = os.path.join(BASE_DIR, 'easyrsa')
CLIENT_CONFIG_DIR = os.path.join(BASE_DIR, 'client_confs')
SERVER_CONFIG_DIR = os.path.join(BASE_DIR, 'server_confs')
PORT_START = 1194

