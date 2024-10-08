from flask import Flask, request, jsonify
from utils.openvpn import initialize_pki, generate_server_cert, generate_client_cert, generate_client_config
from models import db, Server, Client
from config import SERVER_CONFIG_DIR, CLIENT_CONFIG_DIR
import logging
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///openvpn.db'
db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/initialize', methods=['POST'])
def initialize():
    try:
        initialize_pki()
        return jsonify({"status": "PKI initialized"})
    except Exception as e:
        logging.error(f'Error initializing PKI: {str(e)}')
        return jsonify({"status": "Error", "message": str(e)}), 500

@app.route('/create_server', methods=['POST'])
def create_server():
    try:
        data = request.json
        server_name = data['server_name']
        server_ip = data['server_ip']
        server_subnet = data['server_subnet']

        # Check if server name or IP already exists
        if Server.query.filter_by(name=server_name).first():
            return jsonify({"status": "Error", "message": "Server name already exists"}), 400
        if Server.query.filter_by(ip=server_ip).first():
            return jsonify({"status": "Error", "message": f"IP address {server_ip} belongs to another server"}), 400

        logging.debug(f'Creating server with name: {server_name}, IP: {server_ip}, Subnet: {server_subnet}')
        server_port = generate_server_cert(server_name, server_ip, server_subnet)
        logging.debug('Creating Server Class')
        new_server = Server(name=server_name, ip=server_ip, subnet=server_subnet, port=server_port)
        logging.debug('Adding to DB')
        db.session.add(new_server)
        db.session.commit()
        logging.debug(f'Server created with port: {server_port}')
        return jsonify({"status": "Server created", "port": server_port})
    except Exception as e:
        logging.error(f'Error creating server: {str(e)}')
        return jsonify({"status": "Error", "message": str(e)}), 500

@app.route('/create_client', methods=['POST'])
def create_client():
    try:
        data = request.json
        client_name = data['client_name']
        endpoint = data['endpoint']
        server = Server.query.filter_by(name=data['server_name']).first()

        if not server:
            return jsonify({"status": "Error", "message": "Server not found"}), 404

        # Check if client name already exists for this server
        if Client.query.filter_by(name=client_name, server_id=server.id).first():
            return jsonify({"status": "Error", "message": "Client name already exists for this server"}), 400

        client_dir = os.path.join(CLIENT_CONFIG_DIR, f'{server.name}_clients')
        os.makedirs(client_dir, exist_ok=True)

        generate_client_cert(client_name, server.name)
        client_config = generate_client_config(client_name, endpoint, server.port, client_dir,server.name)
        new_client = Client(name=client_name, endpoint=endpoint, server_id=server.id)
        db.session.add(new_client)
        db.session.commit()
        return jsonify({"status": "Client created", "config": client_config})
    except Exception as e:
        logging.error(f'Error creating client: {str(e)}')
        return jsonify({"status": "Error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000)

