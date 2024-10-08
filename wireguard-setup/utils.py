import subprocess
from models import Tenant

#WG_QUICK_COMMAND = ["sudo", "wg-quick"]
WG_QUICK_COMMAND = ["wg-quick"]

def generate_public_key(private_key):
    process = subprocess.Popen(
        ["wg", "pubkey"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        
    )
    stdout, stderr = process.communicate(input=private_key.encode())
    print(process.stdout)
    print(process.stderr)
    if process.returncode != 0:
        raise RuntimeError(f"Failed to generate public key: {stderr.decode().strip()}")
    return stdout.decode().strip()


def find_available_port():

    current_ports = {tenant.listen_port for tenant in Tenant.query.all()}
    port = 51820
    while port in current_ports:
        port += 1
    return port


def restart_wireguard(server_name):
    try:
        t=subprocess.run(WG_QUICK_COMMAND + ["down", server_name],check=True,capture_output = True,text = True)
        #print(t.stdout)
        #print(t.stderr)
        
    except subprocess.CalledProcessError:
        pass  # Ignore errors from 'wg-quick down'
    v=subprocess.run(WG_QUICK_COMMAND + ["up", server_name], stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
#,check=True,capture_output = True,text = True)
    print(v.stdout)
    print(v.stderr)
