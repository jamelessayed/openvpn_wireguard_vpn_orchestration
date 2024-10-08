from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Server(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    ip = db.Column(db.String(50), unique=True, nullable=False)
    subnet = db.Column(db.String(50), nullable=False)
    port = db.Column(db.Integer, nullable=False)

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    endpoint = db.Column(db.String(50), nullable=False)
    server_id = db.Column(db.Integer, db.ForeignKey('server.id'), nullable=False)
    server = db.relationship('Server', back_populates='clients')

Server.clients = db.relationship('Client', order_by=Client.id, back_populates='server')

