import os
from flask import Flask, jsonify, request, abort
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from models import db, Tenant, Peer, Client
import utils
import base64

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# Initialize the database
with app.app_context():
    db.create_all()

WIREGUARD_CONFIG_DIR = "/etc/wireguard/"


@app.route("/tenants", methods=["POST"])
def add_tenant():
    data = request.get_json()
    name = data["name"]
    address = data["address"]

    if Tenant.query.filter_by(name=name).first():
        return {"error": f" {name} already exists"}, 400
    if Tenant.query.filter_by(address=address).first():
        return {"error": f"address {address} already exists"}, 400

    private_key = data.get("private_key") or os.popen("wg genkey").read().strip()
    public_key = utils.generate_public_key(private_key)
    listen_port = utils.find_available_port()

    new_tenant = Tenant(
        name=name,
        address=address,
        public_key=public_key,
        listen_port=listen_port,
        private_key=private_key,
    )

    try:
        db.session.add(new_tenant)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {"error": "Database integrity error, tenant not added"}, 500
    except SQLAlchemyError as e:
        db.session.rollback()
        return {"error": str(e)}, 500

    config_content = f"""[Interface]
Address = {new_tenant.address}
ListenPort = {new_tenant.listen_port}
PrivateKey = {new_tenant.private_key}"""
    config_path = os.path.join(WIREGUARD_CONFIG_DIR, f"{new_tenant.name}.conf")
    with open(config_path, "w") as config_file:
        config_file.write(config_content)

    utils.restart_wireguard(new_tenant.name)  # Restart WireGuard to apply changes

    return new_tenant.to_dict(), 201


@app.route("/clients", methods=["POST"])
def add_client():
    data = request.get_json()
    name = data["name"]
    address = data["address"]

    if Client.query.filter_by(name=name).first():
        return {"error": f"Client {name} already exists"}, 400
    if Client.query.filter_by(address=address).first():
        return {"error": f"address {address} already exists"}, 400

    private_key = data.get("private_key") or os.popen("wg genkey").read().strip()
    public_key = utils.generate_public_key(private_key)
    allowed_ips = "0.0.0.0/0"

    new_client = Client(
        name=name,
        private_key=private_key,
        public_key=public_key,
        allowed_ips=allowed_ips,
        address=address,
    )

    try:
        db.session.add(new_client)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {"error": "Database integrity error, client not added"}, 500
    except SQLAlchemyError as e:
        db.session.rollback()
        return {"error": str(e)}, 500
        
    client_config = f"""[Interface]
Address = {new_client.address}
PrivateKey = {new_client.private_key}"""
    config_path = os.path.join(WIREGUARD_CONFIG_DIR, f"{new_client.name}.conf")
    with open(config_path, "w") as config_file:
        config_file.write(client_config)

    return new_client.to_dict(), 201


@app.route("/tenants/<tenant_name>/peers", methods=["POST"])
def add_peer_to_tenant(tenant_name):
    data = request.get_json()
    client_name = data["client_name"]
    endpoint = data["endpoint"]

    tenant = Tenant.query.filter_by(name=tenant_name).first_or_404()
    client = Client.query.filter_by(name=client_name).first()

    if not client:
        abort(404, description=f"Client {client_name} not found")

    try:
        new_peer = Peer(
            tenant_id=tenant.id,
            client_name=client.name,
            public_key=client.public_key,
            allowed_ips=client.allowed_ips,
            endpoint=endpoint,
            persistent_keepalive=data.get("persistent_keepalive", 25),
        )
        db.session.add(new_peer)
        db.session.commit()

        peer_config_tenant = f"""
[Peer]
PublicKey = {client.public_key}
AllowedIPs = {client.allowed_ips}"""

        tenant_config_path = os.path.join(WIREGUARD_CONFIG_DIR, f"{tenant.name}.conf")
        with open(tenant_config_path, "a") as config_file:
            config_file.write(peer_config_tenant)

        peer_config_client = f"""
[Peer]
PublicKey = {tenant.public_key}
Endpoint = {endpoint}:{tenant.listen_port}
AllowedIPs = 0.0.0.0/0"""

        client_config_path = os.path.join(WIREGUARD_CONFIG_DIR, f"{client.name}.conf")
        with open(client_config_path, "a") as config_file:
            config_file.write(peer_config_client)

        utils.restart_wireguard(tenant.name)  # Restart WireGuard to apply changes

        with open(client_config_path, "r") as config_file:
            client_conf_content = config_file.read()

        return (
           
                {
                    "peer": new_peer.to_dict(),
                    "client_conf_base64": base64.b64encode(
                        client_conf_content.encode()
                    ).decode(),
                }
            ,
            201,
        )

    except IntegrityError:
        db.session.rollback()
        return {"error": "Database integrity error, peer not added"}, 500
    except SQLAlchemyError as e:
        db.session.rollback()
        return {"error": str(e)}, 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
