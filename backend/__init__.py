from flask import Flask
from flask_cors import CORS


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    CORS(app)

    from backend import db, contract, ipfs

    app.register_blueprint(db.bp)
    app.register_blueprint(contract.bp)
    app.register_blueprint(ipfs.bp)

    return app
