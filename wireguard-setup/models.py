from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Tenant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    address = db.Column(db.String(120), nullable=False)
    public_key = db.Column(db.String(44), nullable=False)
    private_key = db.Column(db.String(44), nullable=False)
    listen_port = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "address": self.address,
            "public_key": self.public_key,
            "private_key": self.private_key,
            "listen_port": self.listen_port,
        }


class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    private_key = db.Column(db.String(44), nullable=False)
    public_key = db.Column(db.String(44), nullable=False)
    allowed_ips = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "private_key": self.private_key,
            "public_key": self.public_key,
            "allowed_ips": self.allowed_ips,
            "address": self.address,
        }


class Peer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenant.id"), nullable=False)
    client_name = db.Column(db.String(80), nullable=False)
    public_key = db.Column(db.String(44), nullable=False)
    allowed_ips = db.Column(db.String(120), nullable=False)
    endpoint = db.Column(db.String(120))
    persistent_keepalive = db.Column(db.Integer, nullable=False, default=25)

    tenant = db.relationship("Tenant", backref=db.backref("peers", lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "client_name": self.client_name,
            "public_key": self.public_key,
            "allowed_ips": self.allowed_ips,
            "endpoint": self.endpoint,
            "persistent_keepalive": self.persistent_keepalive,
        }
