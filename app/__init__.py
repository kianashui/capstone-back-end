from flask import Flask

def create_app(test_config=None):
    app = Flask(__name__)

    from .routes import trip_bp
    app.register_blueprint(trip_bp)

    return app