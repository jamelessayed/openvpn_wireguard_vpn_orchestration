import os
import subprocess
import base64
from config import EASYRSA_DIR, CLIENT_CONFIG_DIR, SERVER_CONFIG_DIR, PORT_START

def run_command(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        raise Exception(f'Command failed: {command}\nstdout: {stdout}\nstderr: {stderr}')
    return stdout, stderr

def initialize_pki():
    if not os.path.exists(EASYRSA_DIR):
        run_command(f'make-cadir {EASYRSA_DIR}')
    
    easyrsa_path = os.path.join(EASYRSA_DIR, 'easyrsa')
    if not os.path.exists(easyrsa_path):
        raise Exception(f'EasyRSA not found at {easyrsa_path}')
    
    commands = [
        f'cd {EASYRSA_DIR} && ./easyrsa init-pki',
        f'cd {EASYRSA_DIR} && ./easyrsa --batch build-ca nopass'
    ]
    for command in commands:
        run_command(command)

def generate_server_cert(server_name, server_ip, server_subnet):
    server_dir = os.path.join(SERVER_CONFIG_DIR, server_name)
    os.makedirs(server_dir, exist_ok=True)
    
    easyrsa_dir = os.path.join(server_dir, 'easy-rsa')
    run_command(f'make-cadir {easyrsa_dir}')
    run_command(f'cd {easyrsa_dir} && ./easyrsa init-pki')
    run_command(f'cd {easyrsa_dir} && ./easyrsa --batch build-ca nopass')

    commands = [
        f'cd {easyrsa_dir} && echo -e "\\n\\n\\n\\n\\n\\n\\n" | ./easyrsa gen-req {server_name} nopass',
        f'cd {easyrsa_dir} && echo -e "\\n\\n\\n\\n\\n\\n\\n" | ./easyrsa --batch sign-req server {server_name}',
        f'cd {easyrsa_dir} && ./easyrsa gen-dh',
        f'openvpn --genkey secret {easyrsa_dir}/ta.key'
    ]
    for command in commands:
        run_command(command)
    
    server_port = PORT_START + len(os.listdir(SERVER_CONFIG_DIR)) - 1
    
    with open(os.path.join(server_dir, f'{server_name}.conf'), 'w') as f:
        f.write(f"""port {server_port}
proto udp
dev tun
ca {easyrsa_dir}/pki/ca.crt
cert {easyrsa_dir}/pki/issued/{server_name}.crt
key {easyrsa_dir}/pki/private/{server_name}.key
dh {easyrsa_dir}/pki/dh.pem
auth SHA256
tls-auth {easyrsa_dir}/ta.key 0
topology subnet
server {server_ip} {server_subnet}
ifconfig-pool-persist {server_dir}/ipp.txt
keepalive 10 120
cipher AES-256-CBC
data-ciphers AES-256-GCM:AES-128-GCM:AES-256-CBC
user nobody
group nogroup
persist-key
persist-tun
status {server_dir}/openvpn-status.log
verb 3
""")
    
    os.makedirs('/etc/openvpn', exist_ok=True)
    os.system(f' cp {os.path.join(server_dir, f"{server_name}.conf")} /etc/openvpn/{server_name}.conf')
    subprocess.Popen([ 'openvpn', '--config', f'/etc/openvpn/{server_name}.conf'])
    
    return server_port

def generate_client_cert(client_name, server_name):
    easyrsa_dir = os.path.join(SERVER_CONFIG_DIR, server_name, 'easy-rsa')
    commands = [
        f'cd {easyrsa_dir} && echo -e "\\n\\n\\n\\n\\n\\n\\n" | ./easyrsa gen-req {client_name} nopass',
        f'cd {easyrsa_dir} &&  echo -e "\\n\\n\\n\\n\\n\\n\\n" | ./easyrsa --batch sign-req client {client_name}'
    ]
    for command in commands:
        run_command(command)

def generate_client_config(client_name, endpoint, server_port, client_dir,server_name):
    config_path = os.path.join(client_dir, f'{client_name}.ovpn')
    os.makedirs(client_dir, exist_ok=True)
    
    easyrsa_dir = os.path.join(SERVER_CONFIG_DIR, server_name, 'easy-rsa')
    
    with open(config_path, 'w') as f:
        f.write(f"""client
dev tun
proto udp
remote {endpoint} {server_port}
resolv-retry infinite
nobind
user nobody
group nogroup
persist-key
persist-tun
remote-cert-tls server
cipher AES-256-CBC
auth SHA256
key-direction 1
verb 3
<ca>
""")
        with open(os.path.join(easyrsa_dir, 'pki', 'ca.crt')) as ca:
            f.write(ca.read())
        f.write("</ca>\n<cert>\n")
        with open(os.path.join(easyrsa_dir, 'pki', 'issued', f'{client_name}.crt')) as cert:
            f.write(cert.read())
        f.write("</cert>\n<key>\n")
        with open(os.path.join(easyrsa_dir, 'pki', 'private', f'{client_name}.key')) as key:
            f.write(key.read())
        f.write("</key>\n<tls-auth>\n")
        with open(os.path.join(easyrsa_dir, 'ta.key')) as ta:
            f.write(ta.read())
        f.write("</tls-auth>")
    
    with open(config_path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')

